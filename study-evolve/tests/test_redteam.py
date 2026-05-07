"""Redteam stress + edge case tests for study-evolve.

Run: python -m unittest discover tests -v
"""

from __future__ import annotations

import csv
import sys
import threading
import unittest
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import storage  # noqa: E402
from src.models import StudyRecord  # noqa: E402
from src.utils import parse_date, parse_solve_time  # noqa: E402

from tests.conftest_helpers import TempDataCase  # noqa: E402


def _make_record(rid: int, **overrides) -> StudyRecord:
    base = dict(
        id=rid,
        date=date.today().isoformat(),
        subject="NCS",
        area="자료해석",
        source="테스트",
        problem_no=f"T-{rid}",
        is_correct=False,
        solve_time_sec=90,
        difficulty=3,
        fail_tag="조건 누락",
        memo="",
    )
    base.update(overrides)
    return StudyRecord(**base)


# ───────────────────────────── 1. CSV injection ─────────────────────────────

class TestCsvInjectionBlocked(TempDataCase):

    def test_dangerous_prefix_in_memo_is_quoted(self):
        cases = [
            "=SUM(A:A)",
            "+cmd|'/c calc'",
            "-2+3",
            "@SUM(1)",
            "\tinjection",
            "\rinjection",
        ]
        for memo in cases:
            with self.subTest(memo=memo):
                record = _make_record(1, memo=memo, problem_no="P1")
                storage.append_record(record)
                with storage.RECORDS_CSV.open(encoding="utf-8", newline="") as f:
                    rows = list(csv.DictReader(f))
                self.assertEqual(len(rows), 1)
                # Sanitizer must prefix with single quote
                self.assertTrue(
                    rows[0]["memo"].startswith("'"),
                    f"memo should be sanitized: got {rows[0]['memo']!r}",
                )
                # Original payload preserved after the quote
                self.assertEqual(rows[0]["memo"][1:], memo)
                # Reset for next sub-case
                storage.RECORDS_CSV.unlink()
                storage.SCHEDULE_CSV.unlink()

    def test_safe_text_unchanged(self):
        record = _make_record(1, memo="단위 변환 놓침", problem_no="2024-PSAT-12")
        storage.append_record(record)
        with storage.RECORDS_CSV.open(encoding="utf-8", newline="") as f:
            row = next(csv.DictReader(f))
        self.assertEqual(row["memo"], "단위 변환 놓침")
        self.assertEqual(row["problem_no"], "2024-PSAT-12")


# ─────────────────────────── 2. solve_time bounds ───────────────────────────

