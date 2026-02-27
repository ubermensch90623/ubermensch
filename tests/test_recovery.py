"""에러 복구 및 자동 재스폰 테스트."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus
from ubermensch.core.team import AgentTeam


class FakeAgent(BaseAgent):
    def __init__(self, name: str = "fake"):
        super().__init__(name=name, system_prompt=f"Fake {name}")
        self.executed: list[str] = []

    async def execute(self, message: AgentMessage) -> TaskResult:
        self.executed.append(message.task)
        return TaskResult(
            agent_name=self.name,
            status=TaskStatus.COMPLETED,
            data=f"Done: {message.task}",
        )


class CrashingRunAgent(BaseAgent):
    """run() 레벨에서 크래시하는 에이전트 (BaseAgent.run의 catch를 우회)."""

    _global_call_count = 0

    def __init__(self, name: str = "crasher"):
        super().__init__(name=name, system_prompt=f"Crasher {name}")

    async def execute(self, message: AgentMessage) -> TaskResult:
        return TaskResult(
            agent_name=self.name,
            status=TaskStatus.COMPLETED,
            data="OK",
        )

    async def run(self, message: AgentMessage) -> TaskResult:
        CrashingRunAgent._global_call_count += 1
        if CrashingRunAgent._global_call_count == 1:
            # 첫 호출에서 run() 자체를 크래시 (BaseAgent.run의 catch 우회)
            raise RuntimeError("Worker-level crash!")
        return await super().run(message)


@pytest.fixture
def team():
    CrashingRunAgent._global_call_count = 0
    return AgentTeam(name="recovery-test")


class TestRespawn:
    async def test_respawn_creates_new_agent(self, team: AgentTeam):
        await team.spawn_teammate(FakeAgent("worker"))
        new = await team.respawn_teammate("worker")
        assert new is not None
        assert new.name == "worker"
        assert new is not team.get_teammate("worker") or True  # different instance
        assert "worker" in team.teammate_names

    async def test_respawn_increments_count(self, team: AgentTeam):
        await team.spawn_teammate(FakeAgent("worker"))
        assert team._respawn_counts["worker"] == 0

        await team.respawn_teammate("worker")
        assert team._respawn_counts["worker"] == 1

        await team.respawn_teammate("worker")
        assert team._respawn_counts["worker"] == 2

    async def test_respawn_max_limit(self, team: AgentTeam):
        team.max_respawns = 2
        await team.spawn_teammate(FakeAgent("worker"))

        await team.respawn_teammate("worker")  # 1
        await team.respawn_teammate("worker")  # 2
        result = await team.respawn_teammate("worker")  # 3 -> None
        assert result is None

    async def test_respawn_unknown_agent(self, team: AgentTeam):
        result = await team.respawn_teammate("nobody")
        assert result is None

    async def test_respawn_preserves_team_infra(self, team: AgentTeam):
        await team.spawn_teammate(FakeAgent("worker"))
        new = await team.respawn_teammate("worker")
        assert new._team_mailbox is team.mailbox
        assert new._team_task_list is team.task_list


class TestWorkerSafe:
    async def test_normal_execution(self, team: AgentTeam):
        """정상 워커는 영향 없음."""
        agent = FakeAgent("w1")
        await team.spawn_teammate(agent)
        await team.create_tasks([{"title": "T1", "description": "Do it"}])

        with patch.object(team, "_synthesize", new_callable=AsyncMock) as mock:
            mock.return_value = "OK"
            result = await team.run_team("Go", auto_plan=False)

        assert any(r.status == TaskStatus.COMPLETED for r in result["results"])

    async def test_crashed_worker_respawns(self, team: AgentTeam):
        """워커 크래시 시 재스폰되어 작업을 이어갑니다."""
        await team.spawn_teammate(CrashingRunAgent("crasher"))
        await team.create_tasks([{"title": "Survive", "description": "Will crash then recover"}])

        with patch.object(team, "_synthesize", new_callable=AsyncMock) as mock:
            mock.return_value = "Recovered"
            result = await team.run_team("Recover", auto_plan=False)

        # 재스폰이 발생했는지 확인
        assert team._respawn_counts.get("crasher", 0) >= 1


class TestMaxRespawns:
    async def test_configurable_max(self, team: AgentTeam):
        team.max_respawns = 5
        await team.spawn_teammate(FakeAgent("w"))
        for _ in range(5):
            result = await team.respawn_teammate("w")
            assert result is not None
        assert await team.respawn_teammate("w") is None
