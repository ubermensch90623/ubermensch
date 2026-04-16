"""argparse 기반 CLI: analyze / save / list / show / delete / convert / stats."""
from __future__ import annotations

import argparse
import json as jsonlib
import os
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .analyzer import AnalysisResult, analyze, convert_to_scale
from .i18n import t
from .models import ExamRecord, Section, generate_record_id, record_to_dict
from .storage import (
    append_record,
    default_history_path,
    delete_record,
    find_record,
    load_history,
    save_history,
)


EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_USAGE = 2
EXIT_IO = 3


# ---------------------- 색상 (ANSI) ----------------------

_RESET = "\033[0m"
_BOLD = "\033[1m"
_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_DIM = "\033[2m"


def _should_use_color(no_color_flag: bool) -> bool:
    if no_color_flag:
        return False
    if os.environ.get("NO_COLOR"):
        return False
    # Windows 구형 cmd 에서 색 깨질 수 있으니 기본 비활성
    if os.name == "nt" and not os.environ.get("WT_SESSION") and not os.environ.get("ANSICON"):
        return False
    return sys.stdout.isatty()


def _c(text: str, code: str, enable: bool) -> str:
    return f"{code}{text}{_RESET}" if enable else text


# ---------------------- Section 인자 파싱 ----------------------


def parse_section_arg(spec: str) -> Section:
    """'NAME:SCORE:MAX:WEIGHT' 포맷 파싱. 이름에 콜론이 들어갈 가능성은 무시."""
    parts = spec.split(":")
    if len(parts) != 4:
        raise argparse.ArgumentTypeError(
            f"--section 은 'NAME:SCORE:MAX:WEIGHT' 형식이어야 합니다 (입력: {spec!r})"
        )
    name, score_s, max_s, weight_s = parts
    try:
        score = float(score_s)
        max_score = float(max_s)
        weight = float(weight_s)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"--section 숫자 파싱 실패: {e}") from e
    if max_score <= 0:
        raise argparse.ArgumentTypeError("max_score 는 0보다 커야 합니다")
    if score < 0:
        raise argparse.ArgumentTypeError("score 는 0 이상이어야 합니다")
    if weight <= 0:
        raise argparse.ArgumentTypeError("weight 는 0보다 커야 합니다")
    return Section(name=name.strip(), score=score, max_score=max_score, weight=weight)


# ---------------------- 포매터 ----------------------


def _verdict_label(passed: Optional[bool], use_color: bool) -> str:
    if passed is None:
        return _c(t("pending"), _YELLOW, use_color)
    if passed:
        return _c(t("pass"), _GREEN + _BOLD, use_color)
    return _c(t("fail"), _RED + _BOLD, use_color)


def format_analysis(result: AnalysisResult, use_color: bool, as_json: bool) -> str:
    if as_json:
        return _analysis_to_json(result)

    r = result.record
    lines: List[str] = []
    header = f"[{r.agency}] {r.exam_name} {t('analysis_header')} ({r.date})"
    lines.append(_c(header, _BOLD + _CYAN, use_color))
    lines.append("─" * 60)

    if result.weight_rescaled:
        lines.append(
            _c(
                f"⚠ {t('weight_rescaled')} (원래 합계: {result.original_weight_sum:g})",
                _YELLOW,
                use_color,
            )
        )

    for section, pct, weighted in result.section_breakdown:
        lines.append(
            f"  {section.name:<18}"
            f"{section.score:>7.2f} / {section.max_score:<6g} "
            f"({pct:5.2f}%)  → 환산 {weighted:.2f}점"
        )

    lines.append("─" * 60)
    lines.append(f"  {t('total')}:     {result.total:.2f} / 100")

    if result.cutoff is not None:
        lines.append(f"  {t('cutoff')}:  {result.cutoff:.2f}")
        gap = result.gap if result.gap is not None else 0.0
        gap_color = _GREEN if gap >= 0 else _RED
        sign = "+" if gap >= 0 else ""
        lines.append(f"  {t('gap')}:     {_c(f'{sign}{gap:.2f}점', gap_color, use_color)}")
        lines.append(f"  {t('verdict')}:    {_verdict_label(result.passed, use_color)}")
    else:
        lines.append(f"  {t('no_cutoff')}")

    if result.weakest is not None and len(result.section_breakdown) > 1:
        lines.append("")
        lines.append(
            f"  {t('weakest')}: {result.weakest.name} "
            f"({result.weakest.percentage():.2f}%) — {t('recommend_focus')}"
        )
    if r.record_id:
        lines.append(_c(f"  {t('record_id')}: {r.record_id}", _DIM, use_color))

    return "\n".join(lines)


