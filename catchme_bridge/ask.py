"""CatchMe 자연어 질의 모듈.

CatchMe의 트리 기반 검색을 사용하여 사용자의 활동 기록을 자연어로 조회합니다.

사용 예:
    python catchme_bridge/ask.py "오늘 뭐 했어?"
    python catchme_bridge/ask.py "최근 NCS 공부 활동 요약"
"""

import json
import sys
from subprocess import TimeoutExpired

from catchme_bridge.config import run_catchme_cmd, is_catchme_installed


def ask_catchme(question: str, timeout: int = 120) -> dict:
    """CatchMe에 자연어 질문을 보내고 답변을 받습니다.

    Args:
        question: 자연어 질문 (예: "오늘 뭐 했어?")
        timeout: 응답 대기 시간 (초)

    Returns:
        {"answer": str, "error": str | None}
    """
    if not is_catchme_installed():
        return {
            "answer": None,
            "error": "CatchMe가 설치되어 있지 않습니다. 'CatchMe 설치해줘'라고 말씀해 주세요.",
        }

    try:
        result = run_catchme_cmd(["ask", "--", question], timeout=timeout)

        if result.returncode == 0:
            output = result.stdout.strip()
            if not output:
                return {
                    "answer": "기록이 아직 없습니다. CatchMe를 먼저 시작해 주세요.",
                    "error": None,
                }
            return {"answer": output, "error": None}
        else:
            stderr = result.stderr.strip()
            if "not running" in stderr.lower() or "no data" in stderr.lower():
                return {
                    "answer": None,
                    "error": "CatchMe가 실행 중이 아닙니다. 'CatchMe 켜줘'라고 말씀해 주세요.",
                }
            return {"answer": None, "error": f"CatchMe 오류: {stderr[:200]}"}

    except TimeoutExpired:
        return {
            "answer": None,
            "error": f"CatchMe 응답 시간 초과 ({timeout}초). LLM 제공자를 확인해 주세요.",
        }
    except RuntimeError as e:
        return {"answer": None, "error": str(e)}


def search_catchme(keyword: str) -> dict:
    """CatchMe에서 키워드로 빠른 검색을 합니다.

    Args:
        keyword: 검색할 키워드

    Returns:
        {"results": list[str], "error": str | None}
    """
    if not is_catchme_installed():
        return {"results": [], "error": "CatchMe가 설치되어 있지 않습니다."}

    try:
        result = run_catchme_cmd(["ask", "--", f"'{keyword}' 관련 활동 찾기"], timeout=60)
        if result.returncode == 0 and result.stdout.strip():
            lines = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
            return {"results": lines, "error": None}
        return {"results": [], "error": None}
    except (TimeoutExpired, RuntimeError) as e:
        return {"results": [], "error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "질문을 입력하세요. 예: python ask.py '오늘 뭐 했어?'"}, ensure_ascii=False))
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    result = ask_catchme(question)
    print(json.dumps(result, ensure_ascii=False, indent=2))
