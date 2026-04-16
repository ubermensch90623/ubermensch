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
    """합격하기 위한 구체적 목표 점수 시나리오.

    ※ audit-v1.md 반영: 이전의 `feasibility` 필드(높음/보통/낮음 휴리스틱) 는
    임의 임계값이었기에 제거. 대신 `signal` 은 `범위초과 / 이미달성 / 수치요약`
    3종 중 하나로 중립 분류하고, `description` 은 수치만 담은 중립 설명.
    "이 시나리오가 현실적이다/아니다" 판단은 사용자에게 남긴다.
    """

    name: str                     # 시나리오 설명 (예: "직업기초능력평가만 개선")
    required_raw_scores: Dict[str, float]       # 영역명 → 필요한 원점수
    required_percentages: Dict[str, float]      # 영역명 → 필요한 백분율
    delta_raw: Dict[str, float]                 # 영역명 → 원점수 증가량
    delta_percentage_points: Dict[str, float]   # 영역명 → 백분율 증가량 (pp)
    signal: str                   # "범위초과" | "이미달성" | "수치요약"
    description: str              # 중립 수치 설명


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


def _describe_raw_delta(section: Section, new_score: float) -> Tuple[str, str]:
    """목표 점수의 **중립 수치 설명**. 실현 가능성은 판단하지 않음.

    audit-v1.md §1.2 의 FABRICATION 지적에 따라, 이전의 '높음/보통/낮음'
    휴리스틱 임계값(20pp/15pp/10pp/5pp) 은 근거 없는 임의값이어서 제거됨.
    여기서는 수치만 담백하게 서술하고 판단은 사용자에게 남긴다.
    """
    if new_score > section.max_score:
        return "범위초과", f"만점({section.max_score:g})을 초과하는 목표입니다"
    new_pct = new_score / section.max_score * 100
    delta_pp = new_pct - section.percentage()
    if delta_pp <= 0:
        return "이미달성", f"현재 점수로 충분합니다 (현 {section.percentage():.2f}%)"
    return (
        "수치요약",
        f"현재 {section.percentage():.2f}% → 목표 {new_pct:.2f}% (+{delta_pp:.2f}pp)",
    )


def decompose_contributions(
    sections: List[Section], cutoff: float
) -> List[SectionContribution]:
    """각 영역이 격차에 얼마나 기여했는지 **한 가지 방법으로** 분해.

    사용 로직: "가중치 비율로 안분"
      - 커트라인을 가중치 비율로 안분 → 각 영역의 '기대 환산점수' 산출
      - 실제 환산점수 - 기대 환산점수 = 그 영역의 격차 기여
      - 기여의 총합 = 총점 - 커트라인 = gap (수학적으로 항등)

    ※ 이것은 여러 가능한 분해법 중 하나의 선택. 대안:
      - 각 영역의 '최대 점수 대비 부족률' 기준 분해
      - 각 영역의 '과거 합격자 평균점 대비 편차' 기준 분해 (과거 데이터 필요)
    audit-v1.md §1.2 참조. 지금 출력은 '가중치 비율 안분 기준'임을 명시.
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
        signal, description = _describe_raw_delta(target, new_raw)
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
                signal=signal,
                description=description,
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
    # 균등 시나리오 — 판단 없이 수치만
    if all(req_raws[s.name] <= s.max_score for s in sections):
        equal_signal = "수치요약"
    else:
        equal_signal = "범위초과"
    scenarios.append(
        PassScenario(
            name="모든 영역 균등 개선",
            required_raw_scores=req_raws,
            required_percentages=req_pcts,
            delta_raw=delta_raws,
            delta_percentage_points=delta_pps,
            signal=equal_signal,
            description=f"양 영역 모두 +{equal_pp:.2f}pp 상승",
        )
    )

    return scenarios


def _scenario_trade_offs(
    scenarios: List[PassScenario], sections: List[Section]
) -> Tuple[List[Tuple[PassScenario, str]], str]:
    """각 시나리오의 **trade-off 수치 요약** 반환. 추천 판단 없음.

    ※ audit-v1.md 반영: 이전의 '약점 영역 집중이 학습 효과 크다' 가정은
    사용자 상황을 모르는 일반 통념이었기에 제거. 대신 사용자가 스스로
    판단할 수 있도록 각 시나리오의 수치 특성만 요약 제공.
    """
    if not scenarios:
        return [], "이미 합격 수준"
    trade_offs: List[Tuple[PassScenario, str]] = []
    for sc in scenarios:
        # 증가시켜야 할 총 pp (여러 영역일 수 있음)
        total_pp_to_raise = sum(v for v in sc.delta_percentage_points.values() if v > 0)
        max_pp = max(sc.delta_percentage_points.values(), default=0.0)
        affected = [n for n, v in sc.delta_percentage_points.items() if v > 0.01]
        note = (
            f"집중 영역 수: {len(affected)} | "
            f"최대 단일 상승: +{max_pp:.2f}pp | "
            f"총 pp 상승 합: +{total_pp_to_raise:.2f}pp | "
            f"신호: {sc.signal}"
        )
        trade_offs.append((sc, note))
    note = "판단은 사용자에게 위임. 학습 가용 시간·영역별 적성을 고려해 선택하세요."
    return trade_offs, note


def _build_checklist(
    scenarios: List[PassScenario], sections: List[Section], cutoff: float
) -> List[str]:
    """시나리오별 목표 점수만 담담히 나열한 체크리스트.

    ※ audit-v1.md 반영: '모의고사 5회 이상' 같은 임의 수치 제거.
    일반적 학습 행동 권고 (오답 분석, 반복 회독) 는 지침 없이 짧은 힌트만.
    """
    if not scenarios:
        return ["✓ 이미 합격 수준 — 현 상태 유지"]
    items: List[str] = []
    for sc in scenarios:
        items.append(f"[시나리오] {sc.name}")
        for s in sections:
            need_raw = sc.required_raw_scores.get(s.name, s.score)
            need_pct = sc.required_percentages.get(s.name, s.percentage())
            delta_pp = sc.delta_percentage_points.get(s.name, 0.0)
            if delta_pp < 0.01:
                items.append(f"    - {s.name}: 현 {s.percentage():.2f}% 유지")
            else:
                items.append(
                    f"    - {s.name}: {s.score:.2f} → {need_raw:.2f} / {s.max_score:g} "
                    f"({s.percentage():.2f}% → {need_pct:.2f}%, +{delta_pp:.2f}pp)"
                )
    items.append("[힌트] 오답 분석·반복 회독은 사용자 학습 시간 여건에 맞춰 결정하세요.")
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
