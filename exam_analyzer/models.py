"""데이터 모델: Section, ExamRecord 및 JSON 직렬화 유틸."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


SCHEMA_VERSION = 1


@dataclass
class Section:
    """시험의 한 영역 (예: 직업기초능력평가)."""

    name: str
    score: float
    max_score: float
    weight: float

    def weighted(self) -> float:
        """가중치를 적용한 환산 점수 (100점 만점 스케일 기여도)."""
        if self.max_score <= 0:
            return 0.0
        return (self.score / self.max_score) * self.weight

    def percentage(self) -> float:
        """원점수를 백분율로 변환."""
        if self.max_score <= 0:
            return 0.0
        return (self.score / self.max_score) * 100.0


@dataclass
class ExamRecord:
    """단일 시험 기록."""

    agency: str
    date: str  # ISO "YYYY-MM-DD"
    sections: List[Section] = field(default_factory=list)
    exam_name: str = "필기전형"
    cutoff: Optional[float] = None
    notes: str = ""
    record_id: str = ""

    def total(self) -> float:
        """100점 만점 환산 총점."""
        return sum(s.weighted() for s in self.sections)

    def gap(self) -> Optional[float]:
        """커트라인 대비 격차 (음수면 부족)."""
        if self.cutoff is None:
            return None
        return self.total() - self.cutoff

    def passed(self) -> Optional[bool]:
        """합격 여부. 커트라인이 없으면 None."""
        if self.cutoff is None:
            return None
        return self.total() >= self.cutoff


def generate_record_id(record: ExamRecord) -> str:
    """agency|date|total 의 sha1 첫 8자로 안정적 식별자 생성."""
    payload = f"{record.agency}|{record.date}|{record.total():.4f}".encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:8]


def section_to_dict(s: Section) -> Dict[str, Any]:
    return {
        "name": s.name,
        "score": s.score,
        "max_score": s.max_score,
        "weight": s.weight,
    }


def section_from_dict(d: Dict[str, Any]) -> Section:
    return Section(
        name=d["name"],
        score=float(d["score"]),
        max_score=float(d["max_score"]),
        weight=float(d["weight"]),
    )


def record_to_dict(r: ExamRecord) -> Dict[str, Any]:
    return {
        "record_id": r.record_id or generate_record_id(r),
        "agency": r.agency,
        "exam_name": r.exam_name,
        "date": r.date,
        "sections": [section_to_dict(s) for s in r.sections],
        "cutoff": r.cutoff,
        "notes": r.notes,
    }


def record_from_dict(d: Dict[str, Any]) -> ExamRecord:
    return ExamRecord(
        agency=d["agency"],
        date=d["date"],
        sections=[section_from_dict(s) for s in d.get("sections", [])],
        exam_name=d.get("exam_name", "필기전형"),
        cutoff=d.get("cutoff"),
        notes=d.get("notes", ""),
        record_id=d.get("record_id", ""),
    )
