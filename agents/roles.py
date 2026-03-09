"""사전 정의된 에이전트 역할들"""

from config.settings import AgentConfig


# === 기본 에이전트 역할 프리셋 ===

ARCHITECT = AgentConfig(
    name="설계자",
    role="시스템 아키텍트",
    perspective=(
        "전체 시스템의 구조와 설계에 집중한다. "
        "확장성, 유지보수성, 모듈화를 중시한다. "
        "큰 그림을 보고 각 부분이 어떻게 맞물리는지 분석한다."
    ),
    temperature=0.6,
)

CRITIC = AgentConfig(
    name="비평가",
    role="품질 비평가",
    perspective=(
        "제안의 약점과 위험요소를 찾는 데 집중한다. "
        "엣지 케이스, 보안 취약점, 성능 문제를 지적한다. "
        "건설적 비판을 통해 품질을 높인다."
    ),
    temperature=0.5,
)

IMPLEMENTER = AgentConfig(
    name="구현자",
    role="실행 전문가",
    perspective=(
        "실제 구현 가능성과 실용성에 집중한다. "
        "코드 품질, 테스트 가능성, 배포 용이성을 중시한다. "
        "이론보다 실전에서 동작하는 해결책을 선호한다."
    ),
    temperature=0.7,
)

REVIEWER = AgentConfig(
    name="검토자",
    role="최종 검토자",
    perspective=(
        "전체 토론을 종합하고 균형 잡힌 결론을 도출한다. "
        "각 에이전트의 의견을 공정하게 평가한다. "
        "최종 결과물의 완성도와 일관성을 확인한다."
    ),
    temperature=0.4,
)

CREATIVE = AgentConfig(
    name="창의자",
    role="창의적 사고가",
    perspective=(
        "기존 틀을 벗어난 새로운 접근법을 제시한다. "
        "다른 에이전트들이 놓친 가능성을 탐색한다. "
        "혁신적이고 독창적인 해결책을 추구한다."
    ),
    temperature=0.9,
)

USER_ADVOCATE = AgentConfig(
    name="사용자대변인",
    role="사용자 관점 대변인",
    perspective=(
        "최종 사용자의 입장에서 생각한다. "
        "사용성, 접근성, 사용자 경험을 최우선으로 본다. "
        "기술적 우수성보다 사용자 만족도를 중시한다."
    ),
    temperature=0.6,
)

# 역할 프리셋 레지스트리
ROLE_PRESETS = {
    "architect": ARCHITECT,
    "critic": CRITIC,
    "implementer": IMPLEMENTER,
    "reviewer": REVIEWER,
    "creative": CREATIVE,
    "user_advocate": USER_ADVOCATE,
}


def get_default_team() -> list[AgentConfig]:
    """기본 토론 팀 구성 (4명)"""
    return [ARCHITECT, CRITIC, IMPLEMENTER, REVIEWER]


def get_full_team() -> list[AgentConfig]:
    """전체 팀 구성 (6명)"""
    return list(ROLE_PRESETS.values())
