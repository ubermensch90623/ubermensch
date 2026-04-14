"""The one Agent primitive every coordination pattern composes.

Keeps the standard Anthropic tool-use loop in one place so the examples
only have to show *how they compose agents*, not how each agent runs.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from anthropic import AsyncAnthropic

from .models import MAX_TOKENS
from .tools import ToolRegistry


@dataclass
class TurnLog:
    agent: str
    input_tokens: int
    output_tokens: int
    cache_read: int
    cache_creation: int


@dataclass
class Agent:
    name: str
    system: str
    model: str
    tools: ToolRegistry | None = None
    client: AsyncAnthropic | None = None
    trace: list[TurnLog] = field(default_factory=list)

    def _client(self) -> AsyncAnthropic:
        if self.client is None:
            self.client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        return self.client

    def _system_blocks(self) -> list[dict]:
        # Marking the shared system prompt as ephemeral lets every agent that
        # shares this prefix hit the cache on subsequent calls.
        return [
            {
                "type": "text",
                "text": self.system,
                "cache_control": {"type": "ephemeral"},
            }
        ]

    async def run(self, user_msg: str, max_turns: int = 6) -> str:
        """Run a standard tool-use loop until the model returns plain text."""
        messages: list[dict] = [{"role": "user", "content": user_msg}]
        tool_schema = self.tools.to_anthropic_schema() if self.tools else None

        for _ in range(max_turns):
            kwargs: dict[str, Any] = dict(
                model=self.model,
                max_tokens=MAX_TOKENS,
                system=self._system_blocks(),
                messages=messages,
            )
            if tool_schema:
                kwargs["tools"] = tool_schema

            resp = await self._client().messages.create(**kwargs)

            u = resp.usage
            self.trace.append(
                TurnLog(
                    agent=self.name,
                    input_tokens=u.input_tokens,
                    output_tokens=u.output_tokens,
                    cache_read=getattr(u, "cache_read_input_tokens", 0) or 0,
                    cache_creation=getattr(u, "cache_creation_input_tokens", 0) or 0,
                )
            )

            if resp.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": resp.content})
                tool_results = []
                for block in resp.content:
                    if block.type == "tool_use":
                        assert self.tools is not None
                        result = await self.tools.call(block.name, dict(block.input))
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": str(result),
                            }
                        )
                messages.append({"role": "user", "content": tool_results})
                continue

            # Final text response
            return "".join(
                b.text for b in resp.content if getattr(b, "type", None) == "text"
            ).strip()

        return "(max turns exceeded)"
