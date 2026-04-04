"""Goose 레시피 실행 및 세션 관리 모듈.

Goose CLI를 사용하여 레시피를 실행하거나 대화 세션을 관리합니다.

사용 예:
    python -m goose_bridge.runner recipe ncs-study-assistant --subject 수리 --count 5
    python -m goose_bridge.runner session my-study
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

RECIPES_DIR = Path(__file__).parent.parent / "recipes"


def find_goose() -> str | None:
    """Goose 실행 파일 경로를 찾습니다."""
    # shutil.which로 PATH 탐색
    path = shutil.which("goose")
    if path:
        return path

    # 일반적인 설치 위치 확인
    candidates = [
        Path.home() / ".local" / "bin" / "goose",
        Path.home() / ".goose" / "bin" / "goose",
        Path("/usr/local/bin/goose"),
    ]
    for path in candidates:
        if path.exists():
            return str(path)
    return None


def is_goose_installed() -> bool:
    """Goose가 설치되어 있는지 확인합니다."""
    return find_goose() is not None


def run_recipe(
    recipe_name: str,
    params: dict | None = None,
    timeout: int = 600,
) -> dict:
    """Goose 레시피를 실행합니다.

    Args:
        recipe_name: 레시피 파일명 (확장자 없이) 또는 전체 경로
        params: 레시피 파라미터 (key-value)
        timeout: 실행 타임아웃 (초)

    Returns:
        {"output": str, "error": str | None, "returncode": int}
    """
    goose_bin = find_goose()
    if goose_bin is None:
        return {
            "output": "",
            "error": "Goose가 설치되어 있지 않습니다. 'Goose 설치해줘'라고 말씀해 주세요.",
            "returncode": -1,
        }

    # 레시피 파일 경로 결정
    recipe_path = Path(recipe_name)
    if not recipe_path.exists():
        recipe_path = RECIPES_DIR / f"{recipe_name}.yaml"
    if not recipe_path.exists():
        return {
            "output": "",
            "error": f"레시피 파일을 찾을 수 없습니다: {recipe_name}",
            "returncode": -1,
        }

    cmd = [goose_bin, "run", "--recipe", str(recipe_path)]

    # 파라미터 추가
    if params:
        for key, value in params.items():
            cmd.extend(["--param", f"{key}={value}"])

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
        )
        return {
            "output": result.stdout.strip(),
            "error": result.stderr.strip() if result.returncode != 0 else None,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "output": "",
            "error": f"레시피 실행 시간 초과 ({timeout}초)",
            "returncode": -1,
        }


def start_session(
    name: str | None = None,
    resume: bool = False,
    extensions: list[str] | None = None,
) -> dict:
    """Goose 대화 세션을 시작합니다.

    Args:
        name: 세션 이름
        resume: 이전 세션 이어가기
        extensions: 추가 MCP 확장 목록

    Returns:
        {"command": str, "error": str | None}
        (세션은 대화형이므로 명령어만 반환)
    """
    goose_bin = find_goose()
    if goose_bin is None:
        return {
            "command": "",
            "error": "Goose가 설치되어 있지 않습니다.",
        }

    cmd_parts = [goose_bin, "session"]
    if name:
        cmd_parts.extend(["-n", name])
    if resume:
        cmd_parts.append("--resume")
    if extensions:
        for ext in extensions:
            cmd_parts.extend(["--with-extension", ext])

    return {"command": " ".join(cmd_parts), "error": None}


def list_recipes() -> list[dict]:
    """사용 가능한 레시피 목록을 반환합니다."""
    recipes = []
    if not RECIPES_DIR.exists():
        return recipes

    for yaml_file in sorted(RECIPES_DIR.glob("*.yaml")):
        info = {"name": yaml_file.stem, "path": str(yaml_file)}

        # YAML에서 title과 description 추출 (경량 파싱)
        with open(yaml_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("title:"):
                    info["title"] = line.split(":", 1)[1].strip()
                elif line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip()
                    if desc.startswith(">"):
                        desc = ""
                    info["description"] = desc
                if "title" in info and "description" in info:
                    break

        recipes.append(info)
    return recipes


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "사용법: python -m goose_bridge.runner <recipe|session|list> [인자...]"}, ensure_ascii=False))
        sys.exit(1)

    action = sys.argv[1]

    if action == "list":
        recipes = list_recipes()
        for r in recipes:
            print(f"  {r['name']}: {r.get('title', '(제목 없음)')}")

    elif action == "recipe":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "레시피 이름을 입력하세요."}, ensure_ascii=False))
            sys.exit(1)
        recipe_name = sys.argv[2]
        params = {}
        for arg in sys.argv[3:]:
            if arg.startswith("--") and "=" not in arg and sys.argv.index(arg) + 1 < len(sys.argv):
                continue
            if "=" in arg:
                k, v = arg.split("=", 1)
                params[k.lstrip("-")] = v
        result = run_recipe(recipe_name, params)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif action == "session":
        name = sys.argv[2] if len(sys.argv) > 2 else None
        result = start_session(name=name)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(json.dumps({"error": f"알 수 없는 명령: {action}"}, ensure_ascii=False))
