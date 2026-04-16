"""drill 모듈: 회독 세션 관리.

기능:
- DrillSession: 시작 / 다음 문항 / 답안 기록 / 종료
- 출제 순서: 랜덤 / 약점 집중 / 영역 필터
- 결과는 Attempt 로 누적 → scoring.compute_mastery_report

C-0 준수: 문항 자체는 corpus (1차 소스 또는 reverse_engineered 검증 통과 항목) 에만.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .models import Attempt, CorpusSnapshot, Question, ReviewRound


@dataclass
class DrillSession:
    """회독 세션 state."""

    round_num: int
    started_at: str                  # ISO
    scope: List[Question] = field(default_factory=list)
    current_index: int = 0
    attempts_this_session: List[Attempt] = field(default_factory=list)
    mode: str = "sequential"         # sequential | random | weakest_first
    filter_area: Optional[str] = None


def start_session(
    snapshot: CorpusSnapshot,
    round_num: int,
    mode: str = "sequential",
    filter_area: Optional[str] = None,
    limit: Optional[int] = None,
    weakest_ids: Optional[List[str]] = None,
    seed: Optional[int] = None,
) -> DrillSession:
    """세션 준비 + ReviewRound 로그 시작."""
    if mode not in {"sequential", "random", "weakest_first"}:
        raise ValueError(f"Unsupported mode: {mode}")

    pool = list(snapshot.questions)
    if filter_area:
        pool = [q for q in pool if q.area.startswith(filter_area)]

    if mode == "random":
        rng = random.Random(seed)
        rng.shuffle(pool)
    elif mode == "weakest_first":
        if weakest_ids:
            pool_by_id = {q.id: q for q in pool}
            # weakest_ids 입력 순서 존중 (가장 취약한 것 먼저)
            weak_ordered = [
                pool_by_id[qid] for qid in weakest_ids if qid in pool_by_id
            ]
            weak_id_set = set(weakest_ids)
            rest = [q for q in pool if q.id not in weak_id_set]
            pool = weak_ordered + rest

    if limit is not None:
        pool = pool[:limit]

    session = DrillSession(
        round_num=round_num,
        started_at=datetime.utcnow().isoformat(timespec="seconds"),
        scope=pool,
        current_index=0,
        mode=mode,
        filter_area=filter_area,
    )
    # ReviewRound 기록
    snapshot.rounds.append(
        ReviewRound(
            round_num=round_num,
            started_at=session.started_at,
            scope_question_ids=[q.id for q in pool],
            notes=f"mode={mode} filter={filter_area or '-'} size={len(pool)}",
        )
    )
    return session


def next_question(session: DrillSession) -> Optional[Question]:
    if session.current_index >= len(session.scope):
        return None
    q = session.scope[session.current_index]
    return q


def submit_answer(
    session: DrillSession,
    snapshot: CorpusSnapshot,
    selected_index: Optional[int],
    time_spent_sec: Optional[float] = None,
    confidence: Optional[str] = None,
    note: str = "",
) -> Attempt:
    """현재 문항에 답안 제출 → Attempt 생성 + snapshot 에 누적.

    selected_index=None 이면 skip/미응답.
    """
    if session.current_index >= len(session.scope):
        raise RuntimeError("세션 종료 상태")
    q = session.scope[session.current_index]
    is_correct: Optional[bool]
    if selected_index is None or q.correct_index is None:
        is_correct = None
    else:
        is_correct = (selected_index == q.correct_index)

    attempt = Attempt(
        question_id=q.id,
        round_num=session.round_num,
        attempted_at=datetime.utcnow().isoformat(timespec="seconds"),
        selected_index=selected_index,
        is_correct=is_correct,
        time_spent_sec=time_spent_sec,
        confidence=confidence,  # type: ignore[arg-type]
        note=note,
    )
    snapshot.attempts.append(attempt)
    session.attempts_this_session.append(attempt)
    session.current_index += 1
    return attempt


def end_session(
    session: DrillSession, snapshot: CorpusSnapshot, notes: str = ""
) -> dict:
    """세션 종료. ReviewRound.completed_at 갱신. 요약 반환."""
    completed_at = datetime.utcnow().isoformat(timespec="seconds")
    # 해당 round_num 의 마지막 ReviewRound 갱신
    for r in reversed(snapshot.rounds):
        if r.round_num == session.round_num and not r.completed_at:
            r.completed_at = completed_at
            if notes:
                r.notes = (r.notes + " | " + notes).strip(" |")
            break
    total = len(session.attempts_this_session)
    correct = sum(1 for a in session.attempts_this_session if a.is_correct is True)
    wrong = sum(1 for a in session.attempts_this_session if a.is_correct is False)
    skipped = sum(1 for a in session.attempts_this_session if a.is_correct is None)
    accuracy = (correct / total) if total else 0.0
    return {
        "round_num": session.round_num,
        "started_at": session.started_at,
        "completed_at": completed_at,
        "total_attempted": total,
        "correct": correct,
        "wrong": wrong,
        "skipped": skipped,
        "accuracy": round(accuracy, 4),
        "accuracy_percent": round(accuracy * 100, 2),
        "mode": session.mode,
        "filter_area": session.filter_area,
    }
