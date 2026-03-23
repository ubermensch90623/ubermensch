from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path

from .models import NCSDocument, NCSProblem

QUESTION_START_RE = re.compile(
    r"(?m)^(?P<number>(?:문항|문제)?\s*\d{1,3}[\.)]|\d{1,3}[\.)])\s*(?P<body>.+)$"
)
CHOICE_RE = re.compile(r"(?m)^\s*(?:[①②③④⑤]|[1-5]\))\s*(.+)$")
ANSWER_RE = re.compile(r"(?m)(?:정답|답)\s*[:：]\s*([①②③④⑤1-5])")
EXPLANATION_RE = re.compile(r"(?ms)(?:해설|풀이)\s*[:：]\s*(.+)$")
CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("의사소통", ("대화", "문서", "이메일", "보고서", "발표", "작성")),
    ("수리", ("확률", "비율", "속도", "거리", "표", "그래프", "계산")),
    ("자원관리", ("예산", "일정", "인력", "재고", "시간 관리", "집행")),
    ("문제해결", ("상황", "대안", "우선순위", "원인", "해결")),
    ("정보", ("데이터", "정보", "시스템", "보안", "DB")),
    ("기술", ("도면", "공정", "장비", "품질", "안전")),
]


def normalize_text(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    collapsed = "\n".join(line for line in lines if line.strip())
    return re.sub(r"[ \t]+", " ", collapsed).strip()


def infer_category(text: str) -> str:
    for category, keywords in CATEGORY_RULES:
        if any(keyword in text for keyword in keywords):
            return category
    return "미분류"


def _build_problem(number: str, block: str, page: int, source_file: str) -> NCSProblem:
    normalized = normalize_text(block)
    choices = [match.group(1).strip() for match in CHOICE_RE.finditer(normalized)]
    answer_match = ANSWER_RE.search(normalized)
    explanation_match = EXPLANATION_RE.search(normalized)

    question_lines: list[str] = []
    for line in normalized.splitlines():
        if CHOICE_RE.match(line) or ANSWER_RE.search(line) or line.startswith(("해설", "풀이")):
            break
        question_lines.append(line)

    question_text = "\n".join(question_lines).strip()
    question_text = QUESTION_START_RE.sub(lambda m: f"{m.group('number')} {m.group('body')}", question_text, count=1)

    return NCSProblem(
        number=number.strip(),
        page=page,
        category=infer_category(question_text),
        question=question_text,
        choices=choices,
        answer=answer_match.group(1) if answer_match else None,
        explanation=explanation_match.group(1).strip() if explanation_match else None,
        source_file=source_file,
    )


def extract_problems_from_pages(pages: list[dict[str, str | int]], source_file: str) -> NCSDocument:
    problems: list[NCSProblem] = []

    for page_data in pages:
        page = int(page_data["page"])
        text = normalize_text(str(page_data["text"]))
        if not text:
            continue

        matches = list(QUESTION_START_RE.finditer(text))
        if not matches:
            continue

        for index, match in enumerate(matches):
            start = match.start()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            block = text[start:end].strip()
            number = match.group("number")
            problems.append(_build_problem(number=number, block=block, page=page, source_file=source_file))

    deduped: list[NCSProblem] = []
    seen: set[tuple[str, str]] = set()
    for problem in problems:
        key = (problem.number, problem.question)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(problem)

    return NCSDocument(source_file=Path(source_file).name, problems=deduped)


def regroup_by_category(document: NCSDocument) -> dict[str, list[dict[str, str | int | list[str] | None]]]:
    grouped: dict[str, list[dict[str, str | int | list[str] | None]]] = {}
    for problem in document.problems:
        grouped.setdefault(problem.category, []).append(problem.to_dict())
    return grouped
