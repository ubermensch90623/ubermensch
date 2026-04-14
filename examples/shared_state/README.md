# Shared state

Agents coordinate through a shared store they all read and write. Highest
coordination cost; use only when agents truly need to mutate shared context
concurrently. For linear pipelines, prefer orchestrator-subagent.

Run:
```bash
python -m examples.shared_state "multi-agent coordination"
```
