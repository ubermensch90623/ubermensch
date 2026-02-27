"""Hook 시스템 - 팀 이벤트에 반응하는 콜백 인프라.

지원 이벤트:
    - TeammateIdle: 팀원이 할 일이 없을 때
    - TaskCompleted: 태스크가 완료되었을 때
    - TaskFailed: 태스크가 실패했을 때
    - AgentJoined: 새 에이전트가 팀에 합류했을 때
    - AgentLeft: 에이전트가 팀에서 나갔을 때
    - AllTasksDone: 모든 태스크가 완료되었을 때
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)

# Hook 콜백 타입: async def handler(event: HookEvent) -> None
HookHandler = Callable[["HookEvent"], Coroutine[Any, Any, None]]


class HookType(Enum):
    """훅 이벤트 타입."""

    TEAMMATE_IDLE = "teammate_idle"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    AGENT_JOINED = "agent_joined"
    AGENT_LEFT = "agent_left"
    ALL_TASKS_DONE = "all_tasks_done"


@dataclass
class HookEvent:
    """훅 이벤트 데이터."""

    type: HookType
    agent_name: str = ""
    task_id: str = ""
    task_title: str = ""
    data: Any = None
    team_name: str = ""


class HookRegistry:
    """훅 등록 및 실행 관리.

    사용 예시:
        hooks = HookRegistry()

        @hooks.on(HookType.TASK_COMPLETED)
        async def on_complete(event):
            print(f"{event.agent_name} completed {event.task_title}")

        @hooks.on(HookType.TEAMMATE_IDLE)
        async def on_idle(event):
            # 유휴 에이전트에게 새 작업 할당
            ...

        await hooks.emit(HookEvent(
            type=HookType.TASK_COMPLETED,
            agent_name="plumber",
            task_title="Keep 노트 파싱",
        ))
    """

    def __init__(self) -> None:
        self._handlers: dict[HookType, list[HookHandler]] = {
            hook_type: [] for hook_type in HookType
        }

    def on(self, hook_type: HookType) -> Callable[[HookHandler], HookHandler]:
        """데코레이터: 특정 이벤트 타입에 핸들러를 등록합니다.

        @hooks.on(HookType.TASK_COMPLETED)
        async def handler(event):
            ...
        """

        def decorator(handler: HookHandler) -> HookHandler:
            self._handlers[hook_type].append(handler)
            logger.debug(
                f"Hook registered: {hook_type.value} -> {handler.__name__}"
            )
            return handler

        return decorator

    def register(self, hook_type: HookType, handler: HookHandler) -> None:
        """핸들러를 프로그래밍 방식으로 등록합니다."""
        self._handlers[hook_type].append(handler)

    def unregister(self, hook_type: HookType, handler: HookHandler) -> None:
        """핸들러를 제거합니다."""
        handlers = self._handlers.get(hook_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def clear(self, hook_type: HookType | None = None) -> None:
        """핸들러를 초기화합니다. hook_type 지정 시 해당 타입만."""
        if hook_type:
            self._handlers[hook_type] = []
        else:
            for ht in HookType:
                self._handlers[ht] = []

    async def emit(self, event: HookEvent) -> list[Exception]:
        """이벤트를 발생시키고 등록된 핸들러를 실행합니다.

        모든 핸들러를 병렬로 실행하며, 개별 핸들러 에러가
        다른 핸들러에 영향을 주지 않습니다.

        Returns:
            발생한 예외 목록 (없으면 빈 리스트)
        """
        handlers = self._handlers.get(event.type, [])
        if not handlers:
            return []

        logger.debug(
            f"Emitting {event.type.value}: "
            f"{len(handlers)} handler(s) "
            f"[agent={event.agent_name}, task={event.task_title}]"
        )

        results = await asyncio.gather(
            *(h(event) for h in handlers),
            return_exceptions=True,
        )

        errors: list[Exception] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                handler_name = handlers[i].__name__
                logger.error(
                    f"Hook handler '{handler_name}' failed for "
                    f"{event.type.value}: {result}"
                )
                errors.append(result)

        return errors

    def handler_count(self, hook_type: HookType | None = None) -> int:
        """등록된 핸들러 수."""
        if hook_type:
            return len(self._handlers.get(hook_type, []))
        return sum(len(h) for h in self._handlers.values())

    @property
    def registered_types(self) -> list[HookType]:
        """핸들러가 등록된 이벤트 타입 목록."""
        return [ht for ht in HookType if self._handlers.get(ht)]
