"""Core module - Agent framework essentials"""

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.discussion import Discussion, DiscussionResult, MultiDiscussion
from ubermensch.core.hooks import HookContext, HookEvent, HookRegistry, HookResult
from ubermensch.core.mailbox import Mailbox
from ubermensch.core.message import (
    AgentMessage,
    PlanApproval,
    SharedTask,
    TaskResult,
    TeamMessage,
)
from ubermensch.core.orchestrator import SubagentOrchestrator
from ubermensch.core.persistence import TeamPersistence
from ubermensch.core.shared_task_list import SharedTaskList
from ubermensch.core.team import AgentTeam

__all__ = [
    "AgentMessage",
    "AgentTeam",
    "BaseAgent",
    "Discussion",
    "DiscussionResult",
    "HookContext",
    "HookEvent",
    "HookRegistry",
    "HookResult",
    "Mailbox",
    "MultiDiscussion",
    "PlanApproval",
    "SharedTask",
    "SharedTaskList",
    "SubagentOrchestrator",
    "TaskResult",
    "TeamMessage",
    "TeamPersistence",
]
