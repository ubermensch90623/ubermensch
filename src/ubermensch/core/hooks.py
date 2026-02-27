"""Hook system - event-driven quality gates for Agent Teams.

Claude Code Agent Teams의 TeammateIdle, TaskCompleted 훅을 구현합니다.
훅은 이벤트 발생 시 콜백을 실행하고, 콜백 결과로 이벤트를 차단하거나
피드백을 전달할 수 있습니다.

사용 예:
    hooks = HookRegistry()

    @hooks.on(HookEvent.TASK_COMPLETED)
    async def validate_tests(ctx: HookContext) -> HookResult:
        if "test" not in ctx.data.get("result", ""):
            return HookResult(block=True, feedback="테스트가 포함되어야 합니다.")
        return HookResult(block=False)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)


class HookEvent(Enum):
    """훅이 트리거되는 이벤트 타입."""

    TEAMMATE_IDLE = "teammate_idle"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TEAMMATE_SPAWNED = "teammate_spawned"
    TEAMMATE_SHUTDOWN = "teammate_shutdown"
    MESSAGE_SENT = "message_sent"
    PLAN_SUBMITTED = "plan_submitted"


@dataclass
class HookContext:
    """훅 콜백에 전달되는 컨텍스트."""

    event: HookEvent
    agent_name: str = ""
    task_id: str = ""
    task_title: str = ""
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class HookResult:
    """훅 콜백의 반환값.

    block=True이면 이벤트를 차단합니다.
    feedback이 있으면 에이전트에게 전달됩니다.
    """

    block: bool = False
    feedback: str = ""


# 훅 콜백 타입
HookCallback = Callable[[HookContext], Awaitable[HookResult]]


class HookRegistry:
    """이벤트-콜백 레지스트리.

    특징:
        - 이벤트당 여러 콜백 등록 가능
        - 하나라도 block=True면 전체 block
        - 모든 피드백을 수집하여 반환
        - 데코레이터 방식 등록 지원
    """

    def __init__(self) -> None:
        self._hooks: dict[HookEvent, list[HookCallback]] = {
            event: [] for event in HookEvent
        }

    def register(self, event: HookEvent, callback: HookCallback) -> None:
        """콜백을 이벤트에 등록합니다."""
        self._hooks[event].append(callback)
        logger.debug(f"Hook registered: {event.value} -> {callback.__name__}")

    def on(self, event: HookEvent) -> Callable[[HookCallback], HookCallback]:
        """데코레이터 방식으로 훅을 등록합니다.

        @hooks.on(HookEvent.TASK_COMPLETED)
        async def my_hook(ctx: HookContext) -> HookResult:
            ...
        """

        def decorator(func: HookCallback) -> HookCallback:
            self.register(event, func)
            return func

        return decorator

    def unregister(self, event: HookEvent, callback: HookCallback) -> None:
        """콜백을 제거합니다."""
        try:
            self._hooks[event].remove(callback)
        except ValueError:
            pass

    def clear(self, event: HookEvent | None = None) -> None:
        """특정 이벤트 또는 전체 훅을 제거합니다."""
        if event is not None:
            self._hooks[event] = []
        else:
            for e in HookEvent:
                self._hooks[e] = []

    def has_hooks(self, event: HookEvent) -> bool:
        """해당 이벤트에 등록된 훅이 있는지 확인합니다."""
        return len(self._hooks[event]) > 0

    async def trigger(self, context: HookContext) -> HookResult:
        """이벤트를 트리거하고 모든 콜백을 실행합니다.

        Returns:
            통합된 HookResult:
            - block: 하나라도 block이면 True
            - feedback: 모든 피드백을 줄바꿈으로 합침
        """
        callbacks = self._hooks.get(context.event, [])
        if not callbacks:
            return HookResult(block=False)

        blocked = False
        feedbacks: list[str] = []

        for callback in callbacks:
            try:
                result = await callback(context)
                if result.block:
                    blocked = True
                if result.feedback:
                    feedbacks.append(result.feedback)
            except Exception as e:
                logger.error(
                    f"Hook {callback.__name__} for {context.event.value} "
                    f"raised: {e}"
                )
                feedbacks.append(f"Hook error ({callback.__name__}): {e}")

        return HookResult(
            block=blocked,
            feedback="\n".join(feedbacks) if feedbacks else "",
        )
