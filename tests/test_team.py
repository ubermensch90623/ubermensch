"""AgentTeam 유닛 테스트.

LLM 호출이 필요한 부분은 mock하여 순수 로직만 테스트합니다.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.hooks import HookContext, HookEvent, HookResult
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus
from ubermensch.core.team import AgentTeam


class FakeAgent(BaseAgent):
    """테스트용 가짜 에이전트. execute()는 즉시 성공을 반환."""

    def __init__(self, name: str = "fake", delay: float = 0):
        super().__init__(name=name, system_prompt=f"Fake agent {name}")
        self.delay = delay
        self.executed_tasks: list[str] = []

    async def execute(self, message: AgentMessage) -> TaskResult:
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        self.executed_tasks.append(message.task)
        return TaskResult(
            agent_name=self.name,
            status=TaskStatus.COMPLETED,
            data=f"Done: {message.task}",
        )


class FailingAgent(BaseAgent):
    """테스트용 항상 실패하는 에이전트."""

    def __init__(self, name: str = "failer"):
        super().__init__(name=name, system_prompt="Always fails")

    async def execute(self, message: AgentMessage) -> TaskResult:
        return TaskResult(
            agent_name=self.name,
            status=TaskStatus.FAILED,
            error="Intentional failure",
        )


@pytest.fixture
def team():
    return AgentTeam(name="test-team")


class TestTeamManagement:
    def test_create_team(self, team: AgentTeam):
        assert team.name == "test-team"
        assert team.teammate_names == []

    async def test_spawn_teammate(self, team: AgentTeam):
        agent = FakeAgent("worker1")
        await team.spawn_teammate(agent)
        assert "worker1" in team.teammate_names
        assert agent._team_mailbox is team.mailbox
        assert agent._team_task_list is team.task_list
        assert agent.in_team

    async def test_spawn_multiple(self, team: AgentTeam):
        await team.spawn_teammate(FakeAgent("a"))
        await team.spawn_teammate(FakeAgent("b"))
        await team.spawn_teammate(FakeAgent("c"))
        assert len(team.teammate_names) == 3

    async def test_shutdown_teammate(self, team: AgentTeam):
        await team.spawn_teammate(FakeAgent("worker"))
        await team.shutdown_teammate("worker")
        assert "worker" not in team.teammate_names

    async def test_shutdown_nonexistent_is_safe(self, team: AgentTeam):
        await team.shutdown_teammate("nobody")  # no error

    async def test_get_teammate(self, team: AgentTeam):
        agent = FakeAgent("worker")
        await team.spawn_teammate(agent)
        assert team.get_teammate("worker") is agent
        assert team.get_teammate("nobody") is None


class TestTaskCreation:
    async def test_create_tasks(self, team: AgentTeam):
        tasks = await team.create_tasks(
            [
                {"title": "Task A", "description": "Do A"},
                {"title": "Task B", "description": "Do B", "priority": 5},
            ]
        )
        assert len(tasks) == 2
        assert tasks[0].title == "Task A"
        assert tasks[1].priority == 5

    async def test_assign_task(self, team: AgentTeam):
        agent = FakeAgent("worker")
        await team.spawn_teammate(agent)
        tasks = await team.create_tasks([{"title": "Assign me"}])
        result = await team.assign_task(tasks[0].id, "worker")
        assert result is True
        assert tasks[0].assigned_to == "worker"


class TestTeamExecution:
    async def test_run_team_manual_tasks(self, team: AgentTeam):
        """auto_plan=False로 수동 태스크 실행."""
        agent1 = FakeAgent("w1")
        agent2 = FakeAgent("w2")
        await team.spawn_teammate(agent1)
        await team.spawn_teammate(agent2)

        await team.create_tasks(
            [
                {"title": "Task 1", "description": "First task", "priority": 5},
                {"title": "Task 2", "description": "Second task", "priority": 3},
            ]
        )

        # LLM 종합 호출 mock
        with patch.object(team, "_synthesize", new_callable=AsyncMock) as mock_synth:
            mock_synth.return_value = "Synthesized result"
            result = await team.run_team("Do stuff", auto_plan=False)

        assert result["synthesis"] == "Synthesized result"
        assert len(result["results"]) == 2
        # 두 에이전트가 각각 하나씩 처리
        total_executed = len(agent1.executed_tasks) + len(agent2.executed_tasks)
        assert total_executed == 2

    async def test_run_team_with_dependencies(self, team: AgentTeam):
        """의존성 있는 태스크가 올바른 순서로 실행되는지 확인."""
        agent = FakeAgent("w1")
        await team.spawn_teammate(agent)

        tasks = await team.create_tasks(
            [
                {"title": "Step 1", "description": "First"},
                {"title": "Step 2", "description": "Second"},
            ]
        )
        tasks[1].depends_on = [tasks[0].id]

        with patch.object(team, "_synthesize", new_callable=AsyncMock) as mock_synth:
            mock_synth.return_value = "Done"
            await team.run_team("Sequential", auto_plan=False)

        assert len(agent.executed_tasks) == 2
        assert agent.executed_tasks[0] == "First"
        assert agent.executed_tasks[1] == "Second"

    async def test_run_team_empty_tasks(self, team: AgentTeam):
        """태스크 없이 실행하면 즉시 반환."""
        await team.spawn_teammate(FakeAgent("w1"))
        result = await team.run_team("Nothing", auto_plan=False)
        assert result["synthesis"] == "No tasks were created for the request."

    async def test_run_team_with_failing_agent(self, team: AgentTeam):
        """에이전트 실패 시 태스크가 FAILED로 마킹되는지 확인."""
        await team.spawn_teammate(FailingAgent("failer"))

        await team.create_tasks([{"title": "Will fail", "description": "Doomed"}])

        with patch.object(team, "_synthesize", new_callable=AsyncMock) as mock_synth:
            mock_synth.return_value = "Failed synthesis"
            result = await team.run_team("Fail", auto_plan=False)

        assert any(r.status == TaskStatus.FAILED for r in result["results"])

    async def test_messages_sent_to_lead(self, team: AgentTeam):
        """에이전트가 태스크 완료 시 lead에게 메시지를 보내는지 확인."""
        await team.spawn_teammate(FakeAgent("w1"))
        await team.create_tasks([{"title": "Report", "description": "Report task"}])

        with patch.object(team, "_synthesize", new_callable=AsyncMock) as mock_synth:
            mock_synth.return_value = "OK"
            result = await team.run_team("Go", auto_plan=False)

        assert len(result["messages"]) > 0
        assert result["messages"][0].sender == "w1"
        assert "task_completed" in result["messages"][0].subject


class TestHooks:
    async def test_task_completed_hook_allows(self, team: AgentTeam):
        """TASK_COMPLETED 훅이 통과하면 정상 완료."""

        @team.hooks.on(HookEvent.TASK_COMPLETED)
        async def allow_all(ctx: HookContext) -> HookResult:
            return HookResult(block=False)

        await team.spawn_teammate(FakeAgent("w1"))
        await team.create_tasks([{"title": "Pass", "description": "Will pass"}])

        with patch.object(team, "_synthesize", new_callable=AsyncMock) as mock_synth:
            mock_synth.return_value = "OK"
            result = await team.run_team("Go", auto_plan=False)

        assert any(r.status == TaskStatus.COMPLETED for r in result["results"])

    async def test_task_completed_hook_blocks(self, team: AgentTeam):
        """TASK_COMPLETED 훅이 차단하면 태스크가 FAILED."""

        @team.hooks.on(HookEvent.TASK_COMPLETED)
        async def block_all(ctx: HookContext) -> HookResult:
            return HookResult(block=True, feedback="Tests missing")

        await team.spawn_teammate(FakeAgent("w1"))
        await team.create_tasks([{"title": "Blocked", "description": "Will be blocked"}])

        with patch.object(team, "_synthesize", new_callable=AsyncMock) as mock_synth:
            mock_synth.return_value = "Blocked"
            result = await team.run_team("Go", auto_plan=False)

        assert any(r.status == TaskStatus.FAILED for r in result["results"])

    async def test_teammate_spawned_hook(self, team: AgentTeam):
        """TEAMMATE_SPAWNED 훅이 실행되는지 확인."""
        spawned_names: list[str] = []

        @team.hooks.on(HookEvent.TEAMMATE_SPAWNED)
        async def track_spawn(ctx: HookContext) -> HookResult:
            spawned_names.append(ctx.agent_name)
            return HookResult()

        await team.spawn_teammate(FakeAgent("w1"))
        await team.spawn_teammate(FakeAgent("w2"))
        assert spawned_names == ["w1", "w2"]

    async def test_teammate_shutdown_hook(self, team: AgentTeam):
        """TEAMMATE_SHUTDOWN 훅이 실행되는지 확인."""
        shutdown_names: list[str] = []

        @team.hooks.on(HookEvent.TEAMMATE_SHUTDOWN)
        async def track_shutdown(ctx: HookContext) -> HookResult:
            shutdown_names.append(ctx.agent_name)
            return HookResult()

        await team.spawn_teammate(FakeAgent("w1"))
        await team.shutdown_teammate("w1")
        assert shutdown_names == ["w1"]


class TestPlanApproval:
    @staticmethod
    def _make_mock_client(text: str):
        mock_response = MagicMock()
        mock_block = MagicMock()
        mock_block.type = "text"
        mock_block.text = text
        mock_response.content = [mock_block]

        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        return mock_client

    async def test_plan_approval_approved(self, team: AgentTeam):
        """계획 승인 테스트."""
        team._client = self._make_mock_client("APPROVED: Plan looks good and complete.")

        approval = await team.request_plan_approval(
            agent_name="architect",
            plan="Build a cache layer",
            approval_criteria="Must include error handling",
        )

        assert approval.approved is True
        assert approval.agent_name == "architect"
        assert approval.plan == "Build a cache layer"

    async def test_plan_approval_rejected(self, team: AgentTeam):
        """계획 거부 테스트."""
        team._client = self._make_mock_client("REJECTED: Missing test strategy.")

        approval = await team.request_plan_approval(
            agent_name="architect",
            plan="Build without tests",
        )

        assert approval.approved is False


class TestCleanup:
    async def test_cleanup(self, team: AgentTeam):
        await team.spawn_teammate(FakeAgent("w1"))
        await team.spawn_teammate(FakeAgent("w2"))
        await team.cleanup()
        assert team.teammate_names == []

    async def test_status(self, team: AgentTeam):
        await team.spawn_teammate(FakeAgent("w1"))
        await team.create_tasks([{"title": "T1"}])
        status = team.status()
        assert "test-team" in status
        assert "w1" in status
        assert "T1" in status
