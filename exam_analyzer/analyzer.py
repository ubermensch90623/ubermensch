"""분석 로직: 합격 판정, 격차, 가중치 재조정, 환산."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .models import ExamRecord, Section


@dataclass
class AnalysisResult:
    """analyze() 결과 집계 객체."""

    record: ExamRecord
    total: float
    cutoff: Optional[float]
    gap: Optional[float]
    passed: Optional[bool]
    section_breakdown: List[Tuple[Section, float, float]] = field(default_factory=list)
    # (section, percentage, weighted_score)
    strongest: Optional[Section] = None
    weakest: Optional[Section] = None
    weight_rescaled: bool = False
    original_weight_sum: Optional[float] = None


def compute_total(sections: List[Section]) -> float:
    return sum(s.weighted() for s in sections)


def compute_gap(total: float, cutoff: float) -> float:
    return total - cutoff


def judge_pass(total: float, cutoff: float) -> bool:
    return total >= cutoff


def normalize_weights(sections: List[Section], target: float = 100.0) -> Tuple[List[Section], bool, float]:
    """가중치 합이 target과 다르면 비례 재조정.

    반환: (조정된 sections, 재조정 여부, 원래 가중치 합)
    """
    if not sections:
        return sections, False, 0.0
    weight_sum = sum(s.weight for s in sections)
    if weight_sum == 0:
        return sections, False, 0.0
    if abs(weight_sum - target) < 1e-6:
        return sections, False, weight_sum
    factor = target / weight_sum
    rescaled = [
        Section(name=s.name, score=s.score, max_score=s.max_score, weight=s.weight * factor)
        for s in sections
    ]
    return rescaled, True, weight_sum


def convert_to_scale(score: float, max_score: float, scale: float = 100.0) -> float:
    """원점수를 임의 스케일로 환산."""
    if max_score <= 0:
        return 0.0
    return (score / max_score) * scale


def analyze(record: ExamRecord, auto_normalize: bool = True) -> AnalysisResult:
    """ExamRecord를 받아 종합 분석 결과 생성."""
    sections = record.sections
    weight_rescaled = False
    original_weight_sum: Optional[float] = None
    if auto_normalize and sections:
        sections, weight_rescaled, original_weight_sum = normalize_weights(sections)

    effective_record = ExamRecord(
        agency=record.agency,
        date=record.date,
        sections=sections,
        exam_name=record.exam_name,
        cutoff=record.cutoff,
        notes=record.notes,
        record_id=record.record_id,
    )

    total = compute_total(sections)
    cutoff = record.cutoff
    gap = compute_gap(total, cutoff) if cutoff is not None else None
    passed = judge_pass(total, cutoff) if cutoff is not None else None

    breakdown: List[Tuple[Section, float, float]] = [
        (s, s.percentage(), s.weighted()) for s in sections
    ]

    strongest: Optional[Section] = None
    weakest: Optional[Section] = None
    if sections:
        strongest = max(sections, key=lambda s: s.percentage())
        weakest = min(sections, key=lambda s: s.percentage())

    return AnalysisResult(
        record=effective_record,
        total=total,
        cutoff=cutoff,
        gap=gap,
        passed=passed,
        section_breakdown=breakdown,
        strongest=strongest,
        weakest=weakest,
        weight_rescaled=weight_rescaled,
        original_weight_sum=original_weight_sum,
    )
