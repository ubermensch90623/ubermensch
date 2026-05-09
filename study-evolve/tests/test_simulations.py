"""10가지 자체 시뮬레이션 시나리오 — 발견된 버그는 즉시 보강.

S1  Empty e2e          — 0건 상태에서 모든 9개 명령
S2  Single record      — 1건만 있는 상태의 추천/리뷰
S3  Large dataset      — 300+ 레코드 stats/recommend/sync-vault 성능
S4  Extreme concurrency— 100-thread add (race 0)
S5  Corrupted CSV      — id 문자열·is_correct yes/no·깨진 date 복구
S6  Unicode stress     — 이모지·줄바꿈·따옴표·백슬래시 모든 필드
S7  Date boundaries    — 윤년·연말 review 산술
S8  Vault read-only    — 권한 실패 시 명확한 에러
S9  Non-ASCII vault    — 한글 디렉터리명
S10 Idempotency 10x    — 같은 입력 10회 sync-vault → SHA256 동일
"""

from __future__ import annotations

import csv
import hashlib
import os
import shutil
import stat
import sys
import tempfile
import threading
import time
import unittest
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import obsidian, recommender, review, storage, sync  # noqa: E402
from src.analyzer import (  # noqa: E402
    calculate_overall_stats,
    detect_risk_signals,
)
from src.constants import RECORDS_HEADER, SCHEDULE_HEADER  # noqa: E402
from src.models import StudyRecord  # noqa: E402

from tests.conftest_helpers import TempDataCase  # noqa: E402


def _hash_tree(root: Path) -> dict:
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def _make_record(rid: int, **kw) -> StudyRecord:
    base = dict(
        id=rid,
        date=date.today().isoformat(),
        subject="NCS",
        area="자료해석",
        source="시뮬",
        problem_no=f"S-{rid}",
        is_correct=False,
        solve_time_sec=90,
        difficulty=3,
        fail_tag="조건 누락",
        memo="",
    )
    base.update(kw)
    return StudyRecord(**base)


# ─────────────────────────── S1: Empty e2e ──────────────────────────────────

class S1_EmptyE2E(TempDataCase):

    def test_all_commands_safe_on_empty(self):
        # init
        existed_r, existed_s = storage.ensure_data_files()
        self.assertFalse(existed_r)
        self.assertFalse(existed_s)

        # load empty
        df = storage.load_records()
        self.assertTrue(df.empty)
        sched = storage.load_schedule()
        self.assertTrue(sched.empty)

        # analyzer
        stats = calculate_overall_stats(df)
        self.assertEqual(stats["total"], 0)
        risks = detect_risk_signals(df)
        self.assertEqual(risks["by_tag"], [])

        # recommender
        rec = recommender.generate_recommendations(df, sched)
        self.assertTrue(rec["weak_areas"].empty)
        self.assertTrue(rec["due_reviews"].empty)
        self.assertTrue(rec["success_area"].empty)

        # review
        rep = review.generate_daily_report(df, sched, today=date.today().isoformat())
        self.assertTrue(rep["empty"])

        # obsidian-export on empty vault
        with tempfile.TemporaryDirectory() as v:
            vault = Path(v)
            summary = obsidian.export(df, sched, vault)
            self.assertEqual(summary["records"], 0)
            self.assertTrue((vault / "StudyEvolve" / "index.md").exists())
            # No records dir should be created (or be empty)
            rec_dir = vault / "StudyEvolve" / "records"
            if rec_dir.exists():
                self.assertEqual(list(rec_dir.iterdir()), [])

        # sync-vault on empty (lab fallback should still mirror or skip cleanly)
        with tempfile.TemporaryDirectory() as v:
            vault = Path(v)
            summary = sync.sync_vault(vault, lab_path="/nonexistent/lab/path")
            self.assertEqual(summary["study_evolve"]["records"], 0)


# ─────────────────────── S2: Single record ───────────────────────────────────

class S2_SingleRecord(TempDataCase):

    def test_single_wrong_record(self):
        rec = _make_record(1, fail_tag="공식 혼동", subject="경제학", area="조세")
        storage.append_record(rec)
        storage.append_schedules(rec)

        df = storage.load_records()
        sched = storage.load_schedule()
        self.assertEqual(len(df), 1)
        self.assertEqual(len(sched), 3)  # 1d + 3d + 7d

        out = recommender.generate_recommendations(df, sched)
        # 1건이라 wrong>=2 조건 불만족 → weak 비어있음 (fail_tag 빈도도 1)
        self.assertEqual(out["action"],
                         "문제 풀이 전 관련 공식 1개를 빈 종이에 쓰고 시작한다.")

        with tempfile.TemporaryDirectory() as v:
            obsidian.export(df, sched, Path(v))
            self.assertEqual(len(list((Path(v) / "StudyEvolve" / "records").glob("*.md"))), 1)


