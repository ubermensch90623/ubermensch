"""Discussion pipeline 유닛 테스트."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.discussion import Discussion, MultiDiscussion
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus


class StubAgent(BaseAgent):
    """테스트용 에이전트. 호출 횟수에 따라 다른 응답 반환."""

    def __init__(self, name: str, responses: list[str] | None = None):
        super().__init__(name=name, system_prompt=f"Stub {name}")
        self.responses = responses or [f"{name} response"]
        self._call_count = 0

    async def execute(self, message: AgentMessage) -> TaskResult:
        text = self.responses[min(self._call_count, len(self.responses) - 1)]
        self._call_count += 1
        return TaskResult(
            agent_name=self.name,
            status=TaskStatus.COMPLETED,
            data=text,
        )


class FailStubAgent(BaseAgent):
    """항상 실패하는 테스트용 에이전트."""

    def __init__(self, name: str = "fail_stub"):
        super().__init__(name=name)

    async def execute(self, message: AgentMessage) -> TaskResult:
        return TaskResult(
            agent_name=self.name,
            status=TaskStatus.FAILED,
            error="Intentional failure",
        )


def _mock_consensus_client(consensus_text: str = "합의 결과"):
    mock_response = MagicMock()
    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = consensus_text
    mock_response.content = [mock_block]

    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    return mock_client


class TestDiscussion:
    async def test_basic_discussion(self):
        presenter = StubAgent("reviewer", ["Initial analysis", "Addressed criticism"])
        critic = StubAgent("advocate", ["I challenge your analysis"])

        disc = Discussion(presenter=presenter, critic=critic, rounds=1)
        disc._client = _mock_consensus_client("Final consensus")

        result = await disc.run("Review security")

        assert result.topic == "Review security"
        assert result.presenter_name == "reviewer"
        assert result.critic_name == "advocate"
        assert len(result.turns) == 3  # analysis + challenge + response
        assert result.turns[0].role == "analysis"
        assert result.turns[1].role == "challenge"
        assert result.turns[2].role == "response"
        assert result.consensus == "Final consensus"

    async def test_multiple_rounds(self):
        presenter = StubAgent("p", ["Analysis", "Response 1", "Response 2"])
        critic = StubAgent("c", ["Challenge 1", "Challenge 2"])

        disc = Discussion(presenter=presenter, critic=critic, rounds=2)
        disc._client = _mock_consensus_client()

        result = await disc.run("Topic")

        # 1 analysis + 2*(challenge + response) = 5 turns
        assert len(result.turns) == 5
        assert result.turns[0].role == "analysis"
        assert result.turns[1].role == "challenge"
        assert result.turns[2].role == "response"
        assert result.turns[3].role == "challenge"
        assert result.turns[4].role == "response"

    async def test_discussion_with_context(self):
        presenter = StubAgent("p", ["Found SQL injection"])
        critic = StubAgent("c", ["False positive"])

        disc = Discussion(presenter=presenter, critic=critic, rounds=1)
        disc._client = _mock_consensus_client()

        result = await disc.run(
            "Security review",
            context={"code": "SELECT * FROM users"},
        )
        assert result.turns[0].content == "Found SQL injection"

    async def test_failed_presenter(self):
        presenter = FailStubAgent("fail_presenter")
        critic = StubAgent("c", ["Challenge"])

        disc = Discussion(presenter=presenter, critic=critic, rounds=1)
        disc._client = _mock_consensus_client()

        result = await disc.run("Topic")
        assert "[FAILED]" in result.turns[0].content

    async def test_min_rounds(self):
        """rounds=0이면 최소 1라운드."""
        presenter = StubAgent("p", ["A", "R"])
        critic = StubAgent("c", ["C"])

        disc = Discussion(presenter=presenter, critic=critic, rounds=0)
        disc._client = _mock_consensus_client()

        result = await disc.run("Topic")
        assert len(result.turns) == 3  # 최소 1라운드


class TestDiscussionExtractText:
    def test_extract_string(self):
        result = TaskResult("a", TaskStatus.COMPLETED, data="hello")
        assert Discussion._extract_text(result) == "hello"

    def test_extract_dict_analysis(self):
        result = TaskResult("a", TaskStatus.COMPLETED, data={"analysis": "found bug"})
        assert Discussion._extract_text(result) == "found bug"

    def test_extract_dict_plan(self):
        result = TaskResult("a", TaskStatus.COMPLETED, data={"plan": "build it"})
        assert Discussion._extract_text(result) == "build it"

    def test_extract_failed(self):
        result = TaskResult("a", TaskStatus.FAILED, error="oops")
        assert "[FAILED]" in Discussion._extract_text(result)

    def test_extract_other_type(self):
        result = TaskResult("a", TaskStatus.COMPLETED, data=42)
        assert Discussion._extract_text(result) == "42"


class TestMultiDiscussion:
    async def test_multi_agent_discussion(self):
        agents = [
            StubAgent("security", ["Security analysis", "Security cross-review"]),
            StubAgent("performance", ["Performance analysis", "Performance cross-review"]),
            StubAgent("quality", ["Quality analysis", "Quality cross-review"]),
        ]

        multi = MultiDiscussion(agents=agents, rounds=1)
        multi._client = _mock_consensus_client("Multi consensus")

        result = await multi.run("Review the code")

        assert result.topic == "Review the code"
        # 3 initial analyses + 3 cross-reviews = 6 turns
        assert len(result.turns) == 6
        # First 3 are analyses
        assert all(t.role == "analysis" for t in result.turns[:3])
        # Next 3 are challenges
        assert all(t.role == "challenge" for t in result.turns[3:])
        assert result.consensus == "Multi consensus"

    async def test_multi_with_context(self):
        agents = [
            StubAgent("a", ["A analysis", "A review"]),
            StubAgent("b", ["B analysis", "B review"]),
        ]

        multi = MultiDiscussion(agents=agents, rounds=1)
        multi._client = _mock_consensus_client()

        result = await multi.run("Topic", context={"code": "x = 1"})
        assert len(result.turns) == 4  # 2 analyses + 2 cross-reviews
