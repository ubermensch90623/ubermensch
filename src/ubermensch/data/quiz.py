"""퀴즈 생성기 — 파싱된 노트에서 학습용 퀴즈를 자동 생성.

문제/오답분석/개념정리 유형 노트를 활용하여
복습용 퀴즈를 생성합니다. API 키 불필요.

사용법:
    from ubermensch.data.quiz import QuizGenerator
    gen = QuizGenerator()
    gen.load_notes("notes.json")
    quiz = gen.generate(count=5)
    print(quiz.render())
"""

from __future__ import annotations

import random
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ubermensch.data.note import Note, NoteCategory, NoteType, load_notes


@dataclass
class QuizItem:
    """개별 퀴즈 문항."""
    number: int
    category: str  # NCS / 경제학
    subject: str  # 수리, 미시 등
    question: str
    hint: str = ""
    answer: str = ""
    source_note_id: str = ""
    difficulty: str = "중"

    def render(self) -> str:
        lines = [
            f"Q{self.number}. [{self.category}/{self.subject}] (난이도: {self.difficulty})",
            "",
            self.question,
        ]
        if self.hint:
            lines.append(f"\n  💡 힌트: {self.hint}")
        return "\n".join(lines)

    def render_with_answer(self) -> str:
        text = self.render()
        if self.answer:
            text += f"\n\n  ✅ 정답/해설:\n  {self.answer}"
        return text


@dataclass
class Quiz:
    """퀴즈 세트."""
    items: list[QuizItem] = field(default_factory=list)
    focus_area: str = ""

    def render(self, show_answers: bool = False) -> str:
        lines = [
            "╔══════════════════════════════════════════════════╗",
            f"║  오늘의 퀴즈 — {len(self.items)}문항",
        ]
        if self.focus_area:
            lines.append(f"║  집중 영역: {self.focus_area}")
        lines.append("╚══════════════════════════════════════════════════╝")

        for item in self.items:
            lines.append("")
            lines.append("─" * 50)
            if show_answers:
                lines.append(item.render_with_answer())
            else:
                lines.append(item.render())

        lines.append("")
        lines.append("─" * 50)
        if not show_answers:
            lines.append(f"\n정답 확인: --answers 옵션 사용")

        return "\n".join(lines)