class TestSolveTimeBounds(unittest.TestCase):

    def test_valid_formats(self):
        cases = {
            "90": 90,
            "1:30": 90,
            "2m": 120,
            "1m30s": 90,
            "45s": 45,
            "  60  ": 60,
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(parse_solve_time(raw), expected)

    def test_zero_rejected(self):
        with self.assertRaises(ValueError):
            parse_solve_time("0")

    def test_huge_rejected(self):
        with self.assertRaises(ValueError):
            parse_solve_time("3601")
        with self.assertRaises(ValueError):
            parse_solve_time("999999")

    def test_negative_or_garbage_rejected(self):
        for raw in ["-90", "1.5:30", "::", "1m70s", "abc", "", "  "]:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    parse_solve_time(raw)


# ──────────────────────────── 3. parse_date guard ───────────────────────────

class TestParseDateBounds(unittest.TestCase):

    def test_today_and_tomorrow_allowed(self):
        today = date.today()
        self.assertEqual(parse_date(today.isoformat()), today.isoformat())
        tomorrow = (today + timedelta(days=1)).isoformat()
        self.assertEqual(parse_date(tomorrow), tomorrow)

    def test_far_future_rejected(self):
        with self.assertRaises(ValueError):
            parse_date((date.today() + timedelta(days=2)).isoformat())
        with self.assertRaises(ValueError):
            parse_date("2099-12-31")

    def test_invalid_format_rejected(self):
        for raw in ["2024/01/01", "2024-13-01", "2024-1-1", "yesterday"]:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    parse_date(raw, default_today=False)

    def test_empty_returns_today(self):
        self.assertEqual(parse_date(""), date.today().isoformat())


# ────────────────────────── 4. next_id concurrency ──────────────────────────

class TestNextIdLock(TempDataCase):

    def test_concurrent_writes_no_duplicate_id(self):
        storage.ensure_data_files()
        N = 50

        def worker(idx: int):
            def builder(new_id: int) -> StudyRecord:
                return _make_record(new_id, problem_no=f"T-{idx}")
            storage.append_record_with_id(builder)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(N)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        df = pd.read_csv(storage.RECORDS_CSV)
        self.assertEqual(len(df), N)
        self.assertEqual(df["id"].nunique(), N)
        self.assertEqual(sorted(df["id"].tolist()), list(range(1, N + 1)))


# ──────────────────────── 5. mark_review_done atomic ────────────────────────

class TestMarkReviewDoneAtomic(TempDataCase):

    def test_atomic_write_preserves_other_rows(self):
        storage.ensure_data_files()
        rec1 = _make_record(1, problem_no="P1")
        rec2 = _make_record(2, problem_no="P2")
        storage.append_record(rec1)
        storage.append_record(rec2)
        storage.append_schedules(rec1)
        storage.append_schedules(rec2)

        before = pd.read_csv(storage.SCHEDULE_CSV)
        self.assertGreaterEqual(len(before), 6)  # 3 reviews × 2 records

        ok = storage.mark_review_done(1, "1d")
        self.assertTrue(ok)

        after = pd.read_csv(storage.SCHEDULE_CSV)
        self.assertEqual(len(after), len(before))
        # The targeted row is True
        target = after[(after["record_id"] == 1) & (after["review_type"] == "1d")]
        self.assertEqual(len(target), 1)
        self.assertTrue(str(target.iloc[0]["is_done"]).lower() in ("true", "1"))

    def test_idempotent_already_done(self):
        storage.ensure_data_files()
        rec = _make_record(1)
        storage.append_record(rec)
        storage.append_schedules(rec)

        first = storage.mark_review_done(1, "1d")
        second = storage.mark_review_done(1, "1d")
        self.assertTrue(first)
        self.assertFalse(second)  # second call: no-op (already done)

    def test_no_temp_file_left_behind(self):
        storage.ensure_data_files()
        rec = _make_record(1)
        storage.append_record(rec)
        storage.append_schedules(rec)
        storage.mark_review_done(1, "3d")

        leftovers = list(storage.SCHEDULE_CSV.parent.glob("*.tmp"))
        self.assertEqual(leftovers, [])


# ─────────────────────────── 6. sample idempotency ──────────────────────────

class TestSampleIdempotent(TempDataCase):

    def test_first_run_creates_seeds(self):
        n = storage.generate_sample_data()
        self.assertGreaterEqual(n, 15)

    def test_second_run_skipped_without_force(self):
        storage.generate_sample_data()
        n2 = storage.generate_sample_data()
        self.assertEqual(n2, 0)

    def test_force_appends_again(self):
        first = storage.generate_sample_data()
        forced = storage.generate_sample_data(force=True)
        self.assertEqual(forced, first)
        df = pd.read_csv(storage.RECORDS_CSV)
        self.assertEqual(len(df), first + forced)
        # IDs are unique after two runs
        self.assertEqual(df["id"].nunique(), len(df))


# ────────────────── 7. recommender / analyzer edge cases ────────────────────

class TestRecommenderEdgeCases(TempDataCase):

    def _seed_records(self, records: list[StudyRecord]):
        for r in records:
            storage.append_record(r)
            storage.append_schedules(r)

    def test_all_correct_no_crash(self):
        from src import recommender
        recs = [_make_record(i, is_correct=True, fail_tag="") for i in range(1, 4)]
        self._seed_records(recs)
        df = storage.load_records()
        sched = storage.load_schedule()
        out = recommender.generate_recommendations(df, sched)
        self.assertTrue(out["weak_areas"].empty)
        self.assertTrue(out["fail_tag_stats"].empty)

    def test_single_record(self):
        from src import recommender
        rec = _make_record(1, is_correct=False, fail_tag="조건 누락")
        self._seed_records([rec])
        df = storage.load_records()
        sched = storage.load_schedule()
        out = recommender.generate_recommendations(df, sched)
        # action should match the only fail tag
        self.assertEqual(
            out["action"],
            "문제를 읽은 뒤 조건 2개를 먼저 적고 계산을 시작한다.",
        )

    def test_old_only_records_no_nan(self):
        from src import recommender
        old_date = (date.today() - timedelta(days=120)).isoformat()
        rec = _make_record(1, date=old_date)
        self._seed_records([rec])
        df = storage.load_records()
        sched = storage.load_schedule()
        out = recommender.generate_recommendations(df, sched)
        # Recent (30d) is empty; should not crash
        self.assertTrue(out["weak_areas"].empty)


# ───────────────────────── 8. done-review dedupe ────────────────────────────

class TestDoneReviewDedupe(TempDataCase):

    def test_dedupe_logic(self):
        # Pure logic check (no interactive flow)
        selected_idx = [0, 0, 1, 1, 0]
        deduped = list(dict.fromkeys(selected_idx))
        self.assertEqual(deduped, [0, 1])


# ─────────────────────────────── 9. full cycle ──────────────────────────────

class TestFullCycle(TempDataCase):

    def test_init_sample_stats_review_due_done(self):
        from src import analyzer, recommender, review

        # init
        existed_records, existed_schedule = storage.ensure_data_files()
        self.assertFalse(existed_records)
        self.assertFalse(existed_schedule)

        # sample (first run)
        n = storage.generate_sample_data()
        self.assertGreater(n, 0)

        # stats / analyzer pipeline
        df = storage.load_records()
        self.assertEqual(len(df), n)
        overall = analyzer.calculate_overall_stats(df)
        self.assertEqual(overall["total"], n)
        risks = analyzer.detect_risk_signals(df)
        self.assertTrue(any(t == "조건 누락" for t, _ in risks["by_tag"]))

        # recommend
        sched = storage.load_schedule()
        rec = recommender.generate_recommendations(df, sched)
        self.assertIn("action", rec)

        # review (today record exists at offset=0)
        rep = review.generate_daily_report(df, sched, today=date.today().isoformat())
        self.assertFalse(rep["empty"])

        # due
        today_ts = pd.Timestamp(date.today())
        due = sched[(sched["review_date_dt"] <= today_ts) & (~sched["is_done"])]
        self.assertGreater(len(due), 0)

        # mark a few done — idempotent on re-run
        first_due = due.iloc[0]
        ok = storage.mark_review_done(int(first_due["record_id"]), first_due["review_type"])
        self.assertTrue(ok)
        ok2 = storage.mark_review_done(int(first_due["record_id"]), first_due["review_type"])
        self.assertFalse(ok2)


if __name__ == "__main__":
    unittest.main()
