# ubermensch

A minimal Python reference implementation of Anthropic's
[five multi-agent coordination patterns](https://claude.com/blog/multi-agent-coordination-patterns).

Each pattern runs the **same** task — "research a topic and write a ~200-word
summary" — so the diff between patterns is purely the coordination shape.
Every example is < 200 lines and runs with a single `python -m` command.

## Which pattern when

| Situation | Pattern | Example |
|---|---|---|
| **Default**, single boss decomposes work | orchestrator-subagent | [`examples/orchestrator_subagent`](examples/orchestrator_subagent) |
| Need an independent check of the output | generator-verifier | [`examples/generator_verifier`](examples/generator_verifier) |
| Subtasks are independent and parallelizable | agent teams | [`examples/agent_teams`](examples/agent_teams) |
| >2 consumers per event, loose coupling matters | message bus | [`examples/message_bus`](examples/message_bus) |
| Agents must mutate shared context concurrently | shared state | [`examples/shared_state`](examples/shared_state) |

**If you're unsure, pick orchestrator-subagent.** Reach for bus or shared
state only when the coordination cost observed in the default pattern
exceeds the complexity cost of the alternative. This mirrors the blog's
own advice: *start with the simplest pattern that works and evolve from there.*

## Layout

```
src/ubermensch/       # shared primitives
  agent.py            # Agent wrapper (tool-use loop + prompt caching)
  tools.py            # @tool decorator + ToolRegistry
  prompts.py          # shared system prompt (cached prefix)
  models.py           # model ids (opus-4-6 / sonnet-4-6)
  domain.py           # deterministic fixture tools (web_search / fetch / fact_check)
  message_bus.py      # asyncio pub/sub (pattern 4)
  shared_state.py     # lock-protected store (pattern 5)
examples/             # one directory per pattern
tests/                # unit tests (bus, store, tools)
```

## Run

```bash
pip install -e ".[dev]"
cp .env.example .env       # fill ANTHROPIC_API_KEY

python -m examples.orchestrator_subagent "prompt caching"
python -m examples.generator_verifier    "prompt caching"
python -m examples.agent_teams           "multi-agent coordination"
python -m examples.message_bus           "prompt caching"
python -m examples.shared_state          "multi-agent coordination"

pytest -q                  # no API key needed for bus/store/tools tests
```

Each example prints:
1. A coordination trace (per-turn token usage per agent, cache hits).
2. The final summary.
3. Totals, so you can compare cost between patterns on the same task.

## Deliberate simplifications

These keep the reference readable; they are **not** production guidance.

- No distributed transport. The message bus and shared store are in-process
  asyncio only.
- No persistence — the shared store lives only for the run.
- No retries/backoff beyond what the SDK provides.
- Fake domain tools (`domain.py`) instead of a real web-search provider:
  reviewers focus on coordination, not retrieval.
- No framework dependency (no pydantic, no LangChain-style graph) — just
  `anthropic` + stdlib + `asyncio`.
- No streaming, no extended thinking, no multi-modal — orthogonal to
  coordination.

## References

- [Multi-agent coordination patterns](https://claude.com/blog/multi-agent-coordination-patterns)
- [When to use multi-agent systems](https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them)
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
