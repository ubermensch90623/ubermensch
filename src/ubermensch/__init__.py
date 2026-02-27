"""Übermensch - Multi-Agent Orchestration Framework"""

__version__ = "0.2.0"

from ubermensch.agents.architect import ArchitectAgent
from ubermensch.agents.debugger import DebuggerAgent
from ubermensch.agents.devils_advocate import DevilsAdvocateAgent
from ubermensch.agents.researcher import ResearcherAgent, SummarizerAgent
from ubermensch.agents.reviewers import (
    CodeReviewerAgent,
    PerformanceReviewerAgent,
    SecurityReviewerAgent,
)
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
    "ArchitectAgent",
    "BaseAgent",
    "CodeReviewerAgent",
    "DebuggerAgent",
    "DevilsAdvocateAgent",
    "Discussion",
    "DiscussionResult",
    "HookContext",
    "HookEvent",
    "HookRegistry",
    "HookResult",
    "Mailbox",
    "MultiDiscussion",
    "PerformanceReviewerAgent",
    "PlanApproval",
    "ResearcherAgent",
    "SecurityReviewerAgent",
    "SharedTask",
    "SharedTaskList",
    "SubagentOrchestrator",
    "SummarizerAgent",
    "TaskResult",
    "TeamMessage",
    "TeamPersistence",
]
