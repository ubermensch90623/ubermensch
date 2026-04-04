"""Goose AI 에이전트 연동 모듈.

Block의 Goose를 통해 레시피 실행, 세션 관리, NCS 학습 자동화를 제공합니다.
"""

from goose_bridge.runner import run_recipe, start_session
from goose_bridge.status import get_goose_status

__all__ = ["run_recipe", "start_session", "get_goose_status"]
