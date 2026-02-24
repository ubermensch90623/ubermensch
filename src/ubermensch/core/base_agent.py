"""Base agent class - all agents inherit from this."""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any

import anthropic

from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """에이전트 기본 클래스.

    모든 서브에이전트는 이 클래스를 상속하고 execute()를 구현해야 합니다.
    Claude API를 통해 LLM 호출이 필요할 때 self.ask_llm()을 사용합니다.
    """

    def __init__(
        self,
        name: str,
        model: str = "claude-sonnet-4-20250514",
        system_prompt: str | None = None,
    ):
        self.name = name
        self.model = model
        self.system_prompt = system_prompt or f"You are {name}, a helpful AI agent."
        self._client: anthropic.AsyncAnthropic | None = None
        self._tools: list[dict[str, Any]] = []

    @property
    def client(self) -> anthropic.AsyncAnthropic:
        if self._client is None:
            self._client = anthropic.AsyncAnthropic()
        return self._client

    def register_tool(self, tool_definition: dict[str, Any]) -> None:
        """에이전트가 사용할 수 있는 도구를 등록합니다."""
        self._tools.append(tool_definition)

    async def ask_llm(
        self,
        prompt: str,
        context: list[dict[str, Any]] | None = None,
        max_tokens: int = 4096,
    ) -> str:
        """Claude API를 호출하여 응답을 받습니다."""
        messages = context or []
        messages.append({"role": "user", "content": prompt})

        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": self.system_prompt,
            "messages": messages,
        }
        if self._tools:
            kwargs["tools"] = self._tools

        response = await self.client.messages.create(**kwargs)

        # 텍스트 블록만 추출
        text_parts = [
            block.text for block in response.content if block.type == "text"
        ]
        return "\n".join(text_parts)

    @abstractmethod
    async def execute(self, message: AgentMessage) -> TaskResult:
        """서브에이전트의 핵심 로직. 하위 클래스에서 구현해야 합니다."""
        ...

    async def run(self, message: AgentMessage) -> TaskResult:
        """에이전트를 실행합니다. 에러 핸들링 포함."""
        logger.info(f"[{self.name}] Starting task: {message.task}")
        try:
            result = await self.execute(message)
            logger.info(f"[{self.name}] Task completed: {result.status.value}")
            return result
        except Exception as e:
            logger.error(f"[{self.name}] Task failed: {e}")
            return TaskResult(
                agent_name=self.name,
                status=TaskStatus.FAILED,
                error=str(e),
            )
