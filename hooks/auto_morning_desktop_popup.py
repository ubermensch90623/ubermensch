"""
Hermes Stop hook — 새벽 catch-up 종료 시 종환 데스크톱에 MessageBox 자동 띄움.

배치: C:\\Users\\윤상택\\Desktop\\.claude\\hooks\\auto_morning_desktop_popup.py

자가진화 제안 1 (severity 5, P0, 2026-05-24 채택)
- 관찰: 5/23·5/24 2일 연속 D-cycle 액션 ↔ 실제 실행 매칭 0건. 종환 출근 전 5시 기상 → 양치 → 출근. 데스크톱 파일 클릭 단계 부재. 발견 채널 결함.
- 근본: 자료가 있어도 안 보임 = 없음과 동일.
- 처방: Stop hook 종료 시 PowerShell MessageBox 자동 띄움 → 종환 1클릭 → MVP 열림.

검증 기준 (PostHook):
- 종환 OK 클릭 → ack 로그 1건/일 (auto_morning_ack.log)
- 클릭 없이 dismiss → no_action 로그 → 다음 cycle 강도 ↑
"""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(os.environ.get("HERMES_LOG_DIR", r"C:\Users\윤상택\.hermes\logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)

ACK_LOG = LOG_DIR / "auto_morning_ack.log"
RUN_LOG = LOG_DIR / "auto_morning_popup.log"
INTERNAL_LOG = LOG_DIR / "auto_morning_popup_debug.log"

VAULT_DAILY = Path(
    os.environ.get(
        "HERMES_VAULT_DAILY",
        r"C:\Users\윤상택\Desktop\작업\ObsidianVault\_SSOT\hermes_daily",
    )
)

MVP_PATH = Path(
    os.environ.get(
        "HERMES_MVP_PATH",
        r"C:\Users\윤상택\Desktop\HERMES\hermes_mvp.html",
    )
)

# 새벽 catch-up이 종료되었는지 식별하는 신호. Stop hook payload에 stop_reason
# 또는 transcript의 마지막 메시지에서 "catch-up 종료" 문구가 나타나면 발동.
CATCHUP_DONE_PATTERNS = (
    "catch-up 종료",
    "catch-up done",
    "새벽 catch-up 종료",
    "cycle_D_finished",
)

# 출근 전 1회만 발동하도록 윈도우. 한국시간 04:30~07:00.
ALLOWED_HOUR_RANGE = (4, 7)  # [start, end) — 04:30~07:00


logging.basicConfig(
    filename=INTERNAL_LOG,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
)


def in_allowed_window() -> bool:
    now = datetime.now()
    if now.hour < ALLOWED_HOUR_RANGE[0] or now.hour >= ALLOWED_HOUR_RANGE[1]:
        return False
    if now.hour == ALLOWED_HOUR_RANGE[0] and now.minute < 30:
        return False
    return True


def already_fired_today() -> bool:
    today = datetime.now().strftime("%Y-%m-%d")
    if not ACK_LOG.exists():
        return False
    return today in ACK_LOG.read_text(encoding="utf-8", errors="ignore")


def extract_today_p0() -> str:
    """오늘자 hermes_daily/ 노트에서 첫 줄 P0 액션을 뽑는다.

    실패 시 fallback 문구 반환.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    candidates = sorted(VAULT_DAILY.glob(f"{today}*.md"))
    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            logging.warning("read fail %s: %s", path, exc)
            continue
        # P0 표기 다음의 첫 의미 줄. 예: "## 🎯 P0: NCS 통화승수 1문제 풀기"
        match = re.search(r"P0[:：]\s*(.+)", text)
        if match:
            return match.group(1).strip()
        match = re.search(r"^##\s*[^\n]*P0[^\n]*\n(.+)", text, re.MULTILINE)
        if match:
            return match.group(1).strip()
    return "오늘 P0 액션 미확인 — vault hermes_daily/ 비어있음"


def catchup_finished(payload: dict) -> bool:
    reason = (payload.get("stop_reason") or "").lower()
    if reason in {"end_turn", "stop_sequence", "tool_use_stop"}:
        # transcript 본문 검사.
        transcript = payload.get("transcript_text") or ""
        if any(p.lower() in transcript.lower() for p in CATCHUP_DONE_PATTERNS):
            return True
        # transcript_path가 들어왔을 수도 있음.
        path = payload.get("transcript_path")
        if path:
            try:
                text = Path(path).read_text(encoding="utf-8", errors="ignore")
                return any(p.lower() in text.lower() for p in CATCHUP_DONE_PATTERNS)
            except OSError:
                return False
    return False


def show_message_box(p0_action: str) -> bool:
    """PowerShell MessageBox 띄우고 OK / Cancel 확인."""
    title = "Hermes — 오늘 1건"
    body = f"P0: {p0_action}\n\n[OK] → MVP 열기\n[Cancel] → 나중에"
    # OKCancel = 1, Information = 64
    script = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        f"[System.Windows.Forms.MessageBox]::Show("
        f"'{body.replace(chr(39), chr(39) + chr(39))}', "
        f"'{title}', 'OKCancel', 'Information')"
    )
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=600,  # 10분. 종환이 못 봐도 abandoned로 처리됨.
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        logging.error("messagebox fail: %s", exc)
        return False
    out = (result.stdout or "").strip()
    logging.info("messagebox result: %s", out)
    return out == "OK"


def open_mvp() -> None:
    if not MVP_PATH.exists():
        logging.warning("MVP_PATH not found: %s", MVP_PATH)
        return
    try:
        os.startfile(str(MVP_PATH))  # type: ignore[attr-defined]
    except OSError as exc:
        logging.error("startfile fail: %s", exc)


def log_ack(p0_action: str, ok: bool) -> None:
    ts = datetime.now().isoformat(timespec="seconds")
    line = f"{ts} | {'OK' if ok else 'DISMISS'} | {p0_action}\n"
    ACK_LOG.write_text(
        (ACK_LOG.read_text(encoding="utf-8") if ACK_LOG.exists() else "") + line,
        encoding="utf-8",
    )
    RUN_LOG.write_text(
        (RUN_LOG.read_text(encoding="utf-8") if RUN_LOG.exists() else "") + line,
        encoding="utf-8",
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    except json.JSONDecodeError as exc:
        logging.error("stdin parse fail: %s", exc)
        payload = {}

    if not in_allowed_window():
        logging.info("skip: outside allowed window")
        return 0

    if already_fired_today():
        logging.info("skip: already fired today")
        return 0

    if not catchup_finished(payload):
        logging.info("skip: catch-up not finished")
        return 0

    p0_action = extract_today_p0()
    ok = show_message_box(p0_action)
    log_ack(p0_action, ok)
    if ok:
        open_mvp()
    return 0


if __name__ == "__main__":
    sys.exit(main())
