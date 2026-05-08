"""Vault sync — unify study-evolve + personal_intelligence_lab in one Obsidian vault.

Two operations:
  1. study-evolve obsidian.export() — CSV → vault/StudyEvolve/ markdown tree
  2. lab mirror — copy personal_intelligence_lab/ → vault/PersonalIntelligenceLab/
     (or symlink, --symlink mode, POSIX only)

Auto-trigger: when STUDY_EVOLVE_AUTO_SYNC=1 and OBSIDIAN_VAULT is set,
add / done-review / sample call sync_vault() silently after their main
work. Failures degrade to a warning (main command's exit code unaffected).
"""

from __future__ import annotations

import filecmp
import os
import shutil
import sys
from pathlib import Path

import pandas as pd

from . import obsidian, storage

LAB_SUBDIR = "PersonalIntelligenceLab"
AUTO_SYNC_ENV = "STUDY_EVOLVE_AUTO_SYNC"
LAB_PATH_ENV = "LAB_PATH"


def find_lab_path(explicit: str | None = None) -> Path | None:
    """Resolve personal_intelligence_lab/ location.

    Priority: explicit arg > LAB_PATH env > sibling of study-evolve repo.
    Returns None if not found.
    """
    candidates = []
    if explicit:
        candidates.append(Path(explicit).expanduser().resolve())
    if env := os.environ.get(LAB_PATH_ENV):
        candidates.append(Path(env).expanduser().resolve())
    # study-evolve/src/sync.py → study-evolve/src → study-evolve → repo root → personal_intelligence_lab
    candidates.append(Path(__file__).resolve().parent.parent.parent / "personal_intelligence_lab")

    for p in candidates:
        if p.exists() and p.is_dir():
            return p
    return None


def _mirror_directory(src: Path, dest: Path) -> int:
    """Mirror src tree to dest. Returns count of files written.

    Idempotent: files with identical contents are skipped (mtime unchanged).
    Files in dest not present in src are removed (true mirror).
    """
    dest.mkdir(parents=True, exist_ok=True)
    written = 0

    src_files = {p.relative_to(src) for p in src.rglob("*") if p.is_file()}
    dest_files = {p.relative_to(dest) for p in dest.rglob("*") if p.is_file()}

    # Write/update
    for rel in src_files:
        s = src / rel
        d = dest / rel
        d.parent.mkdir(parents=True, exist_ok=True)
        if d.exists() and filecmp.cmp(s, d, shallow=False):
            continue  # identical, skip
        shutil.copy2(s, d)
        written += 1

    # Remove stale (in dest but not in src)
    for rel in dest_files - src_files:
        try:
            (dest / rel).unlink()
        except OSError:
            pass

    # Prune empty dirs
    for d in sorted((dest.rglob("*")), key=lambda p: -len(p.parts)):
        if d.is_dir() and not any(d.iterdir()):
            try:
                d.rmdir()
            except OSError:
                pass

    return written


def _symlink_directory(src: Path, dest: Path) -> bool:
    """Replace dest with symlink to src. POSIX only. Returns True on success."""
    if dest.exists() or dest.is_symlink():
        if dest.is_symlink():
            target = dest.resolve()
            if target == src.resolve():
                return True  # already correct
            dest.unlink()
        else:
            shutil.rmtree(dest)
    try:
        dest.symlink_to(src, target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        return False


def sync_vault(
    vault: Path,
    include_lab: bool = True,
    lab_path: str | None = None,
    symlink: bool = False,
    include_correct: bool = False,
) -> dict:
    """Sync both study-evolve and lab into one Obsidian vault.

    Returns summary dict for caller to print.
    """
    summary: dict = {"vault": str(vault), "study_evolve": None, "lab": None}

    # 1. study-evolve export
    records_df = storage.load_records()
    schedule_df = storage.load_schedule()
    se_summary = obsidian.export(records_df, schedule_df, vault, include_correct=include_correct)
    summary["study_evolve"] = se_summary

    # 2. lab mirror / symlink
    if include_lab:
        lab = find_lab_path(lab_path)
        if lab is None:
            summary["lab"] = {"status": "skipped", "reason": "lab path not found"}
        else:
            dest = vault / LAB_SUBDIR
            if symlink:
                ok = _symlink_directory(lab, dest)
                summary["lab"] = {
                    "status": "symlinked" if ok else "mirrored-fallback",
                    "src": str(lab),
                    "dest": str(dest),
                }
                if not ok:
                    written = _mirror_directory(lab, dest)
                    summary["lab"]["files"] = written
            else:
                written = _mirror_directory(lab, dest)
                summary["lab"] = {
                    "status": "mirrored",
                    "src": str(lab),
                    "dest": str(dest),
                    "files": written,
                }

    return summary


def auto_sync_if_enabled() -> None:
    """Hook called after add/done-review/sample. Silent unless errors."""
    if os.environ.get(AUTO_SYNC_ENV) != "1":
        return
    vault_raw = os.environ.get("OBSIDIAN_VAULT")
    if not vault_raw:
        return
    try:
        vault = obsidian.resolve_vault(None)  # uses env
        sync_vault(vault, include_lab=True)
    except Exception as e:  # pragma: no cover — defensive
        # Auto-sync failure must NOT break main command
        print(f"[auto-sync 경고] {e}", file=sys.stderr)
