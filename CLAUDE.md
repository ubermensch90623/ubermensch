# Claude Opus 4.7 + Claude Code — Best Practices

Source: <https://claude.com/blog/best-practices-for-using-claude-opus-4-7-with-claude-code>

## Version & model

- Requires Claude Code **v2.1.111 or later** — run `claude update` to upgrade.
- Default model is **Opus 4.7**; **`xhigh`** is the default effort in Claude Code for all plans.

## Effort level

- Start at **`xhigh`** for coding and agentic work; reach for `max` only when `xhigh` isn't enough.
- Change mid-session with `/effort <level>`; drop to `high` (or lower) for routine edits to save tokens and latency.
- Adaptive reasoning lets Claude decide per-step whether to think. Tell it to think more or less directly in the prompt — or here in `CLAUDE.md` — and it will follow within the current effort.

## CLAUDE.md hygiene

- Keep **one shared `CLAUDE.md` at the repo root**, checked into git, with the whole team contributing.
- **When Claude does something wrong, add a rule here** so it isn't repeated.
- Prefer short, imperative rules over long prose.

## Sessions & compaction

- **Start a new session for each new task.** Double-tap `Esc` (or run `/rewind`) to jump back to an earlier message instead of piling context.
- On **Max / Team / Enterprise**, Opus auto-runs with the **1M-token context window** — no configuration needed.
- The Opus 4.7 tokenizer produces **~1.0–1.35× more tokens** for the same text. Leave headroom in `max_tokens` and in compaction triggers.

## Cost & budgets

- Use **task budgets** (public beta) for long agentic runs, e.g. `/config task_budget 50000`. Claude plans around the cap and pauses before exceeding it.
- If a run is trending expensive: drop effort, narrow scope, or split the work into sub-tasks.

## Review & memory

- Use **`/ultrareview`** for deep code review — architecture, security, performance, maintainability. Pro/Max include 3 free per billing cycle.
- Opus 4.7 is noticeably better at **file-based memory** than 4.6. Let it maintain a scratchpad / notes file across sessions for multi-day work.
