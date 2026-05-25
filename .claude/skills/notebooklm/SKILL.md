---
name: notebooklm
description: Complete API for Google NotebookLM - full programmatic access including features not in the web UI. Create notebooks, add sources, generate all artifact types, download in multiple formats. Activates on explicit /notebooklm or intent like "create a podcast about X"
---
<!-- notebooklm-py v0.4.0 -->
<!-- 출처: teng-lin/notebooklm-py (MIT). 종환 vault 32 소스 · 347 노트북 운영 핵심. -->

# NotebookLM Automation

Complete programmatic access to Google NotebookLM—including capabilities not exposed in the web UI. Create notebooks, add sources (URLs, YouTube, PDFs, audio, video, images), chat with content, generate all artifact types, and download results in multiple formats.

## Installation

**From PyPI (Recommended):**
```bash
pip install notebooklm-py
```

**From GitHub (use latest release tag, NOT main branch):**
```bash
LATEST_TAG=$(curl -s https://api.github.com/repos/teng-lin/notebooklm-py/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
pip install "git+https://github.com/teng-lin/notebooklm-py@${LATEST_TAG}"
```

⚠️ **DO NOT install from main branch**. Always use PyPI or a specific release tag.

**Skill install methods:**
- `notebooklm skill install` installs this skill into supported local agent directories.
- `npx skills add teng-lin/notebooklm-py` installs from GitHub into compatible agent skill directories.

## Prerequisites

**IMPORTANT:** Before using any command, you MUST authenticate:

```bash
notebooklm login    # Opens browser for Google OAuth
notebooklm list     # Verify authentication works
```

If commands fail with authentication errors, re-run `notebooklm login`.

### CI/CD, Multiple Accounts, and Parallel Agents

| Variable | Purpose |
|----------|---------|
| `NOTEBOOKLM_HOME` | Custom config directory (default: `~/.notebooklm`) |
| `NOTEBOOKLM_PROFILE` | Active profile name (default: `default`) |
| `NOTEBOOKLM_AUTH_JSON` | Inline auth JSON - no file writes needed |

**Solutions for parallel workflows:**
1. **Always use explicit notebook ID**: Pass `-n <notebook_id>` (for `wait`/`download`) or `--notebook <notebook_id>`
2. **Per-agent isolation via profiles:** `export NOTEBOOKLM_PROFILE=agent-$ID`
3. **Per-agent isolation via home:** `export NOTEBOOKLM_HOME=/tmp/agent-$ID`
4. **Use full UUIDs:** Avoid partial IDs in automation

## Agent Setup Verification

1. `notebooklm status` → "Authenticated as: email@..."
2. `notebooklm list --json` → valid JSON
3. If either fails → `notebooklm login`

## When This Skill Activates

**Explicit:** "/notebooklm", "use notebooklm", or tool name

**Intent detection:**
- "Create a podcast about [topic]"
- "Summarize these URLs/documents"
- "Generate a quiz from my research"
- "Turn this into an audio overview"
- "Create flashcards for studying"
- "Generate a video explainer"
- "Make an infographic"
- "Create a mind map of the concepts"
- "Download the quiz as markdown"
- "Add these sources to NotebookLM"

## Autonomy Rules

**Run automatically (no confirmation):**
- `notebooklm status` / `auth check` / `list`
- `notebooklm source list` / `artifact list`
- `notebooklm language list/get/set`
- `notebooklm artifact wait` / `source wait` / `research wait` (in subagent context)
- `notebooklm research status`
- `notebooklm use <id>` (⚠️ SINGLE-AGENT ONLY)
- `notebooklm create`, `ask "..."` (without `--save-as-note`)
- `notebooklm history` (read-only)
- `notebooklm source add`
- `notebooklm profile list/create/switch`
- `notebooklm doctor`

**Ask before running:**
- `notebooklm delete` - destructive
- `notebooklm generate *` - long-running, may fail
- `notebooklm download *` - writes to filesystem
- Long-running `wait` commands in main conversation
- `notebooklm ask "..." --save-as-note` / `history --save`

## Quick Reference

