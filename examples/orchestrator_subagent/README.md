# Orchestrator-subagent (default)

Use this pattern by default. An orchestrator decomposes the task and delegates
discrete subtasks to short-lived subagents via the `spawn_researcher` tool,
then composes the final answer.

Run:
```bash
python -m examples.orchestrator_subagent "prompt caching"
```
