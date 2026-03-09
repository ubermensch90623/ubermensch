---
name: cancel-ralph
description: Cancel an active Ralph Loop and stop the iterative development cycle.
disable-model-invocation: true
allowed-tools:
  - Bash(*)
---

# Cancel Ralph Loop

Stop the currently active Ralph Loop.

## Steps

1. Check if a Ralph Loop is active by reading `.claude/ralph-loop-state.json`
2. If active, set `active` to `false` and add `cancelled_at` timestamp:

```bash
jq '.active = false | .cancelled = true | .cancelled_at = (now | todate)' \
  "$CLAUDE_PROJECT_DIR/.claude/ralph-loop-state.json" > /tmp/ralph-state-tmp.json \
  && mv /tmp/ralph-state-tmp.json "$CLAUDE_PROJECT_DIR/.claude/ralph-loop-state.json"
```

3. Confirm to user:
```
Ralph Loop cancelled.
- Iterations completed: <current_iteration>
- State file preserved at .claude/ralph-loop-state.json
```

If no active loop exists, inform the user: "No active Ralph Loop found."
