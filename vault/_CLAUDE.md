# _CLAUDE.md — Vault operating manual

This file is read first by any Claude session that operates on this vault. It encodes the rules that bind every read and write. If you are Claude: comply with this file before doing anything else.

## 1. Precedence

This file overrides skill defaults. Skill defaults apply only where this file is silent. If you find a contradiction between this file and a skill's documentation, this file wins inside this vault.

## 2. AI-first preamble — every note

Every note must open with a `## For future Claude` block immediately after the frontmatter. The block has three lines:

```
## For future Claude

This note is a [type] about [topic] saved on [YYYY-MM-DD]. It [main purpose].
[Optional: staleness caveat, confidence qualifier, or scope limitation.]
```

The preamble exists so a future Claude session pulling this single note (with zero surrounding context) still understands what it is and why it was written.

## 3. Universal frontmatter — every note

Every note has YAML frontmatter with at minimum:

```yaml
---
date: YYYY-MM-DD       # creation or last update date
type: <note-type>      # one of the schemas in section 4
tags: [<type>, ...]    # must include the type as a tag; lowercase
ai-first: true         # explicit compliance flag
---
```

`ai-first: true` is the compliance signal. Notes without it are treated as legacy and need a rewrite pass.

## 4. Type-specific frontmatter schemas

Add these fields on top of the universal block.

| Type | Additional fields |
|---|---|
| `daily` | `mood: ""` (optional), `energy: ""` (optional) |
| `project` | `updated: YYYY-MM-DD`, `status: active\|planning\|completed\|archived\|on-hold`, `related-people: []`, `related-projects: []` |
| `person` | `updated: YYYY-MM-DD`, `role: ""`, `company: "[[Companies/...]]"`, `relationship: weak\|medium\|strong`, `last-interaction: YYYY-MM-DD`, `related-projects: []` |
| `idea` | `status: captured\|exploring\|graduated\|shelved`, `related-projects: []` |
| `task` | `status: in-progress\|done\|waiting\|cancelled`, `priority: high\|medium\|low`, `due: YYYY-MM-DD`, `related-projects: []`, `related-people: []` |
| `decision` | `related-projects: []`, `confidence: stated\|high\|medium\|speculation`, `sources: []` |
| `devlog` | `project: "[[Projects/...]]"`, `related-people: []` |
| `review` | `period-start: YYYY-MM-DD`, `period-end: YYYY-MM-DD`, `period: weekly\|monthly\|quarterly` |
| `adr` | `decision: ""`, `status: proposed\|accepted\|superseded`, `related-projects: []`, `supersedes: "[[Knowledge/ADR-...]]"` (optional) |

When in doubt, prefer `type: knowledge` with whatever extra fields make the note self-contained.

## 5. Recency markers

Every external claim needs an inline date and source:

```
- Mem0 raised $24M Series A (as of 2026-04, mem0.ai/blog/series-a)
- Anthropic released native memory (as of 2026-02, anthropic.com/news/memory)
```

Pattern: `(as of YYYY-MM, source-url)`. URL is preserved verbatim — no shortening, no paraphrasing. The point is re-verifiability.

## 6. Confidence levels

Mark every non-trivial claim with one of:

- `stated` — directly quoted or claimed by the source
- `high` — multiple independent sources agree
- `medium` — single source, plausible
- `speculation` — author inference, not sourced

Inline form: `(confidence: medium)`. Frontmatter form: `confidence: high`. Use frontmatter for whole-note confidence; inline for per-claim.

## 7. Wiki-links — mandatory

Every entity reference uses `[[Folder/Name]]` syntax. Examples:

- `[[People/Eugeniu Ghelbur]]`
- `[[Projects/Ubermensch]]`
- `[[Companies/Anthropic]]`
- `[[Knowledge/Bi-temporal-facts]]`

Plain-text names break the graph. If the target stub does not yet exist, **create it** as a minimal note (frontmatter + preamble) so the link resolves. Future-Claude cannot traverse what it cannot link.

## 8. Propagation — every write touches multiple pages

Writing one note in isolation is vault rot. Every meaningful write also updates:

- `Home.md` — if the change is dashboard-relevant (active project, today's focus, open question)
- `Boards/` — if it changes a kanban-tracked status
- `Daily/<today>.md` — if the change is an event worth logging today
- `index.md` — if a new note type or category is introduced
- `log.md` — append `YYYY-MM-DD HH:MM | actor | summary` for every meaningful write

A vault is a graph; writes are graph mutations, not file appends.

## 9. Naming and style

- **Headers**: sentence case (`## What it does`, not `## What It Does`).
- **Emojis**: not in vault output. Allowed only in explicit UI elements that ship as part of the skill.
- **Em-dashes**: not in user-facing prose. Use a regular hyphen with spaces, or restructure the sentence.
- **Dates**: ISO `YYYY-MM-DD` everywhere. Never `today`, `yesterday`, `last week` in metadata.
- **Tags**: lowercase, kebab-case if multi-word. Always include the note's `type` as a tag.
- **Filenames**: human-readable, sentence case for titles, ISO date for daily notes (`Daily/2026-05-06.md`).
- **YAML strings**: double-quote when uncertain (special chars, leading symbols).

## 10. Anti-patterns

| Pattern | Problem |
|---|---|
| `date: today` | Meaningless when read later. Use `YYYY-MM-DD`. |
| Bare claims without dates | "X is the leader" — leader when? |
| Missing source URLs | Cannot re-verify. Breaks audit trail. |
| Plain-text names instead of `[[wikilinks]]` | Breaks graph traversal. |
| Narrative prose instead of structure | Bullets and headers retrieve better than paragraphs. |
| `ai-first: true` omitted | Signals non-compliance; legacy note. |
| Orphan notes | Every note links to or from at least one other note. |
| "see above", "as mentioned" | Not self-contained. Future-Claude pulls one note at a time. |

## 11. Folder map

| Folder | Purpose | Default `type` |
|---|---|---|
| `Daily/` | One file per day, `YYYY-MM-DD.md`, log of what happened | `daily` |
| `Projects/` | One file per active or archived project | `project` |
| `People/` | One file per person, by name | `person` |
| `Companies/` | One file per company | `company` |
| `Ideas/` | Captured ideas, graduated to projects when ready | `idea` |
| `Tasks/` | Standalone tasks not tied to a project's own list | `task` |
| `Dev Logs/` | Development logs, technical decisions, debug sessions | `devlog` |
| `Reviews/` | Weekly, monthly, quarterly reviews | `review` |
| `Boards/` | Kanban boards (markdown checkbox lists or Kanban-plugin format) | (mixed) |
| `Knowledge/` | Distilled, durable knowledge: ADRs, principles, frameworks | `knowledge` or `adr` |
| `Templates/` | Note templates per type. Copy, don't edit in place. | (templates) |

## 12. Root-level vault files

- `Home.md` — dashboard. Active projects, today's focus, recent decisions, open questions.
- `SOUL.md` — identity, values, working style, long-term goals. The "who you are" file.
- `CRITICAL_FACTS.md` — always-true facts. Keep under ~120 tokens. Loaded into every Claude context.
- `index.md` — catalog of notes. Auto-maintained.
- `log.md` — audit trail. Append-only.
