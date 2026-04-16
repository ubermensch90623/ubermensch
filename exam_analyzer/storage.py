"""JSON 이력 저장소 (원자적 쓰기, UTF-8, 크로스플랫폼)."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from .models import (
    SCHEMA_VERSION,
    ExamRecord,
    generate_record_id,
    record_from_dict,
    record_to_dict,
)


DEFAULT_HISTORY_FILENAME = ".exam_history.json"


def default_history_path() -> Path:
    """기본 이력 파일 경로. 환경변수 EXAM_HISTORY_FILE이 있으면 우선 사용."""
    env = os.environ.get("EXAM_HISTORY_FILE")
    if env:
        return Path(env).expanduser()
    return Path.home() / DEFAULT_HISTORY_FILENAME


def load_history(path: Path) -> List[ExamRecord]:
    """JSON 이력 로드. 파일이 없으면 빈 리스트."""
    path = Path(path).expanduser()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    records_raw = data.get("records", []) if isinstance(data, dict) else []
    return [record_from_dict(r) for r in records_raw]


def save_history(path: Path, records: List[ExamRecord]) -> None:
    """원자적 쓰기: 임시 파일에 기록 후 os.replace 로 교체."""
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": SCHEMA_VERSION,
        "records": [record_to_dict(r) for r in records],
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def append_record(path: Path, record: ExamRecord) -> str:
    """기록 추가. record_id가 없으면 자동 생성 후 반환."""
    records = load_history(path)
    if not record.record_id:
        record.record_id = generate_record_id(record)
    records.append(record)
    save_history(path, records)
    return record.record_id


def find_record(path: Path, id_or_prefix: str) -> Optional[ExamRecord]:
    """record_id 전체 또는 접두사로 검색 (접두사가 유일할 때만 반환)."""
    records = load_history(path)
    exact = [r for r in records if r.record_id == id_or_prefix]
    if exact:
        return exact[0]
    prefix_matches = [r for r in records if r.record_id.startswith(id_or_prefix)]
    if len(prefix_matches) == 1:
        return prefix_matches[0]
    return None


def delete_record(path: Path, id_or_prefix: str) -> bool:
    """기록 삭제 성공 시 True."""
    records = load_history(path)
    target = find_record(path, id_or_prefix)
    if target is None:
        return False
    remaining = [r for r in records if r.record_id != target.record_id]
    if len(remaining) == len(records):
        return False
    save_history(path, remaining)
    return True
