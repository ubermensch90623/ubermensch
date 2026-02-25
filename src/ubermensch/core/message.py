"""Agent message types for inter-agent communication."""

from __future__ import annotations

import time
import uuid
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


# --- Agent Teams message types ---


@dataclass
class TeamMessage:
    """에이전트 간 직접 메시지 (Agent Teams 패턴)."""

    sender: str
    recipient: str  # "*" 은 broadcast
    subject: str
    body: Any = None
    timestamp: float = field(default_factory=time.time)
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])


@dataclass
class SharedTask:
    """공유 태스크 리스트의 개별 태스크."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    title: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: str | None = None
    depends_on: list[str] = field(default_factory=list)
    created_by: str = ""
    priority: int = 0
    result: Any = None
    error: str | None = None


@dataclass
class PlanApproval:
    """ArchitectAgent 등의 계획 승인 요청/응답."""

    agent_name: str
    plan: str
    approved: bool = False
    feedback: str | None = None
