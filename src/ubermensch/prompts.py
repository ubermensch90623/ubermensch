"""Shared system prompts.

The SHARED_SYSTEM prefix is stable across every agent so that the prompt cache
can be reused on subsequent calls within the 5-minute TTL. Role-specific
suffixes are appended via `role_prompt`.
"""

SHARED_SYSTEM = """\
You are part of the ubermensch reference system demonstrating Anthropic's
multi-agent coordination patterns. You cooperate with other Claude instances
to research a topic and produce a concise summary (target ~200 words).

General rules:
- Be concise; prefer short, verifiable claims over long exposition.
- When you use a tool, call it with the minimum arguments needed.
- Return plain text as the final answer unless a structured tool is provided.
- Do not fabricate sources; if a claim cannot be supported, say so.
"""


def role_prompt(role: str, extra: str = "") -> str:
    """Build a role-specific prompt on top of the cached shared prefix."""
    suffix = f"\n\nYour role: {role}."
    if extra:
        suffix += f"\n{extra}"
    return SHARED_SYSTEM + suffix
