"""SharedTaskList 유닛 테스트."""

import asyncio

import pytest

from ubermensch.core.message import TaskStatus
from ubermensch.core.shared_task_list import SharedTaskList


@pytest.fixture
def task_list():
    return SharedTaskList()


class TestAddTask:
    async def test_add_single_task(self, task_list: SharedTaskList):
        task = await task_list.add_task(title="Test task", description="desc")
        assert task.title == "Test task"
        assert task.description == "desc"
        assert task.status == TaskStatus.PENDING
        assert task.assigned_to is None
        assert len(task_list.all_tasks) == 1

    async def test_add_task_with_priority(self, task_list: SharedTaskList):
        task = await task_list.add_task(title="High", priority=10)
        assert task.priority == 10

    async def test_add_tasks_batch(self, task_list: SharedTaskList):
        tasks = await task_list.add_tasks(
            [
                {"title": "Task 1", "description": "First"},
                {"title": "Task 2", "description": "Second"},
                {"title": "Task 3", "priority": 5},
            ],
            created_by="lead",
        )
        assert len(tasks) == 3
        assert all(t.created_by == "lead" for t in tasks)
        assert tasks[2].priority == 5

    async def test_get_task(self, task_list: SharedTaskList):
        task = await task_list.add_task(title="Find me")
        found = task_list.get_task(task.id)
        assert found is not None
        assert found.title == "Find me"

    async def test_get_task_not_found(self, task_list: SharedTaskList):
        assert task_list.get_task("nonexistent") is None


class TestDependencies:
    async def test_no_deps_not_blocked(self, task_list: SharedTaskList):
        task = await task_list.add_task(title="No deps")
        assert not task_list.is_blocked(task.id)

    async def test_unresolved_dep_blocks(self, task_list: SharedTaskList):
        t1 = await task_list.add_task(title="First")
        t2 = await task_list.add_task(
            title="Second", depends_on=[t1.id]
        )
        assert task_list.is_blocked(t2.id)

    async def test_completed_dep_unblocks(self, task_list: SharedTaskList):
        t1 = await task_list.add_task(title="First")
        t2 = await task_list.add_task(
            title="Second", depends_on=[t1.id]
        )
        assert task_list.is_blocked(t2.id)

        await task_list.complete_task(t1.id)
        assert not task_list.is_blocked(t2.id)

    async def test_multiple_deps_all_must_complete(self, task_list: SharedTaskList):
        t1 = await task_list.add_task(title="Dep 1")
        t2 = await task_list.add_task(title="Dep 2")
        t3 = await task_list.add_task(
            title="Blocked", depends_on=[t1.id, t2.id]
        )

        assert task_list.is_blocked(t3.id)
        await task_list.complete_task(t1.id)
        assert task_list.is_blocked(t3.id)  # still blocked by t2
        await task_list.complete_task(t2.id)
        assert not task_list.is_blocked(t3.id)

    async def test_missing_dep_blocks(self, task_list: SharedTaskList):
        task = await task_list.add_task(
            title="Bad dep", depends_on=["nonexistent"]
        )
        assert task_list.is_blocked(task.id)


class TestClaiming:
    async def test_claim_task(self, task_list: SharedTaskList):
        task = await task_list.add_task(title="Claim me")
        result = await task_list.claim_task(task.id, "agent_1")
        assert result is True
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.assigned_to == "agent_1"

    async def test_claim_already_claimed(self, task_list: SharedTaskList):
        task = await task_list.add_task(title="Taken")
        await task_list.claim_task(task.id, "agent_1")
        result = await task_list.claim_task(task.id, "agent_2")
        assert result is False
        assert task.assigned_to == "agent_1"

    async def test_claim_blocked_task_fails(self, task_list: SharedTaskList):
        t1 = await task_list.add_task(title="Dep")
        t2 = await task_list.add_task(title="Blocked", depends_on=[t1.id])
        result = await task_list.claim_task(t2.id, "agent_1")
        assert result is False

    async def test_claim_nonexistent_fails(self, task_list: SharedTaskList):
        result = await task_list.claim_task("nope", "agent_1")
        assert result is False

    async def test_claim_next_auto(self, task_list: SharedTaskList):
        await task_list.add_task(title="Low", priority=1)
        await task_list.add_task(title="High", priority=10)
        await task_list.add_task(title="Mid", priority=5)

        task = await task_list.claim_next("agent_1")
        assert task is not None
        assert task.title == "High"
        assert task.assigned_to == "agent_1"

    async def test_claim_next_skips_blocked(self, task_list: SharedTaskList):
        t1 = await task_list.add_task(title="Dep", priority=1)
        await task_list.add_task(
            title="Blocked high", priority=10, depends_on=[t1.id]
        )
        await task_list.add_task(title="Available", priority=5)

        task = await task_list.claim_next("agent_1")
        assert task is not None
        assert task.title == "Available"

    async def test_claim_next_returns_none_when_empty(self, task_list: SharedTaskList):
        task = await task_list.claim_next("agent_1")
        assert task is None

    async def test_concurrent_claim_no_double_assign(self, task_list: SharedTaskList):
        """여러 에이전트가 동시에 같은 태스크를 claim해도 하나만 성공."""
        task = await task_list.add_task(title="Race condition")

        results = await asyncio.gather(
            task_list.claim_task(task.id, "agent_1"),
            task_list.claim_task(task.id, "agent_2"),
            task_list.claim_task(task.id, "agent_3"),
        )
        assert sum(results) == 1  # 정확히 하나만 True


