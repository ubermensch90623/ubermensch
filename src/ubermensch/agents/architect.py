"""Architect agent with plan approval pattern."""

from __future__ import annotations

import logging

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class ArchitectAgent(BaseAgent):
    """아키텍처 설계 에이전트 (Plan Approval 패턴).

    구현 전에 먼저 계획을 수립하고, Lead의 승인을 받은 후에만
    실행하는 에이전트입니다. 복잡하거나 위험한 작업에 적합합니다.

    사용 패턴:
        1. execute() 호출 시 plan_only=True면 계획만 반환
        2. Lead가 계획을 검토하고 승인/거부
        3. 승인 후 plan_only=False로 다시 execute() 호출하여 구현
    """

    def __init__(
        self,
        name: str = "architect",
        model: str = "claude-sonnet-4-20250514",
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "You are an architecture and design agent. Your job is to:\n"
                "1. Analyze requirements and constraints\n"
                "2. Design system architecture and component structure\n"
                "3. Create implementation plans with clear phases\n"
                "4. Identify risks, trade-offs, and alternatives\n\n"
                "Always consider:\n"
                "- Scalability and extensibility\n"
                "- Separation of concerns\n"
                "- API boundaries and contracts\n"
                "- Data flow and state management\n"
                "- Error handling strategy\n"
                "- Testing strategy\n\n"
                "Respond in Korean."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        """아키텍처 분석 및 설계 계획을 수립합니다.

        context에 plan_only=True이면 계획만 반환합니다.
        approved_plan이 있으면 해당 계획의 상세 구현 가이드를 생성합니다.
        """
        plan_only = message.context.get("plan_only", True)
        approved_plan = message.context.get("approved_plan", "")
        constraints = message.context.get("constraints", "")
        existing_architecture = message.context.get("existing_architecture", "")

        if approved_plan:
            # 승인된 계획의 상세 구현 가이드 작성
            return await self._create_implementation_guide(message.task, approved_plan)

        # 계획 수립
        plan_prompt = f"Architecture task: {message.task}\n\n"

        if constraints:
            plan_prompt += f"Constraints:\n{constraints}\n\n"

        if existing_architecture:
            plan_prompt += f"Existing architecture:\n{existing_architecture}\n\n"

        if plan_only:
            plan_prompt += (
                "Create a detailed architecture plan. Include:\n"
                "1. Overview: high-level design description\n"
                "2. Components: each component's responsibility\n"
                "3. Interfaces: API contracts between components\n"
                "4. Data flow: how data moves through the system\n"
                "5. Phases: implementation phases with dependencies\n"
                "6. Risks: potential issues and mitigation strategies\n"
                "7. Alternatives: other approaches considered and why rejected\n\n"
                "This plan will be reviewed before implementation begins."
            )
        else:
            plan_prompt += (
                "Provide a comprehensive architecture analysis and design.\n"
                "Include component diagrams (text-based), interface definitions, "
                "and implementation recommendations."
            )

        analysis = await self.ask_llm(plan_prompt)

        return TaskResult(
            agent_name=self.name,
            status=TaskStatus.COMPLETED,
            data={
                "type": "plan" if plan_only else "analysis",
                "plan": analysis,
                "requires_approval": plan_only,
            },
        )

    async def _create_implementation_guide(
        self,
        task: str,
        approved_plan: str,
    ) -> TaskResult:
        """승인된 계획에 대한 상세 구현 가이드를 생성합니다."""
        prompt = (
            f"Task: {task}\n\n"
            f"Approved plan:\n{approved_plan}\n\n"
            "Create a detailed implementation guide based on this approved plan:\n"
            "1. File structure and module organization\n"
            "2. Class/function signatures for each component\n"
            "3. Step-by-step implementation order\n"
            "4. Key implementation details and gotchas\n"
            "5. Test plan for each component"
        )

        guide = await self.ask_llm(prompt)

        return TaskResult(
            agent_name=self.name,
            status=TaskStatus.COMPLETED,
            data={
                "type": "implementation_guide",
                "guide": guide,
                "requires_approval": False,
            },
        )
