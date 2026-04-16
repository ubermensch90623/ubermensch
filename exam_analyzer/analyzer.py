"""분석 로직: 합격 판정, 격차, 가중치 재조정, 환산, 원인 진단."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

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


# ============================================================
# 정밀 원인 분석 (diagnose)
# ============================================================


@dataclass
class SectionContribution:
    """한 영역이 격차에 얼마나 기여했는지 (정확한 수학적 분해)."""

    section: Section
    weighted_actual: float        # 실제 환산 점수
    weighted_expected: float      # 커트라인 기대 환산 점수 (가중치 비율로 안분)
    deficit: float                # weighted_actual - weighted_expected (음수=부족)
    share_of_gap_percent: float   # 전체 격차에서 이 영역이 차지한 비율 (%)


@dataclass
class PassScenario:
    """합격하기 위한 구체적 목표 점수 시나리오."""

    name: str                     # 시나리오 설명 (예: "직업기초능력평가만 개선")
    required_raw_scores: Dict[str, float]       # 영역명 → 필요한 원점수
    required_percentages: Dict[str, float]      # 영역명 → 필요한 백분율
    delta_raw: Dict[str, float]                 # 영역명 → 원점수 증가량
    delta_percentage_points: Dict[str, float]   # 영역명 → 백분율 증가량 (pp)
    feasibility: str              # "낮음" | "보통" | "높음"
    feasibility_note: str


@dataclass
class Diagnosis:
    """diagnose() 의 종합 결과."""

    record: ExamRecord
    total: float
    cutoff: float
    gap: float                    # 음수면 부족
    contributions: List[SectionContribution]
    primary_cause: Optional[Section]  # 격차의 가장 큰 원인 영역
    scenarios: List[PassScenario]
    recommended_scenario: Optional[PassScenario]
    recommendation_reason: str
    checklist: List[str]


def _feasibility_of_raw_delta(section: Section, new_score: float) -> Tuple[str, str]:
    """새 목표 점수의 현실성 평가 (간단한 휴리스틱)."""
    if new_score > section.max_score:
        return "불가능", f"만점({section.max_score:g})을 초과합니다"
    if new_score <= 0:
        return "불필요", "이미 충분합니다"
    new_pct = new_score / section.max_score * 100
    delta_pp = new_pct - section.percentage()
    if delta_pp <= 0:
        return "이미 달성", "현재 점수로 충분합니다"
    # 보정: 현재 수준에서 상승 난이도가 달라짐
    current_pct = section.percentage()
    if current_pct < 50 and delta_pp <= 20:
        return "높음", f"현재 {current_pct:.1f}% → 하위권이라 학습 효과 큼 (+{delta_pp:.1f}pp)"
    if current_pct < 70 and delta_pp <= 15:
        return "보통", f"현재 {current_pct:.1f}% → 집중 학습으로 달성 가능 (+{delta_pp:.1f}pp)"
    if current_pct < 85 and delta_pp <= 10:
        return "보통", f"현재 {current_pct:.1f}% → 상위권 진입 난이도 있음 (+{delta_pp:.1f}pp)"
    if delta_pp <= 5:
        return "보통", f"적은 상승폭 (+{delta_pp:.1f}pp)"
    return "낮음", f"현재 {current_pct:.1f}% 에서 +{delta_pp:.1f}pp 는 상당한 학습 필요"


def decompose_contributions(
    sections: List[Section], cutoff: float
) -> List[SectionContribution]:
    """각 영역이 격차에 얼마나 기여했는지 정확히 분해.

    로직:
      - 커트라인을 가중치 비율로 안분 → 각 영역의 '기대 환산점수' 산출
      - 실제 환산점수 - 기대 환산점수 = 그 영역의 격차 기여
      - 기여의 총합 = 총점 - 커트라인 = gap (수학적으로 항등)
    """
    weight_sum = sum(s.weight for s in sections)
    if weight_sum == 0:
        return []
    total = sum(s.weighted() for s in sections)
    gap = total - cutoff
    contributions: List[SectionContribution] = []
    for s in sections:
        actual = s.weighted()
        # 가중치 비율로 커트라인 안분
        expected = s.weight / weight_sum * cutoff
        deficit = actual - expected
        # 공유 비율: 절대 격차 대비 이 영역의 부족분 비중
        # gap 이 0 이면 공유 비율은 정의 불가 → 0 처리
        share = 0.0
        if abs(gap) > 1e-9:
            share = (deficit / gap) * 100.0
        contributions.append(
            SectionContribution(
                section=s,
                weighted_actual=actual,
                weighted_expected=expected,
                deficit=deficit,
                share_of_gap_percent=share,
            )
        )
    return contributions


def compute_pass_scenarios(
    sections: List[Section], cutoff: float
) -> List[PassScenario]:
    """합격을 위한 3가지 시나리오 생성.

    A. 한 영역만 개선 (각 영역별로 시나리오 생성)
    B. 모든 영역을 균등하게 백분율 상승
    """
    weight_sum = sum(s.weight for s in sections)
    if weight_sum == 0:
        return []
    total = sum(s.weighted() for s in sections)
    delta_weighted_needed = cutoff - total
    scenarios: List[PassScenario] = []

    if delta_weighted_needed <= 0:
        # 이미 합격
        return []

    # A. 각 영역을 단독으로 끌어올리는 시나리오
    for target in sections:
        # 다른 영역은 현재 유지, 이 영역의 새 원점수 계산:
        # new_weighted(target) = current_weighted(target) + delta_weighted_needed
        # new_weighted(target) = new_raw / target.max_score * target.weight
        # → new_raw = (current_weighted + delta) * target.max_score / target.weight
        current_weighted = target.weighted()
        new_weighted = current_weighted + delta_weighted_needed
        if target.weight <= 0:
            continue
        new_raw = new_weighted * target.max_score / target.weight
        new_pct = new_raw / target.max_score * 100
        delta_raw = new_raw - target.score
        delta_pp = new_pct - target.percentage()
        feas, note = _feasibility_of_raw_delta(target, new_raw)
        scenarios.append(
            PassScenario(
                name=f"{target.name}만 개선",
                required_raw_scores={
                    s.name: (new_raw if s.name == target.name else s.score)
                    for s in sections
                },
                required_percentages={
                    s.name: (new_pct if s.name == target.name else s.percentage())
                    for s in sections
                },
                delta_raw={
                    s.name: (delta_raw if s.name == target.name else 0.0)
                    for s in sections
                },
                delta_percentage_points={
                    s.name: (delta_pp if s.name == target.name else 0.0)
                    for s in sections
                },
                feasibility=feas,
                feasibility_note=note,
            )
        )

    # B. 균등 백분율 상승 (모든 영역 +p pp)
    # sum((pct(i) + p)/100 * weight(i)) = cutoff
    # → sum(pct(i)/100 * weight(i)) + p/100 * sum(weight(i)) = cutoff
    # → total + p * weight_sum / 100 = cutoff
    # → p = (cutoff - total) * 100 / weight_sum
    equal_pp = (cutoff - total) * 100.0 / weight_sum
    req_pcts = {s.name: s.percentage() + equal_pp for s in sections}
    req_raws = {s.name: req_pcts[s.name] / 100.0 * s.max_score for s in sections}
    delta_raws = {s.name: req_raws[s.name] - s.score for s in sections}
    delta_pps = {s.name: equal_pp for s in sections}
    # 균등 시나리오의 실현 가능성은 "평균적 노력 필요" 로 표기
    if all(req_raws[s.name] <= s.max_score for s in sections) and equal_pp <= 15:
        equal_feas = "보통"
    elif equal_pp > 20:
        equal_feas = "낮음"
    else:
        equal_feas = "보통"
    scenarios.append(
        PassScenario(
            name="모든 영역 균등 개선",
            required_raw_scores=req_raws,
            required_percentages=req_pcts,
            delta_raw=delta_raws,
            delta_percentage_points=delta_pps,
            feasibility=equal_feas,
            feasibility_note=f"양 영역 모두 +{equal_pp:.2f}pp 상승 필요",
        )
    )

    return scenarios


def _recommend_scenario(
    scenarios: List[PassScenario], sections: List[Section]
) -> Tuple[Optional[PassScenario], str]:
    """시나리오 중 가장 효율적인 하나를 추천."""
    if not scenarios:
        return None, "이미 합격 수준입니다"

    # 단일 영역 시나리오 중 가장 약한 영역에 집중하는 것을 우선 고려
    # (약점 영역이 학습 상승 여지가 크다는 가정)
    weakest = min(sections, key=lambda s: s.percentage()) if sections else None
    if weakest is None:
        return None, "영역 정보 없음"

    candidate = None
    for sc in scenarios:
        if sc.name == f"{weakest.name}만 개선":
            candidate = sc
            break

    if candidate is None:
        return scenarios[0], "기본 시나리오"

    # 가능성 검증: 불가능(만점 초과)이면 균등 시나리오로 대체
    if candidate.feasibility == "불가능":
        equal = next((s for s in scenarios if s.name == "모든 영역 균등 개선"), None)
        if equal is not None:
            return equal, (
                f"{weakest.name} 단독 개선으로는 만점을 초과하므로 "
                "두 영역을 함께 개선하는 균등 시나리오 권장"
            )

    reason = (
        f"가장 약한 영역인 '{weakest.name}' ({weakest.percentage():.2f}%) 은 "
        "학습 효과가 크게 반영되는 구간입니다. 이 영역에 집중 투자 시 "
        f"{candidate.feasibility} 확률로 합격권 진입 가능합니다."
    )
    return candidate, reason


def _build_checklist(
    recommended: Optional[PassScenario], sections: List[Section], cutoff: float
) -> List[str]:
    """추천 시나리오 기반 다음 시험 준비 체크리스트."""
    if recommended is None:
        return ["✓ 이미 합격 수준 — 현 상태 유지"]
    items: List[str] = []
    for s in sections:
        need_raw = recommended.required_raw_scores.get(s.name, s.score)
        need_pct = recommended.required_percentages.get(s.name, s.percentage())
        delta_pp = recommended.delta_percentage_points.get(s.name, 0.0)
        if delta_pp < 0.01:
            items.append(f"[유지] {s.name}: 현재 {s.percentage():.2f}% 수준 유지")
        else:
            items.append(
                f"[집중] {s.name}: {s.score:.2f} → {need_raw:.2f} / {s.max_score:g} "
                f"({s.percentage():.2f}% → {need_pct:.2f}%, +{delta_pp:.2f}pp)"
            )
    items.append("[복습] 이번 시험 오답 분석 및 취약 유형 노트 작성")
    items.append(f"[모의] 영역별 모의고사 5회 이상, 목표 점수 {cutoff:.1f} 이상 안정 도달")
    return items


def diagnose(record: ExamRecord) -> Diagnosis:
    """정밀 원인 분석: 기여도 분해 + 합격 시나리오 + 추천 전략."""
    if record.cutoff is None:
        raise ValueError("diagnose() 는 커트라인이 지정된 기록에만 가능합니다")
    # 가중치 정규화 (diagnose 는 반드시 정확한 수치를 내야 하므로)
    sections, _, _ = normalize_weights(record.sections)
    cutoff = record.cutoff
    total = compute_total(sections)
    gap = total - cutoff

    contributions = decompose_contributions(sections, cutoff)

    # 주 원인: 가장 큰 음의 deficit 을 가진 영역
    primary_cause: Optional[Section] = None
    if contributions:
        worst = min(contributions, key=lambda c: c.deficit)
        if worst.deficit < 0:
            primary_cause = worst.section

    scenarios = compute_pass_scenarios(sections, cutoff)
    recommended, reason = _recommend_scenario(scenarios, sections)
    checklist = _build_checklist(recommended, sections, cutoff)

    return Diagnosis(
        record=record,
        total=total,
        cutoff=cutoff,
        gap=gap,
        contributions=contributions,
        primary_cause=primary_cause,
        scenarios=scenarios,
        recommended_scenario=recommended,
        recommendation_reason=reason,
        checklist=checklist,
    )
