"""Agents module - concrete agent implementations."""

from ubermensch.agents.architect import ArchitectAgent
from ubermensch.agents.debugger import DebuggerAgent
from ubermensch.agents.devils_advocate import DevilsAdvocateAgent
from ubermensch.agents.researcher import ResearcherAgent, SummarizerAgent
from ubermensch.agents.reviewers import (
    CodeReviewerAgent,
    PerformanceReviewerAgent,
    SecurityReviewerAgent,
)
from ubermensch.agents.corp import LearningAgentCorp, TaskForceManager

__all__ = [
    "ResearcherAgent",
    "SummarizerAgent",
    "SecurityReviewerAgent",
    "PerformanceReviewerAgent",
    "CodeReviewerAgent",
    "ArchitectAgent",
    "DevilsAdvocateAgent",
    "DebuggerAgent",
    "LearningAgentCorp",
    "TaskForceManager",
]
