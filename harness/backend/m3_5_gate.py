"""M3.5 게이트 — P12 '실제 기출 반영' 검증.

자율모드에서는 RESET 지시 대신 log 기록. 사용자 복귀 시 판결.

판정 기준 (P12 spec §4.2 FACT_AUDIT):
- data/restored/ 에 실제 시험 기출 원문 인용 ≥ 5건 존재
- source_type 이 "official_released" 또는 "ebook" 인 claim 포함
- 각 claim 에 C-0 4조건 전부 충족

판정 결과:
- PASS   → M4 진입 가능
- GATED  → 블로커 해소 후 재판정
- RESET  → 자율모드에서는 log 만. 사용자 복귀 시 AskUserQuestion

CLI:
    python m3_5_gate.py           → JSON 판정
    python m3_5_gate.py --log     → docs/m3_5_gate_log.md 에 append
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from schemas import c0_hard_check


HARNESS_ROOT = Path(__file__).resolve().parent.parent
RESTORED_JSONL = HARNESS_ROOT / "data" / "restored" / "c0_passed.jsonl"
LOG_MD = HARNESS_ROOT.parent / "docs" / "m3_5_gate_log.md"
MIN_REAL_EXAM_REFS = 5


def _load_restored() -> List[dict]:
    if not RESTORED_JSONL.exists():
        return []
    out: List[dict] = []
    with RESTORED_JSONL.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def _is_real_exam_ref(rec: dict) -> bool:
    """실제 기출 원문 인용 여부."""
    typ = (rec.get("source_type") or rec.get("kind") or "").lower()
    if typ in ("official_released", "ebook", "primary"):
        if rec.get("quoted_text") and rec.get("source_url"):
            return True
    # fallback: claim 본문 키워드
    url = (rec.get("source_url") or "").lower()
    quoted = rec.get("quoted_text") or ""
    if "shinsa" in url or "kamco" in url or ".pdf" in url:
        if len(quoted) >= 20:
            return True
    return False


def evaluate() -> Dict:
    records = _load_restored()
    real_refs = [r for r in records if _is_real_exam_ref(r)]
    c0_failures = []
    for r in records:
        ok, reasons = c0_hard_check(
            r.get("source_url"),
            r.get("quoted_text"),
            r.get("source_date"),
            int(r.get("independent_sources", 0) or 0),
            primary_source=bool(r.get("primary_source")),
        )
        if not ok:
            c0_failures.append({"claim": (r.get("claim") or "")[:80], "reasons": reasons})

    count = len(real_refs)
    verdict = (
        "PASS" if count >= MIN_REAL_EXAM_REFS and not c0_failures
        else "GATED" if count > 0
        else "RESET_CANDIDATE"
    )
    return {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verdict": verdict,
        "real_exam_refs_count": count,
        "required_min": MIN_REAL_EXAM_REFS,
        "c0_failures": c0_failures,
        "autonomous_mode_note": (
            "RESET 지시는 사용자 복귀 시 AskUserQuestion 으로 위임. "
            "현재 세션에서는 log 만 기록."
        ),
        "proceed_to_m4": verdict == "PASS",
    }


def append_log(result: Dict) -> None:
    LOG_MD.parent.mkdir(parents=True, exist_ok=True)
    header = "# M3.5 P12 게이트 판정 로그\n\n" if not LOG_MD.exists() else ""
    entry = (
        f"## {result['timestamp']}\n"
        f"- verdict: **{result['verdict']}**\n"
        f"- real_exam_refs: {result['real_exam_refs_count']} / {result['required_min']}\n"
        f"- C-0 failures: {len(result['c0_failures'])}\n"
        f"- proceed_to_m4: {result['proceed_to_m4']}\n"
        f"- note: {result['autonomous_mode_note']}\n\n"
    )
    with LOG_MD.open("a", encoding="utf-8") as fp:
        fp.write(header + entry)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", action="store_true", help="append to docs/m3_5_gate_log.md")
    args = parser.parse_args()
    result = evaluate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.log:
        append_log(result)
    return 0 if result["proceed_to_m4"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
