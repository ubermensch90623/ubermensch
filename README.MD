# ubermensch

A personal second brain, modeled on [eugeniughelbur/obsidian-second-brain](https://github.com/eugeniughelbur/obsidian-second-brain) but tailored for this owner. The long-term plan is for this repo to grow into a Claude Code skill (slash commands, hooks, scheduled agents) layered on top of an Obsidian vault.

This first cut is intentionally minimal: just the **vault skeleton** and the operating manual that binds any Claude session writing into it. No commands or automation yet — those come later.

## Layout

- `vault/` — the Obsidian vault. Open this folder in Obsidian to use it.
  - `vault/_CLAUDE.md` — operating manual. Read first by any Claude session.
  - `vault/Home.md`, `SOUL.md`, `CRITICAL_FACTS.md`, `index.md`, `log.md` — root-level vault files.
  - `vault/Templates/` — note templates per type. Copy, don't edit in place.
  - `vault/{Daily,Projects,People,Companies,Ideas,Tasks,Dev Logs,Reviews,Boards,Knowledge}/` — note folders.

## How to use

1. Open `vault/` as a vault in Obsidian (or any markdown editor).
2. Read `vault/_CLAUDE.md` to understand the conventions.
3. Fill in `SOUL.md` and `CRITICAL_FACTS.md` with your own identity and ground-truth facts.
4. Start writing notes. Copy from `Templates/` for each new note.

## Roadmap

- [x] Vault skeleton + `_CLAUDE.md`
- [ ] Core save / daily / world commands
- [ ] Thinking tools (challenge / emerge / connect)
- [ ] Research toolkit (x / web / youtube)
- [ ] Scheduled agents + PostCompact hook

## Credits

Patterns and conventions adapted from [`eugeniughelbur/obsidian-second-brain`](https://github.com/eugeniughelbur/obsidian-second-brain) (MIT). No source files were copied verbatim; structure and rule shapes were transcribed.
