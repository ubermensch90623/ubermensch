"""Übermensch - Multi-Agent Orchestration Framework

API 키 없이도 바로 사용 가능합니다:

    from ubermensch import AgentTeam, MockProvider

    # Mock 모드 (API 키 불필요)
    team = AgentTeam(name="my-team", provider=MockProvider())

    # API 키가 환경변수에 있으면 자동 감지
    team = AgentTeam(name="my-team")

    # 코드에서 한 번만 설정
    from ubermensch import configure
    configure(api_key="sk-ant-...")
"""

__version__ = "0.3.0"

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
from ubermensch.core.provider import (
    AnthropicProvider,
    LLMProvider,
    MockProvider,
    configure,
    get_provider,
)
from ubermensch.core.shared_task_list import SharedTaskList
from ubermensch.core.team import AgentTeam

__all__ = [
    "AgentMessage",
    "AgentTeam",
    "AnthropicProvider",
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
    "LLMProvider",
    "Mailbox",
    "MockProvider",
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
    "configure",
    "get_provider",
]