def _analysis_to_json(result: AnalysisResult) -> str:
    payload = {
        "record": record_to_dict(result.record),
        "total": round(result.total, 4),
        "cutoff": result.cutoff,
        "gap": round(result.gap, 4) if result.gap is not None else None,
        "passed": result.passed,
        "sections": [
            {
                "name": s.name,
                "score": s.score,
                "max_score": s.max_score,
                "weight": s.weight,
                "percentage": round(pct, 4),
                "weighted": round(w, 4),
            }
            for (s, pct, w) in result.section_breakdown
        ],
        "strongest": result.strongest.name if result.strongest else None,
        "weakest": result.weakest.name if result.weakest else None,
        "weight_rescaled": result.weight_rescaled,
        "original_weight_sum": result.original_weight_sum,
    }
    return jsonlib.dumps(payload, ensure_ascii=False, indent=2)


# ---------------------- 서브커맨드 핸들러 ----------------------


def _build_record_from_args(args: argparse.Namespace) -> ExamRecord:
    sections = args.section or []
    if args.interactive and not sections:
        sections = _prompt_sections()
    if not sections:
        raise SystemExit("최소 1개 이상의 --section 이 필요합니다 (또는 --interactive)")
    record = ExamRecord(
        agency=args.agency,
        date=args.date,
        sections=sections,
        exam_name=args.exam_name or "필기전형",
        cutoff=args.cutoff,
        notes=args.notes or "",
    )
    record.record_id = generate_record_id(record)
    return record


def _prompt_sections() -> List[Section]:
    print("대화형 영역 입력 (빈 영역명 입력 시 종료)")
    sections: List[Section] = []
    while True:
        name = input("영역명: ").strip()
        if not name:
            break
        score = float(input("  점수: ").strip())
        max_score = float(input("  만점: ").strip())
        weight = float(input("  가중치(100 기준): ").strip())
        sections.append(Section(name=name, score=score, max_score=max_score, weight=weight))
    return sections


def cmd_analyze(args: argparse.Namespace) -> int:
    record = _build_record_from_args(args)
    result = analyze(record)
    print(format_analysis(result, use_color=_should_use_color(args.no_color), as_json=args.json))
    if args.save:
        path = Path(args.data_file) if args.data_file else default_history_path()
        try:
            rid = append_record(path, record)
            print(f"\n✓ {t('saved')} ({t('record_id')}: {rid})")
        except OSError as e:
            print(f"저장 실패: {e}", file=sys.stderr)
            return EXIT_IO
    if result.passed is None:
        return EXIT_PASS
    return EXIT_PASS if result.passed else EXIT_FAIL


def cmd_save(args: argparse.Namespace) -> int:
    if args.from_json:
        with open(args.from_json, "r", encoding="utf-8") as f:
            data = jsonlib.load(f)
        from .models import record_from_dict

        record = record_from_dict(data)
        record.record_id = generate_record_id(record)
    else:
        record = _build_record_from_args(args)
    path = Path(args.data_file) if args.data_file else default_history_path()
    try:
        rid = append_record(path, record)
    except OSError as e:
        print(f"저장 실패: {e}", file=sys.stderr)
        return EXIT_IO
    print(f"✓ {t('saved')} ({t('record_id')}: {rid})")
    return EXIT_PASS


