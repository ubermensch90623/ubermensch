"""노트 자동 분류기 — 키워드 기반으로 NCS/경제학/기타 분류.

API 키 없이 동작하는 규칙 기반 분류기입니다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from ubermensch.data.note import Note, NoteCategory, NoteType


# ─── 키워드 사전 ──────────────────────────────────────────────

NCS_KEYWORDS = {
    "수리": [
        "수리", "계산", "비율", "확률", "통계", "자료해석", "수열",
        "방정식", "부등식", "경우의 수", "평균", "분산", "표준편차",
        "그래프", "도표", "백분율", "증가율", "감소율",
    ],
    "언어": [
        "언어", "독해", "어휘", "문법", "맞춤법", "독서",
        "지문", "요약", "추론", "문맥", "접속사", "주제",
        "글의 순서", "문장 배열", "빈칸 추론",
    ],
    "추론": [
        "추론", "논리", "명제", "삼단논법", "조건", "참/거짓",
        "진리표", "벤다이어그램", "규칙 찾기", "패턴",
    ],
    "자료해석": [
        "자료해석", "표", "차트", "그래프 해석", "데이터 분석",
        "전년 대비", "구성비", "증감", "추이",
    ],
    "상황판단": [
        "상황판단", "의사결정", "문제해결", "절차", "규정",
        "업무 처리", "우선순위", "갈등", "민원",
    ],
}

ECONOMICS_KEYWORDS = {
    "미시": [
        "미시", "수요", "공급", "균형", "탄력성", "효용",
        "무차별곡선", "예산선", "한계", "비용", "이윤",
        "독점", "과점", "완전경쟁", "시장실패", "외부효과",
        "공공재", "역선택", "도덕적 해이",
    ],
    "거시": [
        "거시", "GDP", "국민소득", "물가", "인플레이션",
        "실업", "경기변동", "IS-LM", "AD-AS", "총수요",
        "총공급", "통화정책", "재정정책", "승수효과",
        "필립스곡선", "금리", "환율",
    ],
    "국제경제": [
        "국제", "무역", "관세", "환율", "국제수지",
        "비교우위", "절대우위", "자유무역", "보호무역",
        "FTA", "WTO", "헥셔-올린",
    ],
    "재정학": [
        "재정", "조세", "세금", "예산", "국채",
        "공공선택", "투표", "지대추구", "공공경제",
    ],
}

NCS_FLAT = [kw for keywords in NCS_KEYWORDS.values() for kw in keywords]
ECONOMICS_FLAT = [kw for keywords in ECONOMICS_KEYWORDS.values() for kw in keywords]

# 문제/풀이/오답분석 패턴
TYPE_PATTERNS = {
    NoteType.PROBLEM: [
        r"문제\s*\d*", r"\d+\.\s", r"다음.*고르시오", r"구하시오",
        r"올바른 것", r"옳은 것", r"틀린 것", r"보기.*서",
    ],
    NoteType.SOLUTION: [
        r"풀이", r"해설", r"정답[:：]", r"답[:：]", r"∴",
        r"따라서", r"그러므로",
    ],
    NoteType.WRONG_ANSWER: [
        r"오답", r"틀린 이유", r"실수", r"함정", r"주의",
        r"헷갈", r"다시 풀기", r"복습",
    ],
    NoteType.CONCEPT: [
        r"개념", r"정의[:：]", r"공식[:：]", r"요약",
        r"핵심", r"암기", r"정리",
    ],
    NoteType.SCHEDULE: [
        r"일정", r"계획", r"오늘", r"내일", r"이번 주",
        r"D-\d+", r"\d+월\s*\d+일",
    ],
}


@dataclass
class ClassificationResult:
    """분류 결과."""
    category: NoteCategory
    note_type: NoteType
    subject: str
    difficulty: str
    tags: list[str]
    confidence: float  # 0.0 ~ 1.0


class NoteClassifier:
    """규칙 기반 노트 분류기.

    사용법:
        classifier = NoteClassifier()
        classified_notes = classifier.classify_all(notes)
        result = classifier.classify(note)
    """

    def classify(self, note: Note) -> Note:
        """단일 노트를 분류합니다. 원본을 수정하고 반환."""
        text = f"{note.title} {note.content}".lower()
        result = self._analyze(text, note.labels)

        note.category = result.category
        note.note_type = result.note_type
        note.subject = result.subject
        note.difficulty = result.difficulty
        note.tags = result.tags

        return note

    def classify_all(self, notes: list[Note]) -> list[Note]:
        """노트 리스트 전체를 분류합니다."""
        return [self.classify(note) for note in notes]

    def _analyze(self, text: str, labels: list[str]) -> ClassificationResult:
        """텍스트와 라벨을 분석하여 분류 결과를 반환."""
        # 1. 카테고리 판별
        ncs_score = self._count_matches(text, NCS_FLAT, labels, ["NCS", "ncs"])
        econ_score = self._count_matches(text, ECONOMICS_FLAT, labels, ["경제", "경제학", "econ"])

        if ncs_score > 0 and econ_score > 0:
            category = NoteCategory.MIXED
        elif ncs_score > econ_score:
            category = NoteCategory.NCS
        elif econ_score > ncs_score:
            category = NoteCategory.ECONOMICS
        else:
            category = NoteCategory.OTHER

        # 2. 세부 과목 판별
        subject = self._detect_subject(text, category)

        # 3. 노트 유형 판별
        note_type = self._detect_type(text)

        # 4. 난이도 판별
        difficulty = self._detect_difficulty(text)

        # 5. 태그 생성
        tags = self._generate_tags(text, category, subject, note_type)

        # 6. 신뢰도
        total_matches = ncs_score + econ_score
        confidence = min(total_matches / 5.0, 1.0) if total_matches > 0 else 0.1

        return ClassificationResult(
            category=category,
            note_type=note_type,
            subject=subject,
            difficulty=difficulty,
            tags=tags,
            confidence=confidence,
        )

    def _count_matches(
        self, text: str, keywords: list[str], labels: list[str], label_matches: list[str]
    ) -> int:
        """키워드 매칭 점수를 계산합니다."""
        score = 0
        for kw in keywords:
            if kw.lower() in text:
                score += 1
        for label in labels:
            if any(m.lower() in label.lower() for m in label_matches):
                score += 3  # 라벨은 가중치 높음
        return score

    def _detect_subject(self, text: str, category: NoteCategory) -> str:
        """세부 과목을 판별합니다."""
        if category == NoteCategory.NCS:
            keywords_map = NCS_KEYWORDS
        elif category == NoteCategory.ECONOMICS:
            keywords_map = ECONOMICS_KEYWORDS
        else:
            return ""

        best_subject = ""
        best_score = 0
        for subject, keywords in keywords_map.items():
            score = sum(1 for kw in keywords if kw.lower() in text)
            if score > best_score:
                best_score = score
                best_subject = subject

        return best_subject

    def _detect_type(self, text: str) -> NoteType:
        """노트 유형을 판별합니다."""
        best_type = NoteType.UNKNOWN
        best_count = 0

        for note_type, patterns in TYPE_PATTERNS.items():
            count = sum(1 for p in patterns if re.search(p, text))
            if count > best_count:
                best_count = count
                best_type = note_type

        return best_type if best_count > 0 else NoteType.MEMO

    def _detect_difficulty(self, text: str) -> str:
        """난이도를 추정합니다."""
        hard_signals = ["어려운", "고난도", "심화", "응용", "함정"]
        easy_signals = ["기본", "기초", "쉬운", "입문", "암기"]

        hard = sum(1 for s in hard_signals if s in text)
        easy = sum(1 for s in easy_signals if s in text)

        if hard > easy:
            return "상"
        elif easy > hard:
            return "하"
        return "중"

    def _generate_tags(
        self, text: str, category: NoteCategory, subject: str, note_type: NoteType
    ) -> list[str]:
        """자동 태그를 생성합니다."""
        tags = []
        if category != NoteCategory.OTHER:
            tags.append(category.value)
        if subject:
            tags.append(subject)
        if note_type != NoteType.UNKNOWN:
            tags.append(note_type.value)
        return tags
