"""harness/ pipeline + schemas 회귀 테스트. stdlib only."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HARNESS_BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(HARNESS_BACKEND))

from schemas import (  # noqa: E402
    LineageEntry,
    append_lineage,
    c0_hard_check,
    latest_stage,
    read_lineage,
)
import reconstruct_pipeline as rp  # noqa: E402


class C0HardCheckTests(unittest.TestCase):
    def test_all_conditions_pass(self):
        ok, reasons = c0_hard_check(
            source_url="https://example.com",
            quoted_text="본문 그대로 인용",
            source_date="2026-04-18",
            independent_sources=2,
        )
        self.assertTrue(ok)
        self.assertEqual(reasons, [])

    def test_missing_url(self):
        ok, reasons = c0_hard_check(None, "quote", "2026-04-18", 2)
        self.assertFalse(ok)
        self.assertIn("source_url 없음", reasons)

    def test_short_quoted(self):
        ok, reasons = c0_hard_check("u", "  ", "2026-04-18", 2)
        self.assertFalse(ok)

    def test_missing_date(self):
        ok, reasons = c0_hard_check("u", "quote", None, 2)
        self.assertFalse(ok)

    def test_insufficient_independent_sources(self):
        ok, reasons = c0_hard_check("u", "quote", "2026-04-18", 1)
        self.assertFalse(ok)

    def test_primary_source_allows_one(self):
        ok, reasons = c0_hard_check("u", "quote", "2026-04-18", 1, primary_source=True)
        self.assertTrue(ok)


class LineageJsonlTests(unittest.TestCase):
    def test_append_and_read_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "l.jsonl"
            e = LineageEntry(
                entry_id="abc",
                claim_id="cid",
                stage="collected",
                actor="P1",
                timestamp="2026-04-18T00:00:00Z",
                source_url="u",
                quoted_text="q",
                source_date="2026-04-18",
                independent_sources=2,
                verdict_detail="ok",
            )
            append_lineage(path, e)
            loaded = read_lineage(path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].stage, "collected")

    def test_latest_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "l.jsonl"
            for st in ("collected", "synthesized", "quarantined"):
                append_lineage(
                    path,
                    LineageEntry(
                        entry_id=st,
                        claim_id="same",
                        stage=st,
                        actor="X",
                        timestamp="t",
                    ),
                )
            entries = read_lineage(path)
            self.assertEqual(latest_stage(entries, "same"), "quarantined")


class PipelineTests(unittest.TestCase):
    def _write_agent_output(self, dir_: Path, name: str, payload: dict) -> Path:
        p = dir_ / f"{name}.json"
        p.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return p

    def test_full_run_routes_correctly(self):
        with tempfile.TemporaryDirectory() as tmp:
            lc = Path(tmp) / "lc"
            lc.mkdir()
            self._write_agent_output(
                lc,
                "p1_raw",
                {
                    "agent_id": "P1",
                    "claims": [
                        {
                            "claim": "캠코 필기 5/9",
                            "source_url": "https://kamco.or.kr",
                            "quoted_text": "필기시험 2026-05-09",
                            "source_date": "2026-04-15",
                            "independent_sources": 2,
                        },
                        {
                            "claim": "추측",
                            "source_url": None,
                            "quoted_text": "",
                            "source_date": None,
                            "independent_sources": 0,
                        },
                    ],
                },
            )
            restored = Path(tmp) / "restored.jsonl"
            quarantine = Path(tmp) / "quarantined.jsonl"
            lineage = Path(tmp) / "lineage.jsonl"
            outputs = rp.load_agent_outputs(lc)
            flat = rp.extract_claims(outputs)
            stats = rp.route_and_log(flat, restored, quarantine, lineage)
            self.assertEqual(stats["c0_passed"], 1)
            self.assertEqual(stats["quarantined"], 1)
            self.assertEqual(len(read_lineage(lineage)), 2)


class Sc2RegressionTests(unittest.TestCase):
    """SC2 2026-04-18 지적 — confidence=high 자동 primary 승격 우회 방지 + 과조기 승격 방지."""

    def test_confidence_high_alone_does_not_promote_primary(self):
        # C-0: independent_sources=1 + confidence=high 만으로는 primary 승격 불가
        claim = {
            "claim": "c",
            "source_url": "u",
            "quoted_text": "quote",
            "source_date": "2026-04-18",
            "independent_sources": 1,
            "confidence": "high",  # 이것만으로는 우회 불가
        }
        stage, _ = rp.c0_gate("P1", claim)
        self.assertEqual(stage, "quarantined")

    def test_explicit_primary_source_allows_single_independent(self):
        claim = {
            "claim": "c",
            "source_url": "u",
            "quoted_text": "quote",
            "source_date": "2026-04-18",
            "independent_sources": 1,
            "primary_source": True,
        }
        stage, _ = rp.c0_gate("P1", claim)
        self.assertEqual(stage, "c0_passed")

    def test_c0_passed_is_not_sc_reviewed(self):
        # c0_passed 통과가 자동으로 sc_reviewed/restored 로 승격되지 않는다
        claim = {
            "claim": "c",
            "source_url": "u",
            "quoted_text": "quote",
            "source_date": "2026-04-18",
            "independent_sources": 2,
        }
        stage, _ = rp.c0_gate("P1", claim)
        self.assertEqual(stage, "c0_passed")
        self.assertNotEqual(stage, "sc_reviewed")
        self.assertNotEqual(stage, "restored")


class P12SecondAuditRegressionTests(unittest.TestCase):
    """P12 2차 심사(2026-04-18) — 멱등성 + P9 라이선스 차단."""

    def test_entry_id_is_unique_across_runs(self):
        """같은 claim_id/stage/timestamp 라도 salt 로 uniqueness 강제."""
        id1 = rp._entry_id("cid", "c0_passed", "2026-04-18T00:00:00Z", salt="run1")
        id2 = rp._entry_id("cid", "c0_passed", "2026-04-18T00:00:00Z", salt="run2")
        self.assertNotEqual(id1, id2)

    def test_license_eligible_for_p9_blocks_kogl4(self):
        self.assertFalse(rp.license_eligible_for_p9("공공누리 4유형"))
        self.assertFalse(rp.license_eligible_for_p9("공공누리 제4유형 (출처·비상업·변형금지)"))
        self.assertFalse(rp.license_eligible_for_p9("KOGL-4"))
        self.assertFalse(rp.license_eligible_for_p9("CC BY-NC-ND"))

    def test_license_eligible_fail_closed_on_empty(self):
        self.assertFalse(rp.license_eligible_for_p9(""))
        self.assertFalse(rp.license_eligible_for_p9(None))

    def test_license_eligible_allows_permissive(self):
        self.assertTrue(rp.license_eligible_for_p9("CC BY 4.0"))
        self.assertTrue(rp.license_eligible_for_p9("MIT License"))
        self.assertTrue(rp.license_eligible_for_p9("공공누리 1유형"))


class RestoreScoreTests(unittest.TestCase):
    """restore_score 매트릭스 빌드 + 히트맵 색상."""

    def test_empty_input_returns_red_alerts(self):
        import restore_score as rs
        matrices = rs.build_matrix([])
        summary = rs.summary_for_ui(matrices)
        self.assertEqual(summary["north_star_goal"], 0.95)
        for alert in summary["alerts"]:
            self.assertEqual(alert["level"], "red")


if __name__ == "__main__":
    unittest.main()
