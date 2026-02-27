"""업데이트팀 (CTO 산하) - 연구 결과를 시스템에 반영."""

from __future__ import annotations

import logging

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class StrategyUpdaterAgent(BaseAgent):
    """전략 업데이터 (팀장) - 연구팀 전략 보고서를 학습 계획에 반영.

    Input: 전략 보고서
    Output: 업데이트된 학습 전략
    """

    def __init__(
        self, name: str = "strategy_updater", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 업데이트팀 팀장 '전략 업데이터'입니다.\n"
                "역할:\n"
                "- 연구팀의 전략 보고서를 실제 학습 계획에 반영\n"
                "- 우선순위 조정 및 학습 방향 수정\n"
                "- 변경 사항의 영향 범위 분석\n"
                "- 팀원(시스템 패치관, 교재 갱신관) 조율\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"전략 업데이트 요청: {message.task}\n\n"
            f"연구 보고서: {context.get('research_report', '')}\n"
            f"현재 학습 전략: {context.get('current_strategy', '')}\n\n"
            "연구 결과를 반영하여 학습 전략 업데이트 계획을 수립해주세요.\n"
            "변경 사항, 영향 범위, 실행 일정을 포함해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class SystemPatcherAgent(BaseAgent):
    """시스템 패치관 - 새 AI 도구/기술을 기존 파이프라인에 통합.

    Input: 기술 업데이트 제안서
    Output: 시스템 패치 + 마이그레이션
    """

    def __init__(
        self, name: str = "system_patcher", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 업데이트팀 '시스템 패치관'입니다.\n"
                "역할:\n"
                "- 새로운 AI 도구/기술을 기존 파이프라인에 통합\n"
                "- 시스템 패치 계획 수립 및 실행\n"
                "- 마이그레이션 계획 작성\n"
                "- 롤백 계획 사전 준비\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"시스템 패치 요청: {message.task}\n\n"
            f"업데이트 제안: {context.get('update_proposal', '')}\n"
            f"현재 시스템: {context.get('current_system', '')}\n\n"
            "시스템 패치 계획을 수립해주세요.\n"
            "통합 방법, 마이그레이션 절차, 롤백 계획을 포함해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class ContentUpdaterAgent(BaseAgent):
    """교재 갱신관 - 출제 트렌드에 맞춰 학습 자료/퀴즈 DB 업데이트.

    Input: 트렌드 리포트 + 기존 DB
    Output: 갱신된 학습 자료
    """

    def __init__(
        self, name: str = "content_updater", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 업데이트팀 '교재 갱신관'입니다.\n"
                "역할:\n"
                "- 출제 트렌드에 맞춰 학습 자료 업데이트\n"
                "- 퀴즈 DB에 새로운 유형 문제 추가\n"
                "- 더 이상 출제되지 않는 유형 비중 축소\n"
                "- 학습 자료 품질 유지\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"교재 갱신 요청: {message.task}\n\n"
            f"트렌드 리포트: {context.get('trend_report', '')}\n"
            f"현재 학습 자료 현황: {context.get('current_materials', '')}\n\n"
            "학습 자료 갱신 계획을 수립해주세요.\n"
            "추가할 콘텐츠, 수정할 콘텐츠, 비중 조정 사항을 포함해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class UpdateRedTeamAgent(BaseAgent):
    """호환성 검증관 (레드팀) - 업데이트가 기존 시스템과 충돌하는지 체크.

    Input: 모든 업데이트 작업
    Output: 호환성 판정 + 롤백 계획
    """

    def __init__(
        self, name: str = "update_redteam", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 업데이트팀 레드팀 '호환성 검증관'입니다.\n"
                "역할:\n"
                "- 모든 업데이트 작업의 호환성 검증 (품질 게이트)\n"
                "- 기존 시스템과의 충돌 탐지\n"
                "- 데이터 손실 위험 체크\n"
                "- 문제 발견 시 롤백 계획 제시\n\n"
                "판정: COMPATIBLE(호환) / CONFLICT(충돌) / RISKY(위험)\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"업데이트 호환성 검증 요청:\n"
            f"업데이트 내용: {message.task}\n\n"
            f"현재 시스템 상태: {context.get('current_state', '')}\n"
            f"영향 받는 컴포넌트: {context.get('affected_components', [])}\n\n"
            "호환성을 검증해주세요:\n"
            "1. 기존 시스템과 충돌하는 부분이 있는가?\n"
            "2. 데이터 손실 위험이 있는가?\n"
            "3. 롤백이 필요한 경우 어떻게 할 것인가?\n\n"
            "판정: COMPATIBLE / CONFLICT / RISKY 중 하나와 근거를 제시해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )
