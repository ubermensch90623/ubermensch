# The Unreasonable Effectiveness of HTML

A static HTML reproduction of the Claude Code infographic — built as a proof of
its own thesis: AI artifacts read better as visual HTML than as walls of
markdown.

## Open it

```
open index.html        # macOS
xdg-open index.html    # Linux
```

No server, no install.

## Build a single shareable file

Inlines every CSS and JS file into one self-contained `dist/artifact.html`:

```
node build.mjs
```

That single file is what you'd attach to a Slack thread, upload to S3, or share
as one link.

## Obsidian × Claude Desktop quiz workflow

The `install/` directory has a complete setup for using this HTML-first
approach on Windows with an Obsidian vault. It includes:

- `INSTALL-WINDOWS.md` — step-by-step setup (10–15 min)
- `claude_desktop_config.example.json` — drop-in Claude Desktop config
- `quiz-prompt.md` — reusable prompt template for the vault
- `quiz-template.html` — empty quiz skeleton for Claude to fill
- `sample-econ-quiz.html` — a fully working example, open it directly in a
  browser to see what the workflow produces

