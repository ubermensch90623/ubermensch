"""Data model — StudyRecord dataclass aligned with records.csv schema."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta

from .constants import RECORDS_HEADER, REVIEW_INTERVALS


@dataclass
class StudyRecord:
    id: int
    date: str
    subject: str
    area: str
    source: str
    problem_no: str
    is_correct: bool
    solve_time_sec: int
    difficulty: int
    fail_tag: str = ""
    memo: str = ""
    review_1d: str = ""
    review_3d: str = ""
    review_7d: str = ""
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.is_correct:
            base = datetime.strptime(self.date, "%Y-%m-%d").date()
            for interval, attr in zip(REVIEW_INTERVALS, ("review_1d", "review_3d", "review_7d")):
                if not getattr(self, attr):
                    setattr(self, attr, (base + timedelta(days=interval)).isoformat())
        else:
            self.fail_tag = ""
            self.review_1d = ""
            self.review_3d = ""
            self.review_7d = ""
        if not self.created_at:
            self.created_at = datetime.now().isoformat(timespec="seconds")

    def to_csv_row(self) -> dict:
        d = asdict(self)
        for col in RECORDS_HEADER:
            d.setdefault(col, "")
        return {col: d[col] for col in RECORDS_HEADER}

    @property
    def review_dates(self) -> list[tuple[str, str]]:
        """Return list of (review_type, review_date) for non-empty reviews."""
        out = []
        for rt, val in (("1d", self.review_1d), ("3d", self.review_3d), ("7d", self.review_7d)):
            if val:
                out.append((rt, val))
        return out
