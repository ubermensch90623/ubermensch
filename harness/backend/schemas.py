"""harness schemas — C-0 데이터 혈통 + 복원 상태 태그.

기존 exam_analyzer.corpus.models 의 Question/Provenance 를 그대로 재사용하되,
harness 전용 wrapper 로 '격리 상태(low_confidence vs restored)' 추적.

헌법 참조:
- C-0: source_url + quoted_text + source_date + independent_sources>=2
- C-9: 모든 사건은 append-only 로 source_lineage.jsonl 에 기록
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Literal, Optional


LineageStage = Literal[
    "collected",        # P1-P5/P13-P15 가 수집한 raw
    "contested",        # P6 회의론자 공격 중
    "synthesized",      # P7 합성 완료
    "reverse_engineered",  # P9 패턴 기반 생성
    "c0_passed",        # C-0 4조건 통과 (아직 SC 심사 전, 2026-04-18 SC2 지적 반영)
    "sc_reviewed",      # SC1/SC2 심사 완료 (c0_passed 이후)
    "p12_approved",     # P12 CEO 승인
    "restored",         # 최종 확정 팩트 (p12_approved 이후)
    "quarantined",      # C-0 미달 — 하류 참조 금지
    "reset",            # P12 RESET 지시로 폐기
]


@dataclass
class LineageEntry:
    """append-only 이벤트."""

    entry_id: str                # sha1(claim_id|stage|timestamp)[:12]
    claim_id: str                # 연결된 claim 의 id
    stage: LineageStage
    actor: str                   # "P1" | "P12" | "SC1" | "Lead" 등
    timestamp: str               # ISO 8601 with Z
    source_url: Optional[str] = None
    quoted_text: Optional[str] = None
    source_date: Optional[str] = None
    independent_sources: int = 0
    verdict_detail: str = ""
    upstream_entries: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "claim_id": self.claim_id,
            "stage": self.stage,
            "actor": self.actor,
            "timestamp": self.timestamp,
            "source_url": self.source_url,
            "quoted_text": self.quoted_text,
            "source_date": self.source_date,
            "independent_sources": self.independent_sources,
            "verdict_detail": self.verdict_detail,
            "upstream_entries": list(self.upstream_entries),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "LineageEntry":
        return cls(
            entry_id=d["entry_id"],
            claim_id=d["claim_id"],
            stage=d["stage"],
            actor=d["actor"],
            timestamp=d["timestamp"],
            source_url=d.get("source_url"),
            quoted_text=d.get("quoted_text"),
            source_date=d.get("source_date"),
            independent_sources=d.get("independent_sources", 0),
            verdict_detail=d.get("verdict_detail", ""),
            upstream_entries=d.get("upstream_entries", []),
        )


def c0_hard_check(
    source_url: Optional[str],
    quoted_text: Optional[str],
    source_date: Optional[str],
    independent_sources: int,
    primary_source: bool = False,
) -> tuple[bool, List[str]]:
    """C-0 4조건 동시 충족 판정.

    Returns (passed, reasons). primary_source=True 이면 independent_sources>=1 허용.
    """
    reasons: List[str] = []
    if not source_url:
        reasons.append("source_url 없음")
    if not quoted_text or len(quoted_text.strip()) < 3:
        reasons.append("quoted_text 없음 또는 너무 짧음")
    if not source_date:
        reasons.append("source_date 없음")
    min_sources = 1 if primary_source else 2
    if independent_sources < min_sources:
        reasons.append(
            f"independent_sources={independent_sources} < 필요 {min_sources}"
        )
    return (len(reasons) == 0, reasons)


def append_lineage(path: Path, entry: LineageEntry) -> None:
    """append-only JSONL 쓰기. 타임아웃 대비 flush."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(entry.to_dict(), ensure_ascii=False))
        fp.write("\n")
        fp.flush()


def read_lineage(path: Path) -> List[LineageEntry]:
    if not path.exists():
        return []
    entries: List[LineageEntry] = []
    with path.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            entries.append(LineageEntry.from_dict(json.loads(line)))
    return entries


def latest_stage(entries: List[LineageEntry], claim_id: str) -> Optional[LineageStage]:
    """claim_id 의 최신 stage — UI 에서 격리 여부 판별용."""
    for e in reversed(entries):
        if e.claim_id == claim_id:
            return e.stage
    return None