# ─────────────────────── S3: Large dataset ───────────────────────────────────

class S3_LargeDataset(TempDataCase):

    def test_300_records_perf(self):
        # Seed 300 records spanning 60 days
        SUBJECTS = ["NCS", "경제학"]
        AREAS = {"NCS": ["자료해석", "수리", "의사소통"],
                 "경제학": ["조세", "독점", "거시경제"]}
        TAGS = ["조건 누락", "공식 혼동", "계산 지연", "선지 판단 오류"]

        for i in range(1, 301):
            d = (date.today() - timedelta(days=i % 60)).isoformat()
            sub = SUBJECTS[i % 2]
            area = AREAS[sub][i % 3]
            is_correct = i % 4 == 0
            tag = "" if is_correct else TAGS[i % 4]
            rec = _make_record(i, date=d, subject=sub, area=area,
                               is_correct=is_correct, fail_tag=tag,
                               problem_no=f"L-{i}")
            storage.append_record(rec)
            if not is_correct:
                storage.append_schedules(rec)

        df = storage.load_records()
        self.assertEqual(len(df), 300)

        t0 = time.time()
        stats = calculate_overall_stats(df)
        t_stats = time.time() - t0
        self.assertEqual(stats["total"], 300)
        self.assertLess(t_stats, 2.0, f"stats took {t_stats:.2f}s on 300 rows")

        t0 = time.time()
        sched = storage.load_schedule()
        rec = recommender.generate_recommendations(df, sched)
        t_rec = time.time() - t0
        self.assertLess(t_rec, 2.0, f"recommend took {t_rec:.2f}s")
        self.assertFalse(rec["weak_areas"].empty)

        with tempfile.TemporaryDirectory() as v:
            t0 = time.time()
            summary = obsidian.export(df, sched, Path(v))
            t_exp = time.time() - t0
            self.assertLess(t_exp, 5.0, f"export took {t_exp:.2f}s")
            self.assertEqual(summary["records"], 225)  # 300 * 3/4 wrong


# ────────────────── S4: Extreme concurrency (100 threads) ────────────────────

class S4_ExtremeConcurrency(TempDataCase):

    def test_100_concurrent_adds(self):
        storage.ensure_data_files()
        N = 100

        def worker(idx: int):
            def builder(new_id: int) -> StudyRecord:
                return _make_record(new_id, problem_no=f"C-{idx}")
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


# ─────────────────────── S5: Corrupted CSV recovery ──────────────────────────

class S5_CorruptedCsv(TempDataCase):

    def test_id_string_recovers(self):
        # Hand-write CSV with a string in id column
        with storage.RECORDS_CSV.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(RECORDS_HEADER)
            w.writerow(["abc", "2026-01-01", "NCS", "자료해석", "테스트", "P1",
                        "False", "90", "3", "조건 누락", "", "2026-01-02",
                        "2026-01-04", "2026-01-08", "2026-01-01T10:00:00"])
            w.writerow(["2", "2026-01-02", "NCS", "수리", "테스트", "P2",
                        "True", "60", "2", "", "", "", "", "", "2026-01-02T10:00:00"])

        # Should not crash on load
        df = storage.load_records()
        self.assertEqual(len(df), 2)
        # Bad id becomes <NA>; well-formed row keeps id 2
        self.assertTrue(pd.isna(df.iloc[0]["id"]))
        self.assertEqual(int(df.iloc[1]["id"]), 2)

        # next_id_unlocked must skip NaN (returns max(2)+1=3, not crash)
        with storage._exclusive_lock(storage.RECORDS_CSV):
            n = storage._next_id_unlocked()
        self.assertEqual(n, 3)

    def test_yes_no_in_is_correct(self):
        with storage.RECORDS_CSV.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(RECORDS_HEADER)
            w.writerow(["1", "2026-01-01", "NCS", "자료해석", "테스트", "P1",
                        "yes", "60", "2", "", "", "", "", "", "2026-01-01T10:00:00"])
            w.writerow(["2", "2026-01-02", "NCS", "수리", "테스트", "P2",
                        "no", "90", "3", "조건 누락", "", "2026-01-03",
                        "2026-01-05", "2026-01-09", "2026-01-02T10:00:00"])

        df = storage.load_records()
        # 'yes' → True, 'no' → False (per _parse_bool)
        self.assertTrue(bool(df.iloc[0]["is_correct"]))
        self.assertFalse(bool(df.iloc[1]["is_correct"]))


# ─────────────────────── S6: Unicode / special chars ─────────────────────────

