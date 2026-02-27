"""Google Keep Takeout 파서 — JSON/HTML 노트를 Note 객체로 변환.

Google Takeout에서 Keep 데이터를 내보내면
Takeout/Keep/ 폴더에 각 노트가 JSON 또는 HTML 파일로 저장됩니다.

JSON 형식 예시:
{
    "color": "DEFAULT",
    "isTrashed": false,
    "isPinned": false,
    "isArchived": false,
    "textContent": "NCS 수리 문제...",
    "title": "수리 오답정리",
    "userEditedTimestampUsec": 1700000000000000,
    "createdTimestampUsec": 1690000000000000,
    "labels": [{"name": "NCS"}]
}
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from ubermensch.data.note import Note

logger = logging.getLogger(__name__)

# Google Keep 타임스탬프는 마이크로초 단위
_USEC_TO_SEC = 1_000_000


class KeepParser:
    """Google Keep Takeout 데이터를 파싱합니다.

    사용법:
        parser = KeepParser()
        notes = parser.parse_directory("/path/to/Takeout/Keep")
        notes = parser.parse_json(json_data)
        note = parser.parse_file("/path/to/note.json")
    """

    def __init__(self, skip_trashed: bool = True, skip_empty: bool = True) -> None:
        self.skip_trashed = skip_trashed
        self.skip_empty = skip_empty
        self._stats = {"total": 0, "parsed": 0, "skipped": 0, "errors": 0}

    @property
    def stats(self) -> dict[str, int]:
        return dict(self._stats)

    def parse_directory(self, path: str | Path) -> list[Note]:
        """Keep Takeout 디렉토리의 모든 JSON 파일을 파싱합니다."""
        directory = Path(path)
        if not directory.is_dir():
            raise NotADirectoryError(f"디렉토리를 찾을 수 없습니다: {directory}")

        notes: list[Note] = []
        json_files = sorted(directory.glob("*.json"))

        for file_path in json_files:
            self._stats["total"] += 1
            try:
                note = self.parse_file(file_path)
                if note is not None:
                    notes.append(note)
                    self._stats["parsed"] += 1
                else:
                    self._stats["skipped"] += 1
            except Exception as e:
                self._stats["errors"] += 1
                logger.warning(f"파싱 실패: {file_path.name} — {e}")

        logger.info(
            f"Keep 파싱 완료: {self._stats['parsed']}/{self._stats['total']}개 "
            f"(스킵 {self._stats['skipped']}, 에러 {self._stats['errors']})"
        )
        return notes

    def parse_file(self, path: str | Path) -> Note | None:
        """단일 JSON 파일을 파싱합니다."""
        file_path = Path(path)
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return self.parse_json(data, source_file=file_path.name)

    def parse_json(self, data: dict[str, Any], source_file: str = "") -> Note | None:
        """JSON 딕셔너리를 Note 객체로 변환합니다."""
        # 휴지통 노트 스킵
        if self.skip_trashed and data.get("isTrashed", False):
            return None

        # 텍스트 추출
        content = data.get("textContent", "").strip()
        title = data.get("title", "").strip()

        # 리스트 형태 노트 처리
        if not content and "listContent" in data:
            items = data["listContent"]
            content = "\n".join(
                item.get("text", "") for item in items if item.get("text")
            )

        # 빈 노트 스킵
        if self.skip_empty and not content and not title:
            return None

        # ID 생성
        note_id = _generate_id(title, content, source_file)

        # 타임스탬프 변환
        created = _usec_to_iso(data.get("createdTimestampUsec", 0))
        updated = _usec_to_iso(data.get("userEditedTimestampUsec", 0))

        # 라벨 추출
        labels = [
            label.get("name", "")
            for label in data.get("labels", [])
            if label.get("name")
        ]

        return Note(
            id=note_id,
            title=title,
            content=content,
            raw_content=content,
            labels=labels,
            created_at=created,
            updated_at=updated,
            source=f"google_keep:{source_file}" if source_file else "google_keep",
        )

    def parse_text_dump(self, text: str) -> list[Note]:
        """텍스트 덤프 (복사/붙여넣기)를 노트 리스트로 변환합니다.

        Keep에서 직접 복사한 텍스트나, 줄바꿈으로 구분된 노트를 처리합니다.
        빈 줄 2개 이상을 노트 구분자로 사용합니다.
        """
        # 빈 줄 2개 이상으로 분리
        chunks = re.split(r"\n{3,}", text.strip())
        if len(chunks) <= 1:
            # 구분자가 없으면 전체를 하나의 노트로
            chunks = [text.strip()]

        notes: list[Note] = []
        for i, chunk in enumerate(chunks):
            chunk = chunk.strip()
            if not chunk:
                continue

            lines = chunk.split("\n", 1)
            title = lines[0].strip() if len(lines) > 1 else ""
            content = lines[1].strip() if len(lines) > 1 else lines[0].strip()

            note_id = _generate_id(title, content, f"text_dump_{i}")
            notes.append(Note(
                id=note_id,
                title=title,
                content=content,
                raw_content=chunk,
                source="text_dump",
            ))

        return notes


def _generate_id(title: str, content: str, source: str) -> str:
    """노트의 고유 ID를 생성합니다."""
    raw = f"{title}:{content[:200]}:{source}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def _usec_to_iso(usec: int) -> str:
    """마이크로초 타임스탬프를 ISO 형식으로 변환합니다."""
    if not usec:
        return ""
    try:
        dt = datetime.fromtimestamp(usec / _USEC_TO_SEC)
        return dt.isoformat()
    except (ValueError, OSError):
        return ""