def cmd_list(args: argparse.Namespace) -> int:
    path = Path(args.data_file) if args.data_file else default_history_path()
    records = load_history(path)
    if args.agency:
        records = [r for r in records if args.agency in r.agency]
    if args.passed_only:
        records = [r for r in records if r.passed() is True]
    if args.failed_only:
        records = [r for r in records if r.passed() is False]
    key = {
        "date": lambda r: r.date,
        "gap": lambda r: (r.gap() if r.gap() is not None else 0.0),
        "total": lambda r: r.total(),
    }.get(args.sort or "date")
    records = sorted(records, key=key, reverse=(args.sort in {"gap", "total"}))
    if not records:
        print(t("empty_history"))
        return EXIT_PASS
    if args.json:
        print(jsonlib.dumps([record_to_dict(r) for r in records], ensure_ascii=False, indent=2))
        return EXIT_PASS
    use_color = _should_use_color(args.no_color)
    print(f"{'ID':<10}{'일자':<12}{'기관':<22}{'총점':>8}{'커트':>8}{'격차':>9}  판정")
    print("─" * 76)
    for r in records:
        gap = r.gap()
        passed = r.passed()
        gap_s = f"{gap:+.2f}" if gap is not None else "  -  "
        cutoff_s = f"{r.cutoff:.2f}" if r.cutoff is not None else "  -  "
        verdict = _verdict_label(passed, use_color)
        print(
            f"{r.record_id:<10}{r.date:<12}{r.agency:<22}"
            f"{r.total():>8.2f}{cutoff_s:>8}{gap_s:>9}  {verdict}"
        )
    return EXIT_PASS


def cmd_show(args: argparse.Namespace) -> int:
    path = Path(args.data_file) if args.data_file else default_history_path()
    record = find_record(path, args.record_id)
    if record is None:
        print(t("not_found"), file=sys.stderr)
        return EXIT_IO
    result = analyze(record)
    print(format_analysis(result, use_color=_should_use_color(args.no_color), as_json=args.json))
    return EXIT_PASS


def cmd_delete(args: argparse.Namespace) -> int:
    path = Path(args.data_file) if args.data_file else default_history_path()
    ok = delete_record(path, args.record_id)
    if not ok:
        print(t("not_found"), file=sys.stderr)
        return EXIT_IO
    print(f"✓ {t('deleted')}")
    return EXIT_PASS


def cmd_convert(args: argparse.Namespace) -> int:
    converted = convert_to_scale(args.score, args.max, args.to)
    if args.weight is not None:
        weighted = (args.score / args.max) * args.weight
        if args.json:
            print(jsonlib.dumps(
                {"converted": round(converted, 4), "weighted": round(weighted, 4)},
                ensure_ascii=False,
            ))
        else:
            print(f"환산({args.to}점 만점): {converted:.4f}")
            print(f"가중 기여: {weighted:.4f} (weight={args.weight})")
    else:
        if args.json:
            print(jsonlib.dumps({"converted": round(converted, 4)}, ensure_ascii=False))
        else:
            print(f"환산({args.to}점 만점): {converted:.4f}")
    return EXIT_PASS


def cmd_stats(args: argparse.Namespace) -> int:
    path = Path(args.data_file) if args.data_file else default_history_path()
    records = load_history(path)
    if args.agency:
        records = [r for r in records if args.agency in r.agency]
    if not records:
        print(t("empty_history"))
        return EXIT_PASS
    judged = [r for r in records if r.passed() is not None]
    total_count = len(records)
    pass_count = sum(1 for r in judged if r.passed())
    pass_rate = (pass_count / len(judged) * 100) if judged else 0.0
    gaps = [r.gap() for r in judged if r.gap() is not None]
    avg_gap = (sum(gaps) / len(gaps)) if gaps else 0.0

    all_sections: List[Section] = [s for r in records for s in r.sections]
    avg_by_name: dict = {}
    for s in all_sections:
        avg_by_name.setdefault(s.name, []).append(s.percentage())
    section_avgs = {name: sum(v) / len(v) for name, v in avg_by_name.items()}

    if args.json:
        print(jsonlib.dumps(
            {
                "total_records": total_count,
                "pass_rate_percent": round(pass_rate, 2),
                "average_gap": round(avg_gap, 2),
                "section_averages": {k: round(v, 2) for k, v in section_avgs.items()},
            },
            ensure_ascii=False,
            indent=2,
        ))
        return EXIT_PASS

    print(f"{t('total_records')}: {total_count}")
    print(f"{t('pass_rate')}: {pass_rate:.2f}% ({pass_count}/{len(judged)})")
    print(f"{t('avg_gap')}: {avg_gap:+.2f}점")
    if section_avgs:
        print("영역별 평균 백분율:")
        for name, avg in sorted(section_avgs.items(), key=lambda kv: kv[1]):
            marker = ""
            if avg == min(section_avgs.values()):
                marker = "  ← 최약"
            elif avg == max(section_avgs.values()):
                marker = "  ← 최강"
            print(f"  {name:<22} {avg:6.2f}%{marker}")
    return EXIT_PASS


