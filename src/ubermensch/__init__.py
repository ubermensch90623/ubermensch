"""Übermensch - Multi-Agent Orchestration Framework"""

__version__ = "0.2.0"

# Core
from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.mailbox import Mailbox
from ubermensch.core.message import (
    AgentMessage,
    PlanApproval,
    SharedTask,
    TaskResult,
    TeamMessage,
)
from ubermensch.core.orchestrator import SubagentOrchestrator
from ubermensch.core.shared_task_list import SharedTaskList
from ubermensch.core.team import AgentTeam

# Agents
from ubermensch.agents.architect import ArchitectAgent
from ubermensch.agents.debugger import DebuggerAgent
from ubermensch.agents.devils_advocate import DevilsAdvocateAgent
from ubermensch.agents.researcher import ResearcherAgent, SummarizerAgent
from ubermensch.agents.reviewers import (
    CodeReviewerAgent,
    PerformanceReviewerAgent,
    SecurityReviewerAgent,
)

__all__ = [
    # Core
    "BaseAgent",
    "SubagentOrchestrator",
    "AgentTeam",
    "SharedTaskList",
    "Mailbox",
    # Messages
    "AgentMessage",
    "TaskResult",
    "TeamMessage",
    "SharedTask",
    "PlanApproval",
    # Agents (8)
    "ResearcherAgent",
    "SummarizerAgent",
    "SecurityReviewerAgent",
    "PerformanceReviewerAgent",
    "CodeReviewerAgent",
    "ArchitectAgent",
    "DevilsAdvocateAgent",
    "DebuggerAgent",
]
