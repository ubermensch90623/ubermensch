"""에이전트 유닛 테스트.

모든 LLM 호출과 외부 I/O는 mock하여 순수 로직만 테스트합니다.
"""

from unittest.mock import AsyncMock, patch

import pytest

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
from ubermensch.core.message import AgentMessage, TaskStatus


# --- 공통 헬퍼 ---


def mock_ask_llm(return_value: str = "mocked response"):
    """ask_llm을 mock하는 데코레이터 팩토리."""
    return patch.object(
        BaseAgent, "ask_llm", new_callable=AsyncMock, return_value=return_value
    )


# --- BaseAgent 테스트 ---


class TestBaseAgent:
    def test_default_properties(self):
        agent = SecurityReviewerAgent()
        assert agent.name == "security_reviewer"
        assert agent.in_team is False
        assert agent.get_received_messages() == []

    def test_register_tool(self):
        agent = SecurityReviewerAgent()
        agent.register_tool({"name": "test_tool"})
        assert len(agent._tools) == 1

    async def test_run_catches_exception(self):
        """execute에서 예외 발생 시 FAILED TaskResult를 반환."""

        class BrokenAgent(BaseAgent):
            async def execute(self, message):
                raise RuntimeError("boom")

        agent = BrokenAgent(name="broken")
        result = await agent.run(AgentMessage(task="crash"))
        assert result.status == TaskStatus.FAILED
        assert "boom" in result.error

    async def test_send_message_without_team(self):
        agent = SecurityReviewerAgent()
        result = await agent.send_message("bob", "hello")
        assert result is None

    async def test_broadcast_without_team(self):
        agent = SecurityReviewerAgent()
        result = await agent.broadcast_message("hello")
        assert result is None


# --- SecurityReviewerAgent 테스트 ---


class TestSecurityReviewer:
    async def test_execute_with_code(self):
        agent = SecurityReviewerAgent()
        with mock_ask_llm("SQL injection found: HIGH severity"):
            result = await agent.run(
                AgentMessage(
                    task="Review login endpoint",
                    context={"code": "SELECT * FROM users WHERE id='{user_input}'"},
                )
            )
        assert result.success
        assert result.data["review_type"] == "security"
        assert "SQL injection" in result.data["analysis"]

    async def test_execute_with_file_paths(self):
        agent = SecurityReviewerAgent()
        with mock_ask_llm("No issues found"):
            result = await agent.run(
                AgentMessage(
                    task="Review auth module",
                    context={"file_paths": ["src/auth.py", "src/login.py"]},
                )
            )
        assert result.success

    async def test_execute_minimal(self):
        agent = SecurityReviewerAgent()
        with mock_ask_llm("Clean"):
            result = await agent.run(AgentMessage(task="Quick check"))
        assert result.success


# --- PerformanceReviewerAgent 테스트 ---


class TestPerformanceReviewer:
    async def test_execute_with_code_and_metrics(self):
        agent = PerformanceReviewerAgent()
        with mock_ask_llm("N+1 query found: HIGH impact"):
            result = await agent.run(
                AgentMessage(
                    task="Review database queries",
                    context={
                        "code": "for user in users: db.query(user.id)",
                        "metrics": {"avg_response_ms": 1500},
                    },
                )
            )
        assert result.success
        assert result.data["review_type"] == "performance"

    async def test_execute_minimal(self):
        agent = PerformanceReviewerAgent()
        with mock_ask_llm("All good"):
            result = await agent.run(AgentMessage(task="Quick perf check"))
        assert result.success


# --- CodeReviewerAgent 테스트 ---


class TestCodeReviewer:
    async def test_execute_with_code_and_tests(self):
        agent = CodeReviewerAgent()
        with mock_ask_llm("Missing edge case tests for negative input"):
            result = await agent.run(
                AgentMessage(
                    task="Review calculator module",
                    context={
                        "code": "def add(a, b): return a + b",
                        "tests": "def test_add(): assert add(1, 2) == 3",
                    },
                )
            )
        assert result.success
        assert result.data["review_type"] == "code_quality"

    async def test_execute_with_pr_diff(self):
        agent = CodeReviewerAgent()
        with mock_ask_llm("Clean diff"):
            result = await agent.run(
                AgentMessage(
                    task="Review PR",
                    context={"pr_diff": "+ def new_func(): pass"},
                )
            )
        assert result.success


# --- ArchitectAgent 테스트 ---


