"""Tests for Obsidian vault exporter."""

from __future__ import annotations

import hashlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import obsidian, storage  # noqa: E402

from tests.conftest_helpers import TempDataCase  # noqa: E402


def _file_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _all_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file())


class TestResolveVault(unittest.TestCase):

    def test_cli_arg_wins(self):
        with tempfile.TemporaryDirectory() as d:
            p = obsidian.resolve_vault(d)
            self.assertEqual(p, Path(d).resolve())

    def test_env_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            old = os.environ.get("OBSIDIAN_VAULT")
            os.environ["OBSIDIAN_VAULT"] = d
            try:
                p = obsidian.resolve_vault(None)
                self.assertEqual(p, Path(d).resolve())
            finally:
                if old is None:
                    os.environ.pop("OBSIDIAN_VAULT", None)
                else:
                    os.environ["OBSIDIAN_VAULT"] = old

    def test_neither_raises(self):
        old = os.environ.pop("OBSIDIAN_VAULT", None)
        try:
            with self.assertRaises(ValueError):
                obsidian.resolve_vault(None)
        finally:
            if old is not None:
                os.environ["OBSIDIAN_VAULT"] = old

    def test_nonexistent_raises(self):
        with self.assertRaises(ValueError):
            obsidian.resolve_vault("/nonexistent/path/should/not/exist")

    def test_file_not_dir_raises(self):
        with tempfile.NamedTemporaryFile() as tf:
            with self.assertRaises(ValueError):
                obsidian.resolve_vault(tf.name)


class TestSanitizeFilename(unittest.TestCase):

    def test_korean_preserved(self):
        self.assertEqual(obsidian.sanitize_filename("경제학"), "경제학")
        self.assertEqual(obsidian.sanitize_filename("자료해석"), "자료해석")

    def test_space_to_underscore(self):
        self.assertEqual(obsidian.sanitize_filename("독점적 경쟁"), "독점적_경쟁")

    def test_invalid_chars_replaced(self):
        self.assertEqual(obsidian.sanitize_filename("a/b\\c:d"), "a_b_c_d")

    def test_empty_returns_underscore(self):
        self.assertEqual(obsidian.sanitize_filename(""), "_")
        self.assertEqual(obsidian.sanitize_filename("   "), "_")

    def test_overlong_truncates(self):
        long = "가" * 200
        out = obsidian.sanitize_filename(long, max_len=80)
        self.assertEqual(len(out), 80)


