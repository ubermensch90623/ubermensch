"""Agent message types for inter-agent communication."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentMessage:
    """Main Agent -> Subagent 로 전달되는 작업 요청."""

    task: str
    context: dict[str, Any] = field(default_factory=dict)
    priority: int = 0


@dataclass
class TaskResult:
    """Subagent -> Main Agent 로 반환되는 작업 결과."""

    agent_name: str
    status: TaskStatus
    data: Any = None
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.status == TaskStatus.COMPLETED
