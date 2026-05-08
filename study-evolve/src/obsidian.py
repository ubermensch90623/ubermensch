"""Obsidian vault exporter.

Converts records.csv + review_schedule.csv into a Markdown tree under
{vault}/StudyEvolve/ that Obsidian can read directly:

  StudyEvolve/
    index.md                        # overall stats + dataview-friendly index
    records/<id>-<date>-<slug>.md   # one note per WRONG record (correct ones skipped by default)
    by-area/<subject>__<area>.md    # per-area aggregates with wiki-links
    by-failtag/<tag>.md             # per-fail-tag aggregates
    daily/<YYYY-MM-DD>.md           # one note per study day

Every note uses YAML frontmatter + [[wiki-links]] so Obsidian's
backlinks and dataview plugin work without extra setup.

Idempotent: re-running with the same data yields byte-identical files
(no timestamps in body). Only files under StudyEvolve/ are touched.
User notes elsewhere in the vault are never modified.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
from datetime import date
from pathlib import Path

import pandas as pd

EXPORT_SUBDIR = "StudyEvolve"


def resolve_vault(cli_vault: str | None) -> Path:
    """Return validated vault path. CLI flag wins; env OBSIDIAN_VAULT is fallback."""
    raw = cli_vault or os.environ.get("OBSIDIAN_VAULT")
    if not raw:
        raise ValueError(
            "vault 경로가 지정되지 않았습니다. "
            "--vault PATH 또는 OBSIDIAN_VAULT 환경변수를 설정하세요."
        )
    path = Path(raw).expanduser().resolve()
    if not path.exists():
        raise ValueError(f"vault 경로가 존재하지 않습니다: {path}")
    if not path.is_dir():
        raise ValueError(f"vault 경로가 디렉터리가 아닙니다: {path}")
    return path


_FILENAME_INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def sanitize_filename(s: str, max_len: int = 80) -> str:
    """Make string safe as a filename component on Win/macOS/Linux + Obsidian.

    Replaces filesystem-invalid chars with '_', collapses whitespace, trims dots.
    Korean / unicode letters are preserved.
    """
    if not s:
        return "_"
    out = _FILENAME_INVALID.sub("_", str(s))
    out = re.sub(r"\s+", "_", out).strip("._-")
    if not out:
        out = "_"
    if len(out) > max_len:
        h = hashlib.sha1(out.encode("utf-8")).hexdigest()[:8]
        out = out[:max_len - 9] + "_" + h
    return out


def _yaml_scalar(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace("\n", " ").replace('"', '\\"')
    if s == "":
        return '""'
    return f'"{s}"'


def _frontmatter(d: dict) -> str:
    lines = ["---"]
    for k, v in d.items():
        if isinstance(v, list):
            inline = "[" + ", ".join(_yaml_scalar(x) for x in v) + "]"
            lines.append(f"{k}: {inline}")
        else:
            lines.append(f"{k}: {_yaml_scalar(v)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def _link(rel_path: str) -> str:
    """Build Obsidian wiki-link from a path relative to the vault root."""
    name = rel_path.rsplit("/", 1)[-1].removesuffix(".md")
    return f"[[{name}]]"


def _record_slug(row: pd.Series) -> str:
    base = sanitize_filename(str(row["problem_no"]))
    return f"{int(row['id'])}-{row['date']}-{base}"


def _area_slug(subject: str, area: str) -> str:
    return f"{sanitize_filename(subject)}__{sanitize_filename(area)}"


def _tag_slug(tag: str) -> str:
    return sanitize_filename(tag)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    # Idempotent write: skip if identical
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")


def _record_note(row: pd.Series, schedule_df: pd.DataFrame) -> tuple[str, str]:
    """Return (relative_path, content) for one record's note."""
    slug = _record_slug(row)
    rel = f"{EXPORT_SUBDIR}/records/{slug}.md"

    fm = {
        "id": int(row["id"]),
        "date": row["date"],
        "subject": row["subject"],
        "area": row["area"],
        "source": row["source"],
        "problem_no": row["problem_no"],
        "is_correct": bool(row["is_correct"]),
        "solve_time_sec": int(row["solve_time_sec"]),
        "difficulty": int(row["difficulty"]) if pd.notna(row["difficulty"]) else None,
        "fail_tag": row.get("fail_tag", ""),
        "tags": ["study-evolve", "wrong" if not row["is_correct"] else "correct"],
    }

    body = [_frontmatter(fm)]
    body.append(f"# {int(row['id'])} — {row['subject']}/{row['area']}/{row['problem_no']}")
    body.append("")
    body.append("> 오답" if not row["is_correct"] else "> 정답")
    body.append("")
    body.append(f"- 풀이 시간: {int(row['solve_time_sec'])}초")
    if pd.notna(row["difficulty"]):
        body.append(f"- 난이도: {int(row['difficulty'])}/5")
    body.append(f"- 출처: {row['source']}")
    if row.get("fail_tag"):
        body.append(f"- 실패 태그: {row['fail_tag']}")
    if row.get("memo"):
        body.append(f"- 메모: {row['memo']}")
    body.append("")

    if not row["is_correct"]:
        body.append("## 복습 일정")
        for col, label in [("review_1d", "1일"), ("review_3d", "3일"), ("review_7d", "7일")]:
            v = row.get(col, "")
            if v:
                done = _is_review_done(schedule_df, int(row["id"]), col.replace("review_", ""))
                mark = "✓" if done else "  "
                body.append(f"- [{mark}] {label} 후: [[{v}]]")
        body.append("")

    body.append("## 관련")
    body.append(f"- [[{_area_slug(row['subject'], row['area'])}]]")
    if row.get("fail_tag"):
        body.append(f"- [[{_tag_slug(row['fail_tag'])}]]")
    body.append(f"- [[{row['date']}]]")
    body.append("")

    return rel, "\n".join(body)


