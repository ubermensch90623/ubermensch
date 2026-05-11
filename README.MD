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

