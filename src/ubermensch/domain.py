"""Deterministic fixture tools shared across examples.

These stand in for real web-search / retrieval so the examples are
reproducible, cheap, and focus the reviewer's attention on the
coordination patterns rather than retrieval quality.
"""

from __future__ import annotations

import json
from .tools import tool


_FIXTURES: dict[str, list[dict]] = {
    "prompt caching": [
        {
            "title": "Prompt caching overview",
            "url": "https://docs.claude.com/prompt-caching",
            "snippet": "Prompt caching lets you reuse large static prefixes across requests, reducing cost and latency via cache_control blocks.",
        },
        {
            "title": "When to cache",
            "url": "https://docs.claude.com/prompt-caching#when",
            "snippet": "Cache stable content such as system prompts, tool definitions, and long documents that are reused across requests.",
        },
    ],
    "multi-agent coordination": [
        {
            "title": "Five coordination patterns",
            "url": "https://claude.com/blog/multi-agent-coordination-patterns",
            "snippet": "Generator-verifier, orchestrator-subagent (recommended default), agent teams, message bus, shared state.",
        },
        {
            "title": "When to use multi-agent systems",
            "url": "https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them",
            "snippet": "Start with the simplest pattern; only add coordination machinery when the default's cost exceeds the alternative's complexity.",
        },
    ],
}

_ARTICLES: dict[str, str] = {
    "https://docs.claude.com/prompt-caching": (
        "Prompt caching stores a prefix of a prompt so future requests that share "
        "the same prefix skip re-processing it. You mark blocks with cache_control. "
        "Caches are ephemeral (~5 minutes) and billed at reduced rates on hits."
    ),
    "https://docs.claude.com/prompt-caching#when": (
        "Good candidates: long system prompts, few-shot examples, large documents. "
        "Bad candidates: user-turn tails that change every request."
    ),
    "https://claude.com/blog/multi-agent-coordination-patterns": (
        "The blog describes five patterns. Orchestrator-subagent is the recommended "
        "default; reach for bus or shared state only when their coordination cost is "
        "justified by observed pain in the default."
    ),
    "https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them": (
        "Multi-agent systems pay off when subtasks are independent and parallelizable, "
        "or when an explicit verifier catches errors a single agent cannot self-detect."
    ),
}


def _lookup(query: str) -> list[dict]:
    q = query.lower().strip()
    for key, hits in _FIXTURES.items():
        if key in q:
            return hits
    # fall back to a generic hit so examples always return something
    return [
        {
            "title": f"Reference entry for {query}",
            "url": f"https://example.com/{query.replace(' ', '-')}",
            "snippet": f"Placeholder reference material for the topic: {query}.",
        }
    ]


@tool("web_search", "Search the reference knowledge base; returns a list of {title,url,snippet}.")
def web_search(query: str) -> str:
    return json.dumps(_lookup(query))


@tool("fetch", "Fetch the full text of a URL previously returned by web_search.")
def fetch(url: str) -> str:
    return _ARTICLES.get(url, f"(no article body on file for {url})")


@tool(
    "fact_check",
    "Check a factual claim against the reference corpus; returns {verdict, evidence}.",
)
def fact_check(claim: str) -> str:
    c = claim.lower()
    corpus = " ".join(_ARTICLES.values()).lower()
    # Crude heuristic: if any content word of the claim appears, call it supported.
    tokens = [t for t in c.split() if len(t) > 4]
    supported = sum(1 for t in tokens if t in corpus)
    verdict = "supported" if supported >= max(1, len(tokens) // 3) else "unsupported"
    return json.dumps({"verdict": verdict, "matches": supported, "tokens": len(tokens)})
