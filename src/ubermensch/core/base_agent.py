"""Base agent class - all agents inherit from this."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus, TeamMessage
from ubermensch.core.provider import LLMProvider, get_provider

if TYPE_CHECKING:
    from ubermensch.core.mailbox import Mailbox
    from ubermensch.core.shared_task_list import SharedTaskList

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """에이전트 기본 클래스.

    모든 서브에이전트는 이 클래스를 상속하고 execute()를 구현해야 합니다.
    Claude API를 통해 LLM 호출이 필요할 때 self.ask_llm()을 사용합니다.

    Agent Teams 지원:
        AgentTeam.spawn_teammate()로 등록하면 _team_mailbox와 _team_task_list가
        자동으로 설정되어 팀 내 메시징과 태스크 관리가 가능합니다.

    Provider:
        provider 인자로 LLM 프로바이더를 지정할 수 있습니다.
        미지정 시 글로벌 설정 또는 자동 감지를 사용합니다.
    """

    def __init__(
        self,
        name: str,
        model: str = "claude-sonnet-4-20250514",
        system_prompt: str | None = None,
        provider: LLMProvider | None = None,
    ):
        self.name = name
        self.model = model
        self.system_prompt = system_prompt or f"You are {name}, a helpful AI agent."
        self._provider: LLMProvider | None = provider
        self._tools: list[dict[str, Any]] = []
        # Agent Teams 인프라 (AgentTeam이 주입)
        self._team_mailbox: Mailbox | None = None
        self._team_task_list: SharedTaskList | None = None
        self._received_messages: list[TeamMessage] = []

    @property
    def provider(self) -> LLMProvider:
        """이 에이전트가 사용하는 LLM 프로바이더."""
        if self._provider is None:
            self._provider = get_provider()
        return self._provider

    @property
    def in_team(self) -> bool:
        """이 에이전트가 팀에 속해 있는지 여부."""
        return self._team_mailbox is not None

    def register_tool(self, tool_definition: dict[str, Any]) -> None:
        """에이전트가 사용할 수 있는 도구를 등록합니다."""
        self._tools.append(tool_definition)

    async def ask_llm(
        self,
        prompt: str,
        context: list[dict[str, Any]] | None = None,
        max_tokens: int = 4096,
    ) -> str:
        """LLM을 호출하여 응답을 받습니다."""
        messages = context or []
        messages.append({"role": "user", "content": prompt})

        return await self.provider.complete(
            messages=messages,
            model=self.model,
            system=self.system_prompt,
            max_tokens=max_tokens,
            tools=self._tools or None,
        )

    # --- Agent Teams 메시징 ---

    async def send_message(
        self, recipient: str, subject: str, body: Any = None
    ) -> TeamMessage | None:
        """팀 내 다른 에이전트에게 메시지를 보냅니다."""
        if self._team_mailbox is None:
            logger.warning(f"[{self.name}] Not in a team, cannot send message")
            return None
        return await self._team_mailbox.send(self.name, recipient, subject, body)

    async def broadcast_message(self, subject: str, body: Any = None) -> TeamMessage | None:
        """팀 전체에 브로드캐스트 메시지를 보냅니다."""
        if self._team_mailbox is None:
            return None
        return await self._team_mailbox.broadcast(self.name, subject, body)

    def get_received_messages(self) -> list[TeamMessage]:
        """수신된 메시지 목록을 반환합니다."""
        return list(self._received_messages)

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
