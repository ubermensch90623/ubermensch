"""Subagent Orchestrator - spawns and manages subagents."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import anthropic

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class SubagentOrchestrator:
    """Main Agent: 서브에이전트를 생성하고 작업을 분배합니다.

    사용 패턴 (이미지의 Subagents 패턴):
        1. Main Agent가 사용자 요청을 분석
        2. 적절한 서브에이전트에게 작업 분배 (병렬)
        3. 각 서브에이전트가 독립적으로 작업 수행
        4. 결과를 수집하여 Main Agent가 종합
    """

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        system_prompt: str | None = None,
    ):
        self.model = model
        self.system_prompt = system_prompt or (
            "You are the main orchestrator agent. "
            "Analyze user requests, break them into subtasks, "
            "and synthesize results from subagents."
        )
        self._agents: dict[str, BaseAgent] = {}
        self._client: anthropic.AsyncAnthropic | None = None

    @property
    def client(self) -> anthropic.AsyncAnthropic:
        if self._client is None:
            self._client = anthropic.AsyncAnthropic()
        return self._client

    def register_agent(self, agent: BaseAgent) -> None:
        """서브에이전트를 등록합니다."""
        self._agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")

    def get_agent(self, name: str) -> BaseAgent | None:
        return self._agents.get(name)

    @property
    def agent_names(self) -> list[str]:
        return list(self._agents.keys())

    async def delegate(
        self,
        agent_name: str,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> TaskResult:
        """특정 서브에이전트에게 작업을 위임합니다."""
        agent = self._agents.get(agent_name)
        if agent is None:
            return TaskResult(
                agent_name=agent_name,
                status=TaskStatus.FAILED,
                error=f"Agent '{agent_name}' not found. Available: {self.agent_names}",
            )

        message = AgentMessage(task=task, context=context or {})
        return await agent.run(message)

    async def delegate_parallel(
        self,
        assignments: list[dict[str, Any]],
    ) -> list[TaskResult]:
        """여러 서브에이전트에게 동시에 작업을 위임합니다.

        Args:
            assignments: [{"agent": "name", "task": "...", "context": {...}}, ...]

        Returns:
            각 에이전트의 TaskResult 리스트
        """
        tasks = []
        for a in assignments:
            tasks.append(
                self.delegate(
                    agent_name=a["agent"],
                    task=a["task"],
                    context=a.get("context", {}),
                )
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 예외를 TaskResult로 변환
        final: list[TaskResult] = []
        for i, r in enumerate(results):
            if isinstance(r, BaseException):
                final.append(
                    TaskResult(
                        agent_name=assignments[i]["agent"],
                        status=TaskStatus.FAILED,
                        error=str(r),
                    )
                )
            else:
                final.append(r)
        return final

    async def run(self, user_request: str) -> str:
        """사용자 요청을 받아 전체 워크플로우를 실행합니다.

        1. LLM으로 요청을 분석하여 서브태스크로 분해
        2. 서브에이전트에게 병렬 위임
        3. 결과를 종합하여 최종 응답 생성
        """
        # Step 1: 요청 분석 및 작업 분배 계획
        agent_list = "\n".join(
            f"- {name}: {agent.system_prompt}" for name, agent in self._agents.items()
        )

        plan_prompt = (
            f"Available agents:\n{agent_list}\n\n"
            f"User request: {user_request}\n\n"
            "Break this request into subtasks and assign each to the most "
            "appropriate agent. Respond in this exact format:\n"
            "AGENT: <agent_name>\nTASK: <task description>\n\n"
            "Repeat for each subtask. Only use agents from the available list."
        )

        plan_response = await self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=self.system_prompt,
            messages=[{"role": "user", "content": plan_prompt}],
        )

        plan_text = "\n".join(block.text for block in plan_response.content if block.type == "text")

        # Step 2: 계획 파싱 및 병렬 실행
        assignments = self._parse_plan(plan_text)
        if not assignments:
            return f"No subtasks could be derived from the request: {user_request}"

        logger.info(f"Executing {len(assignments)} subtasks in parallel")
        results = await self.delegate_parallel(assignments)

        # Step 3: 결과 종합
        results_summary = "\n\n".join(
            f"[{r.agent_name}] ({'OK' if r.success else 'FAIL'})\n"
            f"{r.data if r.success else r.error}"
            for r in results
        )

        synthesis_prompt = (
            f"Original request: {user_request}\n\n"
            f"Subagent results:\n{results_summary}\n\n"
            "Synthesize these results into a comprehensive, well-organized response "
            "for the user. In Korean."
        )

        synthesis_response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self.system_prompt,
            messages=[{"role": "user", "content": synthesis_prompt}],
        )

        return "\n".join(block.text for block in synthesis_response.content if block.type == "text")

    @staticmethod
    def _parse_plan(plan_text: str) -> list[dict[str, Any]]:
        """LLM의 계획 응답을 파싱합니다."""
        assignments: list[dict[str, Any]] = []
        lines = plan_text.strip().split("\n")

        current_agent = None
        for line in lines:
            line = line.strip()
            if line.upper().startswith("AGENT:"):
                current_agent = line.split(":", 1)[1].strip()
            elif line.upper().startswith("TASK:") and current_agent:
                task = line.split(":", 1)[1].strip()
                assignments.append({"agent": current_agent, "task": task})
                current_agent = None

        return assignments
