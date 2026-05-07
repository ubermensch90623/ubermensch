"""study-evolve — CLI entry point."""

from __future__ import annotations

import argparse
import sys
from datetime import date

import pandas as pd

from src import cli, recommender, review, storage
from src.analyzer import (
    calculate_area_stats,
    calculate_fail_tag_stats,
    calculate_overall_stats,
    calculate_subject_stats,
    detect_risk_signals,
    load_recent_records,
)
from src.constants import RECORDS_CSV, SCHEDULE_CSV
from src.recommender import explain_weak_area
from src.utils import format_pct, format_secs, print_table


def cmd_init(_args: argparse.Namespace) -> None:
    records_existed, schedule_existed = storage.ensure_data_files()
    print("[초기화 완료]")
    print(f"- {RECORDS_CSV.relative_to(RECORDS_CSV.parent.parent)} {'확인됨' if records_existed else '생성됨'}")
    print(f"- {SCHEDULE_CSV.relative_to(SCHEDULE_CSV.parent.parent)} {'확인됨' if schedule_existed else '생성됨'}")
    print("이제 python main.py add 로 기록을 추가하세요.")


def cmd_add(_args: argparse.Namespace) -> None:
    storage.ensure_data_files()
    cli.add_interactive()


def cmd_stats(args: argparse.Namespace) -> None:
    storage.ensure_data_files()
    df = storage.load_records()
    if df.empty:
        print("기록이 없습니다. python main.py add 또는 python main.py sample 로 시작하세요.")
        return

    if args.days:
        df = load_recent_records(df, days=args.days)
        period_label = f"최근 {args.days}일"
    else:
        period_label = "전체 기간"

    if df.empty:
        print(f"{period_label} 기록이 없습니다.")
        return

    overall = calculate_overall_stats(df)
    print("[학습 통계]")
    print(f"기간: {period_label}")
    print(f"총 풀이 수: {overall['total']}")
    print(f"정답 수: {overall['correct']}")
    print(f"오답 수: {overall['wrong']}")
    print(f"전체 정답률: {format_pct(overall['correct'], overall['total'])}")
    print(f"평균 풀이 시간: {format_secs(overall['avg_solve_sec'])}")

    print()
    print("[과목별 정답률]")
    subj = calculate_subject_stats(df)
    rows = [
        (r["subject"], int(r["total"]), format_pct(int(r["correct"]), int(r["total"])), format_secs(r["avg_solve_sec"]))
        for _, r in subj.iterrows()
    ]
    print_table(rows, ["과목", "풀이 수", "정답률", "평균 풀이 시간"])

    print()
    print("[영역별 정답률]")
    area = calculate_area_stats(df)
    rows = [
        (r["subject"], r["area"], int(r["total"]), format_pct(int(r["correct"]), int(r["total"])), format_secs(r["avg_solve_sec"]))
        for _, r in area.iterrows()
    ]
    print_table(rows, ["과목", "영역", "풀이 수", "정답률", "평균 풀이 시간"])

    print()
    print("[실패 태그 빈도]")
    tags = calculate_fail_tag_stats(df)
    if tags.empty:
        print("  (오답 태그 없음)")
    else:
        rows = [(r["fail_tag"], int(r["count"]), f"{r['ratio']*100:.1f}%") for _, r in tags.iterrows()]
        print_table(rows, ["실패 태그", "횟수", "비율"])

    print()
    print("[위험 신호]")
    risks = detect_risk_signals(df)
    if not risks["by_tag"] and not risks["by_combo"]:
        print("  (3회 이상 반복된 실패 태그 없음)")
        return
    for tag, count in risks["by_tag"]:
        print(f"- {tag}: {count}회 반복")
    if risks["by_combo"]:
        print()
        print("  · 영역별 조합:")
        for subject, area_name, tag, count in risks["by_combo"]:
            print(f"    - {subject} / {area_name} / {tag}: {count}회")


def cmd_recommend(_args: argparse.Namespace) -> None:
    storage.ensure_data_files()
    records_df = storage.load_records()
    schedule_df = storage.load_schedule()
    if records_df.empty:
        print("기록이 없습니다. python main.py sample 로 샘플 데이터를 만들어 보세요.")
        return

    rec = recommender.generate_recommendations(records_df, schedule_df)
    overall_avg_solve = (
        load_recent_records(records_df, days=30)["solve_time_sec"].mean()
        if not load_recent_records(records_df, days=30).empty else 0.0
    )

    print("[내일 학습 추천]")
    print()

    weak = rec["weak_areas"]
    if weak.empty:
        print("1. 약점 영역이 발견되지 않았습니다. 새 영역을 시도하세요.")
    else:
        for i, (_, row) in enumerate(weak.iterrows(), start=1):
            count = max(3, min(int(row["wrong"]) + 2, 7))
            print(f"{i}. {row['subject']} - {row['area']} {count}문제")
            reasons = explain_weak_area(row, rec["fail_tag_stats"], rec["risk_combos"], overall_avg_solve)
            if reasons:
                print("이유:")
                for r in reasons:
                    print(f"- {r}")
            print()

    print(f"{len(weak) + 1}. 복습 대상")
    due = rec["due_reviews"]
    if due.empty:
        print("- 오늘 복습 대상 없음")
    else:
        # Group by date+subject+area
        for _, row in due.head(5).iterrows():
            print(f"- {row['date']}에 틀린 {row['subject']} {row['area']} 문제 ({row['problem_no']}, {row['review_type']})")
    print()

    print(f"{len(weak) + 2}. 성공 경험용")
    success = rec["success_area"]
    if success.empty:
        print("- 정답률 높은 영역이 아직 없습니다.")
    else:
        for _, row in success.iterrows():
            count = 3
            print(f"- {row['subject']} {row['area']} {count}문제")
            print("이유:")
            print(f"- 최근 정답률 {row['accuracy']*100:.0f}%")
            print(f"- 학습 시작 워밍업용")
    print()

    print("[내일 행동 1개]")
    print(rec["action"])


