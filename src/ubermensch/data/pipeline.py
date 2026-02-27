"""데이터 파이프라인 — Keep → 파싱 → 분류 → 검수 → 저장.

배관공(Plumber) 에이전트가 관리하는 전체 파이프라인을 구현합니다.
API 키 없이 동작합니다.
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ubermensch.data.note import Note, NoteCategory, NoteType, save_notes, load_notes
from ubermensch.data.keep_parser import KeepParser
from ubermensch.data.classifier import NoteClassifier

logger = logging.getLogger(__name__)


@dataclass
class PipelineStats:
    """파이프라인 처리 통계."""
    total_input: int = 0
    parsed: int = 0
    classified: int = 0
    verified: int = 0
    rejected: int = 0
    duplicates_removed: int = 0

    # 분류 결과
    by_category: dict[str, int] = field(default_factory=dict)
    by_type: dict[str, int] = field(default_factory=dict)
    by_subject: dict[str, int] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            "=== 파이프라인 처리 결과 ===",
            f"입력: {self.total_input}개",
            f"파싱: {self.parsed}개",
            f"분류: {self.classified}개",
            f"검수 통과: {self.verified}개",
            f"제외: {self.rejected}개",
            f"중복 제거: {self.duplicates_removed}개",
        ]
        if self.by_category:
            lines.append("\n카테고리별:")
            for cat, count in sorted(self.by_category.items(), key=lambda x: -x[1]):
                lines.append(f"  {cat}: {count}개")
        if self.by_type:
            lines.append("\n유형별:")
            for t, count in sorted(self.by_type.items(), key=lambda x: -x[1]):
                lines.append(f"  {t}: {count}개")
        if self.by_subject:
            lines.append("\n과목별:")
            for s, count in sorted(self.by_subject.items(), key=lambda x: -x[1]):
                lines.append(f"  {s}: {count}개")
        return "\n".join(lines)


@dataclass
class VerificationResult:
    """검수 결과."""
    passed: bool
    note: Note
    issues: list[str] = field(default_factory=list)


class DataPipeline:
    """Keep → 구조화 데이터 파이프라인.

    사용법:
        pipeline = DataPipeline()

        # 방법 1: Keep Takeout 디렉토리에서
        notes = pipeline.run_from_directory("/path/to/Keep")

        # 방법 2: 텍스트에서
        notes = pipeline.run_from_text("복사한 노트 텍스트...")

        # 방법 3: 이미 파싱된 Note 리스트에서
        notes = pipeline.run(raw_notes)

        # 결과 저장
        pipeline.save_results("output.json")
        print(pipeline.stats.summary())
    """

    def __init__(
        self,
        min_content_length: int = 10,
        remove_duplicates: bool = True,
    ) -> None:
        self.parser = KeepParser()
        self.classifier = NoteClassifier()
        self.min_content_length = min_content_length
        self.remove_duplicates = remove_duplicates
        self.stats = PipelineStats()
        self._results: list[Note] = []

    @property
    def results(self) -> list[Note]:
        return list(self._results)

    def run_from_directory(self, path: str | Path) -> list[Note]:
        """Keep Takeout 디렉토리에서 전체 파이프라인 실행."""
        raw_notes = self.parser.parse_directory(path)
        self.stats.total_input = self.parser.stats["total"]
        self.stats.parsed = self.parser.stats["parsed"]
        return self._process(raw_notes)

    def run_from_text(self, text: str) -> list[Note]:
        """텍스트 덤프에서 전체 파이프라인 실행."""
        raw_notes = self.parser.parse_text_dump(text)
        self.stats.total_input = len(raw_notes)
        self.stats.parsed = len(raw_notes)
        return self._process(raw_notes)

    def run(self, notes: list[Note]) -> list[Note]:
        """Note 리스트에서 파이프라인 실행 (분류 + 검수)."""
        self.stats.total_input = len(notes)
        self.stats.parsed = len(notes)
        return self._process(notes)

    def _process(self, notes: list[Note]) -> list[Note]:
        """분류 → 검수 → 중복 제거."""
        # Step 1: 분류
        classified = self.classifier.classify_all(notes)
        self.stats.classified = len(classified)

        # Step 2: 검수
        verified: list[Note] = []
        for note in classified:
            result = self._verify(note)
            if result.passed:
                result.note.verified = True
                verified.append(result.note)
            else:
                self.stats.rejected += 1
                logger.debug(
                    f"검수 탈락: {note.title[:30]} — {result.issues}"
                )

        # Step 3: 중복 제거
        if self.remove_duplicates:
            before = len(verified)
            verified = self._deduplicate(verified)
            self.stats.duplicates_removed = before - len(verified)

        self.stats.verified = len(verified)

        # 통계 집계
        self._compute_stats(verified)
        self._results = verified

        return verified

    def _verify(self, note: Note) -> VerificationResult:
        """개별 노트 검수."""
        issues: list[str] = []

        # 최소 길이
        if len(note.content) < self.min_content_length:
            issues.append(f"내용 너무 짧음 ({len(note.content)}자)")

        # 분류 안 됨
        if note.category == NoteCategory.OTHER and note.note_type == NoteType.UNKNOWN:
            issues.append("카테고리/유형 미분류")

        return VerificationResult(
            passed=len(issues) == 0,
            note=note,
            issues=issues,
        )

    def _deduplicate(self, notes: list[Note]) -> list[Note]:
        """내용 기반 중복 제거."""
        seen: set[str] = set()
        unique: list[Note] = []
        for note in notes:
            # 내용의 앞 200자를 기준으로 중복 판단
            key = note.content[:200].strip().lower()
            if key not in seen:
                seen.add(key)
                unique.append(note)
        return unique

    def _compute_stats(self, notes: list[Note]) -> None:
        """통계 집계."""
        cats = Counter(n.category.value for n in notes)
        types = Counter(n.note_type.value for n in notes)
        subjects = Counter(n.subject for n in notes if n.subject)

        self.stats.by_category = dict(cats)
        self.stats.by_type = dict(types)
        self.stats.by_subject = dict(subjects)

    def save_results(self, path: str | Path) -> Path:
        """검수 통과한 결과를 JSON 파일로 저장."""
        return save_notes(self._results, path)

    def save_stats(self, path: str | Path) -> Path:
        """통계를 JSON 파일로 저장."""
        p = Path(path)
        data = {
            "total_input": self.stats.total_input,
            "parsed": self.stats.parsed,
            "classified": self.stats.classified,
            "verified": self.stats.verified,
            "rejected": self.stats.rejected,
            "duplicates_removed": self.stats.duplicates_removed,
            "by_category": self.stats.by_category,
            "by_type": self.stats.by_type,
            "by_subject": self.stats.by_subject,
        }
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        return p