class S6_UnicodeStress(TempDataCase):

    def test_emoji_quotes_backslash_in_memo(self):
        weird = '🎯 "어려움" \\test 줄바꿈\\n경계'
        rec = _make_record(1, memo=weird, problem_no="유니코드🔥")
        storage.append_record(rec)

        df = storage.load_records()
        self.assertEqual(df.iloc[0]["memo"], weird)
        self.assertEqual(df.iloc[0]["problem_no"], "유니코드🔥")

        # Obsidian export must handle unicode in filenames safely
        with tempfile.TemporaryDirectory() as v:
            sched = storage.load_schedule()
            obsidian.export(df, sched, Path(v))
            files = list((Path(v) / "StudyEvolve" / "records").glob("*.md"))
            self.assertEqual(len(files), 1)
            content = files[0].read_text(encoding="utf-8")
            self.assertIn("유니코드", content)

    def test_newline_in_memo_does_not_break_csv(self):
        rec = _make_record(1, memo="첫 줄\n둘째 줄\n셋째 줄")
        storage.append_record(rec)

        # Reload and verify newline preserved
        df = storage.load_records()
        self.assertIn("\n", df.iloc[0]["memo"])
        self.assertEqual(df.iloc[0]["memo"].count("\n"), 2)


# ─────────────────────── S7: Date boundaries ─────────────────────────────────

class S7_DateBoundaries(TempDataCase):

    def test_leap_year_feb_29(self):
        rec = _make_record(1, date="2024-02-29")
        storage.append_record(rec)
        storage.append_schedules(rec)

        df = storage.load_records()
        # review_1d = 2024-03-01, review_3d = 2024-03-03, review_7d = 2024-03-07
        self.assertEqual(df.iloc[0]["review_1d"], "2024-03-01")
        self.assertEqual(df.iloc[0]["review_3d"], "2024-03-03")
        self.assertEqual(df.iloc[0]["review_7d"], "2024-03-07")

    def test_year_end_rollover(self):
        rec = _make_record(1, date="2024-12-30")
        storage.append_record(rec)

        df = storage.load_records()
        self.assertEqual(df.iloc[0]["review_1d"], "2024-12-31")
        self.assertEqual(df.iloc[0]["review_3d"], "2025-01-02")
        self.assertEqual(df.iloc[0]["review_7d"], "2025-01-06")


# ─────────────────────── S8: Vault permission failure ────────────────────────

class S8_VaultPermissionFail(TempDataCase):

    def setUp(self):
        super().setUp()
        storage.generate_sample_data()

    def test_readonly_vault_clear_error(self):
        if os.geteuid() == 0:
            # root bypasses chmod; skip
            self.skipTest("running as root — chmod read-only is bypassed")
        with tempfile.TemporaryDirectory() as v:
            vault = Path(v)
            os.chmod(vault, stat.S_IRUSR | stat.S_IXUSR)  # read+execute, no write
            try:
                with self.assertRaises((PermissionError, OSError)):
                    sync.sync_vault(vault, lab_path="/nonexistent")
            finally:
                os.chmod(vault, 0o755)


# ─────────────────────── S9: Non-ASCII vault path ────────────────────────────

class S9_NonAsciiVault(TempDataCase):

    def test_korean_directory_works(self):
        storage.generate_sample_data()
        parent = Path(tempfile.mkdtemp(prefix="korean-"))
        try:
            vault = parent / "내문서" / "공부vault"
            vault.mkdir(parents=True)

            # resolve_vault must accept the path
            resolved = obsidian.resolve_vault(str(vault))
            self.assertEqual(resolved, vault.resolve())

            # sync-vault must complete
            summary = sync.sync_vault(vault, lab_path="/nonexistent")
            self.assertEqual(summary["study_evolve"]["records"], 12)

            # Korean filenames inside Korean parent: e.g. 경제학__조세.md exists
            self.assertTrue((vault / "StudyEvolve" / "by-area" / "경제학__조세.md").exists())
        finally:
            shutil.rmtree(parent, ignore_errors=True)


# ─────────────────────── S10: Idempotency 10x ────────────────────────────────

class S10_Idempotency10x(TempDataCase):

    def test_ten_consecutive_syncs_identical(self):
        storage.generate_sample_data()
        with tempfile.TemporaryDirectory() as v:
            vault = Path(v)
            sync.sync_vault(vault, lab_path="/nonexistent")
            baseline = _hash_tree(vault)
            self.assertGreater(len(baseline), 0)

            for i in range(9):
                sync.sync_vault(vault, lab_path="/nonexistent")
                current = _hash_tree(vault)
                self.assertEqual(
                    baseline, current,
                    f"sync iteration {i+2} differs from baseline",
                )


# ──────────────── S11: User notes inside StudyEvolve/ preserved ──────────────

