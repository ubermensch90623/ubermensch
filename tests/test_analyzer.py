"""exam_analyzer 단위 테스트. 서민금융진흥원 실제 점수를 골든 픽스처로 사용."""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

# 저장소 루트를 sys.path 에 추가 (테스트 독립 실행 지원)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exam_analyzer.analyzer import (  # noqa: E402
    analyze,
    compute_gap,
    compute_total,
    convert_to_scale,
    judge_pass,
    normalize_weights,
)
from exam_analyzer.cli import main as cli_main  # noqa: E402
from exam_analyzer.models import (  # noqa: E402
    ExamRecord,
    Section,
    generate_record_id,
    record_from_dict,
    record_to_dict,
)
from exam_analyzer.storage import (  # noqa: E402
    append_record,
    delete_record,
    find_record,
    load_history,
    save_history,
)


def _golden_record() -> ExamRecord:
    """사용자 실제 서민금융진흥원 2026-04 필기 점수."""
    return ExamRecord(
        agency="서민금융진흥원",
        date="2026-04-15",
        sections=[
            Section("직업기초능력평가", 19.33, 40.0, 40.0),
            Section("직무수행능력평가", 38.76, 60.0, 60.0),
        ],
        cutoff=64.48,
    )


class TestGoldenFixture(unittest.TestCase):
    """사용자 실제 점수 — 회귀 방지 골든 테스트."""

    def test_total_matches_58_09(self) -> None:
        rec = _golden_record()
        self.assertAlmostEqual(rec.total(), 58.09, places=2)

    def test_gap_is_minus_6_39(self) -> None:
        rec = _golden_record()
        self.assertAlmostEqual(rec.gap(), -6.39, places=2)

    def test_verdict_is_fail(self) -> None:
        rec = _golden_record()
        self.assertFalse(rec.passed())

    def test_analyze_weakest_is_NCS(self) -> None:
        result = analyze(_golden_record())
        # 직업기초능력평가: 48.33%, 직무수행능력평가: 64.60% → 직업기초가 더 약함
        self.assertIsNotNone(result.weakest)
        self.assertEqual(result.weakest.name, "직업기초능력평가")
        self.assertIsNotNone(result.strongest)
        self.assertEqual(result.strongest.name, "직무수행능력평가")

    def test_analyze_no_weight_rescale_for_40_plus_60(self) -> None:
        result = analyze(_golden_record())
        self.assertFalse(result.weight_rescaled)


class TestPureFunctions(unittest.TestCase):
    def test_compute_total(self) -> None:
        sections = _golden_record().sections
        self.assertAlmostEqual(compute_total(sections), 58.09, places=2)

    def test_compute_gap(self) -> None:
        self.assertAlmostEqual(compute_gap(58.09, 64.48), -6.39, places=2)

    def test_judge_pass_true_on_tie(self) -> None:
        self.assertTrue(judge_pass(70.0, 70.0))
        self.assertTrue(judge_pass(70.01, 70.0))
        self.assertFalse(judge_pass(69.99, 70.0))

    def test_convert_to_scale(self) -> None:
        self.assertAlmostEqual(convert_to_scale(19.33, 40.0, 100.0), 48.325, places=3)
        self.assertAlmostEqual(convert_to_scale(38.76, 60.0, 100.0), 64.6, places=3)

    def test_normalize_weights_rescales(self) -> None:
        sections = [
            Section("a", 10.0, 40.0, 30.0),
            Section("b", 30.0, 60.0, 60.0),
        ]
        rescaled, did, original_sum = normalize_weights(sections, target=100.0)
        self.assertTrue(did)
        self.assertAlmostEqual(original_sum, 90.0)
        self.assertAlmostEqual(sum(s.weight for s in rescaled), 100.0, places=6)

    def test_normalize_weights_noop_when_equal(self) -> None:
        sections = _golden_record().sections
        _, did, s = normalize_weights(sections, target=100.0)
        self.assertFalse(did)
        self.assertAlmostEqual(s, 100.0)


class TestSerialization(unittest.TestCase):
    def test_round_trip(self) -> None:
        rec = _golden_record()
        rec.record_id = generate_record_id(rec)
        d = record_to_dict(rec)
        rec2 = record_from_dict(d)
        rec2.record_id = rec.record_id
        self.assertEqual(rec2.agency, rec.agency)
        self.assertEqual(rec2.date, rec.date)
        self.assertAlmostEqual(rec2.total(), rec.total(), places=4)
        self.assertEqual(len(rec2.sections), 2)

    def test_record_id_stable(self) -> None:
        rec = _golden_record()
        rid1 = generate_record_id(rec)
        rid2 = generate_record_id(rec)
        self.assertEqual(rid1, rid2)
        self.assertEqual(len(rid1), 8)


