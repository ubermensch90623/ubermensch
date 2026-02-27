"""Shared test fixtures."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from ubermensch.agents.corp.organization import LearningAgentCorp


@pytest.fixture
def corp() -> LearningAgentCorp:
    """빈 LearningAgentCorp 인스턴스."""
    return LearningAgentCorp()


@pytest.fixture
def full_corp() -> LearningAgentCorp:
    """전원 채용된 LearningAgentCorp."""
    c = LearningAgentCorp()
    c.hire_all()
    return c


@pytest.fixture
def mock_anthropic():
    """Anthropic API 호출을 모킹합니다."""
    mock_response = AsyncMock()
    mock_response.content = [
        AsyncMock(type="text", text="모킹된 LLM 응답입니다.")
    ]

    with patch("anthropic.AsyncAnthropic") as mock_cls:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_cls.return_value = mock_client
        yield mock_client
