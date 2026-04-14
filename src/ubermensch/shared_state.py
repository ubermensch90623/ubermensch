"""In-memory shared state with lock-protected update.

Deliberate simplifications:
- No persistence; lives only for the run.
- One global asyncio.Lock; fine for a small reference.
- Per-key append-only event log for auditability.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class SharedStore:
    _data: dict[str, Any] = field(default_factory=dict)
    _events: dict[str, list[dict]] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def get(self, key: str) -> Any:
        return self._data.get(key)

    async def set(self, key: str, value: Any, *, by: str = "unknown") -> None:
        async with self._lock:
            self._data[key] = value
            self._events.setdefault(key, []).append({"by": by, "op": "set"})

    async def update(self, key: str, fn: Callable[[Any], Any], *, by: str = "unknown") -> Any:
        async with self._lock:
            new = fn(self._data.get(key))
            self._data[key] = new
            self._events.setdefault(key, []).append({"by": by, "op": "update"})
            return new

    def events(self, key: str) -> list[dict]:
        return list(self._events.get(key, []))

    def snapshot(self) -> dict[str, Any]:
        return dict(self._data)