def _is_review_done(schedule_df: pd.DataFrame, record_id: int, review_type: str) -> bool:
    if schedule_df is None or schedule_df.empty:
        return False
    mask = (schedule_df["record_id"] == record_id) & (schedule_df["review_type"] == review_type)
    sub = schedule_df[mask]
    if sub.empty:
        return False
    return bool(sub.iloc[0]["is_done"])


def _area_note(subject: str, area: str, area_records: pd.DataFrame) -> tuple[str, str]:
    slug = _area_slug(subject, area)
    rel = f"{EXPORT_SUBDIR}/by-area/{slug}.md"

    total = len(area_records)
    correct = int(area_records["is_correct"].sum())
    wrong = total - correct
    accuracy = (correct / total * 100) if total else 0.0
    avg_solve = float(area_records["solve_time_sec"].mean()) if total else 0.0

    fm = {
        "type": "area-index",
        "subject": subject,
        "area": area,
        "total": total,
        "wrong": wrong,
        "correct": correct,
        "accuracy_pct": round(accuracy, 1),
        "avg_solve_sec": round(avg_solve, 1),
        "tags": ["study-evolve", "area-index"],
    }

    body = [_frontmatter(fm)]
    body.append(f"# {subject} / {area}")
    body.append("")
    body.append(f"- 총: **{total}** / 정답: **{correct}** / 오답: **{wrong}**")
    body.append(f"- 정답률: **{accuracy:.1f}%**")
    body.append(f"- 평균 풀이 시간: **{int(avg_solve)}초**")
    body.append("")

    wrongs = area_records[~area_records["is_correct"]].sort_values("date", ascending=False)
    if not wrongs.empty:
        body.append("## 오답 목록")
        for _, r in wrongs.iterrows():
            tag = r.get("fail_tag", "")
            body.append(f"- [[{_record_slug(r)}]] — {tag}".rstrip(" —"))
        body.append("")

    tag_counts = (
        area_records[~area_records["is_correct"]]
        .groupby("fail_tag").size().sort_values(ascending=False)
    )
    if not tag_counts.empty:
        body.append("## 실패 태그 누적")
        for tag, n in tag_counts.items():
            if not tag:
                continue
            body.append(f"- [[{_tag_slug(tag)}]]: {int(n)}회")
        body.append("")

    return rel, "\n".join(body)


def _tag_note(tag: str, tag_records: pd.DataFrame) -> tuple[str, str]:
    slug = _tag_slug(tag)
    rel = f"{EXPORT_SUBDIR}/by-failtag/{slug}.md"

    total = len(tag_records)
    fm = {
        "type": "failtag-index",
        "fail_tag": tag,
        "total": total,
        "tags": ["study-evolve", "failtag-index"],
    }

    body = [_frontmatter(fm)]
    body.append(f"# 실패 태그: {tag}")
    body.append("")
    body.append(f"누적: **{total}회**")
    body.append("")
    body.append("## 발생 기록")
    for _, r in tag_records.sort_values("date", ascending=False).iterrows():
        body.append(f"- [[{_record_slug(r)}]] — {r['subject']}/{r['area']}")
    body.append("")
    return rel, "\n".join(body)


