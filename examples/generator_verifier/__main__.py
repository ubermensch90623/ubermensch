"""Generator-verifier: writer + fact-checker loop.

A writer (Sonnet) drafts a summary. A verifier (Opus) fact-checks it using the
domain `fact_check` tool and returns an explicit verdict via `submit_verdict`.
We loop until approved or N attempts exhausted.

Use this pattern when a second agent can apply criteria the first cannot
self-evaluate (factuality, tests pass, schema valid, etc.).
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


_LAST_VERDICT: dict = {}


@tool(
    "submit_verdict",
    "Submit a verification verdict. approved is a boolean; reasons explains failures.",
)
def submit_verdict(approved: bool, reasons: str) -> str:
    _LAST_VERDICT["approved"] = approved
    _LAST_VERDICT["reasons"] = reasons
    return "ok"


async def main(topic: str = "prompt caching", max_rounds: int = 3) -> str:
    load_env()

    writer = Agent(
        name="writer",
        system=role_prompt(
            "writer",
            "Produce a ~200-word summary. Keep claims verifiable.",
        ),
        model=MODEL_WORKER,
    )

    verifier_tools = (
        ToolRegistry().register(domain.fact_check).register(submit_verdict)
    )
    verifier = Agent(
        name="verifier",
        system=role_prompt(
            "verifier",
            "Check each factual claim with fact_check, then call submit_verdict. "
            "Criteria: factuality (no unsupported claims), length ~200 words.",
        ),
        model=MODEL_ORCHESTRATOR,
        tools=verifier_tools,
    )

    draft = await writer.run(f"Write a ~200-word summary of: {topic}")
    feedback = ""

    for round_num in range(1, max_rounds + 1):
        _LAST_VERDICT.clear()
        await verifier.run(
            "Verify this draft and call submit_verdict with your result.\n\n"
            f"DRAFT:\n{draft}"
        )
        verdict = dict(_LAST_VERDICT)
        print(f"[round {round_num}] verdict={json.dumps(verdict)}")
        if verdict.get("approved"):
            break
        feedback = verdict.get("reasons", "unspecified")
        draft = await writer.run(
            f"Revise your summary of {topic!r}. Verifier feedback: {feedback}\n\n"
            f"Previous draft:\n{draft}"
        )

    print("\n=== FINAL SUMMARY ===\n" + draft)
    print_trace("generator_verifier", writer, verifier)
    return draft


if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) or "prompt caching"
    asyncio.run(main(topic))
