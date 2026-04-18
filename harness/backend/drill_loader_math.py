"""drill_loader_math — NCS 수리능력 MD 실전문제집 파서.

입력:
  - Cowork_작업폴더/02_NCS_학습자료/NCS_수리능력_실전30제.md (최우선)
  - 추가 .md 파일 필요시 MD_SOURCES 리스트에 추가

출력: harness/data/study_notes/drill_items.json (경제학 카드 덮어쓰기)

MD 구조 가정:
  ## 섹션 1: 기초연산/응용계산 (5문제)
  ### 1번 문제
  질문 텍스트
  **선택지:**
  - ① 선지1
  - ② 선지2
  ...
  **정답:** ④ 정답 텍스트
  **풀이과정:**
  - ...
  **핵심 팁:**
  - ...
  ---
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


NCS_DIR = Path("C:/Users/윤상택/Desktop/Cowork_작업폴더/02_NCS_학습자료")
MD_SOURCES = [
    NCS_DIR / "NCS_수리능력_실전30제.md",
]
OUTPUT = Path(__file__).resolve().parent.parent / "data" / "study_notes" / "drill_items.json"

CHOICE_MARKERS = {"①": 1, "②": 2, "③": 3, "④": 4, "⑤": 5}
# 도메인 태그 (섹션명 → 4하위능력 매핑, P12 Q3 우선순위 기준)
SECTION_TO_DOMAIN = [
    (re.compile(r"기초연산|응용계산|연산"), ("기초연산", "기초연산능력")),
    (re.compile(r"자료해석|도표분석|도표.?이해"), ("도표분석", "도표분석능력")),
    (re.compile(r"통계|확률|평균|분산"), ("기초통계", "기초통계능력")),
    (re.compile(r"속도|농도|일률|비율|금융|이자|환율"), ("기초연산", "응용수리")),
    (re.compile(r"도표작성|그래프작성"), ("도표작성", "도표작성능력")),
]


def _classify_section(section: str) -> Tuple[str, str]:
    for pat, (dom, sub) in SECTION_TO_DOMAIN:
        if pat.search(section):
            return dom, sub
    return "기타", section.strip()


def _split_sections(md: str) -> List[Tuple[str, str]]:
    """##섹션 단위 분할 → [(section_title, body)]."""
    parts = re.split(r"^## ", md, flags=re.MULTILINE)
    out = []
    for p in parts[1:]:
        lines = p.splitlines()
        title = lines[0].strip() if lines else ""
        body = "\n".join(lines[1:])
        out.append((title, body))
    return out


def _split_problems(body: str) -> List[str]:
    """### N번 문제 단위 분할."""
    parts = re.split(r"^### \d+번 문제\s*$", body, flags=re.MULTILINE)
    # parts[0] 는 헤더 앞. 나머지가 각 문제 body
    return [p.strip() for p in parts[1:] if p.strip()]


def _parse_problem(body: str, source_file: str, section: str, idx_in_section: int) -> Optional[Dict]:
    # 선지 블록 찾기
    m_choices = re.search(r"\*\*선택지[^*]*\*\*\s*\n((?:- [①②③④⑤][^\n]*\n?)+)", body)
    if not m_choices:
        return None
    choice_lines = [ln.strip() for ln in m_choices.group(1).splitlines() if ln.strip().startswith("-")]
    choices: List[str] = []
    for ln in choice_lines:
        # "- ① 910억 원" → "910억 원"
        mm = re.match(r"-\s*[①②③④⑤]\s*(.+)", ln)
        if mm:
            choices.append(mm.group(1).strip().rstrip("✓").strip())
    if len(choices) < 4:
        return None

    # 정답 마커
    m_ans = re.search(r"\*\*정답[^*]*\*\*\s*([①②③④⑤])\s*([^\n]*)", body)
    if not m_ans:
        return None
    correct_idx = CHOICE_MARKERS[m_ans.group(1)]
    raw_marker = f"{m_ans.group(1)} {m_ans.group(2).strip()}"

    # 문제 본문: 선택지 블록 앞까지
    question = body[: m_choices.start()].strip()
    # 풀이과정 + 핵심팁 추출 (해설로)
    explanation_parts: List[str] = []
    for key in ("풀이과정", "핵심 팁", "핵심팁"):
        mm = re.search(rf"\*\*{re.escape(key)}[^*]*\*\*\s*\n((?:(?!\*\*)[\s\S])*?)(?=(?:\*\*|---|\Z))", body)
        if mm:
            explanation_parts.append(f"**{key}**\n{mm.group(1).strip()}")
    explanation = "\n\n".join(explanation_parts) if explanation_parts else None

    dom, sub = _classify_section(section)
    pid = f"수리_{section.split(':')[0].strip().replace(' ','')}_{idx_in_section:02d}"

    return {
        "id": pid,
        "filename": Path(source_file).name,
        "title": f"{section} · {idx_in_section}번",
        "domain": dom,
        "subtopic": sub,
        "section": section,
        "question": question,
        "choices": choices,
        "correct_index": correct_idx,
        "raw_correct_marker": raw_marker,
        "explanation": explanation,
        "drillable": True,
        "card_path": None,  # HTML 해설카드 없음. UI 에서 explanation 필드 사용
    }


def build() -> Dict:
    items: List[Dict] = []
    for src in MD_SOURCES:
        if not src.exists():
            continue
        md = src.read_text(encoding="utf-8", errors="ignore")
        for section_title, body in _split_sections(md):
            problems = _split_problems(body)
            for i, pbody in enumerate(problems, start=1):
                item = _parse_problem(pbody, str(src), section_title, i)
                if item:
                    items.append(item)

    drillable = sum(1 for it in items if it["drillable"])
    by_dom: Dict[str, int] = {}
    for it in items:
        by_dom[it["domain"]] = by_dom.get(it["domain"], 0) + 1

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "schema": "ncs_math_v1",
        "total": len(items),
        "drillable": drillable,
        "readonly": 0,
        "by_domain": by_dom,
        "source_files": [str(s).replace("\\", "/") for s in MD_SOURCES if s.exists()],
        "items": items,
    }


def main() -> int:
    res = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[drill_loader_math] total={res['total']} drillable={res['drillable']}")
    print("by_domain:", json.dumps(res["by_domain"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