class TestCompletion:
    async def test_complete_task(self, task_list: SharedTaskList):
        task = await task_list.add_task(title="Complete me")
        await task_list.claim_task(task.id, "agent_1")
        result = await task_list.complete_task(task.id, result={"key": "value"})
        assert result is True
        assert task.status == TaskStatus.COMPLETED
        assert task.result == {"key": "value"}

    async def test_fail_task(self, task_list: SharedTaskList):
        task = await task_list.add_task(title="Fail me")
        await task_list.claim_task(task.id, "agent_1")
        result = await task_list.fail_task(task.id, error="Something broke")
        assert result is True
        assert task.status == TaskStatus.FAILED
        assert task.error == "Something broke"

    async def test_complete_nonexistent(self, task_list: SharedTaskList):
        assert await task_list.complete_task("nope") is False

    async def test_fail_nonexistent(self, task_list: SharedTaskList):
        assert await task_list.fail_task("nope", "err") is False


class TestStatusQueries:
    async def test_counts(self, task_list: SharedTaskList):
        t1 = await task_list.add_task(title="A")
        t2 = await task_list.add_task(title="B")
        t3 = await task_list.add_task(title="C")

        assert task_list.pending_count == 3
        assert task_list.in_progress_count == 0
        assert task_list.completed_count == 0

        await task_list.claim_task(t1.id, "agent_1")
        assert task_list.pending_count == 2
        assert task_list.in_progress_count == 1

        await task_list.complete_task(t1.id)
        assert task_list.completed_count == 1

    async def test_all_done(self, task_list: SharedTaskList):
        t1 = await task_list.add_task(title="A")
        t2 = await task_list.add_task(title="B")
        assert not task_list.all_done

        await task_list.complete_task(t1.id)
        assert not task_list.all_done

        await task_list.fail_task(t2.id, "err")
        assert task_list.all_done  # FAILED도 "done"으로 취급

    async def test_get_available_tasks_sorted(self, task_list: SharedTaskList):
        await task_list.add_task(title="Low", priority=1)
        await task_list.add_task(title="High", priority=10)
        await task_list.add_task(title="Mid", priority=5)

        available = task_list.get_available_tasks()
        assert [t.title for t in available] == ["High", "Mid", "Low"]

    async def test_get_tasks_by_agent(self, task_list: SharedTaskList):
        t1 = await task_list.add_task(title="A")
        t2 = await task_list.add_task(title="B")
        t3 = await task_list.add_task(title="C")

        await task_list.claim_task(t1.id, "alice")
        await task_list.claim_task(t2.id, "bob")
        await task_list.claim_task(t3.id, "alice")

        alice_tasks = task_list.get_tasks_by_agent("alice")
        assert len(alice_tasks) == 2
        assert {t.title for t in alice_tasks} == {"A", "C"}

    async def test_summary_output(self, task_list: SharedTaskList):
        await task_list.add_task(title="Test task")
        summary = task_list.summary()
        assert "Tasks: 1 total" in summary
        assert "Test task" in summary


class TestWaitAllDone:
    async def test_wait_all_done_immediate(self, task_list: SharedTaskList):
        t1 = await task_list.add_task(title="A")
        await task_list.complete_task(t1.id)
        result = await task_list.wait_all_done(timeout=1.0)
        assert result is True

    async def test_wait_all_done_timeout(self, task_list: SharedTaskList):
        await task_list.add_task(title="A")
        result = await task_list.wait_all_done(timeout=0.1)
        assert result is False

    async def test_wait_all_done_completes_during_wait(self, task_list: SharedTaskList):
        t1 = await task_list.add_task(title="A")

        async def complete_later():
            await asyncio.sleep(0.05)
            await task_list.complete_task(t1.id)

        asyncio.create_task(complete_later())
        result = await task_list.wait_all_done(timeout=2.0)
        assert result is True
