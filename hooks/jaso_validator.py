"""
jaso_validator Stop hook — 자소서 생성·수정 직후 자동 검증.

배치: C:\\Users\\윤상택\\Desktop\\.claude\\hooks\\jaso_validator.py

자가진화 제안 3 (severity 4, 2026-05-24 채택)
- 관찰: 5/24 7건 자소서 vault append. KDIC·SGI sed 추출 실패로 147~252B placeholder.
  글자수·금칙어·자격증/경력 누락 자동 검증 부재 → 종환 검토 시간 낭비.
- 처방: 자소서 .md 파일 mtime 변동 시 자동 5단계 검증, ✅/⚠️ vault 표시.

검증 5단계:
  1. 글자 수 카운트 (회사별 폼 기준)
  2. AI tic 금칙어 11종 grep (자소서_피드백_누적.md 기반)
  3. 박-계열 12종 grep (CLAUDE.md 헌법)
  4. 자격증 5개·경력 3건 누락 grep
  5. 소제목 문항당 1개 룰 검증
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable

LOG_DIR = Path(os.environ.get("HERMES_LOG_DIR", r"C:\Users\윤상택\.hermes\logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
INTERNAL_LOG = LOG_DIR / "jaso_validator_debug.log"

logging.basicConfig(
    filename=INTERNAL_LOG,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
)

# 자소서 파일 watch 위치 (mtime 변동 검사)
JASO_DIRS = [
    Path(r"C:\Users\윤상택\Desktop\작업\ObsidianVault\_SSOT\자소서_28건_2026-05-24"),
    Path(r"C:\Users\윤상택\Desktop"),  # 회사별 자소서 작업 디렉토리
]

# 회사별 글자 수 폼 (자가진화 보고서 5/24 기준)
COMPANY_LIMITS = {
    "KEPCO": 5500,
    "한전": 5500,
    "KHNP": 5700,
    "한수원": 5700,
    "KDIC": 6700,
    "예금보험공사": 6700,
    "HF": 4500,
    "한국주택금융공사": 4500,
    "SGI": 4300,
    "서울보증보험": 4300,
    "신보": 4600,
    "신용보증기금": 4600,
    "캠코": 5000,
    "한국자산관리공사": 5000,
}

# AI tic 금지어 11종 (자소서_피드백_누적.md)
JASO_FORBIDDEN = [
    "자연스러운 경로", "현금 리듬", "이중 경험", "네 축", "재정렬",
    "21시 루틴", "기록자", "기업주의 개인신용", "감각을 끌어올리는",
    "한 곳입니다", "해 나가겠습니다",
]

# 박-계열 12종 (CLAUDE.md 헌법)
PARK_FORBIDDEN = [
    "박아", "박음", "박혀", "박힌", "박힘", "박혔",
    "박을", "박는", "박혀있", "박혀있는",
]

# 자격증 5개 (이해도 확보용)
REQUIRED_CERTS = [
    "투자자산운용사", "자산관리사", "신용상담사", "컴활", "한국사",
]

# 경력 3건 (실무 도구)
REQUIRED_CAREERS = [
    "신용보증기금",  # 인턴 2020.09~11
    "근로복지공단",  # 2021.06~2022.07
    "서민금융진흥원",  # 2023.03~
]


def detect_company(text: str, path: Path) -> str | None:
    for name in COMPANY_LIMITS:
        if name in text or name in path.name or name in str(path.parent.name):
            return name
    return None


def count_chars_korean(text: str) -> int:
    """공백 포함 글자 수 (한국 자소서 폼 기준)."""
    # markdown front-matter 제외
    lines = []
    in_fm = False
    for line in text.splitlines():
        if line.strip() == "---":
            in_fm = not in_fm
            continue
        if in_fm:
            continue
        lines.append(line)
    return sum(len(l) for l in lines)


def find_hits(text: str, terms: Iterable[str]) -> list[str]:
    return [t for t in terms if t in text]


def find_h2_per_question(text: str) -> dict[str, int]:
    """문항별 ## 소제목 개수. 문항당 1개가 룰."""
    sections = re.split(r"\n#\s+", text)  # # 1문항 / # 2문항 단위
    counts = {}
    for sec in sections[1:]:
        title = sec.splitlines()[0].strip()
        h2_count = sum(1 for line in sec.splitlines() if line.startswith("## "))
        counts[title] = h2_count
    return counts