class QuizGenerator:
    """파싱된 노트에서 퀴즈를 생성합니다."""

    def __init__(self) -> None:
        self._notes: list[Note] = []
        self._by_category: dict[str, list[Note]] = {}
        self._by_subject: dict[str, list[Note]] = {}

    def load_notes(self, path: str | Path = "notes.json") -> int:
        """노트를 로드하고 인덱싱합니다. 로드된 퀴즈 소스 수를 반환."""
        all_notes = load_notes(path)

        # 퀴즈 가능한 노트만 필터
        self._notes = [
            n for n in all_notes
            if n.note_type in (NoteType.PROBLEM, NoteType.WRONG_ANSWER, NoteType.CONCEPT)
            and len(n.content) > 20
        ]

        # 인덱싱
        self._by_category = {}
        self._by_subject = {}
        for n in self._notes:
            cat = n.category.value
            self._by_category.setdefault(cat, []).append(n)
            if n.subject:
                self._by_subject.setdefault(n.subject, []).append(n)

        return len(self._notes)

    def generate(
        self,
        count: int = 5,
        focus_area: str = "",
        focus_category: str = "",
    ) -> Quiz:
        """퀴즈를 생성합니다.

        Args:
            count: 문항 수
            focus_area: 집중 영역 (예: "수리", "미시")
            focus_category: 카테고리 필터 (예: "NCS", "경제학")
        """
        # 풀에서 선택
        pool = list(self._notes)

        if focus_category and focus_category in self._by_category:
            pool = self._by_category[focus_category]
        if focus_area and focus_area in self._by_subject:
            pool = self._by_subject[focus_area]

        if not pool:
            return Quiz(focus_area=focus_area or focus_category)

        selected = random.sample(pool, min(count, len(pool)))
        items: list[QuizItem] = []

        for i, note in enumerate(selected, 1):
            item = self._note_to_quiz(i, note)
            items.append(item)

        return Quiz(items=items, focus_area=focus_area or focus_category or "종합")

    def _note_to_quiz(self, number: int, note: Note) -> QuizItem:
        """노트를 퀴즈 문항으로 변환."""
        content = note.content.strip()
        lines = content.split("\n")

        if note.note_type == NoteType.PROBLEM:
            # 문제 유형: 질문 부분 추출, 답은 숨김
            question, answer = self._split_problem(lines)
        elif note.note_type == NoteType.WRONG_ANSWER:
            # 오답 유형: "이 문제에서 틀린 이유는?" 형태로 변환
            question = self._make_wrong_answer_quiz(lines, note)
            answer = self._extract_wrong_reason(lines)
        else:
            # 개념 유형: 빈칸 채우기로 변환
            question, answer = self._make_concept_quiz(lines, note)

        return QuizItem(
            number=number,
            category=note.category.value,
            subject=note.subject or "일반",
            question=question,
            answer=answer,
            source_note_id=note.id,
            difficulty=note.difficulty or "중",
        )

    def _split_problem(self, lines: list[str]) -> tuple[str, str]:
        """문제에서 질문과 답을 분리."""
        question_lines: list[str] = []
        answer_lines: list[str] = []
        in_answer = False

        answer_markers = ["정답", "답:", "답 :", "풀이", "해설", "∴", "따라서"]

        for line in lines:
            stripped = line.strip().lower()
            if any(m in stripped for m in answer_markers):
                in_answer = True
            if in_answer:
                answer_lines.append(line)
            else:
                question_lines.append(line)

        question = "\n".join(question_lines).strip() or "\n".join(lines[:3]).strip()
        answer = "\n".join(answer_lines).strip() or "(정답 정보 없음)"

        return question, answer

    def _make_wrong_answer_quiz(self, lines: list[str], note: Note) -> str:
        """오답노트를 퀴즈로 변환."""
        # 앞부분에서 문제 상황 추출
        context = "\n".join(lines[:4]).strip()
        return (
            f"다음 문제에서 자주 틀리는 이유를 설명하세요:\n\n"
            f"{context}\n\n"
            f"왜 틀렸는지, 올바른 접근법은?"
        )

    def _extract_wrong_reason(self, lines: list[str]) -> str:
        """오답 이유 추출."""
        reason_markers = ["오답", "틀린", "이유", "주의", "함정"]
        for i, line in enumerate(lines):
            if any(m in line for m in reason_markers):
                return "\n".join(lines[i:]).strip()
        return "\n".join(lines[-3:]).strip()

    def _make_concept_quiz(self, lines: list[str], note: Note) -> tuple[str, str]:
        """개념 노트를 빈칸 채우기 퀴즈로 변환."""
        full_text = "\n".join(lines).strip()

        # 핵심 키워드를 ___로 대체
        # 제목에 있는 키워드를 찾아서 빈칸으로
        if note.title:
            keywords = [w for w in note.title.split() if len(w) >= 2]
            blanked = full_text
            replaced = []
            for kw in keywords[:2]:
                if kw.lower() in blanked.lower():
                    blanked = blanked.replace(kw, "______", 1)
                    replaced.append(kw)

            if replaced:
                question = f"빈칸에 들어갈 용어를 채우세요:\n\n{blanked}"
                answer = f"빈칸 정답: {', '.join(replaced)}\n\n원문:\n{full_text}"
                return question, answer

        # 빈칸 만들기 실패 → 요약 퀴즈
        preview = "\n".join(lines[:3])
        question = f"다음 개념을 설명하세요:\n\n{note.title}\n{preview}..."
        answer = full_text

        return question, answer