class TestArchitect:
    async def test_plan_only_mode(self):
        agent = ArchitectAgent()
        with mock_ask_llm("Phase 1: Design API\nPhase 2: Implement"):
            result = await agent.run(
                AgentMessage(
                    task="Design notification system",
                    context={"plan_only": True},
                )
            )
        assert result.success
        assert result.data["type"] == "plan"
        assert result.data["requires_approval"] is True

    async def test_analysis_mode(self):
        agent = ArchitectAgent()
        with mock_ask_llm("Architecture looks solid"):
            result = await agent.run(
                AgentMessage(
                    task="Analyze existing system",
                    context={"plan_only": False},
                )
            )
        assert result.success
        assert result.data["type"] == "analysis"
        assert result.data["requires_approval"] is False

    async def test_implementation_guide_with_approved_plan(self):
        agent = ArchitectAgent()
        with mock_ask_llm("Step 1: Create models\nStep 2: Add routes"):
            result = await agent.run(
                AgentMessage(
                    task="Implement notification system",
                    context={"approved_plan": "Use WebSocket with Redis pub/sub"},
                )
            )
        assert result.success
        assert result.data["type"] == "implementation_guide"
        assert result.data["requires_approval"] is False

    async def test_with_constraints(self):
        agent = ArchitectAgent()
        with mock_ask_llm("Constrained plan"):
            result = await agent.run(
                AgentMessage(
                    task="Design with limits",
                    context={
                        "plan_only": True,
                        "constraints": "Max 100MB memory",
                        "existing_architecture": "Monolith",
                    },
                )
            )
        assert result.success


# --- DevilsAdvocateAgent 테스트 ---


class TestDevilsAdvocate:
    async def test_challenge_findings(self):
        agent = DevilsAdvocateAgent()
        with mock_ask_llm("CHALLENGES:\n1. The analysis assumes single-threaded..."):
            result = await agent.run(
                AgentMessage(
                    task="Review security analysis",
                    context={
                        "findings": "No race conditions found",
                        "source_agent": "security_reviewer",
                    },
                )
            )
        assert result.success
        assert result.data["review_type"] == "devils_advocate"
        assert result.data["source_agent"] == "security_reviewer"

    async def test_challenge_hypothesis(self):
        agent = DevilsAdvocateAgent()
        with mock_ask_llm("The hypothesis has weak evidence"):
            result = await agent.run(
                AgentMessage(
                    task="Challenge debugging hypothesis",
                    context={"hypothesis": "Memory leak in connection pool"},
                )
            )
        assert result.success

    async def test_minimal(self):
        agent = DevilsAdvocateAgent()
        with mock_ask_llm("No strong objections"):
            result = await agent.run(AgentMessage(task="Quick review"))
        assert result.success


# --- DebuggerAgent 테스트 ---


class TestDebugger:
    async def test_full_investigation(self):
        agent = DebuggerAgent()
        with mock_ask_llm("Hypothesis 1: Connection timeout (70%)\n"
                          "Hypothesis 2: Race condition (20%)"):
            result = await agent.run(
                AgentMessage(
                    task="Investigate connection drops",
                    context={
                        "symptoms": "WebSocket drops after first message",
                        "error_logs": "Connection closed unexpectedly",
                        "code": "async def handle(ws): await ws.send(data)",
                        "environment": "Python 3.11, websockets 12.0",
                    },
                )
            )
        assert result.success
        assert result.data["investigation_type"] == "competing_hypothesis"

    async def test_with_other_hypotheses(self):
        agent = DebuggerAgent()
        with mock_ask_llm("Challenging hypothesis: Memory leak unlikely"):
            result = await agent.run(
                AgentMessage(
                    task="Cross-validate hypotheses",
                    context={
                        "other_hypotheses": [
                            "Memory leak in pool",
                            "DNS resolution failure",
                        ],
                    },
                )
            )
        assert result.success

    async def test_minimal(self):
        agent = DebuggerAgent()
        with mock_ask_llm("Need more info"):
            result = await agent.run(AgentMessage(task="Debug crash"))
        assert result.success


# --- SummarizerAgent 테스트 ---


class TestSummarizer:
    async def test_summarize_text(self):
        agent = SummarizerAgent()
        with mock_ask_llm("요약: AI 에이전트 시스템의 핵심은..."):
            result = await agent.run(
                AgentMessage(
                    task="Summarize this article",
                    context={"text": "Long article about AI agents..."},
                )
            )
        assert result.success
        assert "summary" in result.data

    async def test_summarize_with_max_length(self):
        agent = SummarizerAgent()
        with mock_ask_llm("Short summary"):
            result = await agent.run(
                AgentMessage(
                    task="Brief summary",
                    context={"text": "Content here", "max_length": "100 words"},
                )
            )
        assert result.success


# --- ResearcherAgent 테스트 ---


class TestResearcher:
    async def test_research_with_urls(self):
        agent = ResearcherAgent()
        mock_crawl_result = type(
            "CrawlResult", (), {
                "url": "https://example.com",
                "title": "Example",
                "text": "Example content",
                "links": [],
                "status_code": 200,
            }
        )()

        with patch.object(
            agent.crawler, "fetch_multiple",
            new_callable=AsyncMock,
            return_value=[mock_crawl_result],
        ), mock_ask_llm("Analysis of example.com content"):
            result = await agent.run(
                AgentMessage(
                    task="Analyze example.com",
                    context={"urls": ["https://example.com"]},
                )
            )
        assert result.success
        assert result.data["sources"] == ["https://example.com"]

    async def test_research_no_results(self):
        agent = ResearcherAgent()
        with patch.object(
            agent.crawler, "search_and_fetch",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await agent.run(AgentMessage(task="Search nothing"))
        assert result.status == TaskStatus.FAILED
