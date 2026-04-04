"""CatchMe 설정 관리 모듈."""

import json
import shutil
import subprocess
from pathlib import Path

DEFAULT_CONFIG_DIR = Path.home() / ".catchme"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.json"


def _find_catchme_bin() -> str | None:
    """catchme 실행 파일 경로를 찾습니다."""
    # 1. 시스템 PATH에서 직접 찾기
    path = shutil.which("catchme")
    if path:
        return path

    # 2. conda 환경에서 찾기
    try:
        result = subprocess.run(
            ["conda", "run", "-n", "catchme", "which", "catchme"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None


def is_catchme_installed() -> bool:
    """CatchMe가 설치되어 있는지 확인합니다."""
    return _find_catchme_bin() is not None


def run_catchme_cmd(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    """CatchMe CLI 명령을 실행합니다.

    직접 실행을 시도하고, 실패하면 conda 환경에서 실행합니다.

    Args:
        args: catchme 뒤에 붙는 인자 목록 (예: ["ask", "--", "질문"])
        timeout: 타임아웃 (초)

    Returns:
        subprocess.CompletedProcess

    Raises:
        RuntimeError: CatchMe가 설치되지 않은 경우
    """
    # 1. 직접 실행 시도
    catchme_bin = _find_catchme_bin()
    if catchme_bin:
        try:
            cmd = [catchme_bin] + args
            return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    # 2. conda 환경에서 시도
    try:
        cmd = ["conda", "run", "-n", "catchme", "catchme"] + args
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        pass

    raise RuntimeError(
        "CatchMe가 설치되어 있지 않습니다. "
        "'CatchMe 설치해줘'라고 말씀해 주세요."
    )


def get_catchme_config() -> dict:
    """현재 CatchMe 설정을 읽어 반환합니다."""
    if not DEFAULT_CONFIG_PATH.exists():
        return {}
    with open(DEFAULT_CONFIG_PATH) as f:
        return json.load(f)


def update_catchme_config(updates: dict) -> None:
    """CatchMe 설정을 업데이트합니다."""
    config = get_catchme_config()

    for key, value in updates.items():
        if isinstance(value, dict) and key in config and isinstance(config[key], dict):
            config[key].update(value)
        else:
            config[key] = value

    DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(DEFAULT_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
