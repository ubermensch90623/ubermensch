"""Shared state: agents coordinate via a persistent store.

- outline_agent writes key `outline`
- body_agent reads `outline`, writes key `draft`
- polish_agent reads `draft`, writes `final`

Warning: this pattern has the highest coordination cost. It is justified only
when agents truly need to mutate shared context concurrently. For the linear
flow shown here, orchestrator-subagent is simpler and preferred.
"""

from __future__ import annotations

import asyncio
import sys

from ubermensch.agent import Agent
from ubermensch.models import MODEL_ORCHESTRATOR, MODEL_WORKER
from ubermensch.prompts import role_prompt
from ubermensch.shared_state import SharedStore

from .._common import load_env, print_trace


async def outline_proc(store: SharedStore, topic: str, agents: list[Agent]) -> None:
    a = Agent(
        name="outline_agent",
        system=role_prompt("outline_agent", "Produce 3 bullet-point subtopics."),
        model=MODEL_WORKER,
    )
    agents.append(a)
    out = await a.run(f"Outline: {topic}")
    await store.set("outline", out, by=a.name)


async def body_proc(store: SharedStore, topic: str, agents: list[Agent]) -> None:
    a = Agent(
        name="body_agent",
        system=role_prompt("body_agent", "Expand an outline into a ~180-word draft."),
        model=MODEL_WORKER,
    )
    agents.append(a)
    # Wait for outline to appear (simple poll keeps the example short).
    while (outline := await store.get("outline")) is None:
        await asyncio.sleep(0.05)
    draft = await a.run(
        f"Topic: {topic}\nOutline:\n{outline}\n\nWrite the draft."
    )
    await store.set("draft", draft, by=a.name)


async def polish_proc(store: SharedStore, agents: list[Agent]) -> None:
    a = Agent(
        name="polish_agent",
        system=role_prompt("polish_agent", "Polish for clarity, keep ~200 words."),
        model=MODEL_ORCHESTRATOR,
    )
    agents.append(a)
    while (draft := await store.get("draft")) is None:
        await asyncio.sleep(0.05)
    final = await a.run(f"Polish this draft:\n{draft}")
    await store.set("final", final, by=a.name)


async def main(topic: str = "multi-agent coordination") -> str:
    load_env()
    store = SharedStore()
    agents: list[Agent] = []

    await asyncio.gather(
        outline_proc(store, topic, agents),
        body_proc(store, topic, agents),
        polish_proc(store, agents),
    )

    final = await store.get("final")
    print("\n=== FINAL SUMMARY ===\n" + (final or "(missing)"))
    print("\n--- store events ---")
    for key in ("outline", "draft", "final"):
        print(f"{key}: {store.events(key)}")
    print_trace("shared_state", *agents)
    return final or ""


if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) or "multi-agent coordination"
    asyncio.run(main(topic))
