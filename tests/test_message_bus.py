import asyncio

import pytest

from ubermensch.message_bus import MessageBus


async def test_exact_topic_delivery():
    bus = MessageBus()
    q = bus.subscribe("facts.raw")
    await bus.publish("facts.raw", {"x": 1})
    msg = await asyncio.wait_for(q.get(), timeout=1.0)
    assert msg == {"topic": "facts.raw", "payload": {"x": 1}}


async def test_wildcard_match():
    bus = MessageBus()
    q = bus.subscribe("summary.*")
    await bus.publish("summary.draft", {"d": "abc"})
    await bus.publish("facts.raw", {"should": "not deliver"})
    msg = await asyncio.wait_for(q.get(), timeout=1.0)
    assert msg["topic"] == "summary.draft"
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(q.get(), timeout=0.1)


async def test_multiple_subscribers_fanout():
    bus = MessageBus()
    a = bus.subscribe("*")
    b = bus.subscribe("facts.raw")
    await bus.publish("facts.raw", {"k": 1})
    assert (await a.get())["topic"] == "facts.raw"
    assert (await b.get())["topic"] == "facts.raw"
