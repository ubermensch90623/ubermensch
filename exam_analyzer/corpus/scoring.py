"""corpus 숙련도 산출 — 북극성(복원률 95%) 측정 도구.

정의 (reconstruction-plan.md v3 §3):
- **숙련도 (Mastery)**: 등재 문항 중 "최근 N회독 연속 정답률 ≥ 임계치" 충족 비율
- 기본값: 최근 3회독 이상 연속 90% 이상 = 해당 문항 '숙달'
- 전체 숙달률 ≥ 95% = 북극성 도달
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional

from .models import Attempt, CorpusSnapshot, Question


@dataclass
class MasteryReport:
    """전체 corpus 의 숙련도 리포트."""

    total_questions: int
    mastered_count: int
    mastery_rate: float                  # 0..1
    by_area: Dict[str, float]            # 영역별 숙련도
    weakest_questions: List[str]         # 최약 문항 ID (상위 N개)
    never_attempted: List[str]           # 시도 기록 없는 문항 ID
    rounds_completed: int                # 현재까지 완료된 회독 수


def _attempts_for_question(
    snapshot: CorpusSnapshot, qid: str
) -> List[Attempt]:
    """문항별 시도 기록을 round_num 오름차순으로 반환."""
    return sorted(
        (a for a in snapshot.attempts if a.question_id == qid),
        key=lambda a: (a.round_num, a.attempted_at),
    )


def is_mastered(
    attempts: List[Attempt],
    min_consecutive: int = 3,
    required_accuracy: float = 0.9,
) -> bool:
    """문항 숙달 판정.

    기준: 최근 `min_consecutive` 회독에서 정답률 ≥ `required_accuracy`.
    - 시도 기록 `min_consecutive` 미만이면 False.
    - 각 회독의 대표 시도 = 마지막 attempt (한 회독에 여러 번 풀었다면).
    """
    if len(attempts) < min_consecutive:
        return False
    # 회독별 마지막 시도 수집
    by_round: Dict[int, Attempt] = {}
    for a in attempts:
        by_round[a.round_num] = a  # attempts 이미 정렬되어 있어 마지막 시도가 마지막
    recent_rounds = sorted(by_round.keys())[-min_consecutive:]
    correct = sum(1 for r in recent_rounds if by_round[r].is_correct is True)
    return (correct / min_consecutive) >= required_accuracy


def compute_mastery_report(
    snapshot: CorpusSnapshot,
    min_consecutive: int = 3,
    required_accuracy: float = 0.9,
    weakest_top_n: int = 10,
) -> MasteryReport:
    total = len(snapshot.questions)
    if total == 0:
        return MasteryReport(
            total_questions=0,
            mastered_count=0,
            mastery_rate=0.0,
            by_area={},
            weakest_questions=[],
            never_attempted=[],
            rounds_completed=0,
        )
    mastered = 0
    never_attempted: List[str] = []
    # 영역별 집계
    by_area_counts: Dict[str, List[bool]] = defaultdict(list)
    # 문항별 정답률 (weakest 선정용)
    per_question_accuracy: Dict[str, float] = {}

    for q in snapshot.questions:
        attempts = _attempts_for_question(snapshot, q.id)
        if not attempts:
            never_attempted.append(q.id)
            by_area_counts[q.area].append(False)
            per_question_accuracy[q.id] = 0.0
            continue
        m = is_mastered(attempts, min_consecutive, required_accuracy)
        if m:
            mastered += 1
        by_area_counts[q.area].append(m)
        correct = sum(1 for a in attempts if a.is_correct is True)
        per_question_accuracy[q.id] = correct / len(attempts)

    by_area = {
        area: (sum(bools) / len(bools)) if bools else 0.0
        for area, bools in by_area_counts.items()
    }
    weakest = sorted(per_question_accuracy.items(), key=lambda kv: kv[1])
    weakest_ids = [qid for qid, _ in weakest[:weakest_top_n]]

    return MasteryReport(
        total_questions=total,
        mastered_count=mastered,
        mastery_rate=mastered / total if total else 0.0,
        by_area=by_area,
        weakest_questions=weakest_ids,
        never_attempted=never_attempted,
        rounds_completed=len(snapshot.rounds),
    )


def mastery_report_to_dict(r: MasteryReport) -> Dict:
    return {
        "total_questions": r.total_questions,
        "mastered_count": r.mastered_count,
        "mastery_rate": round(r.mastery_rate, 4),
        "mastery_rate_percent": round(r.mastery_rate * 100, 2),
        "by_area": {k: round(v, 4) for k, v in r.by_area.items()},
        "weakest_questions": list(r.weakest_questions),
        "never_attempted": list(r.never_attempted),
        "rounds_completed": r.rounds_completed,
        "north_star_reached": r.mastery_rate >= 0.95,
    }
