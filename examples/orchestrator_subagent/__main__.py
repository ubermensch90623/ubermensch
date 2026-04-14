"""Orchestrator-subagent: the recommended default pattern.

One orchestrator (Opus) decomposes a topic into subtopics and delegates each
to a fresh researcher subagent (Sonnet) via a tool call. The orchestrator
then writes the final summary from the returned findings.

This is deliberately sequential. For the parallel variant, see examples.agent_teams.
"""

from __future__ import annotations

import asyncio
import json
import sys

from ubermensch.agent import Agent
from ubermensch.models import MODEL_ORCHESTRATOR, MODEL_WORKER
from ubermensch.prompts import role_prompt
from ubermensch.tools import ToolRegistry, tool
from ubermensch import domain

from .._common import load_env, print_trace


async def _run_researcher(subtopic: str) -> str:
    researcher_tools = ToolRegistry().register(domain.web_search).register(domain.fetch)
    researcher = Agent(
        name="researcher",
        system=role_prompt("researcher", "Return 2-3 sentences of findings."),
        model=MODEL_WORKER,
        tools=researcher_tools,
    )
    result = await researcher.run(f"Research this subtopic briefly: {subtopic}")
    # Let the orchestrator's trace also see the subagent's turns.
    _SUBAGENT_TRACES.append(researcher)
    return result


_SUBAGENT_TRACES: list[Agent] = []


@tool(
    "spawn_researcher",
    "Spawn a researcher subagent on a subtopic and return its findings.",
)
async def spawn_researcher(subtopic: str) -> str:
    findings = await _run_researcher(subtopic)
    return json.dumps({"subtopic": subtopic, "findings": findings})


async def main(topic: str = "multi-agent coordination") -> str:
    load_env()
    orch_tools = ToolRegistry().register(spawn_researcher)
    orchestrator = Agent(
        name="orchestrator",
        system=role_prompt(
            "orchestrator",
            "Decompose the topic into 2-3 subtopics, call spawn_researcher for "
            "each, then write a ~200-word summary from their findings.",
        ),
        model=MODEL_ORCHESTRATOR,
        tools=orch_tools,
    )
    summary = await orchestrator.run(f"Produce a ~200-word summary of: {topic}")
    print("\n=== FINAL SUMMARY ===\n" + summary)
    print_trace("orchestrator_subagent", orchestrator, *_SUBAGENT_TRACES)
    return summary


if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) or "multi-agent coordination"
    asyncio.run(main(topic))