class S11_UserNotesInExportSubdir(TempDataCase):
    """If user manually adds a note inside vault/StudyEvolve/, current code
    rmtree's the whole subdir → user data lost. We must preserve user files."""

    def test_user_extra_note_in_export_subdir_preserved(self):
        storage.generate_sample_data()
        with tempfile.TemporaryDirectory() as v:
            vault = Path(v)
            sync.sync_vault(vault, lab_path="/nonexistent")

            # User adds their own note inside StudyEvolve/
            user_in_se = vault / "StudyEvolve" / "my_personal_review.md"
            user_in_se.write_text("# 사용자가 직접 작성\n\n중요한 회고", encoding="utf-8")

            # User adds a note in records/ subdir
            user_in_records = vault / "StudyEvolve" / "records" / "my_extra_note.md"
            user_in_records.write_text("# 추가 노트\n", encoding="utf-8")

            # Re-sync
            sync.sync_vault(vault, lab_path="/nonexistent")

            self.assertTrue(user_in_se.exists(),
                            "사용자가 StudyEvolve/에 직접 만든 노트가 사라짐")
            self.assertTrue(user_in_records.exists(),
                            "사용자가 StudyEvolve/records/에 직접 만든 노트가 사라짐")
            self.assertIn("중요한 회고", user_in_se.read_text(encoding="utf-8"))


# ─────────────────── S12: Orphan schedule rows ───────────────────────────────

class S12_OrphanSchedule(TempDataCase):

    def test_schedule_with_missing_record_safe(self):
        storage.ensure_data_files()

        # Inject schedule row referencing non-existent record_id=999
        with storage.SCHEDULE_CSV.open("a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=SCHEDULE_HEADER)
            w.writerow({"record_id": 999, "review_date": "2026-01-01",
                        "review_type": "1d", "is_done": False, "done_at": ""})

        # mark_review_done on orphan returns True (it does mark) — that's ok
        ok = storage.mark_review_done(999, "1d")
        self.assertTrue(ok)

        # Re-marking is idempotent
        ok2 = storage.mark_review_done(999, "1d")
        self.assertFalse(ok2)


# ───────────────────────── S13: NaN difficulty ───────────────────────────────

class S13_NaNDifficulty(TempDataCase):

    def test_empty_difficulty_column_does_not_crash(self):
        with storage.RECORDS_CSV.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(RECORDS_HEADER)
            # difficulty column empty
            w.writerow(["1", "2026-01-01", "NCS", "자료해석", "외부", "P1",
                        "False", "90", "", "조건 누락", "", "2026-01-02",
                        "2026-01-04", "2026-01-08", "2026-01-01T10:00:00"])

        df = storage.load_records()
        self.assertEqual(len(df), 1)
        # difficulty is now Int64 NA — pd.isna check
        self.assertTrue(pd.isna(df.iloc[0]["difficulty"]))

        # obsidian.export must handle NaN difficulty (frontmatter: null)
        with tempfile.TemporaryDirectory() as v:
            sched = storage.load_schedule()
            obsidian.export(df, sched, Path(v))
            note = next((Path(v) / "StudyEvolve" / "records").glob("*.md"))
            content = note.read_text(encoding="utf-8")
            self.assertIn("difficulty: null", content)
            # Body should NOT show '난이도: ' line when null
            self.assertNotIn("난이도: 0", content)


# ─────────────────── S14: Huge memo (10K chars) ─────────────────────────────

class S14_HugeMemo(TempDataCase):

    def test_10k_char_memo_round_trip(self):
        big = "긴" * 10_000
        rec = _make_record(1, memo=big)
        storage.append_record(rec)

        df = storage.load_records()
        self.assertEqual(df.iloc[0]["memo"], big)
        self.assertEqual(len(df.iloc[0]["memo"]), 10_000)

        # Obsidian export must not truncate
        with tempfile.TemporaryDirectory() as v:
            sched = storage.load_schedule()
            obsidian.export(df, sched, Path(v))
            note = next((Path(v) / "StudyEvolve" / "records").glob("*.md"))
            content = note.read_text(encoding="utf-8")
            self.assertIn("긴" * 1000, content)  # at least first 1k preserved


# ─────────────────── S15: Concurrent sync-vault (2 threads) ──────────────────

class S15_ConcurrentSync(TempDataCase):

    def test_two_simultaneous_syncs_no_corruption(self):
        storage.generate_sample_data()
        with tempfile.TemporaryDirectory() as v:
            vault = Path(v)
            results = []

            def runner():
                try:
                    sync.sync_vault(vault, lab_path="/nonexistent")
                    results.append("ok")
                except Exception as e:
                    results.append(str(e))

            threads = [threading.Thread(target=runner) for _ in range(2)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            # At least one must succeed; no Python-level uncaught exception
            self.assertTrue(any(r == "ok" for r in results),
                            f"both syncs failed: {results}")
            # Final vault must have the index
            self.assertTrue((vault / "StudyEvolve" / "index.md").exists())


if __name__ == "__main__":
    unittest.main()
