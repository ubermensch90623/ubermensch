"""promote — C-0 통과 claim 을 SC 심사 · P12 승인 경로로 승격.

stage 전이:
    c0_passed  → sc_reviewed   (SC1 AND SC2 심사 PASS 인자 받음)
    sc_reviewed → p12_approved (P12 CEO PASS)
    p12_approved → restored    (최종 확정)

파일:
    data/restored/c0_passed.jsonl      — c0_passed stage
    data/restored/sc_reviewed.jsonl
    data/restored/p12_approved.jsonl
    data/restored/final.jsonl          — restored 확정본

호출 예:
    python promote.py --claim abc123 --to sc_reviewed --sc1-pass --sc2-pass
    python promote.py --claim abc123 --to p12_approved --p12-pass
    python promote.py --claim abc123 --to restored
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from schemas import LineageEntry, append_lineage


HARNESS_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = HARNESS_ROOT / "data"
RESTORED_DIR = DATA_ROOT / "restored"
LINEAGE_PATH = DATA_ROOT / "source_lineage.jsonl"

STAGE_FILE = {
    "c0_passed": RESTORED_DIR / "c0_passed.jsonl",
    "sc_reviewed": RESTORED_DIR / "sc_reviewed.jsonl",
    "p12_approved": RESTORED_DIR / "p12_approved.jsonl",
    "restored": RESTORED_DIR / "final.jsonl",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def find_claim(claim_id: str, source_stage: str) -> Optional[dict]:
    fp = STAGE_FILE.get(source_stage)
    if not fp or not fp.exists():
        return None
    with fp.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("claim_id") == claim_id:
                return rec
    return None


def promote(
    claim_id: str,
    to_stage: str,
    actor: str,
    sc1_pass: bool = False,
    sc2_pass: bool = False,
    p12_pass: bool = False,
    verdict_note: str = "",
) -> Dict:
    prev_map = {
        "sc_reviewed": "c0_passed",
        "p12_approved": "sc_reviewed",
        "restored": "p12_approved",
    }
    source = prev_map.get(to_stage)
    if not source:
        return {"ok": False, "error": f"invalid to_stage {to_stage}"}
    if to_stage == "sc_reviewed" and not (sc1_pass and sc2_pass):
        return {"ok": False, "error": "sc_reviewed 승격은 SC1 AND SC2 PASS 동시 필요"}
    if to_stage == "p12_approved" and not p12_pass:
        return {"ok": False, "error": "p12_approved 승격은 P12 PASS 필요"}
    rec = find_claim(claim_id, source)
    if not rec:
        return {"ok": False, "error": f"claim {claim_id} not in {source}"}
    target = STAGE_FILE[to_stage]
    target.parent.mkdir(parents=True, exist_ok=True)
    rec["stage"] = to_stage
    with target.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    ts = _now()
    append_lineage(
        LINEAGE_PATH,
        LineageEntry(
            entry_id=f"{claim_id[:8]}-{to_stage[:4]}-{ts[-8:]}",
            claim_id=claim_id,
            stage=to_stage,
            actor=actor,
            timestamp=ts,
            verdict_detail=verdict_note or f"promoted from {source}",
        ),
    )
    # P12 3차 recommendation #2 (2026-04-18): p12_approved 전이 시 m3_5_gate 자동 호출
    post_check: Dict = {}
    if to_stage == "p12_approved":
        try:
            import m3_5_gate
            post_check = m3_5_gate.evaluate()
        except ImportError:
            post_check = {"error": "m3_5_gate import failed"}
    return {"ok": True, "promoted_to": to_stage, "post_check": post_check}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--claim", required=True)
    p.add_argument("--to", required=True, choices=["sc_reviewed", "p12_approved", "restored"])
    p.add_argument("--actor", default="Lead")
    p.add_argument("--sc1-pass", action="store_true")
    p.add_argument("--sc2-pass", action="store_true")
    p.add_argument("--p12-pass", action="store_true")
    p.add_argument("--note", default="")
    args = p.parse_args()
    result = promote(
        args.claim, args.to, args.actor,
        sc1_pass=args.sc1_pass, sc2_pass=args.sc2_pass,
        p12_pass=args.p12_pass, verdict_note=args.note,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
