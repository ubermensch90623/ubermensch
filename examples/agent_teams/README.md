# Agent teams

Orchestrator-subagent with parallel execution. Subagents run concurrently via
`asyncio.gather`. Use when subtasks are independent.

Run:
```bash
python -m examples.agent_teams "multi-agent coordination"
```
