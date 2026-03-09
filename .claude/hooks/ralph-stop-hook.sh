#!/bin/bash
# Ralph Loop Stop Hook
# Intercepts Claude's exit and re-feeds the prompt for iterative development.
# Uses exit code 2 to block stopping and inject reason back into Claude.

set -euo pipefail

STATE_FILE="${CLAUDE_PROJECT_DIR:-.}/.claude/ralph-loop-state.json"

# Read hook input from stdin
INPUT=$(cat)

# Check if stop hook is already active (prevent infinite loops)
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
  exit 0
fi

# Check if ralph loop state file exists and is active
if [ ! -f "$STATE_FILE" ]; then
  exit 0
fi

ACTIVE=$(jq -r '.active // false' "$STATE_FILE" 2>/dev/null)
if [ "$ACTIVE" != "true" ]; then
  exit 0
fi

# Read state
PROMPT=$(jq -r '.prompt' "$STATE_FILE")
MAX_ITERATIONS=$(jq -r '.max_iterations // 20' "$STATE_FILE")
CURRENT_ITERATION=$(jq -r '.current_iteration // 0' "$STATE_FILE")
COMPLETION_PROMISE=$(jq -r '.completion_promise // ""' "$STATE_FILE")

# Check completion promise in last assistant message
# Supports both plain text match and <promise>TEXT</promise> tag format
LAST_MESSAGE=$(echo "$INPUT" | jq -r '.last_assistant_message // ""')
if [ -n "$COMPLETION_PROMISE" ]; then
  FOUND=false
  # Check plain text match
  if echo "$LAST_MESSAGE" | grep -qF "$COMPLETION_PROMISE"; then
    FOUND=true
  fi
  # Check <promise> tag format
  if echo "$LAST_MESSAGE" | grep -qP "<promise>\s*${COMPLETION_PROMISE}\s*</promise>"; then
    FOUND=true
  fi
  if [ "$FOUND" = "true" ]; then
    # Task completed - deactivate loop
    jq '.active = false | .completed = true | .completed_at = (now | todate)' "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
    exit 0
  fi
fi

# Check max iterations
NEXT_ITERATION=$((CURRENT_ITERATION + 1))
if [ "$MAX_ITERATIONS" -gt 0 ] && [ "$NEXT_ITERATION" -gt "$MAX_ITERATIONS" ]; then
  # Max iterations reached - deactivate loop
  jq '.active = false | .max_reached = true' "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
  exit 0
fi

# Update iteration counter
jq --argjson iter "$NEXT_ITERATION" '.current_iteration = $iter' "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"

# Block exit and re-feed prompt
jq -n \
  --arg reason "Ralph Loop iteration ${NEXT_ITERATION}/${MAX_ITERATIONS:-∞}. Continue working on the task. Original prompt: ${PROMPT}" \
  '{ "decision": "block", "reason": $reason }'