def cmd_review(_args: argparse.Namespace) -> None:
    storage.ensure_data_files()
    records_df = storage.load_records()
    schedule_df = storage.load_schedule()
    today = date.today().isoformat()
    rep = review.generate_daily_report(records_df, schedule_df, today=today)

    if rep["empty"]:
        print(f"오늘 기록이 없습니다. python main.py add로 먼저 기록하세요.")
        return

    print("[오늘의 학습 리포트]")
    print()
    print(f"날짜: {rep['date']}")
    print()
    print(f"총 풀이 문제 수: {rep['total']}")
    print(f"정답률: {rep['accuracy_text']}")
    print(f"평균 풀이 시간: {rep['avg_solve_text']}")
    print()

    tags = rep["fail_tag_stats"]
    if tags.empty:
        print("오늘 가장 많이 나온 실패 태그: (없음)")
    else:
        print("오늘 가장 많이 나온 실패 태그:")
        for i, (_, row) in enumerate(tags.head(5).iterrows(), start=1):
            print(f"{i}. {row['fail_tag']}: {int(row['count'])}회")
    print()

    print("오늘의 핵심 버그:")
    print(rep["core_bug"])
    print()

    print("내일 수정할 행동 1개:")
    print(rep["action"])
    print()

    rc = rep["review_counts"]
    print("복습 예정:")
    print(f"- 1일 후 복습: {rc['1d']}문제")
    print(f"- 3일 후 복습: {rc['3d']}문제")
    print(f"- 7일 후 복습: {rc['7d']}문제")


def cmd_due(_args: argparse.Namespace) -> None:
    storage.ensure_data_files()
    schedule_df = storage.load_schedule()
    records_df = storage.load_records()
    if schedule_df.empty:
        print("복습 스케줄이 비어 있습니다.")
        return
    today_ts = pd.Timestamp(date.today())
    due = schedule_df[(schedule_df["review_date_dt"] <= today_ts) & (~schedule_df["is_done"])]
    if due.empty:
        print("오늘 복습 대상 없음.")
        return
    if records_df.empty:
        print("records.csv가 비어 있어 매핑할 수 없습니다.")
        return
    merged = due.merge(
        records_df[["id", "subject", "area", "source", "problem_no", "fail_tag", "memo"]],
        left_on="record_id", right_on="id", how="left",
    ).sort_values("review_date_dt")

    print("[오늘 복습 대상]")
    print()
    for i, (_, row) in enumerate(merged.iterrows(), start=1):
        print(f"{i}. {row['subject']} / {row['area']} / {row['problem_no']}")
        print(f"   - 원래 실패 태그: {row['fail_tag'] or '-'}")
        print(f"   - 원래 메모: {row['memo'] or '-'}")
        print(f"   - 복습 유형: {row['review_type']}")
        print()
    print("복습 후에는 python main.py done-review 로 완료 처리하세요.")


def cmd_done_review(_args: argparse.Namespace) -> None:
    storage.ensure_data_files()
    cli.done_review_interactive()


def cmd_export(_args: argparse.Namespace) -> None:
    storage.ensure_data_files()
    print("[내보내기]")
    print("학습 기록:")
    print(f"  {RECORDS_CSV}")
    print()
    print("복습 스케줄:")
    print(f"  {SCHEDULE_CSV}")
    print()
    print("이 파일을 Google Sheets 또는 Excel에서 열 수 있습니다.")


def cmd_sample(_args: argparse.Namespace) -> None:
    created = storage.generate_sample_data()
    print(f"[샘플 데이터 생성 완료: {created}건]")
    print("이제 python main.py stats / recommend / review 를 실행해 보세요.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="study-evolve",
        description="개인 AlphaEvolve식 학습 진화 시스템 — NCS·경제학 점수 상승 엔진",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="data 폴더와 CSV 파일 생성").set_defaults(func=cmd_init)
    sub.add_parser("add", help="학습 기록 추가 (인터랙티브)").set_defaults(func=cmd_add)

    p_stats = sub.add_parser("stats", help="학습 통계")
    p_stats.add_argument("--days", type=int, default=None, help="최근 N일 기준")
    p_stats.set_defaults(func=cmd_stats)

    sub.add_parser("recommend", help="내일 학습 추천").set_defaults(func=cmd_recommend)
    sub.add_parser("review", help="오늘의 학습 리포트").set_defaults(func=cmd_review)
    sub.add_parser("due", help="오늘 복습할 문제 목록").set_defaults(func=cmd_due)
    sub.add_parser("done-review", help="복습 완료 처리 (인터랙티브)").set_defaults(func=cmd_done_review)
    sub.add_parser("export", help="CSV 경로 안내").set_defaults(func=cmd_export)
    sub.add_parser("sample", help="샘플 데이터 생성").set_defaults(func=cmd_sample)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
