"""CSV storage — init, append, load, schedule, sample seeder."""

from __future__ import annotations

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

from .constants import (
    DATA_DIR,
    RECORDS_CSV,
    RECORDS_HEADER,
    SCHEDULE_CSV,
    SCHEDULE_HEADER,
)
from .models import StudyRecord
from .utils import now_iso


def ensure_data_files() -> tuple[bool, bool]:
    """Create data dir and CSV files (with headers) if missing.

    Returns (records_existed, schedule_existed).
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    records_existed = RECORDS_CSV.exists()
    schedule_existed = SCHEDULE_CSV.exists()
    if not records_existed:
        _write_header(RECORDS_CSV, RECORDS_HEADER)
    if not schedule_existed:
        _write_header(SCHEDULE_CSV, SCHEDULE_HEADER)
    return records_existed, schedule_existed


def _write_header(path: Path, header: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)


def next_id() -> int:
    if not RECORDS_CSV.exists():
        return 1
    df = load_records()
    if df.empty:
        return 1
    return int(df["id"].max()) + 1


def append_record(record: StudyRecord) -> None:
    ensure_data_files()
    row = record.to_csv_row()
    with RECORDS_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RECORDS_HEADER)
        writer.writerow(row)


def append_schedules(record: StudyRecord) -> None:
    if record.is_correct:
        return
    ensure_data_files()
    rows = []
    for review_type, review_date in record.review_dates:
        rows.append({
            "record_id": record.id,
            "review_date": review_date,
            "review_type": review_type,
            "is_done": False,
            "done_at": "",
        })
    if not rows:
        return
    with SCHEDULE_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SCHEDULE_HEADER)
        for r in rows:
            writer.writerow(r)


def load_records() -> pd.DataFrame:
    ensure_data_files()
    df = pd.read_csv(RECORDS_CSV, dtype=str, keep_default_na=False)
    if df.empty:
        return df
    df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
    df["is_correct"] = df["is_correct"].map(_parse_bool).astype(bool)
    df["solve_time_sec"] = pd.to_numeric(df["solve_time_sec"], errors="coerce").fillna(0).astype(int)
    df["difficulty"] = pd.to_numeric(df["difficulty"], errors="coerce").fillna(0).astype(int)
    df["date_dt"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def load_schedule() -> pd.DataFrame:
    ensure_data_files()
    df = pd.read_csv(SCHEDULE_CSV, dtype=str, keep_default_na=False)
    if df.empty:
        return df
    df["record_id"] = pd.to_numeric(df["record_id"], errors="coerce").astype("Int64")
    df["is_done"] = df["is_done"].map(_parse_bool).astype(bool)
    df["review_date_dt"] = pd.to_datetime(df["review_date"], errors="coerce")
    return df


def _parse_bool(v) -> bool:
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    return s in ("true", "1", "y", "yes", "t")


def mark_review_done(record_id: int, review_type: str) -> bool:
    """Mark a single review as done. Returns True if updated."""
    if not SCHEDULE_CSV.exists():
        return False
    df = pd.read_csv(SCHEDULE_CSV, dtype=str, keep_default_na=False)
    if df.empty:
        return False
    mask = (df["record_id"].astype(str) == str(record_id)) & (df["review_type"] == review_type)
    if not mask.any():
        return False
    df.loc[mask, "is_done"] = "True"
    df.loc[mask, "done_at"] = now_iso()
    df.to_csv(SCHEDULE_CSV, index=False, encoding="utf-8")
    return True


def generate_sample_data() -> int:
    """Seed sample records illustrating the patterns required for testing.

    Returns number of records created.
    """
    ensure_data_files()
    today = date.today()
    rng = random.Random(42)

    # (offset_days, subject, area, source, problem_no, is_correct, solve_sec, diff, fail_tag, memo)
    seeds = [
        (13, "경제학", "조세", "전공기출", "2024-전공-15", False, 220, 4, "공식 혼동", "종량세/이윤세 효과 혼동"),
        (12, "NCS", "자료해석", "민경채 PSAT", "2023-12", False, 180, 3, "조건 누락", "단위 변환 놓침"),
        (11, "NCS", "의사소통", "공기업단기", "2024-05", True, 60, 2, "", "선지 분석 빠르게"),
        (10, "경제학", "조세", "전공기출", "2024-전공-22", False, 200, 4, "공식 혼동", "종량세 균형가격 식 혼동"),
        (9, "NCS", "자료해석", "봉투모의고사", "2024-3-08", False, 165, 3, "조건 누락", "전제 조건 1개 누락"),
        (8, "NCS", "의사소통", "해커스", "기본-12", True, 55, 2, "", ""),
        (7, "경제학", "독점", "전공기출", "2024-전공-08", False, 240, 5, "개념 미흡", "독점 가격차별 1·2·3급 구분 미흡"),
        (6, "NCS", "자료해석", "민경채 PSAT", "2024-19", False, 200, 4, "조건 누락", "단위 환산 단계 누락"),
        (6, "NCS", "수리", "공기업단기", "심화-04", True, 75, 3, "", ""),
        (5, "경제학", "조세", "전공기출", "2024-전공-31", False, 210, 4, "공식 혼동", "이윤세 부담 귀착 식 헷갈림"),
        (4, "NCS", "자료해석", "봉투모의고사", "2024-4-11", False, 175, 3, "계산 지연", "어림산 안 함, 정밀 계산 시도"),
        (4, "NCS", "의사소통", "해커스", "기본-25", True, 58, 2, "", ""),
        (3, "경제학", "독점적 경쟁", "전공기출", "2024-전공-12", False, 230, 5, "개념 미흡", "장기균형 P=AC 조건 미흡"),
        (2, "NCS", "자료해석", "민경채 PSAT", "2023-25", False, 195, 4, "조건 누락", "표 단위 변경 놓침"),
        (2, "NCS", "의사소통", "공기업단기", "2024-09", True, 50, 2, "", ""),
        (1, "NCS", "수리", "공기업단기", "심화-09", False, 150, 3, "계산 지연", "비율 비교 늦음"),
        (0, "경제학", "독점", "전공기출", "2024-전공-40", False, 220, 5, "선지 판단 오류", "선지 비교 전 값 미정의"),
    ]

    df_existing = load_records()
    start_id = int(df_existing["id"].max()) + 1 if not df_existing.empty else 1

    created = 0
    for offset, subject, area, source, problem_no, is_correct, solve_sec, diff, fail_tag, memo in seeds:
        rec_date = (today - timedelta(days=offset)).isoformat()
        record = StudyRecord(
            id=start_id + created,
            date=rec_date,
            subject=subject,
            area=area,
            source=source,
            problem_no=problem_no,
            is_correct=is_correct,
            solve_time_sec=solve_sec,
            difficulty=diff,
            fail_tag=fail_tag,
            memo=memo,
        )
        append_record(record)
        append_schedules(record)
        created += 1

    return created