def validate(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    company = detect_company(text, path)
    char_count = count_chars_korean(text)
    limit = COMPANY_LIMITS.get(company) if company else None

    failures = []

    # 1. 글자 수
    if limit and char_count > limit * 1.05:
        failures.append(f"글자수 초과: {char_count}자 / 폼 {limit}자 (+{char_count - limit}자)")
    elif limit and char_count < limit * 0.7:
        failures.append(f"글자수 부족: {char_count}자 / 폼 {limit}자 (-{limit - char_count}자)")

    # 2. 자소서 금지어
    jaso_hits = find_hits(text, JASO_FORBIDDEN)
    if jaso_hits:
        failures.append(f"자소서 AI tic 금지어 {len(jaso_hits)}건: {', '.join(jaso_hits[:3])}")

    # 3. 박-계열
    park_hits = find_hits(text, PARK_FORBIDDEN)
    if park_hits:
        failures.append(f"박-계열 어휘 {len(park_hits)}건: {', '.join(park_hits[:3])}")

    # 4. 자격증 / 경력 누락 (전체 자소서 기준)
    missing_certs = [c for c in REQUIRED_CERTS if c not in text]
    missing_careers = [c for c in REQUIRED_CAREERS if c not in text]
    if missing_certs:
        failures.append(f"자격증 누락 {len(missing_certs)}건: {', '.join(missing_certs)}")
    if missing_careers:
        failures.append(f"경력 누락 {len(missing_careers)}건: {', '.join(missing_careers)}")

    # 5. 문항당 ## 1개 룰
    h2_counts = find_h2_per_question(text)
    over = {q: n for q, n in h2_counts.items() if n > 1}
    if over:
        failures.append(f"소제목 문항당 1개 위반 {len(over)}건: {list(over.items())[:2]}")

    return {
        "path": str(path),
        "company": company,
        "char_count": char_count,
        "limit": limit,
        "failures": failures,
        "passed": len(failures) == 0,
    }


def append_vault_marker(result: dict) -> None:
    """vault `_SSOT/자소서_피드백_누적.md` 끝에 결과 1줄 append."""
    vault_log = Path(
        r"C:\Users\윤상택\Desktop\작업\ObsidianVault\_SSOT\자소서_피드백_누적.md"
    )
    if not vault_log.parent.exists():
        return
    marker = "✅" if result["passed"] else "⚠️"
    line = (
        f"\n- {datetime.now().isoformat(timespec='seconds')} | {marker} | "
        f"{result['company'] or '?'} | {result['char_count']}자 | "
        f"{Path(result['path']).name} | "
    )
    if result["failures"]:
        line += "; ".join(result["failures"][:3])
    else:
        line += "통과"

    with vault_log.open("a", encoding="utf-8") as f:
        f.write(line)


def iter_modified_jaso(stop_payload: dict) -> Iterable[Path]:
    """Stop hook payload에서 직전에 수정된 자소서 .md 추출."""
    edited = stop_payload.get("edited_files") or []
    for p in edited:
        path = Path(p)
        if path.suffix == ".md" and any(
            keyword in str(path).lower()
            for keyword in ["자소서", "jaso", "_v1", "_v2", "_v3", "_v4", "_v5", "_v6"]
        ):
            yield path

    # fallback: JASO_DIRS에서 최근 5분 내 수정된 .md
    now = datetime.now().timestamp()
    for jdir in JASO_DIRS:
        if not jdir.exists():
            continue
        for path in jdir.rglob("*.md"):
            try:
                if now - path.stat().st_mtime < 300:  # 5분 이내
                    if any(k in path.name.lower() for k in ["자소서", "jaso"]):
                        yield path
            except OSError:
                continue


def main() -> int:
    try:
        payload = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    except json.JSONDecodeError as exc:
        logging.error("stdin parse fail: %s", exc)
        payload = {}

    targets = list({p.resolve() for p in iter_modified_jaso(payload)})
    if not targets:
        logging.info("no recent jaso .md changes")
        return 0

    logging.info("validating %d jaso files", len(targets))
    any_failure = False
    for path in targets:
        try:
            result = validate(path)
        except OSError as exc:
            logging.error("read fail %s: %s", path, exc)
            continue
        append_vault_marker(result)
        if not result["passed"]:
            any_failure = True
            logging.warning(
                "%s: %d failures — %s",
                path.name, len(result["failures"]),
                "; ".join(result["failures"][:2]),
            )

    return 1 if any_failure else 0


if __name__ == "__main__":
    sys.exit(main())
