"""Mailbox - inter-agent direct messaging system."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from ubermensch.core.message import TeamMessage

logger = logging.getLogger(__name__)

BROADCAST = "*"


class Mailbox:
    """에이전트 간 메시징 시스템.

    특징:
        - 1:1 메시지 전송 (send)
        - 전체 브로드캐스트 (broadcast)
        - 비동기 큐 기반 비차단 수신
        - 등록된 에이전트만 수신 가능
    """

    def __init__(self) -> None:
        self._boxes: dict[str, asyncio.Queue[TeamMessage]] = {}
        self._agents: set[str] = set()

    def register(self, agent_name: str) -> None:
        """에이전트를 메일박스에 등록합니다."""
        if agent_name not in self._boxes:
            self._boxes[agent_name] = asyncio.Queue()
            self._agents.add(agent_name)

    def unregister(self, agent_name: str) -> None:
        """에이전트를 메일박스에서 제거합니다."""
        self._boxes.pop(agent_name, None)
        self._agents.discard(agent_name)

    @property
    def registered_agents(self) -> list[str]:
        return list(self._agents)

    async def send(
        self,
        sender: str,
        recipient: str,
        subject: str,
        body: Any = None,
    ) -> TeamMessage:
        """특정 에이전트에게 메시지를 보냅니다."""
        msg = TeamMessage(
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=body,
        )
        box = self._boxes.get(recipient)
        if box is None:
            logger.warning(f"Recipient '{recipient}' not registered in mailbox")
            return msg
        await box.put(msg)
        logger.debug(f"Mail: {sender} -> {recipient}: {subject}")
        return msg

    async def broadcast(
        self,
        sender: str,
        subject: str,
        body: Any = None,
    ) -> TeamMessage:
        """모든 등록된 에이전트에게 메시지를 보냅니다 (발신자 제외)."""
        msg = TeamMessage(
            sender=sender,
            recipient=BROADCAST,
            subject=subject,
            body=body,
        )
        for name, box in self._boxes.items():
            if name != sender:
                await box.put(msg)
        logger.debug(f"Broadcast from {sender}: {subject}")
        return msg

    async def receive(
        self,
        agent_name: str,
        timeout: float | None = None,
    ) -> TeamMessage | None:
        """메시지를 수신합니다. timeout 초 대기 후 None 반환."""
        box = self._boxes.get(agent_name)
        if box is None:
            return None
        try:
            if timeout is not None:
                return await asyncio.wait_for(box.get(), timeout=timeout)
            return await box.get()
        except TimeoutError:
            return None

    def receive_nowait(self, agent_name: str) -> TeamMessage | None:
        """메시지를 비차단 수신합니다."""
        box = self._boxes.get(agent_name)
        if box is None:
            return None
        try:
            return box.get_nowait()
        except asyncio.QueueEmpty:
            return None

    def has_mail(self, agent_name: str) -> bool:
        """수신 대기 중인 메시지가 있는지 확인합니다."""
        box = self._boxes.get(agent_name)
        return box is not None and not box.empty()

    def pending_count(self, agent_name: str) -> int:
        """대기 중인 메시지 수를 반환합니다."""
        box = self._boxes.get(agent_name)
        return box.qsize() if box else 0

    def drain(self, agent_name: str) -> list[TeamMessage]:
        """모든 대기 메시지를 한 번에 가져옵니다."""
        box = self._boxes.get(agent_name)
        if box is None:
            return []
        messages = []
        while not box.empty():
            try:
                messages.append(box.get_nowait())
            except asyncio.QueueEmpty:
                break
        return messages
