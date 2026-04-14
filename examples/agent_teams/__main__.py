"""Agent teams: orchestrator-subagent + parallel execution.

The diff from examples.orchestrator_subagent is intentionally small: the
orchestrator first plans subtopics (via a `plan_subtopics` tool), then we
run all researcher subagents concurrently with asyncio.gather, then the
orchestrator writes the final summary from the combined findings.

Use this pattern when subtasks are independent and parallelizable.
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


_PLAN: list[str] = []


@tool(
    "plan_subtopics",
    "Submit a list of 2-3 subtopics to research in parallel. Pass JSON array of strings as 'subtopics'.",
)
def plan_subtopics(subtopics: str) -> str:
    _PLAN.clear()
    _PLAN.extend(json.loads(subtopics))
    return f"planned {len(_PLAN)} subtopics"


async def _researcher(subtopic: str) -> tuple[Agent, str]:
    tools = ToolRegistry().register(domain.web_search).register(domain.fetch)
    agent = Agent(
        name=f"researcher[{subtopic[:18]}]",
        system=role_prompt("researcher", "Return 2-3 sentences of findings."),
        model=MODEL_WORKER,
        tools=tools,
    )
    findings = await agent.run(f"Research: {subtopic}")
    return agent, findings


async def main(topic: str = "multi-agent coordination") -> str:
    load_env()

    planner = Agent(
        name="planner",
        system=role_prompt(
            "planner",
            "Call plan_subtopics with 2-3 concise subtopics covering the topic.",
        ),
        model=MODEL_ORCHESTRATOR,
        tools=ToolRegistry().register(plan_subtopics),
    )
    await planner.run(f"Plan subtopics for: {topic}")
    if not _PLAN:
        _PLAN.extend([topic])

    results = await asyncio.gather(*(_researcher(s) for s in _PLAN))
    sub_agents = [a for a, _ in results]
    findings = [{"subtopic": s, "findings": f} for s, (_, f) in zip(_PLAN, results)]

    writer = Agent(
        name="writer",
        system=role_prompt(
            "writer",
            "Combine the provided findings into a ~200-word summary.",
        ),
        model=MODEL_ORCHESTRATOR,
    )
    summary = await writer.run(
        "Write a ~200-word summary from these findings:\n" + json.dumps(findings, indent=2)
    )
    print("\n=== FINAL SUMMARY ===\n" + summary)
    print_trace("agent_teams", planner, *sub_agents, writer)
    return summary


if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) or "multi-agent coordination"
    asyncio.run(main(topic))
