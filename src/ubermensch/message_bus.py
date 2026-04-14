"""Minimal in-process pub/sub bus.

Deliberate simplifications:
- Single process, asyncio only (no network transport).
- Topic patterns support a trailing '*' wildcard (e.g. 'research.*').
- No retention: subscribers only receive events published after they subscribe.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field


@dataclass
class MessageBus:
    _subscribers: list[tuple[str, asyncio.Queue]] = field(default_factory=list)

    def subscribe(self, topic_pattern: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers.append((topic_pattern, q))
        return q

    async def publish(self, topic: str, payload: dict) -> None:
        for pattern, q in self._subscribers:
            if _match(pattern, topic):
                await q.put({"topic": topic, "payload": payload})


def _match(pattern: str, topic: str) -> bool:
    if pattern == topic:
        return True
    if pattern.endswith(".*"):
        return topic.startswith(pattern[:-1])
    if pattern == "*":
        return True
    return False
