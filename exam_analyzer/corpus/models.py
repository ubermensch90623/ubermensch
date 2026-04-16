"""corpus 데이터 모델 — 기출 · 예상 · 회독 · 시도 기록.

설계 원칙 (CLAUDE.md 반영):
- 모든 Question 에 provenance (소스 체인) 필수
- 리버스 엔지니어링 생성 문항은 `kind="reverse_engineered"` + `rationale_chain` 필수
- Attempt 는 결정론적 로그. 휴리스틱 조언 포함 금지.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional


CORPUS_SCHEMA_VERSION = 1


QuestionKind = Literal[
    "primary",           # 사용자 구매 이북 등 1차 소스 원문
    "reverse_engineered",  # 패턴 기반 생성 예상 문항 (근거 체인 필수)
    "official_released",  # 공공기관 공개 기출 (출처 URL 필수)
]


@dataclass
class Provenance:
    """소스 체인 (하류 분석의 데이터 혈통)."""

    source_type: str          # "ebook" | "official_site" | "community_review" | "reverse_engineered"
    source_name: str          # "알라딘 이북 제목" 또는 URL
    source_citation: str      # 페이지 번호 또는 직접 인용구
    source_date: str          # 자료 작성일 또는 취득일 (YYYY-MM-DD)
    chain: List[str] = field(default_factory=list)
    # 파생 연결 (예: P9 예상 문항이 참조한 1차 문항 ID들)


@dataclass
class Choice:
    """선지 (원문 단어 단위 보존)."""

    index: int                # 1..N
    text: str                 # 원문 그대로
    is_correct: bool = False
    trap_type: Optional[str] = None  # "수치변경"|"조건누락"|"유사개념"|"시제함정" 등


@dataclass
class Question:
    """단일 문항."""

    id: str                   # sha1(agency|area|topic|first_30_chars)[:10]
    kind: QuestionKind
    agency: str               # "서민금융진흥원" | "일반 금융공기업 공통" 등
    area: str                 # "NCS/의사소통" | "직무/경영" | "직무/서민금융법률" 등
    subtype: str              # "문단배열" | "조문적용" | "수치계산" 등
    question_text: str        # 원문 그대로
    choices: List[Choice]
    correct_index: Optional[int] = None
    explanation: str = ""
    related_law_articles: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    provenance: Optional[Provenance] = None
    # 리버스 엔지니어링 전용
    rationale_chain: List[str] = field(default_factory=list)
    # 예: ["기출A Q#42", "후기B URL", "법령 §14"]
    confidence: Optional[Literal["high", "mid", "low"]] = None
    counter_arguments: List[str] = field(default_factory=list)
    # 이 예상 문항이 틀릴 수 있는 반박 근거


@dataclass
class Attempt:
    """회독 중 1회 풀이 시도."""

    question_id: str
    round_num: int
    attempted_at: str         # ISO datetime
    selected_index: Optional[int]
    is_correct: Optional[bool]  # None = 정답 미확인 문항
    time_spent_sec: Optional[float] = None
    confidence: Optional[Literal["sure", "guess", "eliminated"]] = None
    note: str = ""


@dataclass
class ReviewRound:
    """한 회의 회독 세션."""

    round_num: int
    started_at: str
    completed_at: Optional[str] = None
    scope_question_ids: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class CorpusSnapshot:
    """전체 corpus 스냅샷 (JSON 직렬화 대상)."""

    version: int = CORPUS_SCHEMA_VERSION
    questions: List[Question] = field(default_factory=list)
    attempts: List[Attempt] = field(default_factory=list)
    rounds: List[ReviewRound] = field(default_factory=list)


def generate_question_id(kind: QuestionKind, agency: str, area: str, text: str) -> str:
    """안정적 문항 ID (소스 동일하면 같은 ID)."""
    payload = f"{kind}|{agency}|{area}|{text[:60]}".encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:10]


# ---------------- 직렬화 ----------------


def _choice_to_dict(c: Choice) -> Dict[str, Any]:
    return {
        "index": c.index,
        "text": c.text,
        "is_correct": c.is_correct,
        "trap_type": c.trap_type,
    }


def _choice_from_dict(d: Dict[str, Any]) -> Choice:
    return Choice(
        index=d["index"],
        text=d["text"],
        is_correct=d.get("is_correct", False),
        trap_type=d.get("trap_type"),
    )


def _provenance_to_dict(p: Optional[Provenance]) -> Optional[Dict[str, Any]]:
    if p is None:
        return None
    return {
        "source_type": p.source_type,
        "source_name": p.source_name,
        "source_citation": p.source_citation,
        "source_date": p.source_date,
        "chain": list(p.chain),
    }


def _provenance_from_dict(d: Optional[Dict[str, Any]]) -> Optional[Provenance]:
    if d is None:
        return None
    return Provenance(
        source_type=d["source_type"],
        source_name=d["source_name"],
        source_citation=d.get("source_citation", ""),
        source_date=d.get("source_date", ""),
        chain=d.get("chain", []),
    )


def question_to_dict(q: Question) -> Dict[str, Any]:
    return {
        "id": q.id,
        "kind": q.kind,
        "agency": q.agency,
        "area": q.area,
        "subtype": q.subtype,
        "question_text": q.question_text,
        "choices": [_choice_to_dict(c) for c in q.choices],
        "correct_index": q.correct_index,
        "explanation": q.explanation,
        "related_law_articles": list(q.related_law_articles),
        "tags": list(q.tags),
        "provenance": _provenance_to_dict(q.provenance),
        "rationale_chain": list(q.rationale_chain),
        "confidence": q.confidence,
        "counter_arguments": list(q.counter_arguments),
    }


def question_from_dict(d: Dict[str, Any]) -> Question:
    return Question(
        id=d["id"],
        kind=d["kind"],
        agency=d["agency"],
        area=d["area"],
        subtype=d.get("subtype", ""),
        question_text=d["question_text"],
        choices=[_choice_from_dict(c) for c in d.get("choices", [])],
        correct_index=d.get("correct_index"),
        explanation=d.get("explanation", ""),
        related_law_articles=d.get("related_law_articles", []),
        tags=d.get("tags", []),
        provenance=_provenance_from_dict(d.get("provenance")),
        rationale_chain=d.get("rationale_chain", []),
        confidence=d.get("confidence"),
        counter_arguments=d.get("counter_arguments", []),
    )


def attempt_to_dict(a: Attempt) -> Dict[str, Any]:
    return {
        "question_id": a.question_id,
        "round_num": a.round_num,
        "attempted_at": a.attempted_at,
        "selected_index": a.selected_index,
        "is_correct": a.is_correct,
        "time_spent_sec": a.time_spent_sec,
        "confidence": a.confidence,
        "note": a.note,
    }


def attempt_from_dict(d: Dict[str, Any]) -> Attempt:
    return Attempt(
        question_id=d["question_id"],
        round_num=d["round_num"],
        attempted_at=d["attempted_at"],
        selected_index=d.get("selected_index"),
        is_correct=d.get("is_correct"),
        time_spent_sec=d.get("time_spent_sec"),
        confidence=d.get("confidence"),
        note=d.get("note", ""),
    )


def round_to_dict(r: ReviewRound) -> Dict[str, Any]:
    return {
        "round_num": r.round_num,
        "started_at": r.started_at,
        "completed_at": r.completed_at,
        "scope_question_ids": list(r.scope_question_ids),
        "notes": r.notes,
    }


def round_from_dict(d: Dict[str, Any]) -> ReviewRound:
    return ReviewRound(
        round_num=d["round_num"],
        started_at=d["started_at"],
        completed_at=d.get("completed_at"),
        scope_question_ids=d.get("scope_question_ids", []),
        notes=d.get("notes", ""),
    )


def snapshot_to_dict(s: CorpusSnapshot) -> Dict[str, Any]:
    return {
        "version": s.version,
        "questions": [question_to_dict(q) for q in s.questions],
        "attempts": [attempt_to_dict(a) for a in s.attempts],
        "rounds": [round_to_dict(r) for r in s.rounds],
    }


def snapshot_from_dict(d: Dict[str, Any]) -> CorpusSnapshot:
    return CorpusSnapshot(
        version=d.get("version", CORPUS_SCHEMA_VERSION),
        questions=[question_from_dict(q) for q in d.get("questions", [])],
        attempts=[attempt_from_dict(a) for a in d.get("attempts", [])],
        rounds=[round_from_dict(r) for r in d.get("rounds", [])],
    )
