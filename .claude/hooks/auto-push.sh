#!/usr/bin/env sh
# Auto-push Claude Code session changes to origin.
# POSIX sh so it runs on Linux, macOS, and Git Bash (Windows).
# Exits 0 to not block Claude; logs to stderr so issues are visible.

set -u

log() { printf '[auto-push] %s\n' "$*" >&2; }

# Never let git hang on a credential prompt.
export GIT_TERMINAL_PROMPT=0
export GIT_ASKPASS=/bin/true

# Drain any hook JSON from stdin (non-blocking if no stdin).
# Used only to detect stop_hook_active to avoid recursive Stop loops.
INPUT=""
if [ ! -t 0 ]; then
  INPUT=$(cat 2>/dev/null || true)
fi
case "$INPUT" in
  *'"stop_hook_active"'*true*)
    log "stop_hook_active=true; skip to avoid loop"
    exit 0
    ;;
esac

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || { log "no project dir; skip"; exit 0; }

git rev-parse --git-dir >/dev/null 2>&1 || { log "not a git repo; skip"; exit 0; }

branch=$(git symbolic-ref --short HEAD 2>/dev/null) || {
  log "detached HEAD; skip"
  exit 0
}

case "$branch" in
  main|master|production|prod|release|release/*|prod/*)
    log "protected branch '$branch'; skip"
    exit 0
    ;;
esac

git remote get-url origin >/dev/null 2>&1 || { log "no 'origin' remote; skip"; exit 0; }

# Ensure identity exists so commit doesn't fail.
git config user.email >/dev/null 2>&1 || git config user.email "claude@local"
git config user.name  >/dev/null 2>&1 || git config user.name  "Claude Code"

git add -A

if git diff --cached --quiet; then
  exit 0
fi

# Block obvious secrets from leaking into the remote.
secret_regex='(^|/)(\.env(\..+)?|credentials(\.json)?|secrets?\.(json|ya?ml|toml)|.*\.pem|id_rsa|id_ed25519|\.aws/credentials)$'
staged=$(git diff --cached --name-only)
hits=$(printf '%s\n' "$staged" | grep -E "$secret_regex" || true)
if [ -n "$hits" ]; then
  log "ABORT: secret-like files staged:"
  printf '%s\n' "$hits" >&2
  git reset --quiet
  exit 0
fi

ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
if ! git commit -m "auto: claude session snapshot ${ts}" >/dev/null 2>&1; then
  log "commit failed (pre-commit hook or config issue)"
  exit 0
fi

# Cap push time so the hook never hangs. 30s is plenty for snapshots.
push_out=$( (
  if command -v timeout >/dev/null 2>&1; then
    timeout 30 git push origin "$branch" 2>&1
  else
    git push origin "$branch" 2>&1
  fi
) )
push_rc=$?

if [ "$push_rc" -ne 0 ]; then
  log "push failed (rc=$push_rc) — commit is local only:"
  printf '%s\n' "$push_out" >&2
  exit 0
fi

log "pushed '$branch' snapshot $ts"
exit 0
