"""Hook 시스템 테스트."""

from __future__ import annotations

import pytest

from ubermensch.core.hooks import HookEvent, HookRegistry, HookType


@pytest.fixture
def hooks() -> HookRegistry:
    return HookRegistry()


class TestHookRegistration:
    """훅 등록/해제 테스트."""

    def test_register_handler(self, hooks: HookRegistry):
        async def handler(event: HookEvent) -> None:
            pass

        hooks.register(HookType.TASK_COMPLETED, handler)
        assert hooks.handler_count(HookType.TASK_COMPLETED) == 1

    def test_register_with_decorator(self, hooks: HookRegistry):
        @hooks.on(HookType.TEAMMATE_IDLE)
        async def handler(event: HookEvent) -> None:
            pass

        assert hooks.handler_count(HookType.TEAMMATE_IDLE) == 1

    def test_unregister_handler(self, hooks: HookRegistry):
        async def handler(event: HookEvent) -> None:
            pass

        hooks.register(HookType.TASK_COMPLETED, handler)
        hooks.unregister(HookType.TASK_COMPLETED, handler)
        assert hooks.handler_count(HookType.TASK_COMPLETED) == 0

    def test_clear_specific_type(self, hooks: HookRegistry):
        async def h1(event: HookEvent) -> None:
            pass

        async def h2(event: HookEvent) -> None:
            pass

        hooks.register(HookType.TASK_COMPLETED, h1)
        hooks.register(HookType.TASK_FAILED, h2)

        hooks.clear(HookType.TASK_COMPLETED)
        assert hooks.handler_count(HookType.TASK_COMPLETED) == 0
        assert hooks.handler_count(HookType.TASK_FAILED) == 1

    def test_clear_all(self, hooks: HookRegistry):
        async def handler(event: HookEvent) -> None:
            pass

        hooks.register(HookType.TASK_COMPLETED, handler)
        hooks.register(HookType.TASK_FAILED, handler)
        hooks.clear()
        assert hooks.handler_count() == 0

    def test_multiple_handlers_same_type(self, hooks: HookRegistry):
        async def h1(event: HookEvent) -> None:
            pass

        async def h2(event: HookEvent) -> None:
            pass

        hooks.register(HookType.TASK_COMPLETED, h1)
        hooks.register(HookType.TASK_COMPLETED, h2)
        assert hooks.handler_count(HookType.TASK_COMPLETED) == 2

    def test_registered_types(self, hooks: HookRegistry):
        async def handler(event: HookEvent) -> None:
            pass

        hooks.register(HookType.TASK_COMPLETED, handler)
        hooks.register(HookType.TEAMMATE_IDLE, handler)

        types = hooks.registered_types
        assert HookType.TASK_COMPLETED in types
        assert HookType.TEAMMATE_IDLE in types
        assert HookType.TASK_FAILED not in types


class TestHookEmission:
    """훅 이벤트 발생 테스트."""

    @pytest.mark.asyncio
    async def test_emit_calls_handler(self, hooks: HookRegistry):
        received: list[HookEvent] = []

        @hooks.on(HookType.TASK_COMPLETED)
        async def handler(event: HookEvent) -> None:
            received.append(event)

        event = HookEvent(
            type=HookType.TASK_COMPLETED,
            agent_name="plumber",
            task_title="파이프라인 설계",
        )
        await hooks.emit(event)

        assert len(received) == 1
        assert received[0].agent_name == "plumber"
        assert received[0].task_title == "파이프라인 설계"

    @pytest.mark.asyncio
    async def test_emit_calls_multiple_handlers(self, hooks: HookRegistry):
        calls: list[str] = []

        @hooks.on(HookType.TASK_COMPLETED)
        async def h1(event: HookEvent) -> None:
            calls.append("h1")

        @hooks.on(HookType.TASK_COMPLETED)
        async def h2(event: HookEvent) -> None:
            calls.append("h2")

        await hooks.emit(HookEvent(type=HookType.TASK_COMPLETED))
        assert "h1" in calls
        assert "h2" in calls

    @pytest.mark.asyncio
    async def test_emit_no_handlers_returns_empty(self, hooks: HookRegistry):
        errors = await hooks.emit(HookEvent(type=HookType.TASK_COMPLETED))
        assert errors == []

    @pytest.mark.asyncio
    async def test_emit_handler_error_does_not_break_others(
        self, hooks: HookRegistry
    ):
        calls: list[str] = []

        @hooks.on(HookType.TASK_COMPLETED)
        async def bad_handler(event: HookEvent) -> None:
            raise ValueError("테스트 에러")

        @hooks.on(HookType.TASK_COMPLETED)
        async def good_handler(event: HookEvent) -> None:
            calls.append("good")

        errors = await hooks.emit(HookEvent(type=HookType.TASK_COMPLETED))

        # good_handler는 실행됨
        assert "good" in calls
        # bad_handler 에러가 반환됨
        assert len(errors) == 1
        assert isinstance(errors[0], ValueError)

    @pytest.mark.asyncio
    async def test_emit_only_matching_type(self, hooks: HookRegistry):
        completed_calls: list[str] = []
        failed_calls: list[str] = []

        @hooks.on(HookType.TASK_COMPLETED)
        async def on_completed(event: HookEvent) -> None:
            completed_calls.append("completed")

        @hooks.on(HookType.TASK_FAILED)
        async def on_failed(event: HookEvent) -> None:
            failed_calls.append("failed")

        await hooks.emit(HookEvent(type=HookType.TASK_COMPLETED))

        assert len(completed_calls) == 1
        assert len(failed_calls) == 0


class TestHookEvent:
    """HookEvent 데이터 테스트."""

    def test_event_defaults(self):
        event = HookEvent(type=HookType.TASK_COMPLETED)
        assert event.agent_name == ""
        assert event.task_id == ""
        assert event.data is None
        assert event.team_name == ""

    def test_event_with_data(self):
        event = HookEvent(
            type=HookType.TEAMMATE_IDLE,
            agent_name="plumber",
            data={"reason": "no tasks"},
            team_name="데이터팀",
        )
        assert event.agent_name == "plumber"
        assert event.data["reason"] == "no tasks"


class TestTeamHookIntegration:
    """AgentTeam과 Hook 통합 테스트."""

    def test_team_has_hook_registry(self):
        from ubermensch.core.team import AgentTeam

        team = AgentTeam(name="test-team")
        assert isinstance(team.hooks, HookRegistry)

    def test_team_hook_registration(self):
        from ubermensch.core.team import AgentTeam

        team = AgentTeam(name="test-team")

        @team.hooks.on(HookType.TASK_COMPLETED)
        async def on_complete(event: HookEvent) -> None:
            pass

        assert team.hooks.handler_count(HookType.TASK_COMPLETED) == 1
