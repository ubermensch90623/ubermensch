"""CatchMe AI 메모리 시스템 연동 모듈.

CatchMe CLI를 subprocess로 호출하여 활동 기록 조회, 상태 확인,
NCS 학습 추천 기능을 제공합니다.
"""

from catchme_bridge.ask import ask_catchme
from catchme_bridge.status import get_status, format_status_korean
from catchme_bridge.study import get_study_recommendation

__all__ = ["ask_catchme", "get_status", "format_status_korean", "get_study_recommendation"]
