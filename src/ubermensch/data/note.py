"""Note 데이터 모델 — Keep 노트를 구조화된 형태로 표현."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any


class NoteCategory(str, Enum):
    """노트 대분류."""
    NCS = "NCS"
    ECONOMICS = "경제학"
    MIXED = "혼합"
    OTHER = "기타"


class NoteType(str, Enum):
    """노트 유형."""
    PROBLEM = "문제"
    SOLUTION = "풀이"
    WRONG_ANSWER = "오답분석"
    CONCEPT = "개념정리"
    MEMO = "메모"
    SCHEDULE = "일정"
    UNKNOWN = "미분류"


@dataclass
class Note:
    """구조화된 노트.

    Keep에서 파싱한 원본 데이터를 분류/태깅한 결과입니다.
    """

    # 기본 정보
    id: str = ""
    title: str = ""
    content: str = ""
    raw_content: str = ""  # 원본 텍스트 보존

    # 분류
    category: NoteCategory = NoteCategory.OTHER
    note_type: NoteType = NoteType.UNKNOWN
    subject: str = ""  # 세부 과목 (수리, 언어, 미시경제 등)
    difficulty: str = ""  # 상/중/하

    # 태그
    tags: list[str] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)  # Keep 원본 라벨

    # 메타데이터
    created_at: str = ""
    updated_at: str = ""
    source: str = "google_keep"

    # 검수
    verified: bool = False
    verification_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["category"] = self.category.value
        d["note_type"] = self.note_type.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Note:
        data = dict(data)
        if "category" in data:
            data["category"] = NoteCategory(data["category"])
        if "note_type" in data:
            data["note_type"] = NoteType(data["note_type"])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, text: str) -> Note:
        return cls.from_dict(json.loads(text))


def save_notes(notes: list[Note], path: str | Path) -> Path:
    """노트 리스트를 JSON 파일로 저장."""
    p = Path(path)
    data = [n.to_dict() for n in notes]
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return p


def load_notes(path: str | Path) -> list[Note]:
    """JSON 파일에서 노트 리스트 로드."""
    p = Path(path)
    data = json.loads(p.read_text())
    return [Note.from_dict(d) for d in data]
