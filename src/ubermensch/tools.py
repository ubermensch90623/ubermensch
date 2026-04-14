"""Tiny tool registry.

A `@tool` decorator converts a typed Python function into an Anthropic
tool schema and stores it in a `ToolRegistry` for execution during
`messages.create` tool-use loops.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable, get_type_hints


_PY_TO_JSON = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


def _schema_for(fn: Callable) -> dict:
    hints = get_type_hints(fn)
    sig = inspect.signature(fn)
    props: dict[str, dict] = {}
    required: list[str] = []
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        py_type = hints.get(name, str)
        json_type = _PY_TO_JSON.get(py_type, "string")
        props[name] = {"type": json_type}
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return {"type": "object", "properties": props, "required": required}


@dataclass
class _ToolEntry:
    name: str
    description: str
    fn: Callable[..., Any]
    schema: dict


def tool(name: str, description: str) -> Callable:
    """Mark a function as an Anthropic tool.

    The callable may be sync or async; `ToolRegistry.call` awaits when needed.
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        fn.__tool__ = _ToolEntry(  # type: ignore[attr-defined]
            name=name, description=description, fn=fn, schema=_schema_for(fn)
        )
        return fn

    return decorator


@dataclass
class ToolRegistry:
    entries: dict[str, _ToolEntry] = field(default_factory=dict)

    def register(self, fn: Callable[..., Any]) -> "ToolRegistry":
        entry = getattr(fn, "__tool__", None)
        if entry is None:
            raise TypeError(f"{fn!r} was not decorated with @tool")
        self.entries[entry.name] = entry
        return self

    def to_anthropic_schema(self) -> list[dict]:
        return [
            {
                "name": e.name,
                "description": e.description,
                "input_schema": e.schema,
            }
            for e in self.entries.values()
        ]

    async def call(self, name: str, arguments: dict) -> Any:
        entry = self.entries[name]
        result = entry.fn(**arguments)
        if inspect.isawaitable(result):
            result = await result
        return result
