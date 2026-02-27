"""채용팀 (CEO 직속) - 조직 역량 강화."""

from __future__ import annotations

import logging

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class RecruiterAgent(BaseAgent):
    """채용관 (팀장) - 능력 갭 분석 -> 새 에이전트 설계 -> 시범 운영.

    Input: TF 결과 보고서, 에이전트 성과 데이터, 사용자 요구
    Output: 신규 에이전트 설계서 + 배치 권고
    """

    def __init__(
        self, name: str = "recruiter", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 채용팀 팀장 '채용관'입니다.\n"
                "역할:\n"
                "- 조직의 능력 갭 분석\n"
                "- 새 에이전트의 Role/Goal/Backstory 설계\n"
                "- Input/Output 정의\n"
                "- 시범 운영 계획 수립\n"
                "- 정식 배치 또는 폐기 결정\n\n"
                "채용 프로세스:\n"
                "1. 갭 발견 -> 2. 기존 재활용 검토 -> 3. 신규 설계\n"
                "-> 4. 시범 운영 (1주일) -> 5. 정식 배치 or 폐기\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"채용 검토 요청: {message.task}\n\n"
            f"능력 갭: {context.get('capability_gap', '')}\n"
            f"현재 에이전트 목록: {context.get('current_agents', [])}\n"
            f"TF 결과: {context.get('tf_result', '')}\n\n"
            "새 에이전트 설계서를 작성해주세요.\n"
            "Role, Goal, Backstory, Input, Output, KPI를 포함해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class CapabilityEvaluatorAgent(BaseAgent):
    """역량 평가관 - 기존 에이전트 성과 평가, 역할 중복/공백 식별.

    Input: 전사 성과 데이터 + 에이전트별 활동 로그
    Output: 역량 갭 보고서 + 조직 최적화 제안
    """

    def __init__(
        self,
        name: str = "capability_evaluator",
        model: str = "claude-sonnet-4-20250514",
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 채용팀 '역량 평가관'입니다.\n"
                "역할:\n"
                "- 기존 에이전트의 성과 평가\n"
                "- 역할 중복 식별 및 통합 제안\n"
                "- 역할 공백 식별 및 충원 권고\n"
                "- 조직 효율성 분석\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"역량 평가 요청: {message.task}\n\n"
            f"에이전트 성과 데이터: {context.get('performance_data', {})}\n"
            f"활동 로그: {context.get('activity_log', [])}\n"
            f"조직 구조: {context.get('org_structure', '')}\n\n"
            "역량 갭 분석 보고서를 작성해주세요.\n"
            "중복 역할, 공백 역할, 조직 최적화 제안을 포함해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class RecruitmentRedTeamAgent(BaseAgent):
    """조직 비대화 검증관 (레드팀) - 불필요한 채용 방지.

    Input: 신규 에이전트 설계서
    Output: 채용 필요성 판정 (필요/기존 재활용/불필요)
    """

    def __init__(
        self,
        name: str = "recruitment_redteam",
        model: str = "claude-sonnet-4-20250514",
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 채용팀 레드팀 '조직 비대화 검증관'입니다.\n"
                "역할:\n"
                "- 신규 에이전트 채용의 필요성 검증 (품질 게이트)\n"
                "- '이 에이전트 진짜 필요해?' 관점에서 검토\n"
                "- 기존 에이전트 역할 확장으로 해결 가능한지 먼저 검토\n"
                "- 불필요한 조직 비대화 경고\n\n"
                "판정:\n"
                "- NEEDED: 신규 채용 필요\n"
                "- REUSE: 기존 에이전트 재활용 가능\n"
                "- UNNECESSARY: 불필요한 채용\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"채용 필요성 검증 요청:\n"
            f"신규 에이전트 설계서: {message.task}\n\n"
            f"기존 에이전트 역량: {context.get('existing_capabilities', [])}\n"
            f"요청 사유: {context.get('reason', '')}\n\n"
            "채용 필요성을 검증해주세요:\n"
            "1. 기존 에이전트의 역할 확장으로 해결 가능한가?\n"
            "2. 유사한 역할의 에이전트가 이미 있지 않은가?\n"
            "3. 이 에이전트가 실제로 가치를 만들어낼 수 있는가?\n"
            "4. 조직 복잡도 증가 대비 기대 효과가 충분한가?\n\n"
            "판정: NEEDED / REUSE / UNNECESSARY 중 하나와 근거를 제시해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )
