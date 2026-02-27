"""Agent Team - team creation, coordination, and lifecycle management."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import anthropic

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.hooks import HookEvent, HookRegistry, HookType
from ubermensch.core.mailbox import Mailbox
from ubermensch.core.message import (
    AgentMessage,
    PlanApproval,
    SharedTask,
    TaskResult,
    TaskStatus,
    TeamMessage,
)
from ubermensch.core.shared_task_list import SharedTaskList

logger = logging.getLogger(__name__)


class AgentTeam:
    """에이전트 팀 관리 클래스.

    구성:
        - TeamLead: 팀 조율 (이 클래스 내에서 역할 수행)
        - Teammates: 독립 에이전트들
        - SharedTaskList: 공유 태스크 리스트
        - Mailbox: 에이전트 간 메시징

    Claude Code의 Agent Teams 패턴을 프로그래밍 방식으로 구현합니다.
    """

    def __init__(
        self,
        name: str,
        model: str = "claude-sonnet-4-20250514",
    ) -> None:
        self.name = name
        self.model = model
        self.task_list = SharedTaskList()
        self.mailbox = Mailbox()
        self.hooks = HookRegistry()
        self._teammates: dict[str, BaseAgent] = {}
        self._client: anthropic.AsyncAnthropic | None = None
        self._running_tasks: dict[str, asyncio.Task[Any]] = {}

        # Lead 를 메일박스에 등록
        self.mailbox.register("lead")

    @property
    def client(self) -> anthropic.AsyncAnthropic:
        if self._client is None:
            self._client = anthropic.AsyncAnthropic()
        return self._client

    # --- 팀원 관리 ---

    async def _emit(self, event: HookEvent) -> None:
        """훅 이벤트를 발생시킵니다 (에러 무시)."""
        event.team_name = self.name
        await self.hooks.emit(event)

    def spawn_teammate(self, agent: BaseAgent) -> None:
        """에이전트를 팀에 추가합니다."""
        self._teammates[agent.name] = agent
        self.mailbox.register(agent.name)
        # 에이전트에게 팀 인프라 참조 전달
        agent._team_mailbox = self.mailbox
        agent._team_task_list = self.task_list
        logger.info(f"[{self.name}] Spawned teammate: {agent.name}")

    def shutdown_teammate(self, name: str) -> None:
        """에이전트를 팀에서 제거합니다."""
        agent = self._teammates.pop(name, None)
        if agent:
            self.mailbox.unregister(name)
            # 실행 중인 작업 취소
            running = self._running_tasks.pop(name, None)
            if running and not running.done():
                running.cancel()
            logger.info(f"[{self.name}] Shutdown teammate: {name}")

    @property
    def teammate_names(self) -> list[str]:
        return list(self._teammates.keys())

    def get_teammate(self, name: str) -> BaseAgent | None:
        return self._teammates.get(name)

    # --- 태스크 분배 ---

    async def create_tasks(
        self,
        tasks: list[dict[str, Any]],
    ) -> list[SharedTask]:
        """태스크를 생성하고 태스크 리스트에 추가합니다."""
        return await self.task_list.add_tasks(tasks, created_by="lead")

    async def assign_task(self, task_id: str, agent_name: str) -> bool:
        """특정 태스크를 특정 에이전트에게 할당합니다."""
        return await self.task_list.claim_task(task_id, agent_name)

    # --- 팀 실행 ---

    async def run_team(
        self,
        user_request: str,
        auto_plan: bool = True,
    ) -> dict[str, Any]:
        """팀 전체 워크플로우를 실행합니다.

        1. LLM으로 요청 분석 → 태스크 생성
        2. 팀원에게 태스크 분배 (자동 claim)
        3. 병렬 실행 + 메시지 교환
        4. 결과 종합

        Args:
            user_request: 사용자 요청
            auto_plan: True면 LLM으로 자동 태스크 분해

        Returns:
            {"synthesis": str, "results": list[TaskResult], "messages": list}
        """
        # Step 1: 태스크 계획
        if auto_plan:
            await self._plan_tasks(user_request)

        if not self.task_list.all_tasks:
            return {
                "synthesis": "No tasks were created for the request.",
                "results": [],
                "messages": [],
            }

        # Step 2: 팀원별 워커 실행
        results: list[TaskResult] = []
        workers = []
        for name, agent in self._teammates.items():
            worker = asyncio.create_task(
                self._agent_worker(agent), name=f"worker-{name}"
            )
            self._running_tasks[name] = worker
            workers.append(worker)

        # Step 3: 모든 태스크 완료 대기
        done = await self.task_list.wait_all_done(timeout=300)
        if not done:
            logger.warning(f"[{self.name}] Timed out waiting for tasks")

        # 워커들 정리
        for w in workers:
            if not w.done():
                w.cancel()
        await asyncio.gather(*workers, return_exceptions=True)

        # 결과 수집
        for task in self.task_list.all_tasks:
            results.append(
                TaskResult(
                    agent_name=task.assigned_to or "unassigned",
                    status=task.status,
                    data=task.result,
                    error=task.error,
                )
            )

        # Step 4: Lead 메일 수거
        lead_messages = self.mailbox.drain("lead")

        # Step 5: 결과 종합
        synthesis = await self._synthesize(user_request, results, lead_messages)

        return {
            "synthesis": synthesis,
            "results": results,
            "messages": lead_messages,
        }

    async def _agent_worker(self, agent: BaseAgent) -> None:
        """개별 에이전트 워커: 태스크를 자동 claim하고 실행합니다."""
        while True:
            # 대기 메시지 처리
            await self._process_agent_mail(agent)

            # 다음 태스크 claim
            task = await self.task_list.claim_next(agent.name)
            if task is None:
                # 남은 태스크가 있으면 잠시 대기 후 재시도
                if not self.task_list.all_done:
                    # TeammateIdle 훅 발생
                    await self._emit(HookEvent(
                        type=HookType.TEAMMATE_IDLE,
                        agent_name=agent.name,
                    ))
                    await asyncio.sleep(0.5)
                    continue
                break

            # 태스크 실행
            message = AgentMessage(
                task=task.description or task.title,
                context={"task_id": task.id, "task_title": task.title},
                priority=task.priority,
            )

            result = await agent.run(message)

            if result.success:
                await self.task_list.complete_task(task.id, result.data)
                # TaskCompleted 훅 발생
                await self._emit(HookEvent(
                    type=HookType.TASK_COMPLETED,
                    agent_name=agent.name,
                    task_id=task.id,
                    task_title=task.title,
                    data=result.data,
                ))
                # Lead에게 완료 보고
                await self.mailbox.send(
                    sender=agent.name,
                    recipient="lead",
                    subject=f"task_completed:{task.id}",
                    body={"task_title": task.title, "result": result.data},
                )
            else:
                await self.task_list.fail_task(task.id, result.error or "Unknown error")
                # TaskFailed 훅 발생
                await self._emit(HookEvent(
                    type=HookType.TASK_FAILED,
                    agent_name=agent.name,
                    task_id=task.id,
                    task_title=task.title,
                    data=result.error,
                ))
                await self.mailbox.send(
                    sender=agent.name,
                    recipient="lead",
                    subject=f"task_failed:{task.id}",
                    body={"task_title": task.title, "error": result.error},
                )

            # AllTasksDone 체크
            if self.task_list.all_done:
                await self._emit(HookEvent(
                    type=HookType.ALL_TASKS_DONE,
                ))

    async def _process_agent_mail(self, agent: BaseAgent) -> None:
        """에이전트의 대기 메시지를 처리합니다."""
        messages = self.mailbox.drain(agent.name)
        for msg in messages:
            logger.debug(f"[{agent.name}] received mail from {msg.sender}: {msg.subject}")
            # 에이전트가 메시지를 컨텍스트로 활용할 수 있도록 저장
            if not hasattr(agent, "_received_messages"):
                agent._received_messages = []
            agent._received_messages.append(msg)

    async def _plan_tasks(self, user_request: str) -> None:
        """LLM을 사용하여 사용자 요청을 태스크로 분해합니다."""
        agent_descriptions = "\n".join(
            f"- {name}: {agent.system_prompt}"
            for name, agent in self._teammates.items()
        )

        plan_prompt = (
            f"Available team members:\n{agent_descriptions}\n\n"
            f"User request: {user_request}\n\n"
            "Break this request into independent, parallelizable tasks. "
            "Each task should be assignable to one team member.\n\n"
            "Respond in this JSON-like format, one task per line:\n"
            "TASK: <title> | DESCRIPTION: <what to do> | PRIORITY: <0-10>\n\n"
            "Create tasks that can be worked on independently. "
            "If a task depends on another, add: DEPENDS: <task_number>\n"
            "Task numbers start at 1."
        )

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=(
                "You are a team lead. Break work into clear, independent tasks. "
                "Respond only in the requested format."
            ),
            messages=[{"role": "user", "content": plan_prompt}],
        )

        plan_text = "\n".join(
            block.text for block in response.content if block.type == "text"
        )

        # 태스크 파싱
        task_defs: list[dict[str, Any]] = []
        task_id_map: dict[int, str] = {}  # task_number -> task_id

        for line in plan_text.strip().split("\n"):
            line = line.strip()
            if not line.upper().startswith("TASK:"):
                continue

            parts: dict[str, str] = {}
            for segment in line.split("|"):
                segment = segment.strip()
                if ":" in segment:
                    key, value = segment.split(":", 1)
                    parts[key.strip().upper()] = value.strip()

            if "TASK" not in parts:
                continue

            priority = 0
            try:
                priority = int(parts.get("PRIORITY", "0"))
            except ValueError:
                pass

            task_def: dict[str, Any] = {
                "title": parts["TASK"],
                "description": parts.get("DESCRIPTION", parts["TASK"]),
                "priority": priority,
                "depends_on": [],
            }
            task_defs.append(task_def)

        # 태스크 생성 (의존성 매핑을 위해 두 패스)
        created = await self.task_list.add_tasks(task_defs, created_by="lead")

        # 태스크 번호 → ID 매핑
        for i, task in enumerate(created):
            task_id_map[i + 1] = task.id

        # 의존성 연결 (DEPENDS 파싱)
        for i, line in enumerate(plan_text.strip().split("\n")):
            if "DEPENDS:" in line.upper():
                dep_part = line.upper().split("DEPENDS:")[1].strip()
                try:
                    dep_num = int(dep_part.split()[0])
                    if dep_num in task_id_map and i < len(created):
                        created[i].depends_on.append(task_id_map[dep_num])
                except (ValueError, IndexError):
                    pass

        logger.info(f"[{self.name}] Created {len(created)} tasks from plan")

    async def _synthesize(
        self,
        user_request: str,
        results: list[TaskResult],
        messages: list[TeamMessage],
    ) -> str:
        """모든 결과를 종합하여 최종 응답을 생성합니다."""
        results_text = "\n\n".join(
            f"[{r.agent_name}] ({'OK' if r.success else 'FAIL'})\n"
            f"{r.data if r.success else r.error}"
            for r in results
        )

        msg_text = ""
        if messages:
            msg_text = "\n\nTeam communications:\n" + "\n".join(
                f"  {m.sender} -> {m.recipient}: {m.subject}"
                for m in messages
            )

        prompt = (
            f"Original request: {user_request}\n\n"
            f"Team results:\n{results_text}"
            f"{msg_text}\n\n"
            "Synthesize these results into a comprehensive, well-organized response. "
            "Highlight agreements, disagreements, and key insights across team members. "
            "In Korean."
        )

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=(
                "You are the team lead synthesizing results from your team. "
                "Provide a unified, comprehensive answer."
            ),
            messages=[{"role": "user", "content": prompt}],
        )

        return "\n".join(
            block.text for block in response.content if block.type == "text"
        )

    # --- Plan Approval ---

    async def request_plan_approval(
        self,
        agent_name: str,
        plan: str,
        approval_criteria: str | None = None,
    ) -> PlanApproval:
        """에이전트의 계획을 Lead가 LLM으로 검토합니다."""
        criteria = approval_criteria or "Review the plan for completeness and correctness."

        prompt = (
            f"Agent '{agent_name}' submitted this plan:\n\n{plan}\n\n"
            f"Approval criteria: {criteria}\n\n"
            "Should this plan be approved? Respond with:\n"
            "APPROVED: <reason>\n"
            "or\n"
            "REJECTED: <feedback for the agent>"
        )

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system="You are a team lead reviewing an agent's plan.",
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = "\n".join(
            block.text for block in response.content if block.type == "text"
        )

        approved = "APPROVED" in response_text.upper().split("\n")[0]
        feedback = response_text.split(":", 1)[1].strip() if ":" in response_text else response_text

        return PlanApproval(
            agent_name=agent_name,
            plan=plan,
            approved=approved,
            feedback=feedback,
        )

    # --- 정리 ---

    async def cleanup(self) -> None:
        """팀 리소스를 정리합니다."""
        # 남은 워커 취소
        for name, task in self._running_tasks.items():
            if not task.done():
                task.cancel()
        self._running_tasks.clear()

        # 메일박스 정리
        for name in list(self._teammates.keys()):
            self.mailbox.unregister(name)
        self.mailbox.unregister("lead")

        self._teammates.clear()
        logger.info(f"[{self.name}] Team cleaned up")

    def status(self) -> str:
        """팀 상태 요약을 반환합니다."""
        lines = [
            f"Team: {self.name}",
            f"Teammates: {', '.join(self.teammate_names) or '(none)'}",
            self.task_list.summary(),
        ]
        return "\n".join(lines)
