"""CatchMe 설정 관리 모듈."""

import json
import subprocess
from pathlib import Path

CONDA_ENV = "catchme"
DEFAULT_CONFIG_DIR = Path.home() / ".catchme"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.json"


def get_catchme_env() -> str | None:
    """CatchMe가 설치된 conda 환경 이름을 반환합니다.

    Returns:
        conda env 이름 (문자열) 또는 None (미설치 시)
    """
    try:
        result = subprocess.run(
            ["conda", "run", "-n", CONDA_ENV, "catchme", "--help"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            return CONDA_ENV
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def is_catchme_installed() -> bool:
    """CatchMe가 설치되어 있는지 확인합니다."""
    return get_catchme_env() is not None


def run_catchme_cmd(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    """CatchMe CLI 명령을 conda 환경에서 실행합니다.

    Args:
        args: catchme 뒤에 붙는 인자 목록 (예: ["ask", "--", "질문"])
        timeout: 타임아웃 (초)

    Returns:
        subprocess.CompletedProcess

    Raises:
        RuntimeError: CatchMe가 설치되지 않은 경우
    """
    env_name = get_catchme_env()
    if env_name is None:
        raise RuntimeError(
            "CatchMe가 설치되어 있지 않습니다. "
            "'bash scripts/setup-catchme.sh'를 실행하세요."
        )

    cmd = ["conda", "run", "-n", env_name, "catchme"] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def get_catchme_config() -> dict:
    """현재 CatchMe 설정을 읽어 반환합니다."""
    if not DEFAULT_CONFIG_PATH.exists():
        return {}
    with open(DEFAULT_CONFIG_PATH) as f:
        return json.load(f)


def update_catchme_config(updates: dict) -> None:
    """CatchMe 설정을 업데이트합니다.

    Args:
        updates: 업데이트할 키-값 쌍 (중첩 dict 지원)
    """
    config = get_catchme_config()

    for key, value in updates.items():
        if isinstance(value, dict) and key in config and isinstance(config[key], dict):
            config[key].update(value)
        else:
            config[key] = value

    DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(DEFAULT_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
