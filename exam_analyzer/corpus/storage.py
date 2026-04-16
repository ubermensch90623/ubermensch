"""corpus 저장소 — ~/.exam_corpus.json (원자적 쓰기, UTF-8).

중요: 사용자가 구매한 이북 원문이 포함될 수 있으므로 **저장소 커밋 금지**.
.gitignore 에 ~/.exam_corpus.json 패턴 포함 (로컬 PC 재개 시에도 안전).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from .models import (
    CorpusSnapshot,
    Question,
    snapshot_from_dict,
    snapshot_to_dict,
)


DEFAULT_CORPUS_FILENAME = ".exam_corpus.json"


def default_corpus_path() -> Path:
    """기본 corpus 파일 경로. `EXAM_CORPUS_FILE` 환경변수로 override."""
    env = os.environ.get("EXAM_CORPUS_FILE")
    if env:
        return Path(env).expanduser()
    return Path.home() / DEFAULT_CORPUS_FILENAME


def load_corpus(path: Optional[Path] = None) -> CorpusSnapshot:
    p = Path(path).expanduser() if path else default_corpus_path()
    if not p.exists():
        return CorpusSnapshot()
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return snapshot_from_dict(data)


def save_corpus(snapshot: CorpusSnapshot, path: Optional[Path] = None) -> None:
    p = Path(path).expanduser() if path else default_corpus_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = snapshot_to_dict(snapshot)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, p)


def add_question(snapshot: CorpusSnapshot, q: Question) -> bool:
    """문항 추가. 동일 ID 이미 있으면 False (덮어쓰기 원하면 remove 후 add)."""
    if any(existing.id == q.id for existing in snapshot.questions):
        return False
    snapshot.questions.append(q)
    return True


def find_question(snapshot: CorpusSnapshot, qid_or_prefix: str) -> Optional[Question]:
    exact = [q for q in snapshot.questions if q.id == qid_or_prefix]
    if exact:
        return exact[0]
    prefix = [q for q in snapshot.questions if q.id.startswith(qid_or_prefix)]
    if len(prefix) == 1:
        return prefix[0]
    return None


def remove_question(snapshot: CorpusSnapshot, qid: str) -> bool:
    before = len(snapshot.questions)
    snapshot.questions = [q for q in snapshot.questions if q.id != qid]
    return len(snapshot.questions) != before