def _daily_note(d: str, day_records: pd.DataFrame) -> tuple[str, str]:
    rel = f"{EXPORT_SUBDIR}/daily/{d}.md"
    total = len(day_records)
    correct = int(day_records["is_correct"].sum())
    wrong = total - correct
    accuracy = (correct / total * 100) if total else 0.0
    avg_solve = float(day_records["solve_time_sec"].mean()) if total else 0.0

    fm = {
        "type": "daily",
        "date": d,
        "total": total,
        "wrong": wrong,
        "correct": correct,
        "accuracy_pct": round(accuracy, 1),
        "avg_solve_sec": round(avg_solve, 1),
        "tags": ["study-evolve", "daily"],
    }

    body = [_frontmatter(fm)]
    body.append(f"# {d}")
    body.append("")
    body.append(f"- 총: {total} / 정답: {correct} / 오답: {wrong}")
    body.append(f"- 정답률: {accuracy:.1f}%")
    body.append(f"- 평균 풀이 시간: {int(avg_solve)}초")
    body.append("")

    body.append("## 풀이 기록")
    for _, r in day_records.sort_values("id").iterrows():
        marker = "✓" if r["is_correct"] else "✗"
        body.append(f"- {marker} [[{_record_slug(r)}]] — {r['subject']}/{r['area']}")
    body.append("")

    tag_counts = (
        day_records[~day_records["is_correct"]]
        .groupby("fail_tag").size().sort_values(ascending=False)
    )
    if not tag_counts.empty:
        body.append("## 오늘의 실패 태그")
        for tag, n in tag_counts.items():
            if not tag:
                continue
            body.append(f"- [[{_tag_slug(tag)}]]: {int(n)}회")
        body.append("")

    return rel, "\n".join(body)


def _index_note(records_df: pd.DataFrame) -> tuple[str, str]:
    rel = f"{EXPORT_SUBDIR}/index.md"
    total = len(records_df)
    correct = int(records_df["is_correct"].sum())
    wrong = total - correct
    accuracy = (correct / total * 100) if total else 0.0

    fm = {
        "type": "index",
        "total": total,
        "wrong": wrong,
        "correct": correct,
        "accuracy_pct": round(accuracy, 1),
        "tags": ["study-evolve", "index"],
    }

    body = [_frontmatter(fm)]
    body.append("# Study Evolve — Index")
    body.append("")
    body.append(f"- 총 풀이 수: **{total}**")
    body.append(f"- 정답: **{correct}** / 오답: **{wrong}**")
    body.append(f"- 정답률: **{accuracy:.1f}%**")
    body.append("")
    body.append("## 영역별 인덱스")
    for (subject, area), _ in records_df.groupby(["subject", "area"]):
        body.append(f"- [[{_area_slug(subject, area)}]]")
    body.append("")

    tag_counts = (
        records_df[~records_df["is_correct"]]
        .groupby("fail_tag").size().sort_values(ascending=False)
    )
    if not tag_counts.empty:
        body.append("## 실패 태그 인덱스")
        for tag, n in tag_counts.items():
            if not tag:
                continue
            body.append(f"- [[{_tag_slug(tag)}]] — {int(n)}회")
        body.append("")

    body.append("## 일일 노트")
    for d in sorted(records_df["date"].unique(), reverse=True):
        body.append(f"- [[{d}]]")
    body.append("")
    body.append("## Dataview 예시")
    body.append("```dataview")
    body.append("table id, subject, area, fail_tag, difficulty")
    body.append('from #study-evolve and #wrong')
    body.append("sort date desc")
    body.append("```")
    body.append("")
    return rel, "\n".join(body)


def export(records_df: pd.DataFrame, schedule_df: pd.DataFrame, vault: Path,
           include_correct: bool = False) -> dict:
    """Write the StudyEvolve/ tree under vault. Return summary dict."""
    target_root = vault / EXPORT_SUBDIR

    # Clean only StudyEvolve subtree (preserve user's other notes).
    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.mkdir(parents=True, exist_ok=True)

    if records_df.empty:
        _write(vault / f"{EXPORT_SUBDIR}/index.md",
               _frontmatter({"type": "index", "total": 0, "tags": ["study-evolve", "index"]}) +
               "\n# Study Evolve — Index\n\n기록이 없습니다.\n")
        return {"records": 0, "areas": 0, "tags": 0, "days": 0}

    df = records_df.copy()
    if "fail_tag" not in df.columns:
        df["fail_tag"] = ""
    df["fail_tag"] = df["fail_tag"].fillna("").astype(str)

    # Records
    rec_subset = df if include_correct else df[~df["is_correct"]]
    written = 0
    for _, row in rec_subset.iterrows():
        rel, content = _record_note(row, schedule_df)
        _write(vault / rel, content)
        written += 1

    # Areas
    areas = 0
    for (subject, area), area_df in df.groupby(["subject", "area"]):
        rel, content = _area_note(subject, area, area_df)
        _write(vault / rel, content)
        areas += 1

    # Tags (wrong only)
    tags = 0
    wrong_df = df[~df["is_correct"]]
    if not wrong_df.empty:
        for tag, tag_df in wrong_df.groupby("fail_tag"):
            if not tag:
                continue
            rel, content = _tag_note(tag, tag_df)
            _write(vault / rel, content)
            tags += 1

    # Daily
    days = 0
    for d, day_df in df.groupby("date"):
        rel, content = _daily_note(d, day_df)
        _write(vault / rel, content)
        days += 1

    # Index
    rel, content = _index_note(df)
    _write(vault / rel, content)

    return {
        "records": written,
        "areas": areas,
        "tags": tags,
        "days": days,
        "vault": str(vault),
        "subdir": EXPORT_SUBDIR,
    }
