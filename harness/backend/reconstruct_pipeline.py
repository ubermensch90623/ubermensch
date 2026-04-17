"""reconstruct_pipeline — 에이전트 raw 수집물을 C-0 게이트에 통과시키는 파이프라인.

단계:
1. load_agent_outputs(low_confidence/*.json) — P1..P15 raw 수집
2. extract_claims() — 평탄화
3. c0_gate() — 4조건 전수 검사 (schemas.c0_hard_check)
4. route() — 통과: data/restored/  미통과: data/low_confidence/ (유지) + 혈통 append
5. emit_lineage() — source_lineage.jsonl 로그

stdlib only. CLAUDE.md §3 타임아웃 규칙: 150줄 이하 유지.
"""
from __future__ import annotations

import json
import hashlib
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from schemas import (
    LineageEntry,
    LineageStage,
    append_lineage,
    c0_hard_check,
)


HARNESS_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = HARNESS_ROOT / "data"
LINEAGE_PATH = DATA_ROOT / "source_lineage.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _claim_id(agent_id: str, claim: Dict[str, Any]) -> str:
    payload = f"{agent_id}|{claim.get('claim','')}|{claim.get('source_url','')}"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]


def _entry_id(claim_id: str, stage: str, ts: str, salt: str = "") -> str:
    """entry_id 멱등성: P12 2차 지적(2026-04-18) — 같은 ts 에 같은 claim/stage 로 두 번 append 방지.
    salt 에 run_id(uuid) 또는 monotonic seq 합쳐 uniqueness 강제.
    """
    if not salt:
        salt = uuid.uuid4().hex[:8]
    return hashlib.sha1(
        f"{claim_id}|{stage}|{ts}|{salt}".encode("utf-8")
    ).hexdigest()[:12]


# 공공누리 4유형 등 파생 금지 라이선스 — P9 input 에서 자동 제외 (P12 2차 지적)
BLOCKED_LICENSES_FOR_P9 = {
    "공공누리 4유형",
    "공공누리 제4유형",
    "KOGL-4",
    "kogl4",
    "CC BY-ND",
    "CC BY-NC-ND",
}


def license_eligible_for_p9(license_str: str) -> bool:
    """License 가 파생(리버스 엔지니어링) 허용인지. fail-closed: 불명이면 False."""
    if not license_str:
        return False
    lic = license_str.strip().lower()
    for blocked in BLOCKED_LICENSES_FOR_P9:
        if blocked.lower() in lic:
            return False
    return True


def load_agent_outputs(low_confidence_dir: Path) -> List[Tuple[str, Dict[str, Any]]]:
    """디렉토리의 p*.json 파일을 (agent_id, raw_dict) 리스트로 반환."""
    results: List[Tuple[str, Dict[str, Any]]] = []
    if not low_confidence_dir.exists():
        return results
    for jf in sorted(low_confidence_dir.glob("p*.json")):
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        agent_id = data.get("agent_id", jf.stem)
        results.append((agent_id, data))
    return results


def extract_claims(
    outputs: Iterable[Tuple[str, Dict[str, Any]]]
) -> List[Tuple[str, Dict[str, Any]]]:
    """(agent_id, single_claim_dict) 평탄화."""
    flat: List[Tuple[str, Dict[str, Any]]] = []
    for agent_id, raw in outputs:
        for key in ("claims", "contracts", "books", "tools", "items"):
            if key in raw and isinstance(raw[key], list):
                for c in raw[key]:
                    if isinstance(c, dict):
                        flat.append((agent_id, c))
    return flat


def c0_gate(
    agent_id: str,
    claim: Dict[str, Any],
) -> Tuple[LineageStage, List[str]]:
    """claim 을 C-0 4조건으로 판정.

    SC2 지적(2026-04-18): confidence=='high' 자동 primary 승격은 우회 구멍.
    primary_source 는 오직 claim 에 명시된 구조화 플래그로만 판정.
    C-0 통과 = 'c0_passed' (중간 단계). 'sc_reviewed' 는 SC1/SC2 수동 승인 후에만.
    """
    primary = bool(claim.get("primary_source"))
    passed, reasons = c0_hard_check(
        source_url=claim.get("source_url"),
        quoted_text=claim.get("quoted_text"),
        source_date=claim.get("source_date"),
        independent_sources=int(claim.get("independent_sources", 0) or 0),
        primary_source=primary,
    )
    if passed:
        return ("c0_passed", reasons)
    return ("quarantined", reasons)


def route_and_log(
    flat_claims: Iterable[Tuple[str, Dict[str, Any]]],
    restored_path: Path,
    quarantine_path: Path,
    lineage_path: Path = LINEAGE_PATH,
) -> Dict[str, int]:
    """C-0 통과: c0_passed.jsonl append. 미통과: quarantine. 혈통 기록."""
    restored_path.parent.mkdir(parents=True, exist_ok=True)
    quarantine_path.parent.mkdir(parents=True, exist_ok=True)
    stats = {"c0_passed": 0, "quarantined": 0}
    run_id = os.environ.get("HARNESS_RUN_ID") or uuid.uuid4().hex[:8]
    with restored_path.open("a", encoding="utf-8") as r_fp, \
         quarantine_path.open("a", encoding="utf-8") as q_fp:
        for agent_id, claim in flat_claims:
            cid = _claim_id(agent_id, claim)
            stage, reasons = c0_gate(agent_id, claim)
            ts = _now()
            entry = LineageEntry(
                entry_id=_entry_id(cid, stage, ts, salt=run_id),
                claim_id=cid,
                stage=stage,
                actor=agent_id,
                timestamp=ts,
                source_url=claim.get("source_url"),
                quoted_text=(claim.get("quoted_text") or "")[:400],
                source_date=claim.get("source_date"),
                independent_sources=int(claim.get("independent_sources", 0) or 0),
                verdict_detail="; ".join(reasons) if reasons else "PASS",
            )
            append_lineage(lineage_path, entry)
            record = {"claim_id": cid, "agent_id": agent_id, **claim, "stage": stage}
            # c0_passed 는 restored 아님 — c0_passed.jsonl 에 쌓이되 restored 카운트 제외.
            # stage='restored' 는 p12_approved 이후 별도 승격 경로에서만 기록.
            if stage == "c0_passed":
                r_fp.write(json.dumps(record, ensure_ascii=False) + "\n")
                stats["c0_passed"] = stats.get("c0_passed", 0) + 1
            else:
                q_fp.write(json.dumps(record, ensure_ascii=False) + "\n")
                stats["quarantined"] = stats.get("quarantined", 0) + 1
    return stats


def run_pipeline(
    low_confidence_dir: Path = DATA_ROOT / "low_confidence",
    restored_jsonl: Path = DATA_ROOT / "restored" / "c0_passed.jsonl",
    quarantine_jsonl: Path = DATA_ROOT / "low_confidence" / "c0_failed.jsonl",
) -> Dict[str, int]:
    outputs = load_agent_outputs(low_confidence_dir)
    flat = extract_claims(outputs)
    return route_and_log(flat, restored_jsonl, quarantine_jsonl)


if __name__ == "__main__":
    print(json.dumps(run_pipeline(), indent=2))
