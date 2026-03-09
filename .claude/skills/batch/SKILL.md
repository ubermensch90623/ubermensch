---
name: batch
description: Orchestrate large-scale codebase changes in parallel. Decomposes work into independent units, spawns one agent per unit in isolated git worktrees, runs tests, and opens pull requests. Use for migrations, refactors, or any change that touches many files independently.
argument-hint: "<instruction>"
disable-model-invocation: true
allowed-tools:
  - Bash(git *)
  - Bash(gh *)
  - Agent
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# Batch: Parallel Codebase Changes

Orchestrate large-scale changes across a codebase in parallel. You receive a high-level instruction and decompose it into independent units of work.

## Phase 1: Research

Understand the scope of the requested change: `$ARGUMENTS`

1. Use Grep and Glob to find all files affected by the change
2. Read representative files to understand current patterns
3. Identify the boundaries of independent units

## Phase 2: Decompose into Units

Break the work into **5 to 30 independent units**. Each unit must be:

- **Self-contained**: completable without knowledge of other units
- **Testable**: verifiable with existing tests or a simple check
- **Non-overlapping**: no two units touch the same file

Present the plan as a numbered table:

| # | Unit | Files | Description |
|---|------|-------|-------------|
| 1 | ... | ... | ... |

**Wait for user approval before proceeding.**

## Phase 3: Execute in Parallel

After approval, spawn **one background Agent per unit** using `isolation: "worktree"` so each agent works in an isolated git worktree.

Each agent must:

1. Check out a new branch: `batch/<unit-name>`
2. Implement the change for its unit
3. Run relevant tests to verify correctness
4. Run `/simplify` to auto-review the changes
5. Commit with a clear message describing the unit change
6. Create a pull request using `gh pr create`

Launch all agents concurrently in a single message for true parallel execution.

## Phase 4: Monitor and Report

After all agents complete, produce a summary table:

| # | Unit | Status | PR |
|---|------|--------|----|
| 1 | ... | Success/Failed | #123 |

Report the final tally: "X/Y units landed as PRs."

If any unit failed, explain the failure and suggest next steps.
