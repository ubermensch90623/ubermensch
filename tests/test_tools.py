import asyncio

from ubermensch.tools import ToolRegistry, tool


@tool("add", "Add two integers.")
def add(a: int, b: int) -> int:
    return a + b


@tool("hello", "Say hello.")
async def hello(name: str) -> str:
    return f"hi {name}"


async def test_schema_roundtrip():
    reg = ToolRegistry().register(add).register(hello)
    schemas = reg.to_anthropic_schema()
    names = {s["name"] for s in schemas}
    assert names == {"add", "hello"}
    add_schema = next(s for s in schemas if s["name"] == "add")
    assert add_schema["input_schema"]["properties"]["a"]["type"] == "integer"
    assert "a" in add_schema["input_schema"]["required"]


async def test_call_sync_and_async():
    reg = ToolRegistry().register(add).register(hello)
    assert await reg.call("add", {"a": 2, "b": 3}) == 5
    assert await reg.call("hello", {"name": "world"}) == "hi world"
