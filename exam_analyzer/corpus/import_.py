"""사용자 이북/공고 발췌본 → Question 반입.

지원 입력:
- JSON (questions 배열)
- 플레인 텍스트 (간단 포맷: Q:/A:/B:/C:/D:/정답:/해설:)
- 대화형 (향후 추가)

C-0 준수: provenance 필수. 출처 없는 문항 반입 거부.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .models import Choice, Provenance, Question, generate_question_id


class ImportError(Exception):  # noqa: A001 (shadow builtin)
    pass


def _validate_provenance(prov: Optional[Provenance]) -> None:
    if prov is None:
        raise ImportError("provenance 필드 필수 (C-0 데이터 혈통)")
    required = [prov.source_type, prov.source_name, prov.source_date]
    if not all(required):
        raise ImportError(
            f"provenance 필수 필드(source_type/name/date) 누락: {prov}"
        )


def question_from_user_dict(d: Dict[str, Any]) -> Question:
    """사용자 제공 dict → Question. provenance 필수 검증."""
    if "provenance" not in d or d["provenance"] is None:
        raise ImportError("'provenance' 필드 누락 (C-0 위반)")

    prov_d = d["provenance"]
    provenance = Provenance(
        source_type=prov_d["source_type"],
        source_name=prov_d["source_name"],
        source_citation=prov_d.get("source_citation", ""),
        source_date=prov_d["source_date"],
        chain=prov_d.get("chain", []),
    )
    _validate_provenance(provenance)

    choices = [
        Choice(
            index=c.get("index", i + 1),
            text=c["text"],
            is_correct=c.get("is_correct", False),
            trap_type=c.get("trap_type"),
        )
        for i, c in enumerate(d.get("choices", []))
    ]

    kind = d.get("kind", "primary")
    agency = d["agency"]
    area = d.get("area", "")
    question_text = d["question_text"]

    qid = d.get("id") or generate_question_id(kind, agency, area, question_text)

    return Question(
        id=qid,
        kind=kind,
        agency=agency,
        area=area,
        subtype=d.get("subtype", ""),
        question_text=question_text,
        choices=choices,
        correct_index=d.get("correct_index"),
        explanation=d.get("explanation", ""),
        related_law_articles=d.get("related_law_articles", []),
        tags=d.get("tags", []),
        provenance=provenance,
        rationale_chain=d.get("rationale_chain", []),
        confidence=d.get("confidence"),
        counter_arguments=d.get("counter_arguments", []),
    )


def import_from_json_file(path: Path) -> List[Question]:
    """JSON 파일 → Question 리스트. 포맷:

    {
      "questions": [
        {"agency": "...", "area": "...", "question_text": "...", "provenance": {...}, ...},
        ...
      ]
    }

    또는 질문 배열만 있어도 OK.
    """
    path = Path(path).expanduser()
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        raw = data.get("questions", [])
    elif isinstance(data, list):
        raw = data
    else:
        raise ImportError(f"Unsupported JSON structure: {type(data).__name__}")

    out: List[Question] = []
    errors: List[str] = []
    for i, d in enumerate(raw):
        try:
            out.append(question_from_user_dict(d))
        except Exception as e:  # noqa: BLE001
            errors.append(f"item[{i}]: {e}")
    if errors:
        raise ImportError(
            f"{len(errors)}건 반입 실패 ({len(out)}건은 성공): "
            + "; ".join(errors[:5])
            + ("..." if len(errors) > 5 else "")
        )
    return out


def parse_simple_text_block(
    block: str,
    agency: str,
    area: str,
    provenance: Provenance,
    subtype: str = "",
) -> Question:
    """간단 텍스트 포맷 1문항 파싱.

    포맷 (줄바꿈 구분):
      Q: 문제 본문 ...
      1) 선지1
      2) 선지2
      3) 선지3
      4) 선지4
      정답: 2
      해설: (선택)

    provenance 는 호출자가 전달 (C-0 필수).
    """
    _validate_provenance(provenance)

    lines = [ln.strip() for ln in block.strip().splitlines() if ln.strip()]
    if not lines:
        raise ImportError("빈 블록")

    q_text = ""
    choices: List[Choice] = []
    correct: Optional[int] = None
    explanation = ""
    current_section = "question"

    for ln in lines:
        if ln.startswith("Q:") or ln.startswith("Q."):
            q_text = ln.split(":", 1)[-1].split(".", 1)[-1].strip()
            current_section = "question"
        elif ln.startswith("정답:"):
            try:
                correct = int(ln.split(":", 1)[1].strip())
            except ValueError:
                raise ImportError(f"정답 번호 파싱 실패: {ln}")
            current_section = "after"
        elif ln.startswith("해설:"):
            explanation = ln.split(":", 1)[1].strip()
            current_section = "explanation"
        elif ln[:2] in ("1)", "2)", "3)", "4)", "5)"):
            try:
                idx = int(ln[0])
            except ValueError:
                raise ImportError(f"선지 인덱스 파싱 실패: {ln}")
            text = ln[2:].strip()
            choices.append(Choice(index=idx, text=text))
            current_section = "choices"
        else:
            if current_section == "question":
                q_text += " " + ln
            elif current_section == "explanation":
                explanation += " " + ln
            elif current_section == "choices" and choices:
                choices[-1].text += " " + ln

    if not q_text:
        raise ImportError("Q: 로 시작하는 문제 본문 없음")
    if not choices:
        raise ImportError("선지 없음")

    if correct is not None and 1 <= correct <= len(choices):
        for c in choices:
            c.is_correct = c.index == correct

    qid = generate_question_id("primary", agency, area, q_text)
    return Question(
        id=qid,
        kind="primary",
        agency=agency,
        area=area,
        subtype=subtype,
        question_text=q_text,
        choices=choices,
        correct_index=correct,
        explanation=explanation,
        provenance=provenance,
    )


def import_from_simple_text(
    content: str,
    agency: str,
    area: str,
    provenance: Provenance,
    subtype: str = "",
    separator: str = "\n---\n",
) -> List[Question]:
    """여러 문항이 separator 로 구분된 텍스트 → Question 리스트."""
    blocks = [b for b in content.split(separator) if b.strip()]
    results = []
    for b in blocks:
        results.append(
            parse_simple_text_block(b, agency, area, provenance, subtype)
        )
    return results


def deduplicate(
    existing: Iterable[Question], new: Iterable[Question]
) -> List[Question]:
    """기존 corpus 와 신규 사이 ID 충돌 제거. 신규에서만 제거."""
    existing_ids = {q.id for q in existing}
    return [q for q in new if q.id not in existing_ids]
