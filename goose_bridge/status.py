"""Goose 상태 확인 모듈.

Goose 설치 상태, 버전, 설정된 LLM 제공자 등을 확인합니다.

사용 예:
    python -m goose_bridge.status
"""

import json
import subprocess
import sys

from goose_bridge.runner import find_goose, list_recipes


def get_goose_status() -> dict:
    """Goose 시스템 상태를 확인합니다.

    Returns:
        {
            "installed": bool,
            "version": str,
            "goose_path": str,
            "recipes_count": int,
            "recipes": list[dict],
            "error": str | None,
        }
    """
    status = {
        "installed": False,
        "version": "",
        "goose_path": "",
        "recipes_count": 0,
        "recipes": [],
        "error": None,
    }

    goose_bin = find_goose()
    if goose_bin is None:
        status["error"] = "Goose가 설치되어 있지 않습니다."
        return status

    status["installed"] = True
    status["goose_path"] = goose_bin

    # 버전 확인
    try:
        result = subprocess.run(
            [goose_bin, "version"], capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            status["version"] = result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # 레시피 목록
    recipes = list_recipes()
    status["recipes"] = recipes
    status["recipes_count"] = len(recipes)

    return status


def format_status_korean(status: dict) -> str:
    """상태를 한국어로 포맷합니다."""
    lines = []

    if not status["installed"]:
        return "Goose가 아직 설치되지 않았습니다. 'Goose 설치해줘'라고 말씀해 주세요."

    lines.append("=== Goose AI 에이전트 상태 ===")
    lines.append("")
    lines.append(f"상태: 설치됨")

    if status["version"]:
        lines.append(f"버전: {status['version']}")

    lines.append(f"실행 파일: {status['goose_path']}")

    if status["recipes"]:
        lines.append(f"\n사용 가능한 레시피 ({status['recipes_count']}개):")
        for r in status["recipes"]:
            title = r.get("title", r["name"])
            lines.append(f"  - {title}")

    return "\n".join(lines)


if __name__ == "__main__":
    status = get_goose_status()
    print(format_status_korean(status))