class TestExport(TempDataCase):

    def setUp(self):
        super().setUp()
        storage.generate_sample_data()
        self.vault = Path(tempfile.mkdtemp(prefix="study-vault-"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.vault, ignore_errors=True)
        super().tearDown()

    def test_export_creates_tree(self):
        records = storage.load_records()
        schedule = storage.load_schedule()
        summary = obsidian.export(records, schedule, self.vault)

        root = self.vault / "StudyEvolve"
        self.assertTrue((root / "index.md").exists())
        self.assertTrue((root / "records").is_dir())
        self.assertTrue((root / "by-area").is_dir())
        self.assertTrue((root / "by-failtag").is_dir())
        self.assertTrue((root / "daily").is_dir())

        # Records are wrong-only by default
        wrong = int((~records["is_correct"]).sum())
        self.assertEqual(summary["records"], wrong)
        self.assertEqual(len(list((root / "records").glob("*.md"))), wrong)

    def test_idempotent(self):
        records = storage.load_records()
        schedule = storage.load_schedule()

        obsidian.export(records, schedule, self.vault)
        first = {p.relative_to(self.vault): _file_hash(p)
                 for p in _all_files(self.vault)}

        obsidian.export(records, schedule, self.vault)
        second = {p.relative_to(self.vault): _file_hash(p)
                  for p in _all_files(self.vault)}

        self.assertEqual(first, second, "두 번째 export 결과가 첫 번째와 다름")

    def test_user_notes_outside_subdir_preserved(self):
        # User has their own note in the vault root
        user_note = self.vault / "MyDailyJournal.md"
        user_note.write_text("# 내 노트\n\n사용자가 직접 만든 파일\n", encoding="utf-8")

        sub_note = self.vault / "OtherFolder" / "note.md"
        sub_note.parent.mkdir(parents=True)
        sub_note.write_text("# 다른 폴더\n", encoding="utf-8")

        records = storage.load_records()
        schedule = storage.load_schedule()
        obsidian.export(records, schedule, self.vault)

        self.assertTrue(user_note.exists())
        self.assertTrue(sub_note.exists())
        self.assertIn("내 노트", user_note.read_text(encoding="utf-8"))

    def test_record_note_has_frontmatter_and_wikilinks(self):
        records = storage.load_records()
        schedule = storage.load_schedule()
        obsidian.export(records, schedule, self.vault)

        rec_dir = self.vault / "StudyEvolve" / "records"
        files = sorted(rec_dir.glob("*.md"))
        self.assertGreater(len(files), 0)

        sample = files[0].read_text(encoding="utf-8")
        # frontmatter
        self.assertTrue(sample.startswith("---\n"))
        self.assertIn("id:", sample)
        self.assertIn("subject:", sample)
        self.assertIn("fail_tag:", sample)
        # tags must be YAML list, not python repr string
        self.assertIn("tags: [", sample)
        self.assertNotIn("tags: \"['", sample)
        # wiki-links to area + failtag + daily
        self.assertIn("[[", sample)
        self.assertIn("]]", sample)

    def test_korean_area_filename_safe(self):
        records = storage.load_records()
        schedule = storage.load_schedule()
        obsidian.export(records, schedule, self.vault)

        area_dir = self.vault / "StudyEvolve" / "by-area"
        names = [p.name for p in area_dir.glob("*.md")]
        # 독점적 경쟁 → 경제학__독점적_경쟁.md (공백 → _)
        self.assertIn("경제학__독점적_경쟁.md", names)
        self.assertIn("경제학__조세.md", names)

    def test_include_correct_flag(self):
        records = storage.load_records()
        schedule = storage.load_schedule()

        obsidian.export(records, schedule, self.vault, include_correct=True)
        rec_dir = self.vault / "StudyEvolve" / "records"
        self.assertEqual(len(list(rec_dir.glob("*.md"))), len(records))

    def test_empty_records(self):
        # Wipe data first
        storage.RECORDS_CSV.write_text("id,date,subject,area,source,problem_no,is_correct,solve_time_sec,difficulty,fail_tag,memo,review_1d,review_3d,review_7d,created_at\n", encoding="utf-8")
        storage.SCHEDULE_CSV.write_text("record_id,review_date,review_type,is_done,done_at\n", encoding="utf-8")

        records = storage.load_records()
        schedule = storage.load_schedule()

        # Should not crash
        summary = obsidian.export(records, schedule, self.vault)
        self.assertEqual(summary["records"], 0)
        self.assertTrue((self.vault / "StudyEvolve" / "index.md").exists())

    def test_stale_records_cleaned_after_dataset_shrinks(self):
        # First export with full sample
        records = storage.load_records()
        schedule = storage.load_schedule()
        obsidian.export(records, schedule, self.vault)

        rec_dir = self.vault / "StudyEvolve" / "records"
        first_count = len(list(rec_dir.glob("*.md")))
        self.assertGreater(first_count, 0)

        # Capture one record path that should be cleaned after shrinking
        soon_stale = sorted(rec_dir.glob("*.md"))[0]
        self.assertTrue(soon_stale.exists())

        # Shrink dataset to a single record (simulate user deleting rows)
        records_small = records.iloc[-1:].copy()
        obsidian.export(records_small, schedule, self.vault)

        # Stale records (from prior export but not in new dataset) must be cleaned
        second_count = len(list(rec_dir.glob("*.md")))
        self.assertEqual(second_count, 1)
        self.assertFalse(soon_stale.exists(),
                         "이전 export에서 만든 stale record 노트가 정리 안 됨")

    def test_user_authored_file_in_export_subdir_preserved(self):
        records = storage.load_records()
        schedule = storage.load_schedule()
        obsidian.export(records, schedule, self.vault)

        # User adds their own note inside StudyEvolve/ — sync must NOT delete it
        user_note = self.vault / "StudyEvolve" / "my_review.md"
        user_note.write_text("# 사용자 회고\n", encoding="utf-8")

        user_in_records = self.vault / "StudyEvolve" / "records" / "_my_extra.md"
        user_in_records.write_text("# 사용자가 records에 추가\n", encoding="utf-8")

        obsidian.export(records, schedule, self.vault)
        self.assertTrue(user_note.exists())
        self.assertTrue(user_in_records.exists())


if __name__ == "__main__":
    unittest.main()
