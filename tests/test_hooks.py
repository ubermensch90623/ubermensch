"""HookRegistry 유닛 테스트."""

import pytest

from ubermensch.core.hooks import HookContext, HookEvent, HookRegistry, HookResult


@pytest.fixture
def hooks():
    return HookRegistry()


class TestRegistration:
    def test_register_callback(self, hooks: HookRegistry):
        async def my_hook(ctx: HookContext) -> HookResult:
            return HookResult()

        hooks.register(HookEvent.TASK_COMPLETED, my_hook)
        assert hooks.has_hooks(HookEvent.TASK_COMPLETED)

    def test_no_hooks_initially(self, hooks: HookRegistry):
        assert not hooks.has_hooks(HookEvent.TASK_COMPLETED)

    def test_decorator_registration(self, hooks: HookRegistry):
        @hooks.on(HookEvent.TASK_COMPLETED)
        async def my_hook(ctx: HookContext) -> HookResult:
            return HookResult()

        assert hooks.has_hooks(HookEvent.TASK_COMPLETED)

    def test_unregister(self, hooks: HookRegistry):
        async def my_hook(ctx: HookContext) -> HookResult:
            return HookResult()

        hooks.register(HookEvent.TASK_COMPLETED, my_hook)
        hooks.unregister(HookEvent.TASK_COMPLETED, my_hook)
        assert not hooks.has_hooks(HookEvent.TASK_COMPLETED)

    def test_unregister_nonexistent_is_safe(self, hooks: HookRegistry):
        async def my_hook(ctx: HookContext) -> HookResult:
            return HookResult()

        hooks.unregister(HookEvent.TASK_COMPLETED, my_hook)  # no error

    def test_clear_specific_event(self, hooks: HookRegistry):
        @hooks.on(HookEvent.TASK_COMPLETED)
        async def hook1(ctx):
            return HookResult()

        @hooks.on(HookEvent.TASK_FAILED)
        async def hook2(ctx):
            return HookResult()

        hooks.clear(HookEvent.TASK_COMPLETED)
        assert not hooks.has_hooks(HookEvent.TASK_COMPLETED)
        assert hooks.has_hooks(HookEvent.TASK_FAILED)

    def test_clear_all(self, hooks: HookRegistry):
        @hooks.on(HookEvent.TASK_COMPLETED)
        async def hook1(ctx):
            return HookResult()

        @hooks.on(HookEvent.TASK_FAILED)
        async def hook2(ctx):
            return HookResult()

        hooks.clear()
        assert not hooks.has_hooks(HookEvent.TASK_COMPLETED)
        assert not hooks.has_hooks(HookEvent.TASK_FAILED)


class TestTrigger:
    async def test_trigger_no_hooks(self, hooks: HookRegistry):
        ctx = HookContext(event=HookEvent.TASK_COMPLETED, agent_name="test")
        result = await hooks.trigger(ctx)
        assert result.block is False
        assert result.feedback == ""

    async def test_trigger_non_blocking(self, hooks: HookRegistry):
        @hooks.on(HookEvent.TASK_COMPLETED)
        async def allow(ctx: HookContext) -> HookResult:
            return HookResult(block=False, feedback="Looks good")

        ctx = HookContext(event=HookEvent.TASK_COMPLETED, agent_name="test")
        result = await hooks.trigger(ctx)
        assert result.block is False
        assert result.feedback == "Looks good"

    async def test_trigger_blocking(self, hooks: HookRegistry):
        @hooks.on(HookEvent.TASK_COMPLETED)
        async def block(ctx: HookContext) -> HookResult:
            return HookResult(block=True, feedback="Tests missing")

        ctx = HookContext(event=HookEvent.TASK_COMPLETED, agent_name="test")
        result = await hooks.trigger(ctx)
        assert result.block is True
        assert "Tests missing" in result.feedback

    async def test_multiple_hooks_one_blocks(self, hooks: HookRegistry):
        """하나라도 block이면 전체 block."""

        @hooks.on(HookEvent.TASK_COMPLETED)
        async def allow(ctx: HookContext) -> HookResult:
            return HookResult(block=False, feedback="OK")

        @hooks.on(HookEvent.TASK_COMPLETED)
        async def block(ctx: HookContext) -> HookResult:
            return HookResult(block=True, feedback="Nope")

        ctx = HookContext(event=HookEvent.TASK_COMPLETED, agent_name="test")
        result = await hooks.trigger(ctx)
        assert result.block is True
        assert "OK" in result.feedback
        assert "Nope" in result.feedback

    async def test_multiple_hooks_feedbacks_merged(self, hooks: HookRegistry):
        @hooks.on(HookEvent.TASK_COMPLETED)
        async def hook1(ctx: HookContext) -> HookResult:
            return HookResult(feedback="Feedback 1")

        @hooks.on(HookEvent.TASK_COMPLETED)
        async def hook2(ctx: HookContext) -> HookResult:
            return HookResult(feedback="Feedback 2")

        ctx = HookContext(event=HookEvent.TASK_COMPLETED, agent_name="test")
        result = await hooks.trigger(ctx)
        assert "Feedback 1" in result.feedback
        assert "Feedback 2" in result.feedback

    async def test_hook_exception_handled(self, hooks: HookRegistry):
        """콜백에서 예외가 발생해도 다른 콜백은 실행됨."""

        @hooks.on(HookEvent.TASK_COMPLETED)
        async def broken(ctx: HookContext) -> HookResult:
            raise RuntimeError("Hook crashed")

        @hooks.on(HookEvent.TASK_COMPLETED)
        async def working(ctx: HookContext) -> HookResult:
            return HookResult(feedback="Still works")

        ctx = HookContext(event=HookEvent.TASK_COMPLETED, agent_name="test")
        result = await hooks.trigger(ctx)
        assert "Still works" in result.feedback
        assert "Hook error" in result.feedback

    async def test_context_data_passed(self, hooks: HookRegistry):
        received_data: dict = {}

        @hooks.on(HookEvent.TASK_COMPLETED)
        async def capture(ctx: HookContext) -> HookResult:
            received_data.update(ctx.data)
            return HookResult()

        ctx = HookContext(
            event=HookEvent.TASK_COMPLETED,
            agent_name="test",
            task_id="t1",
            task_title="My Task",
            data={"result": "some data"},
        )
        await hooks.trigger(ctx)
        assert received_data == {"result": "some data"}


class TestHookEvents:
    def test_all_events_exist(self):
        expected = {
            "teammate_idle",
            "task_completed",
            "task_failed",
            "teammate_spawned",
            "teammate_shutdown",
            "message_sent",
            "plan_submitted",
        }
        actual = {e.value for e in HookEvent}
        assert actual == expected
