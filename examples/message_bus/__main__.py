"""Message bus: event-driven fan-out without a central orchestrator.

Pipeline:
    researcher  -> publishes facts.raw
    summarizer  -> subscribes facts.raw, publishes summary.draft
    editor      -> subscribes summary.*, publishes summary.final

Use when you have multiple independent consumers per event or want loose
coupling. For simpler task flows prefer orchestrator-subagent.
"""

from __future__ import annotations

import asyncio
import sys

from ubermensch.agent import Agent
from ubermensch.message_bus import MessageBus
from ubermensch.models import MODEL_ORCHESTRATOR, MODEL_WORKER
from ubermensch.prompts import role_prompt
from ubermensch.tools import ToolRegistry
from ubermensch import domain

from .._common import load_env, print_trace


async def researcher_proc(bus: MessageBus, topic: str, agent_box: list[Agent]) -> None:
    tools = ToolRegistry().register(domain.web_search).register(domain.fetch)
    agent = Agent(
        name="researcher",
        system=role_prompt("researcher", "Return 3-4 sentences of raw findings."),
        model=MODEL_WORKER,
        tools=tools,
    )
    agent_box.append(agent)
    facts = await agent.run(f"Research: {topic}")
    await bus.publish("facts.raw", {"topic": topic, "facts": facts})


async def summarizer_proc(bus: MessageBus, agent_box: list[Agent]) -> None:
    q = bus.subscribe("facts.raw")
    agent = Agent(
        name="summarizer",
        system=role_prompt("summarizer", "Compress findings into a ~150-word draft."),
        model=MODEL_WORKER,
    )
    agent_box.append(agent)
    msg = await q.get()
    draft = await agent.run(
        f"Summarize these facts about {msg['payload']['topic']!r}:\n"
        f"{msg['payload']['facts']}"
    )
    await bus.publish("summary.draft", {"draft": draft})


async def editor_proc(bus: MessageBus, agent_box: list[Agent]) -> str:
    q = bus.subscribe("summary.*")
    agent = Agent(
        name="editor",
        system=role_prompt("editor", "Polish for clarity; keep to ~200 words."),
        model=MODEL_ORCHESTRATOR,
    )
    agent_box.append(agent)
    msg = await q.get()
    final = await agent.run(f"Edit this draft:\n{msg['payload']['draft']}")
    await bus.publish("summary.final", {"final": final})
    return final


async def main(topic: str = "prompt caching") -> str:
    load_env()
    bus = MessageBus()
    agents: list[Agent] = []

    editor_task = asyncio.create_task(editor_proc(bus, agents))
    summarizer_task = asyncio.create_task(summarizer_proc(bus, agents))
    # small yield so subscribers register before researcher publishes
    await asyncio.sleep(0)
    await researcher_proc(bus, topic, agents)
    await summarizer_task
    final = await editor_task

    print("\n=== FINAL SUMMARY ===\n" + final)
    print_trace("message_bus", *agents)
    return final


if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) or "prompt caching"
    asyncio.run(main(topic))
