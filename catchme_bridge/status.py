"""CatchMe 상태 집계 모듈.

RAM, 디스크 사용량, LLM 비용 등 CatchMe 시스템 상태를 조회합니다.

사용 예:
    python catchme_bridge/status.py
"""

import json
import re
import sys
from subprocess import TimeoutExpired

from catchme_bridge.config import run_catchme_cmd, is_catchme_installed


def get_status() -> dict:
    """CatchMe 시스템 상태를 수집합니다.

    Returns:
        {
            "installed": bool,
            "running": bool,
            "ram_info": str,
            "disk_info": str,
            "cost_info": str,
            "error": str | None,
        }
    """
    status = {
        "installed": False,
        "running": False,
        "ram_info": "",
        "disk_info": "",
        "cost_info": "",
        "error": None,
    }

    if not is_catchme_installed():
        status["error"] = "CatchMe가 설치되어 있지 않습니다."
        return status

    status["installed"] = True

    # RAM 사용량
    try:
        result = run_catchme_cmd(["ram"], timeout=10)
        if result.returncode == 0:
            status["ram_info"] = result.stdout.strip()
            status["running"] = bool(result.stdout.strip())
    except (TimeoutExpired, RuntimeError):
        pass

    # 디스크 사용량
    try:
        result = run_catchme_cmd(["disk"], timeout=10)
        if result.returncode == 0:
            status["disk_info"] = result.stdout.strip()
    except (TimeoutExpired, RuntimeError):
        pass

    # LLM 비용
    try:
        result = run_catchme_cmd(["cost"], timeout=10)
        if result.returncode == 0:
            status["cost_info"] = result.stdout.strip()
    except (TimeoutExpired, RuntimeError):
        pass

    return status


def format_status_korean(status: dict) -> str:
    """상태 정보를 한국어로 읽기 쉽게 포맷합니다."""
    lines = []

    if not status["installed"]:
        return "CatchMe가 아직 설치되지 않았습니다. 'CatchMe 설치해줘'라고 말씀해 주세요."

    lines.append("=== CatchMe 상태 ===")
    lines.append("")

    # 실행 상태
    if status["running"]:
        lines.append("상태: 실행 중")
    else:
        lines.append("상태: 중지됨")

    # RAM
    if status["ram_info"]:
        lines.append(f"\n메모리 사용량:\n{status['ram_info']}")

    # 디스크
    if status["disk_info"]:
        lines.append(f"\n저장 공간:\n{status['disk_info']}")

    # 비용
    if status["cost_info"]:
        lines.append(f"\nLLM 비용:\n{status['cost_info']}")

    if status["error"]:
        lines.append(f"\n참고: {status['error']}")

    return "\n".join(lines)


if __name__ == "__main__":
    status = get_status()
    print(format_status_korean(status))
