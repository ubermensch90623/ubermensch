"""import_cards — Cowork_작업폴더/해설_카드/*.html 을 harness 학습 자료로 인덱싱.

출력: harness/data/study_notes/card_catalog.json
  - 86개 HTML 의 메타 (파일명·주제·제목·토픽 태그) + 절대경로
  - stage='study_note' (1차 기출 아님, restored 와 분리)
  - UI 에서 iframe 또는 새 탭으로 열람 가능
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


CARDS_DIR = Path("C:/Users/윤상택/Desktop/Cowork_작업폴더/해설_카드")
OUTPUT = Path(__file__).resolve().parent.parent / "data" / "study_notes" / "card_catalog.json"


TOPIC_MAP = {
    # prefix → (domain, subtopic)
    "PPF": ("미시", "생산가능곡선"),
    "함수_PPF": ("미시", "생산가능곡선"),
    "함수_효용": ("미시", "소비자이론"),
    "함수_수요공급": ("미시", "수요공급"),
    "대체재_보완재": ("미시", "수요공급"),
    "수요합산": ("미시", "수요공급"),
    "함수_탄력성": ("미시", "탄력성"),
    "함수_생산비용": ("미시", "비용함수"),
    "함수_독점": ("미시", "시장구조/독점"),
    "독점_이윤극대화": ("미시", "시장구조/독점"),
    "리카도_대등정리": ("거시", "재정정책"),
    "균형재정_승수": ("거시", "재정정책"),
    "함수_승수": ("거시", "재정정책"),
    "M5_세율포함_승수": ("거시", "재정정책"),
    "ISLM_완전정복": ("거시", "IS-LM"),
    "함수_ISLM": ("거시", "IS-LM"),
    "유동성함정_그래프": ("거시", "IS-LM"),
    "함수_GDP": ("거시", "국민소득"),
    "함수_실업": ("거시", "실업률"),
    "함수_화폐": ("거시", "화폐금융"),
    "화폐중립성_고전학파": ("거시", "화폐금융"),
    "리카도_비교우위_모형": ("국제", "비교우위"),
    "PPF_비교우위_2인": ("국제", "비교우위"),
    "함수_환율": ("국제", "환율/먼델플레밍"),
    "경제학_학파": ("거시", "학파"),
    "헷갈리는_개념_전수조사": ("종합", "개념정리"),
    "함수_기타": ("종합", "기타"),
    "00_D-DAY_대시보드": ("시험전략", "D-DAY 대시보드"),
    "01_시험장_새벽4시_플래시카드": ("시험전략", "시험장 플래시카드"),
    "02_시험장_대기실_계속보기": ("시험전략", "시험장 대기실"),
    "03_시험당일_최종체크리스트": ("시험전략", "당일 체크리스트"),
    "04_NCS_40점_최약점_집중": ("NCS", "최약점 집중"),
    "05_경제학_학파_5종_5초판단": ("거시", "학파 5초 판단"),
    "06_경제학_계산_드릴_12문": ("미시거시", "계산 드릴"),
    "07_최후5분_종이한장_비상": ("시험전략", "최후 5분"),
}


def _classify(filename: str) -> tuple[str, str]:
    stem = filename.replace(".html", "")
    for prefix, (dom, sub) in TOPIC_MAP.items():
        if stem.startswith(prefix) or stem == prefix:
            return dom, sub
    return "미분류", stem


def _extract_title(html_path: Path) -> str:
    """<title> 또는 첫 <h1>/<p class="sub"> 텍스트."""
    try:
        text = html_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return html_path.stem
    m = re.search(r"<title>(.+?)</title>", text, re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1).strip()
    m2 = re.search(r'<p\s+class="sub">(.+?)</p>', text, re.IGNORECASE | re.DOTALL)
    if m2:
        return re.sub(r"<[^>]+>", "", m2.group(1)).strip()
    return html_path.stem


def build_catalog() -> Dict:
    if not CARDS_DIR.exists():
        return {"error": f"{CARDS_DIR} 없음", "cards": []}
    cards: List[Dict] = []
    for html in sorted(CARDS_DIR.glob("*.html")):
        if html.name == "index.html":
            continue
        dom, sub = _classify(html.name)
        cards.append({
            "filename": html.name,
            "absolute_path": str(html).replace("\\", "/"),
            "domain": dom,
            "subtopic": sub,
            "title": _extract_title(html),
            "stage": "study_note",
            "size_bytes": html.stat().st_size,
        })
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total": len(cards),
        "source_dir": str(CARDS_DIR).replace("\\", "/"),
        "cards": cards,
        "by_domain": {
            dom: sum(1 for c in cards if c["domain"] == dom)
            for dom in {c["domain"] for c in cards}
        },
    }


def main() -> int:
    catalog = build_catalog()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"imported {catalog.get('total', 0)} cards → {OUTPUT}")
    print(json.dumps(catalog.get("by_domain", {}), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
