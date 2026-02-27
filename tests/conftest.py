"""공유 테스트 fixture 및 헬퍼.

테스트 전반에서 사용되는 공통 에이전트, mock 팩토리 등을 정의합니다.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus

# --- 공용 Fake 에이전트 ---


class FakeAgent(BaseAgent):
    """테스트용 가짜 에이전트. execute()는 즉시 성공을 반환."""

    def __init__(self, name: str = "fake", delay: float = 0, **kwargs):
        super().__init__(name=name, system_prompt=f"Fake agent {name}")
        self.delay = delay
        self.executed_tasks: list[str] = []

    async def execute(self, message: AgentMessage) -> TaskResult:
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        self.executed_tasks.append(message.task)
        return TaskResult(
            agent_name=self.name,
            status=TaskStatus.COMPLETED,
            data=f"Done: {message.task}",
        )


class FailingAgent(BaseAgent):
    """테스트용 항상 실패하는 에이전트."""

    def __init__(self, name: str = "failer", **kwargs):
        super().__init__(name=name, system_prompt="Always fails")

    async def execute(self, message: AgentMessage) -> TaskResult:
        return TaskResult(
            agent_name=self.name,
            status=TaskStatus.FAILED,
            error="Intentional failure",
        )


class StubAgent(BaseAgent):
    """테스트용 에이전트. 호출 횟수에 따라 다른 응답 반환."""

    def __init__(self, name: str, responses: list[str] | None = None, **kwargs):
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


# --- Mock 팩토리 ---


def make_mock_llm_client(response_text: str = "mocked response") -> MagicMock:
    """LLM API 클라이언트 mock을 생성합니다."""
    mock_response = MagicMock()
    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = response_text
    mock_response.content = [mock_block]

    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    return mock_client


def mock_ask_llm(return_value: str = "mocked response"):
    """BaseAgent.ask_llm을 mock하는 patch 컨텍스트 매니저."""
    from unittest.mock import patch

    return patch.object(BaseAgent, "ask_llm", new_callable=AsyncMock, return_value=return_value)


# --- 공용 Fixtures ---


@pytest.fixture
def fake_agent():
    """단일 FakeAgent fixture."""
    return FakeAgent("test_agent")


@pytest.fixture
def failing_agent():
    """단일 FailingAgent fixture."""
    return FailingAgent("test_failer")
