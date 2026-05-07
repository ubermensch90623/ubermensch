"""Test helpers: redirect storage's CSV paths into a temp directory per test."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path


class TempDataCase(unittest.TestCase):
    """Re-points DATA_DIR/RECORDS_CSV/SCHEDULE_CSV to a per-test tempdir.

    Modules that read these constants at import time (e.g. main.py) must NOT
    cache them. Storage uses module-level constants — we patch the module
    attributes (not the import-bound copies in other modules).
    """

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="study-evolve-test-"))
        from src import constants, storage
        self._patches = []
        for mod in (constants, storage):
            self._patches.append((mod, "DATA_DIR", getattr(mod, "DATA_DIR", None)))
            self._patches.append((mod, "RECORDS_CSV", getattr(mod, "RECORDS_CSV", None)))
            self._patches.append((mod, "SCHEDULE_CSV", getattr(mod, "SCHEDULE_CSV", None)))
            mod.DATA_DIR = self.tmp
            mod.RECORDS_CSV = self.tmp / "records.csv"
            mod.SCHEDULE_CSV = self.tmp / "review_schedule.csv"

    def tearDown(self) -> None:
        for mod, attr, original in self._patches:
            if original is not None:
                setattr(mod, attr, original)
        shutil.rmtree(self.tmp, ignore_errors=True)
