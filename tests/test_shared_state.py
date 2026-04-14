import asyncio

from ubermensch.shared_state import SharedStore


async def test_set_get_events():
    s = SharedStore()
    await s.set("k", 1, by="writer")
    assert await s.get("k") == 1
    evs = s.events("k")
    assert evs and evs[0]["by"] == "writer"


async def test_update_is_serialized():
    s = SharedStore()
    await s.set("counter", 0)

    async def inc():
        await s.update("counter", lambda v: (v or 0) + 1, by="inc")

    await asyncio.gather(*(inc() for _ in range(50)))
    assert await s.get("counter") == 50
    assert len(s.events("counter")) == 51  # 1 set + 50 updates
