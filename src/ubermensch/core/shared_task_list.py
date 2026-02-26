"""Shared task list with dependency tracking, claiming, and locking."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from ubermensch.core.message import SharedTask, TaskStatus

logger = logging.getLogger(__name__)


class SharedTaskList:
    """에이전트 팀이 공유하는 태스크 리스트.

    특징:
        - asyncio.Lock 기반의 동시 접근 제어 (claim race condition 방지)
        - 태스크 간 의존성 추적 (depends_on)
        - 의존성이 해결된 태스크만 claim 가능
    """

    def __init__(self) -> None:
        self._tasks: dict[str, SharedTask] = {}
        self._lock = asyncio.Lock()
        self._completion_event = asyncio.Event()

    # --- 태스크 추가/조회 ---

    async def add_task(
        self,
        title: str,
        description: str = "",
        depends_on: list[str] | None = None,
        created_by: str = "",
        priority: int = 0,
    ) -> SharedTask:
        """새 태스크를 추가합니다."""
        task = SharedTask(
            title=title,
            description=description,
            depends_on=depends_on or [],
            created_by=created_by,
            priority=priority,
        )
        async with self._lock:
            self._tasks[task.id] = task
        logger.info(f"Task added: [{task.id}] {title}")
        return task

    async def add_tasks(
        self,
        tasks: list[dict[str, Any]],
        created_by: str = "",
    ) -> list[SharedTask]:
        """여러 태스크를 한 번에 추가합니다."""
        results = []
        for t in tasks:
            task = await self.add_task(
                title=t["title"],
                description=t.get("description", ""),
                depends_on=t.get("depends_on", []),
                created_by=created_by,
                priority=t.get("priority", 0),
            )
            results.append(task)
        return results

    def get_task(self, task_id: str) -> SharedTask | None:
        return self._tasks.get(task_id)

    @property
    def all_tasks(self) -> list[SharedTask]:
        return list(self._tasks.values())

    # --- 의존성 확인 ---

    def is_blocked(self, task_id: str) -> bool:
        """태스크가 미완료 의존성 때문에 블록되어 있는지 확인합니다."""
        task = self._tasks.get(task_id)
        if task is None:
            return True
        for dep_id in task.depends_on:
            dep = self._tasks.get(dep_id)
            if dep is None or dep.status != TaskStatus.COMPLETED:
                return True
        return False

    def get_available_tasks(self) -> list[SharedTask]:
        """Claim 가능한 태스크: PENDING 이고 의존성이 모두 해결된 태스크."""
        available = []
        for task in self._tasks.values():
            if task.status == TaskStatus.PENDING and not self.is_blocked(task.id):
                available.append(task)
        # 우선순위 높은 순 정렬
        available.sort(key=lambda t: t.priority, reverse=True)
        return available

    # --- 태스크 상태 변경 (Lock 보호) ---

    async def claim_task(self, task_id: str, agent_name: str) -> bool:
        """에이전트가 태스크를 claim합니다. Lock으로 race condition 방지."""
        async with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return False
            if task.status != TaskStatus.PENDING:
                return False
            if self.is_blocked(task_id):
                return False
            task.status = TaskStatus.IN_PROGRESS
            task.assigned_to = agent_name
        logger.info(f"[{agent_name}] claimed task [{task_id}] {task.title}")
        return True

    async def claim_next(self, agent_name: str) -> SharedTask | None:
        """다음 사용 가능한 태스크를 자동으로 claim합니다."""
        async with self._lock:
            for task in sorted(
                self._tasks.values(), key=lambda t: t.priority, reverse=True
            ):
                if (
                    task.status == TaskStatus.PENDING
                    and not self.is_blocked(task.id)
                ):
                    task.status = TaskStatus.IN_PROGRESS
                    task.assigned_to = agent_name
                    logger.info(
                        f"[{agent_name}] auto-claimed task [{task.id}] {task.title}"
                    )
                    return task
        return None

    async def complete_task(
        self, task_id: str, result: Any = None
    ) -> bool:
        """태스크를 완료 처리합니다."""
        async with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return False
            task.status = TaskStatus.COMPLETED
            task.result = result
        logger.info(f"Task completed: [{task_id}] {task.title}")
        self._check_all_done()
        return True

    async def fail_task(self, task_id: str, error: str) -> bool:
        """태스크를 실패 처리합니다."""
        async with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return False
            task.status = TaskStatus.FAILED
            task.error = error
        logger.warning(f"Task failed: [{task_id}] {task.title} - {error}")
        self._check_all_done()
        return True

    # --- 상태 확인 ---

    @property
    def pending_count(self) -> int:
        return sum(1 for t in self._tasks.values() if t.status == TaskStatus.PENDING)

    @property
    def in_progress_count(self) -> int:
        return sum(
            1 for t in self._tasks.values() if t.status == TaskStatus.IN_PROGRESS
        )

    @property
    def completed_count(self) -> int:
        return sum(
            1 for t in self._tasks.values() if t.status == TaskStatus.COMPLETED
        )

    @property
    def all_done(self) -> bool:
        """모든 태스크가 완료(COMPLETED 또는 FAILED)되었는지."""
        return all(
            t.status in (TaskStatus.COMPLETED, TaskStatus.FAILED)
            for t in self._tasks.values()
        )

    def _check_all_done(self) -> None:
        if self.all_done:
            self._completion_event.set()

    async def wait_all_done(self, timeout: float | None = None) -> bool:
        """모든 태스크가 완료될 때까지 대기합니다."""
        if self.all_done:
            return True
        self._completion_event.clear()
        try:
            await asyncio.wait_for(self._completion_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False

    def get_tasks_by_agent(self, agent_name: str) -> list[SharedTask]:
        return [t for t in self._tasks.values() if t.assigned_to == agent_name]

    def summary(self) -> str:
        """태스크 리스트의 텍스트 요약을 반환합니다."""
        lines = [f"Tasks: {len(self._tasks)} total"]
        lines.append(
            f"  pending={self.pending_count} "
            f"in_progress={self.in_progress_count} "
            f"completed={self.completed_count}"
        )
        for task in self._tasks.values():
            assigned = f" -> {task.assigned_to}" if task.assigned_to else ""
            deps = f" (deps: {task.depends_on})" if task.depends_on else ""
            lines.append(
                f"  [{task.id}] {task.status.value:12s} {task.title}{assigned}{deps}"
            )
        return "\n".join(lines)
