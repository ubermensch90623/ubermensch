"""Model identifiers used across examples.

Opus for reasoning-heavy roles (orchestrator, verifier).
Sonnet for worker/subagent roles where cost and latency matter more.
"""

MODEL_ORCHESTRATOR = "claude-opus-4-6"
MODEL_WORKER = "claude-sonnet-4-6"
MAX_TOKENS = 1024