| Task | Command |
|------|---------|
| Authenticate | `notebooklm login` |
| Diagnose auth | `notebooklm auth check` |
| List notebooks | `notebooklm list` |
| Create notebook | `notebooklm create "Title"` |
| Set context | `notebooklm use <notebook_id>` |
| Add URL source | `notebooklm source add "https://..."` |
| Add file | `notebooklm source add ./file.pdf` |
| Add YouTube | `notebooklm source add "https://youtube.com/..."` |
| List sources | `notebooklm source list` |
| Delete by ID | `notebooklm source delete <id>` |
| Delete by title | `notebooklm source delete-by-title "Exact Title"` |
| Wait for processing | `notebooklm source wait <id>` |
| Web research (fast) | `notebooklm source add-research "query"` |
| Web research (deep) | `notebooklm source add-research "query" --mode deep --no-wait` |
| Chat | `notebooklm ask "question"` |
| Chat (with refs) | `notebooklm ask "..." --json` |
| Chat (save) | `notebooklm ask "..." --save-as-note` |
| History | `notebooklm history` / `history --save` |
| Get source fulltext | `notebooklm source fulltext <id>` |
| Generate podcast | `notebooklm generate audio "instructions"` |
| Generate video | `notebooklm generate video "instructions"` |
| Generate report | `notebooklm generate report --format briefing-doc` |
| Generate quiz | `notebooklm generate quiz` |
| Revise slide | `notebooklm generate revise-slide "prompt" --artifact <id> --slide 0` |
| Check artifact | `notebooklm artifact list` |
| Wait for completion | `notebooklm artifact wait <artifact_id>` |
| Download audio | `notebooklm download audio ./output.mp3` |
| Download video | `notebooklm download video ./output.mp4` |
| Download slide (PDF) | `notebooklm download slide-deck ./slides.pdf` |
| Download slide (PPTX) | `notebooklm download slide-deck ./slides.pptx --format pptx` |
| Download quiz | `notebooklm download quiz quiz.json` |
| Download flashcards | `notebooklm download flashcards cards.json` |
| Delete notebook | `notebooklm notebook delete <id>` |
| Set language | `notebooklm language set ko` |

**Parallel safety:** Use explicit notebook IDs in parallel workflows. Commands supporting `-n` shorthand: `artifact wait`, `source wait`, `research wait/status`, `download *`. Other commands use `--notebook`.

**Partial IDs:** Use first 6+ characters of UUIDs. Must be unique prefix.

## Generation Types

All generate commands support: `-s, --source`, `--language`, `--json`, `--retry N`

| Type | Command | Options | Download |
|------|---------|---------|----------|
| Podcast | `generate audio` | `--format [deep-dive\|brief\|critique\|debate]`, `--length [short\|default\|long]` | .mp3 |
| Video | `generate video` | `--format [explainer\|brief]`, `--style [auto\|classic\|whiteboard\|...]` | .mp4 |
| Slide Deck | `generate slide-deck` | `--format [detailed\|presenter]`, `--length [default\|short]` | .pdf / .pptx |
| Slide Revision | `generate revise-slide` | `--artifact <id> --slide N` | (re-downloads parent deck) |
| Infographic | `generate infographic` | `--orientation [landscape\|portrait\|square]`, `--detail [concise\|standard\|detailed]`, `--style` | .png |
| Report | `generate report` | `--format [briefing-doc\|study-guide\|blog-post\|custom]`, `--append "..."` | .md |
| Mind Map | `generate mind-map` | (sync, instant) | .json |
| Data Table | `generate data-table` | description required | .csv |
| Quiz | `generate quiz` | `--difficulty`, `--quantity` | .json/.md/.html |
| Flashcards | `generate flashcards` | `--difficulty`, `--quantity` | .json/.md/.html |

## Common Workflows

### Research to Podcast (Interactive)
**Time:** 5-10 minutes total

1. `notebooklm create "Research: [topic]"`
2. `notebooklm source add` for each URL/document
3. Wait for sources: `notebooklm source list --json` until all `status=READY`
4. `notebooklm generate audio "Focus on [angle]"` (confirm)
5. Note the artifact ID returned
6. `notebooklm artifact list` later for status
7. `notebooklm download audio ./podcast.mp3` when complete

### Research to Podcast (Subagent / Automated)

