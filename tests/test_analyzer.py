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
    compute_pass_scenarios,
    compute_total,
    convert_to_scale,
    decompose_contributions,
    diagnose,
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


class TestDiagnose(unittest.TestCase):
    """정밀 원인 분석 — 서민금융진흥원 골든 픽스처로 수학 검증."""

    def test_contributions_sum_equals_gap(self) -> None:
        """기여도 합 = 격차 (수학적 항등성)."""
        rec = _golden_record()
        contribs = decompose_contributions(rec.sections, rec.cutoff)
        total_deficit = sum(c.deficit for c in contribs)
        expected_gap = rec.total() - rec.cutoff
        self.assertAlmostEqual(total_deficit, expected_gap, places=4)

    def test_contribution_values_for_user_scores(self) -> None:
        """서민금융진흥원 실제 점수로 계산한 기여도."""
        rec = _golden_record()
        contribs = decompose_contributions(rec.sections, rec.cutoff)
        by_name = {c.section.name: c for c in contribs}
        # 직업기초: 실제=19.33, 기대 = 40 * 64.48/100 = 25.792, 기여 = -6.462
        self.assertAlmostEqual(by_name["직업기초능력평가"].weighted_actual, 19.33, places=4)
        self.assertAlmostEqual(by_name["직업기초능력평가"].weighted_expected, 25.792, places=3)
        self.assertAlmostEqual(by_name["직업기초능력평가"].deficit, -6.462, places=3)
        # 직무수행: 실제=38.76, 기대 = 60 * 64.48/100 = 38.688, 기여 = +0.072
        self.assertAlmostEqual(by_name["직무수행능력평가"].weighted_actual, 38.76, places=4)
        self.assertAlmostEqual(by_name["직무수행능력평가"].weighted_expected, 38.688, places=3)
        self.assertAlmostEqual(by_name["직무수행능력평가"].deficit, 0.072, places=3)

    def test_pass_scenarios_single_section_math(self) -> None:
        """한 영역만 개선하는 시나리오의 목표 점수 정확성."""
        rec = _golden_record()
        scenarios = compute_pass_scenarios(rec.sections, rec.cutoff)
        by_name = {sc.name: sc for sc in scenarios}
        # 직업기초만 개선: 필요 원점수 = 19.33 + 6.39 = 25.72
        s_ncs = by_name["직업기초능력평가만 개선"]
        self.assertAlmostEqual(
            s_ncs.required_raw_scores["직업기초능력평가"], 25.72, places=2
        )
        # 직무수행만 개선: 필요 원점수 = 38.76 + 6.39 = 45.15
        s_job = by_name["직무수행능력평가만 개선"]
        self.assertAlmostEqual(
            s_job.required_raw_scores["직무수행능력평가"], 45.15, places=2
        )

    def test_pass_scenario_validates_via_recomputation(self) -> None:
        """시나리오의 목표 점수로 ExamRecord 재구성 시 합격 여부 확인."""
        rec = _golden_record()
        scenarios = compute_pass_scenarios(rec.sections, rec.cutoff)
        for sc in scenarios:
            new_sections = [
                Section(
                    name=s.name,
                    score=sc.required_raw_scores[s.name],
                    max_score=s.max_score,
                    weight=s.weight,
                )
                for s in rec.sections
            ]
            new_total = sum(s.weighted() for s in new_sections)
            # 시나리오대로 맞췄을 때 커트라인에 도달해야 함 (수치 오차 허용)
            self.assertAlmostEqual(new_total, rec.cutoff, places=2, msg=f"시나리오: {sc.name}")

    def test_equal_pp_scenario_equals_negative_gap(self) -> None:
        """균등 개선 시나리오는 |gap| 만큼 백분율 상승 (weights=100 인 경우)."""
        rec = _golden_record()
        scenarios = compute_pass_scenarios(rec.sections, rec.cutoff)
        equal = next(sc for sc in scenarios if sc.name == "모든 영역 균등 개선")
        # 각 영역 delta_pp 는 같아야 함
        pps = list(equal.delta_percentage_points.values())
        self.assertAlmostEqual(pps[0], pps[1], places=4)
        # 그리고 그 값은 -gap 과 같음 (weights sum to 100)
        self.assertAlmostEqual(pps[0], 6.39, places=2)

    def test_diagnose_primary_cause_is_NCS(self) -> None:
        """주 원인은 직업기초능력평가 (더 큰 음의 기여)."""
        d = diagnose(_golden_record())
        self.assertIsNotNone(d.primary_cause)
        self.assertEqual(d.primary_cause.name, "직업기초능력평가")

    def test_diagnose_scenarios_contain_all_three(self) -> None:
        """
        ※ audit-v1.md 반영: 이전 test_diagnose_recommended_scenario_targets_weakest 는
        약점 집중 = 옳다 라는 HEURISTIC 을 고정시키는 잘못된 테스트였음.
        제거하고 대신 3개 시나리오 전부 존재하는지 (수학적 사실) 만 검증.
        """
        d = diagnose(_golden_record())
        names = {sc.name for sc in d.scenarios}
        self.assertIn("직업기초능력평가만 개선", names)
        self.assertIn("직무수행능력평가만 개선", names)
        self.assertIn("모든 영역 균등 개선", names)
        self.assertEqual(len(d.scenario_trade_offs), 3)

    def test_diagnose_requires_cutoff(self) -> None:
        rec = ExamRecord(
            agency="x",
            date="2026-01-01",
            sections=[Section("a", 10, 40, 40), Section("b", 30, 60, 60)],
            cutoff=None,
        )
        with self.assertRaises(ValueError):
            diagnose(rec)

    def test_diagnose_already_passed(self) -> None:
        """이미 합격이면 시나리오는 비어있고 체크리스트는 '유지' 메시지."""
        rec = ExamRecord(
            agency="x",
            date="2026-01-01",
            sections=[Section("a", 40, 40, 40), Section("b", 60, 60, 60)],
            cutoff=50.0,
        )
        d = diagnose(rec)
        self.assertGreaterEqual(d.gap, 0)
        self.assertEqual(d.scenarios, [])
        self.assertTrue(any("합격" in item for item in d.checklist))

    def test_diagnose_cli_output_contains_key_info(self) -> None:
        """CLI diagnose 출력에 정확한 수치가 포함되어 있는지."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli_main([
                "--no-color",
                "diagnose",
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
        self.assertEqual(code, 0)
        out = buf.getvalue()
        # 핵심 수치 확인
        self.assertIn("58.09", out)
        self.assertIn("64.48", out)
        self.assertIn("-6.39", out)
        self.assertIn("25.79", out)  # 직업기초 기대
        self.assertIn("25.72", out)  # 직업기초 목표 원점수
        self.assertIn("45.15", out)  # 직무수행 목표 원점수
        self.assertIn("주 원인", out)  # 수학적 사실 (최대 음의 기여)
        self.assertIn("직업기초능력평가", out)

    def test_diagnose_cli_json(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli_main([
                "--no-color",
                "--json",
                "diagnose",
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
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertAlmostEqual(payload["total"], 58.09, places=2)
        self.assertAlmostEqual(payload["gap"], -6.39, places=2)
        self.assertEqual(payload["primary_cause"], "직업기초능력평가")
        # audit-v1.md: recommended_scenario 제거. 모든 시나리오의 trade-off 만 제공
        self.assertEqual(len(payload["scenarios"]), 3)
        self.assertEqual(len(payload["scenario_trade_offs"]), 3)
        # 기여도 합 = gap
        total_deficit = sum(c["deficit"] for c in payload["contributions"])
        self.assertAlmostEqual(total_deficit, payload["gap"], places=2)

    def test_diagnose_from_saved_id(self) -> None:
        """--from-id 로 이력에서 기록을 불러와 진단."""
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        tmp.close()
        os.unlink(tmp.name)
        try:
            # 먼저 저장
            buf_save = io.StringIO()
            with redirect_stdout(buf_save):
                cli_main([
                    "--no-color",
                    "--data-file",
                    tmp.name,
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
            records = load_history(Path(tmp.name))
            self.assertEqual(len(records), 1)
            rid = records[0].record_id
            # 진단
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_main([
                    "--no-color",
                    "--data-file",
                    tmp.name,
                    "diagnose",
                    "--from-id",
                    rid,
                ])
            self.assertEqual(code, 0)
            self.assertIn("58.09", buf.getvalue())
        finally:
            p = Path(tmp.name)
            if p.exists():
                p.unlink()


if __name__ == "__main__":
    unittest.main()
