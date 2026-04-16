"""match 모듈: 2차 소스 후기 키워드 ↔ 1차 corpus 문항 매핑.

사용 시나리오:
- 공개 후기에서 "서민금융생활지원법 §14 휴면예금 관련 문제 출제됨" 같은 주장 수집
- 이를 1차 corpus (사용자 이북 기출) 에 있는 같은 주제 문항과 연결
- 연결된 문항 = 이번 시험 재등장 확률 높음 (재탕 지표)

C-0 준수: 매핑은 MID 신뢰도 신호. 확정 팩트로 즉시 승격 금지. 수석위원 심사 필요.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set, Tuple

from .models import CorpusSnapshot, Question


@dataclass
class MatchHit:
    """키워드와 corpus 문항의 매칭 결과."""

    keyword: str
    matched_question_id: str
    match_score: float           # 0..1
    matched_fields: List[str]    # 'question_text', 'area', 'tags', 'related_law_articles' 등
    secondary_source_url: Optional[str] = None
    secondary_source_quote: Optional[str] = None


@dataclass
class SecondaryClaim:
    """2차 소스 후기가 주장한 출제 키워드/주제."""

    keyword: str                 # 예: "휴면예금", "신용보증법 제3조"
    source_url: str
    quoted_text: str
    source_date: str             # YYYY-MM-DD
    confidence_self: str = "mid"  # 후기 작성자의 자기 확신 (high|mid|low)


def _normalize(text: str) -> str:
    """간단 정규화: 공백 축약, lower (영문), 구두점 제거."""
    text = text.lower().strip()
    text = re.sub(r"[^\w가-힣\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _tokenize(text: str) -> Set[str]:
    """단순 토큰 (공백 분리). 한국어 형태소 분석기 미사용 (stdlib-only)."""
    return set(_normalize(text).split())


def keyword_in_question(
    keyword: str, q: Question, matched_fields: List[str]
) -> float:
    """문항의 여러 필드에서 키워드 유사도 측정. 0..1.

    간단 규칙:
    - 정확 부분문자열 일치 → 해당 필드 만점 기여
    - 토큰 교집합 비율 → 부분 점수
    - 여러 필드에서 공통 매칭 → 가산
    """
    kw_norm = _normalize(keyword)
    kw_tokens = _tokenize(keyword)
    if not kw_tokens:
        return 0.0

    scores = []

    checks = {
        "question_text": q.question_text,
        "area": q.area,
        "subtype": q.subtype,
        "explanation": q.explanation,
        "tags": " ".join(q.tags),
        "related_law_articles": " ".join(q.related_law_articles),
    }
    for field_name, field_value in checks.items():
        if not field_value:
            continue
        fv_norm = _normalize(field_value)
        fv_tokens = _tokenize(field_value)
        if not fv_tokens:
            continue
        exact = 1.0 if kw_norm and kw_norm in fv_norm else 0.0
        intersect = len(kw_tokens & fv_tokens)
        partial = intersect / len(kw_tokens) if kw_tokens else 0.0
        f_score = max(exact, partial)
        if f_score > 0:
            matched_fields.append(field_name)
            scores.append(f_score)

    if not scores:
        return 0.0
    # 가중 평균: 최대 필드 점수 + 여러 필드 매칭 보너스
    primary = max(scores)
    bonus = min(0.2, 0.05 * (len(scores) - 1))
    return min(1.0, primary + bonus)


def match_claim_to_corpus(
    claim: SecondaryClaim,
    corpus: CorpusSnapshot,
    min_score: float = 0.3,
    top_n: int = 5,
) -> List[MatchHit]:
    """단일 2차 주장(SecondaryClaim) → 1차 corpus 에서 매칭 문항 top_n.

    min_score 미만은 제외.
    """
    hits: List[MatchHit] = []
    for q in corpus.questions:
        matched_fields: List[str] = []
        score = keyword_in_question(claim.keyword, q, matched_fields)
        if score >= min_score:
            hits.append(
                MatchHit(
                    keyword=claim.keyword,
                    matched_question_id=q.id,
                    match_score=score,
                    matched_fields=matched_fields,
                    secondary_source_url=claim.source_url,
                    secondary_source_quote=claim.quoted_text,
                )
            )
    hits.sort(key=lambda h: h.match_score, reverse=True)
    return hits[:top_n]


@dataclass
class MatchReport:
    """전체 2차 주장 리스트에 대한 매핑 리포트."""

    total_claims: int
    matched_claims: int
    unmatched_claims: List[str]  # keyword list
    hits_by_question: Dict[str, List[MatchHit]]  # question_id → hits
    reappearance_candidates: List[str]  # 재탕 후보 question_id (score 높은 순)


def build_match_report(
    claims: Iterable[SecondaryClaim],
    corpus: CorpusSnapshot,
    min_score: float = 0.3,
) -> MatchReport:
    claims = list(claims)
    hits_by_q: Dict[str, List[MatchHit]] = {}
    unmatched = []
    matched_count = 0

    for c in claims:
        hits = match_claim_to_corpus(c, corpus, min_score=min_score)
        if not hits:
            unmatched.append(c.keyword)
        else:
            matched_count += 1
            for h in hits:
                hits_by_q.setdefault(h.matched_question_id, []).append(h)

    # 재탕 후보: 여러 claim 이 같은 문항을 가리키거나 점수 높은 순
    ranked = sorted(
        hits_by_q.items(),
        key=lambda kv: (
            -len(kv[1]),            # 가리키는 claim 수 많은 순
            -max(h.match_score for h in kv[1]),  # 최고 점수 순
        ),
    )
    reappearance = [qid for qid, _ in ranked]

    return MatchReport(
        total_claims=len(claims),
        matched_claims=matched_count,
        unmatched_claims=unmatched,
        hits_by_question=hits_by_q,
        reappearance_candidates=reappearance,
    )


def report_to_dict(r: MatchReport) -> Dict:
    return {
        "total_claims": r.total_claims,
        "matched_claims": r.matched_claims,
        "unmatched_claims": list(r.unmatched_claims),
        "reappearance_candidates": list(r.reappearance_candidates),
        "hits_by_question": {
            qid: [
                {
                    "keyword": h.keyword,
                    "score": round(h.match_score, 4),
                    "matched_fields": list(h.matched_fields),
                    "source_url": h.secondary_source_url,
                    "source_quote": h.secondary_source_quote,
                }
                for h in hits
            ]
            for qid, hits in r.hits_by_question.items()
        },
        "caveat": "이 매칭은 MID 신뢰도 신호입니다. 수석위원 심사 없이 하류 사용 금지 (C-0).",
    }