# ---------------------- 파서 ----------------------


def _add_common_input_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--agency", required=False, help="기관명 (예: 서민금융진흥원)")
    p.add_argument("--date", required=False, help="시험 일자 ISO (YYYY-MM-DD)")
    p.add_argument("--exam-name", dest="exam_name", default=None, help="시험명 (기본: 필기전형)")
    p.add_argument(
        "--section",
        type=parse_section_arg,
        action="append",
        help="영역: 'NAME:SCORE:MAX:WEIGHT' (반복 가능)",
    )
    p.add_argument("--cutoff", type=float, default=None, help="합격 커트라인 (100점 만점)")
    p.add_argument("--notes", default=None, help="자유 메모")
    p.add_argument("-i", "--interactive", action="store_true", help="영역을 대화형으로 입력")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="exam_analyzer",
        description="공공기관 필기전형 점수 분석 도구",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--data-file", dest="data_file", help="이력 JSON 경로 (기본: ~/.exam_history.json)")
    parser.add_argument("--no-color", dest="no_color", action="store_true", help="ANSI 색상 비활성")
    parser.add_argument("--json", action="store_true", help="JSON 출력")

    subs = parser.add_subparsers(dest="command", required=True)

    p_analyze = subs.add_parser("analyze", help="점수 분석 (합격/격차)")
    _add_common_input_flags(p_analyze)
    p_analyze.add_argument("--save", action="store_true", help="이력에 저장")
    p_analyze.set_defaults(func=cmd_analyze)

    p_save = subs.add_parser("save", help="기록 저장")
    _add_common_input_flags(p_save)
    p_save.add_argument("--from-json", dest="from_json", help="JSON 파일에서 기록 읽기")
    p_save.set_defaults(func=cmd_save)

    p_list = subs.add_parser("list", help="이력 표로 출력")
    p_list.add_argument("--agency", help="기관명 부분일치 필터")
    p_list.add_argument("--passed-only", dest="passed_only", action="store_true")
    p_list.add_argument("--failed-only", dest="failed_only", action="store_true")
    p_list.add_argument("--sort", choices=["date", "gap", "total"], default="date")
    p_list.set_defaults(func=cmd_list)

    p_show = subs.add_parser("show", help="단일 기록 상세")
    p_show.add_argument("record_id", help="기록 ID (전체 또는 접두사)")
    p_show.set_defaults(func=cmd_show)

    p_delete = subs.add_parser("delete", help="기록 삭제")
    p_delete.add_argument("record_id", help="기록 ID")
    p_delete.set_defaults(func=cmd_delete)

    p_convert = subs.add_parser("convert", help="점수 환산 유틸")
    p_convert.add_argument("--score", type=float, required=True)
    p_convert.add_argument("--max", type=float, required=True)
    p_convert.add_argument("--weight", type=float, default=None)
    p_convert.add_argument("--to", type=float, default=100.0, help="목표 스케일 (기본 100)")
    p_convert.set_defaults(func=cmd_convert)

    p_stats = subs.add_parser("stats", help="이력 통계")
    p_stats.add_argument("--agency", help="기관명 부분일치 필터")
    p_stats.set_defaults(func=cmd_stats)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001 - 최후의 보루
        print(f"오류: {e}", file=sys.stderr)
        return EXIT_IO
