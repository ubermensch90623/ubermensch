"""drill_loader — 해설카드 85개 HTML 에서 문제·선지·정답 추출 (회독 엔진 연료).

출력: harness/data/study_notes/drill_items.json
스키마:
  {
    "generated_at": "...",
    "total": N,
    "drillable": M,  # 문제·정답 모두 추출된 카드 수
    "readonly": K,   # 참고용 (대시보드·플래시카드 등 풀 수 없음)
    "items": [
      {
        "id": "함수_GDP_01",
        "filename": "함수_GDP_01.html",
        "title": "GDP 01 — 노동·자본 대체탄력도",
        "domain": "거시",
        "subtopic": "국민소득",
        "question": "노동과 자본 사이의 대체탄력도(σ)의 설명 중 틀린 것은?",
        "choices": ["σ=1일 때 ...", "생산함수가 ...", ...],
        "correct_index": 2,   # 1-based (① = 1)
        "raw_correct_marker": "② Cobb-Douglas는 규모수익불변이 아니어도 σ=1",
        "drillable": true,
        "card_path": "/study/함수_GDP_01.html"
      },
      ...
    ]
  }
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Dict, List, Optional, Tuple


CARDS_DIR = Path("C:/Users/윤상택/Desktop/Cowork_작업폴더/해설_카드")
CATALOG = Path(__file__).resolve().parent.parent / "data" / "study_notes" / "card_catalog.json"
OUTPUT = Path(__file__).resolve().parent.parent / "data" / "study_notes" / "drill_items.json"


# ①②③④⑤ → 1~5
CHOICE_MARKERS = {"①": 1, "②": 2, "③": 3, "④": 4, "⑤": 5}
CHOICE_PATTERN = re.compile(r"^[①②③④⑤]")

# <p>...①...</p> 캡처
CHOICE_P_RE = re.compile(
    r"<p[^>]*>\s*([①②③④⑤])\s*(.+?)\s*</p>",
    re.IGNORECASE | re.DOTALL,
)

# 문제 원문 card0 내 story-box
CARD0_RE = re.compile(
    r'<div[^>]*class="[^"]*card\s+active[^"]*"[^>]*id="card0"[^>]*>.*?'
    r'<div[^>]*class="[^"]*story-box[^"]*"[^>]*>(.+?)</div>\s*</div>',
    re.IGNORECASE | re.DOTALL,
)

# 정답 섹션: "정답: ② ...", "정답 ②", "공식 정답은 ④", "정답은 ③"
ANSWER_RE_STRICT = re.compile(
    r"정답\s*[::]\s*(?:<[^>]+>\s*)*([①②③④⑤])\s*([^<\n]{0,200})",
    re.DOTALL,
)
ANSWER_RE_LOOSE = re.compile(
    r"(?:공식\s*)?정답(?:은)?\s*[^가-힣\d<\n]{0,10}([①②③④⑤])",
    re.DOTALL,
)

# HTML 태그 제거
TAG_RE = re.compile(r"<[^>]+>")


def _strip_tags(html: str) -> str:
    return unescape(TAG_RE.sub("", html)).strip()


def _extract_question_choices(html: str) -> Tuple[Optional[str], List[str]]:
    """card0 에서 문제 원문 + 선지 5개."""
    m = CARD0_RE.search(html)
    if not m:
        return None, []
    block = m.group(1)
    # 모든 <p> 추출
    ps = re.findall(r"<p[^>]*>(.+?)</p>", block, re.IGNORECASE | re.DOTALL)
    if not ps:
        return None, []
    question = None
    choices: List[str] = []
    for p in ps:
        text = _strip_tags(p)
        if not text:
            continue
        # 한 p 안에 ①②③④⑤ 다수 포함된 경우(조합형) → split
        markers_in_p = [c for c in text if c in CHOICE_MARKERS]
        if len(markers_in_p) >= 2:
            # split by marker. re.split 으로 ① 앞까지 분리
            parts = re.split(r"(?=[①②③④⑤])", text)
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                if CHOICE_PATTERN.match(part):
                    choices.append(re.sub(r"^[①②③④⑤]\s*", "", part).strip())
            continue
        if CHOICE_PATTERN.match(text):
            stripped = re.sub(r"^[①②③④⑤]\s*", "", text)
            choices.append(stripped.strip())
        elif question is None:
            question = text
    return question, choices


def _extract_answer(html: str) -> Tuple[Optional[int], Optional[str]]:
    m = ANSWER_RE_STRICT.search(html)
    if m:
        marker = m.group(1)
        tail = _strip_tags(m.group(2)).strip()
        return CHOICE_MARKERS.get(marker), f"{marker} {tail}".strip()
    m2 = ANSWER_RE_LOOSE.search(html)
    if m2:
        marker = m2.group(1)
        return CHOICE_MARKERS.get(marker), marker
    return None, None


def _card_meta_from_catalog(catalog: Dict, filename: str) -> Dict:
    for c in catalog.get("cards", []):
        if c.get("filename") == filename:
            return c
    return {
        "filename": filename,
        "domain": "미분류",
        "subtopic": filename.replace(".html", ""),
        "title": filename,
    }


def build_drill_items() -> Dict:
    if not CATALOG.exists():
        return {"error": "catalog 미생성 (import_cards.py 먼저 실행)", "items": []}

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))

    items: List[Dict] = []
    drillable = 0
    readonly = 0

    for html_file in sorted(CARDS_DIR.glob("*.html")):
        if html_file.name == "index.html":
            continue
        try:
            html = html_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        meta = _card_meta_from_catalog(catalog, html_file.name)
        q, choices = _extract_question_choices(html)
        correct_idx, correct_raw = _extract_answer(html)

        has_q = bool(q)
        has_choices = len(choices) >= 4  # 최소 4지선다 (① ~ ④ 이상)
        has_ans = correct_idx is not None
        is_drillable = has_q and has_choices and has_ans

        if is_drillable:
            drillable += 1
        else:
            readonly += 1

        items.append({
            "id": html_file.stem,
            "filename": html_file.name,
            "title": meta.get("title", html_file.stem),
            "domain": meta.get("domain", "미분류"),
            "subtopic": meta.get("subtopic", ""),
            "question": q,
            "choices": choices,
            "correct_index": correct_idx,
            "raw_correct_marker": correct_raw,
            "drillable": is_drillable,
            "card_path": f"/study/{html_file.name}",
            "debug": {
                "has_question": has_q,
                "choices_count": len(choices),
                "has_answer": has_ans,
            },
        })

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total": len(items),
        "drillable": drillable,
        "readonly": readonly,
        "source_dir": str(CARDS_DIR).replace("\\", "/"),
        "items": items,
    }


def main() -> int:
    result = build_drill_items()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[drill_loader] total={result.get('total')}, drillable={result.get('drillable')}, readonly={result.get('readonly')}")
    # 도메인별 drillable
    by_dom: Dict[str, int] = {}
    for it in result.get("items", []):
        if it["drillable"]:
            by_dom[it["domain"]] = by_dom.get(it["domain"], 0) + 1
    print("drillable by domain:", json.dumps(by_dom, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