class TestStorage(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        self.tmp.close()
        self.path = Path(self.tmp.name)
        os.unlink(self.path)  # 존재하지 않는 상태로 시작

    def tearDown(self) -> None:
        if self.path.exists():
            self.path.unlink()

    def test_load_missing_returns_empty(self) -> None:
        self.assertEqual(load_history(self.path), [])

    def test_append_and_load(self) -> None:
        rec = _golden_record()
        rid = append_record(self.path, rec)
        self.assertEqual(len(rid), 8)
        loaded = load_history(self.path)
        self.assertEqual(len(loaded), 1)
        self.assertAlmostEqual(loaded[0].total(), 58.09, places=2)

    def test_find_by_prefix(self) -> None:
        rec = _golden_record()
        rid = append_record(self.path, rec)
        found = find_record(self.path, rid[:4])
        self.assertIsNotNone(found)
        self.assertEqual(found.record_id, rid)

    def test_delete(self) -> None:
        rec = _golden_record()
        rid = append_record(self.path, rec)
        self.assertTrue(delete_record(self.path, rid))
        self.assertEqual(load_history(self.path), [])
        self.assertFalse(delete_record(self.path, rid))

    def test_utf8_korean_preserved(self) -> None:
        rec = _golden_record()
        append_record(self.path, rec)
        raw = self.path.read_text(encoding="utf-8")
        self.assertIn("서민금융진흥원", raw)
        self.assertIn("직업기초능력평가", raw)

    def test_save_load_roundtrip(self) -> None:
        rec = _golden_record()
        save_history(self.path, [rec])
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(data["version"], 1)
        self.assertEqual(len(data["records"]), 1)


class TestCLI(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        self.tmp.close()
        self.path = self.tmp.name
        os.unlink(self.path)

    def tearDown(self) -> None:
        p = Path(self.path)
        if p.exists():
            p.unlink()

    def _run(self, argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli_main(argv)
        return code, buf.getvalue()

    def test_analyze_golden_returns_fail_exit_code(self) -> None:
        code, out = self._run([
            "--no-color",
            "--data-file",
            self.path,
            "analyze",
            "--agency",
            "서민금융진흥원",
            "--date",
            "2026-04-15",
            "--section",
            "직업기초능력평가:19.33:40:40",
            "--section",
            "직무수행능력평가:38.76:60:60",
            "--cutoff",
            "64.48",
        ])
        self.assertEqual(code, 1)  # EXIT_FAIL
        self.assertIn("58.09", out)
        self.assertIn("불합격", out)
        self.assertIn("-6.39", out)

    def test_analyze_json_output(self) -> None:
        code, out = self._run([
            "--no-color",
            "--json",
            "--data-file",
            self.path,
            "analyze",
            "--agency",
            "서민금융진흥원",
            "--date",
            "2026-04-15",
            "--section",
            "직업기초능력평가:19.33:40:40",
            "--section",
            "직무수행능력평가:38.76:60:60",
            "--cutoff",
            "64.48",
        ])
        self.assertEqual(code, 1)
        payload = json.loads(out)
        self.assertAlmostEqual(payload["total"], 58.09, places=2)
        self.assertAlmostEqual(payload["gap"], -6.39, places=2)
        self.assertFalse(payload["passed"])
        self.assertEqual(payload["weakest"], "직업기초능력평가")

    def test_analyze_save_then_list_then_delete(self) -> None:
        code, _ = self._run([
            "--no-color",
            "--data-file",
            self.path,
            "analyze",
            "--agency",
            "서민금융진흥원",
            "--date",
            "2026-04-15",
            "--section",
            "직업기초능력평가:19.33:40:40",
            "--section",
            "직무수행능력평가:38.76:60:60",
            "--cutoff",
            "64.48",
            "--save",
        ])
        self.assertEqual(code, 1)  # 저장은 성공하지만 시험은 불합격 → 1
        code, out = self._run(["--no-color", "--data-file", self.path, "list"])
        self.assertEqual(code, 0)
        self.assertIn("서민금융진흥원", out)
        # list 에서 record_id 추출
        records = load_history(Path(self.path))
        self.assertEqual(len(records), 1)
        rid = records[0].record_id
        # show
        code, out = self._run(["--no-color", "--data-file", self.path, "show", rid])
        self.assertEqual(code, 0)
        self.assertIn("58.09", out)
        # delete
        code, _ = self._run(["--no-color", "--data-file", self.path, "delete", rid])
        self.assertEqual(code, 0)
        self.assertEqual(load_history(Path(self.path)), [])

    def test_convert_command(self) -> None:
        code, out = self._run([
            "--no-color",
            "--json",
            "convert",
            "--score",
            "19.33",
            "--max",
            "40",
            "--to",
            "100",
        ])
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertAlmostEqual(payload["converted"], 48.325, places=3)

    def test_weight_rescale_warning(self) -> None:
        code, out = self._run([
            "--no-color",
            "--data-file",
            self.path,
            "analyze",
            "--agency",
            "기관",
            "--date",
            "2026-01-01",
            "--section",
            "A:10:40:30",
            "--section",
            "B:30:60:60",
            "--cutoff",
            "50",
        ])
        self.assertIn("재조정", out)

    def test_pass_exit_code_zero(self) -> None:
        code, _ = self._run([
            "--no-color",
            "--data-file",
            self.path,
            "analyze",
            "--agency",
            "기관",
            "--date",
            "2026-01-01",
            "--section",
            "A:40:40:40",
            "--section",
            "B:60:60:60",
            "--cutoff",
            "50",
        ])
        self.assertEqual(code, 0)

    def test_stats_empty(self) -> None:
        code, out = self._run(["--no-color", "--data-file", self.path, "stats"])
        self.assertEqual(code, 0)
        self.assertIn("저장된 기록이 없습니다", out)


class TestEnvironmentOverride(unittest.TestCase):
    def test_env_variable_overrides_path(self) -> None:
        """EXAM_HISTORY_FILE 환경변수가 기본 경로를 override 하는지."""
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        tmp.close()
        os.unlink(tmp.name)
        original = os.environ.get("EXAM_HISTORY_FILE")
        os.environ["EXAM_HISTORY_FILE"] = tmp.name
        try:
            from exam_analyzer.storage import default_history_path

            self.assertEqual(str(default_history_path()), tmp.name)
        finally:
            if original is None:
                del os.environ["EXAM_HISTORY_FILE"]
            else:
                os.environ["EXAM_HISTORY_FILE"] = original
            p = Path(tmp.name)
            if p.exists():
                p.unlink()


if __name__ == "__main__":
    unittest.main()
