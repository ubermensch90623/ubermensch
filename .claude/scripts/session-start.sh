#!/bin/bash
set -eo pipefail
cd "$CLAUDE_PROJECT_DIR"

# Persist vault path for the session
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export VAULT_PATH=\"$CLAUDE_PROJECT_DIR\"" >> "$CLAUDE_ENV_FILE"
fi

# Incremental QMD re-index (fast, non-blocking if qmd not installed)
qmd update 2>/dev/null || true

# Helper: run a command with a timeout, fall back to alternative
run_with_timeout() {
  local timeout_sec=$1; shift
  local fallback_cmd=$1; shift
  if command -v gtimeout &>/dev/null; then
    gtimeout "$timeout_sec" "$@" 2>/dev/null || eval "$fallback_cmd"
  elif command -v timeout &>/dev/null; then
    timeout "$timeout_sec" "$@" 2>/dev/null || eval "$fallback_cmd"
  else
    "$@" 2>/dev/null || eval "$fallback_cmd"
  fi
}

# Build context summary
echo "## Session Context"
echo ""
echo "### Date"
echo "$(date +%Y-%m-%d) ($(date +%A))"
echo ""

echo "### North Star (current goals)"
if command -v obsidian &>/dev/null; then
  run_with_timeout 5 'cat brain/North\ Star.md 2>/dev/null | head -30' obsidian read file="North Star" | head -30
else
  cat brain/North\ Star.md 2>/dev/null | head -30 || echo "(not found)"
fi
echo ""

echo "### Recent Changes (last 48h)"
git log --oneline --since="48 hours ago" --no-merges 2>/dev/null | head -15 || echo "(no git history)"
echo ""

echo "### Open Tasks"
if command -v obsidian &>/dev/null; then
  run_with_timeout 5 'echo "(CLI timed out)"' obsidian tasks daily todo | head -10
else
  echo "(Obsidian CLI not available)"
fi
echo ""

echo "### Active Work"
ls work/active/*.md 2>/dev/null | sed 's|work/active/||;s|\.md$||' | head -10 || echo "(none)"
echo ""

echo "### Vault File Listing"
find . -name "*.md" -not -path "./.git/*" -not -path "./.obsidian/*" -not -path "./thinking/*" -not -path "./.claude/*" | sort