```
Task(
  prompt="Wait for artifact {artifact_id} in notebook {notebook_id} to complete, then download.
   Use: notebooklm artifact wait {artifact_id} -n {notebook_id} --timeout 600
   Then: notebooklm download audio ./podcast.mp3 -a {artifact_id} -n {notebook_id}",
  subagent_type="general-purpose"
)
```

### Bulk Import + Source Waiting (Subagent)

```bash
notebooklm source add "https://url1.com" --json   # → {"source": {"id": "abc...", ...}}
notebooklm source add "https://url2.com" --json   # → {"source": {"id": "def...", ...}}
```

Then spawn agent to `notebooklm source wait` for each ID.

**Source limits (account-side):** Standard 50 / Plus 100 / Pro 300 / Ultra 600 per notebook.
**Supported types:** PDFs, YouTube URLs, web URLs, Google Docs, text files, Markdown, Word docs, EPUB, audio files, video files, images

### Deep Web Research (Subagent)

```bash
notebooklm create "Research: [topic]"
notebooklm source add-research "topic query" --mode deep --no-wait
```

Then subagent waits with `notebooklm research wait -n <id> --import-all --timeout 300`.

**Modes:**
- `--mode fast`: 5-10 sources, seconds
- `--mode deep`: 20+ sources, 2-5 min

**Sources:** `--from web` (default) / `--from drive`

## Output Style

**Progress updates:** Brief status per step
**Fire-and-forget for long ops:** Return artifact ID immediately. Do NOT poll in main conversation.

### JSON output (`--json`)

```bash
notebooklm list --json
notebooklm auth check --json
notebooklm source list --json
notebooklm artifact list --json
```

**Key schemas:**
- `list`: `{"notebooks": [{"id":"...","title":"...","is_owner":true}], "count": N}`
- `source list`: `{"sources": [{"id":"...","title":"...","type":"SourceType.WEB_PAGE","status":"ready|processing|error"}]}`
- `artifact list`: `{"artifacts": [{"id":"...","type":"Audio","status":"in_progress|pending|completed"}]}`

**Status values:**
- Sources: `processing` → `ready` (or `error`)
- Artifacts: `pending` / `in_progress` → `completed`

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| Auth/cookie error | Session expired | `notebooklm auth check` then `notebooklm login` |
| "No notebook context" | Context not set | Use `-n <id>` or `--notebook <id>` (parallel), or `notebooklm use <id>` (single) |
| "No result found for RPC ID" | Rate limiting | Wait 5-10 min, retry |
| `GENERATION_FAILED` | Google rate limit | Wait and retry |
| Download fails | Generation incomplete | Check `artifact list` |
| Invalid ID | Wrong ID | `notebooklm list` to verify |
| RPC protocol error | Google API changed | CLI may need update |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error |
| 2 | Timeout (wait commands only) |

## Known Limitations

**Rate limiting affects:** Audio, video, quiz, flashcards, infographic, slide deck generation
**Reliable operations:** Notebooks (list/create/delete), Sources (add/list/delete), Chat, Mind-map, study-guide, report, data-table

| Operation | Typical | Timeout |
|-----------|---------|---------|
| Source processing | 30s - 10 min | 600s |
| Research (fast) | 30s - 2 min | 180s |
| Research (deep) | 15 - 30+ min | 1800s |
| Mind-map | instant (sync) | n/a |
| Quiz, flashcards | 5 - 15 min | 900s |
| Report, data-table | 5 - 15 min | 900s |
| Audio | 10 - 20 min | 1200s |
| Video | 15 - 45 min | 2700s |

**Polling intervals:** 15-30 seconds when checking manually.

## Language Configuration

Language is a **GLOBAL** setting for artifact generation:

```bash
notebooklm language list             # 80+ supported
notebooklm language get
notebooklm language set ko           # 한국어 (종환 기본)
notebooklm language set en
notebooklm language set zh_Hans
```

**Override per command:**
```bash
notebooklm generate audio --language ja
notebooklm generate video --language zh_Hans
```

**Offline:** `notebooklm language set ko --local`

## Troubleshooting

```bash
notebooklm --help
notebooklm auth check                # Diagnose auth
notebooklm auth check --test         # Full network test
notebooklm doctor                    # Environment health
notebooklm doctor --fix              # Auto-fix
notebooklm --version
notebooklm skill install             # Refresh skill install
```
