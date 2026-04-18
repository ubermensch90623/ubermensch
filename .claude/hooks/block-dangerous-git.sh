#!/usr/bin/env sh
# PreToolUse hook for Bash(git *): block destructive git operations.
# Exit 2 blocks the call and feeds stderr back to Claude as feedback.
#
# Inspired by git-safe (https://dev.to/boucle2026/git-safe-stop-claude-code-from-force-pushing-your-branch-115f)
# and ChrisWiles/claude-code-showcase main-branch protection.
#
# Works without jq: the command text appears as a JSON string in stdin,
# so substring matching on the raw input is reliable for PreToolUse.

set -u

INPUT=$(cat 2>/dev/null || true)
[ -z "$INPUT" ] && exit 0

block() {
  printf 'BLOCKED by safety hook: %s\n' "$1" >&2
  printf 'Safer alternative: %s\n' "$2" >&2
  exit 2
}

# --- force push variants (allow --force-with-lease) ---
case "$INPUT" in
  *"git push"*"--force-with-lease"*) : ;;  # allowed
  *"git push"*"--force"*)
    block "git push --force rewrites remote history" \
          "use 'git push --force-with-lease' (checks the remote ref first)" ;;
  *"git push -f "*|*"git push -f\\\""*|*"git push -f'"*|*"git push "*" -f"*)
    block "git push -f is equivalent to --force" \
          "use 'git push --force-with-lease'" ;;
  *"git push --mirror"*)
    block "git push --mirror overwrites ALL remote refs (branches, tags)" \
          "push only the branch you intend, e.g. 'git push origin <branch>'" ;;
esac

# --- destructive working-tree operations ---
case "$INPUT" in
  *"git reset --hard"*|*"git reset --merge"*)
    block "git reset --hard discards uncommitted work" \
          "stash first ('git stash push -m wip'), or use 'git reset --mixed' to keep changes" ;;
  *"git clean -f"*|*"git clean -d"*|*"git clean -x"*|*"git clean -X"*|*"git clean -i"*)
    block "git clean -f permanently deletes untracked files" \
          "run 'git clean -n' (dry run) first to see what would be removed" ;;
  *"git checkout -- "*|*"git checkout ."*|*"git checkout -- ."*)
    block "'git checkout --' discards uncommitted changes in the worktree" \
          "use 'git stash' to save, or name the specific file you want to revert" ;;
  *"git restore --source"*|*"git restore --staged --worktree"*)
    block "'git restore' with --source / --worktree can discard uncommitted work" \
          "stash first, or restore a specific file" ;;
  *"git branch -D "*|*"git branch --delete --force"*|*"git branch -D\n"*)
    block "'git branch -D' force-deletes branches even if unmerged" \
          "use 'git branch -d' (lower-case) — refuses to drop unmerged work" ;;
esac

# --- amending already-pushed commits ---
case "$INPUT" in
  *"git commit --amend"*)
    # Amending is fine locally, but combined with push --force it destroys history.
    # Let the push --force rule above catch the push; warn via stderr only.
    printf 'NOTE: git commit --amend detected. Only safe if the commit has NOT been pushed.\n' >&2
    ;;
esac

exit 0
