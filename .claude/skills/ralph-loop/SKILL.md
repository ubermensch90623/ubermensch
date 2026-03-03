---
name: ralph-loop
description: Start an autonomous iterative development loop. Claude keeps working on a task until completion or max iterations. Use for TDD workflows, migrations, or any task with clear success criteria.
argument-hint: "<prompt>" --max-iterations <n> --completion-promise "<text>"
disable-model-invocation: true
allowed-tools:
  - Bash(*)
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - Agent
---

# Ralph Loop: Autonomous Iterative Development

You are starting a Ralph Loop — an autonomous development cycle that continues until the task is complete.

## Step 1: Parse Arguments

Parse the arguments from: `$ARGUMENTS`

Extract:
- **prompt**: The main task description (the quoted string)
- **--max-iterations**: Maximum number of iterations (default: 20)
- **--completion-promise**: The exact string that signals completion (default: "DONE")

## Step 2: Initialize State

Create the state file at `.claude/ralph-loop-state.json`:

```json
{
  "active": true,
  "prompt": "<extracted prompt>",
  "max_iterations": <n>,
  "current_iteration": 0,
  "completion_promise": "<text>",
  "started_at": "<ISO timestamp>"
}
```

Write this file using the Bash tool:

```bash
cat > "$CLAUDE_PROJECT_DIR/.claude/ralph-loop-state.json" << 'STATEEOF'
{
  "active": true,
  "prompt": "...",
  "max_iterations": ...,
  "current_iteration": 0,
  "completion_promise": "...",
  "started_at": "..."
}
STATEEOF
```

## Step 3: Confirm to User

Display:
```
Ralph Loop started!
- Task: <prompt summary>
- Max iterations: <n>
- Completion promise: "<text>"
- State file: .claude/ralph-loop-state.json

The Stop hook will automatically re-feed the prompt after each response.
To cancel: /cancel-ralph
```

## Step 4: Begin Working

Start executing the task described in the prompt. Work on it thoroughly. When the task is complete and all success criteria are met, output the completion promise string exactly as specified.

**Important**: The Stop hook at `.claude/hooks/ralph-stop-hook.sh` will intercept your exit and re-feed the prompt automatically. Each iteration, you will see your previous work in the codebase. Improve iteratively.

### Tips for Success:
- Read your previous work before making changes
- Check git status/diff to see what changed in prior iterations
- Run tests to verify progress
- When ALL criteria are met, output the completion promise exactly
