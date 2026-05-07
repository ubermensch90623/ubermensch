#!/usr/bin/env bash
#
# auto-sync.sh
#
# Claude Code 세션 시작/종료 시 자동으로:
#   --start  →  git pull, 과거 세션 임포트, claude.ai fetch (키 있으면), commit & push
#   --stop   →  방금 끝난 세션 임포트, commit & push
#
# ~/.claude/settings.json의 SessionStart/Stop hooks에 등록되어 손 안 대도 돌아간다.
# 이 저장소가 아닌 곳에서는 vault/ 가 없으니 조용히 종료한다.
#
# 로그: /tmp/ubermensch-auto-sync.log

set -u

readonly REPO="/home/user/ubermensch"
readonly LOG="/tmp/ubermensch-auto-sync.log"
readonly MODE="${1:-}"

[[ -d "${REPO}/vault" ]] || exit 0
cd "${REPO}" || exit 0

readonly BRANCH="$(git branch --show-current 2>/dev/null)"
[[ -z "${BRANCH}" ]] && exit 0

log() {
  echo "[$(date -Iseconds)] $*" >> "${LOG}"
}

import_code() {
  if [[ -x "${REPO}/scripts/import-claude-code-sessions.py" ]]; then
    python3 "${REPO}/scripts/import-claude-code-sessions.py" "$@" >> "${LOG}" 2>&1 || true
  fi
}

fetch_claude_ai() {
  # 비공식 API. CLAUDE_AI_SESSION_KEY 있을 때만 시도.
  local key=""
  if [[ -f "${REPO}/.env" ]]; then
    key=$(grep -E '^CLAUDE_AI_SESSION_KEY=' "${REPO}/.env" | head -n1 | cut -d= -f2- | tr -d '"' | tr -d "'")
  fi
  [[ -z "${key}" ]] && key="${CLAUDE_AI_SESSION_KEY:-}"
  [[ -z "${key}" ]] && { log "skip claude.ai fetch (no session key)"; return 0; }
  [[ -x "${REPO}/scripts/fetch-claude-ai.py" ]] || return 0

  local since_file="${REPO}/.claude-ai-last-fetch"
  local since=""
  [[ -f "${since_file}" ]] && since=$(cat "${since_file}" 2>/dev/null)

  if [[ -n "${since}" ]]; then
    log "fetch claude.ai since ${since}"
    python3 "${REPO}/scripts/fetch-claude-ai.py" --since "${since}" >> "${LOG}" 2>&1 || true
  else
    log "fetch claude.ai (initial, --limit 50)"
    python3 "${REPO}/scripts/fetch-claude-ai.py" --limit 50 >> "${LOG}" 2>&1 || true
  fi
  date -u +%Y-%m-%d > "${since_file}"
}

commit_and_push() {
  local msg="$1"
  if [[ -z "$(git status --porcelain vault/ 2>/dev/null)" ]]; then
    log "no vault changes, skip commit"
    return 0
  fi
  git add vault/ >> "${LOG}" 2>&1 || return 0
  git commit -m "${msg}" >> "${LOG}" 2>&1 || { log "commit failed"; return 0; }
  log "committed: ${msg}"

  # 네트워크 에러 시 지수 백오프 재시도
  for i in 1 2 3 4; do
    if git push --quiet origin "${BRANCH}" 2>> "${LOG}"; then
      log "pushed (try ${i})"
      return 0
    fi
    sleep $((2**i))
  done
  log "push failed after retries"
}

case "${MODE}" in
  --start)
    log "=== START on ${BRANCH} ==="
    if git pull --ff-only --quiet origin "${BRANCH}" 2>> "${LOG}"; then
      log "pulled latest"
    else
      log "pull skipped or failed (ok if first session or local diverged)"
    fi
    import_code
    fetch_claude_ai
    commit_and_push "auto-sync: session start"
    ;;
  --stop)
    log "=== STOP on ${BRANCH} ==="
    sleep 1  # 현재 세션의 jsonl이 디스크에 flush될 시간
    import_code --skip-active 0
    commit_and_push "auto-sync: session end"
    ;;
  *)
    echo "사용법: $0 --start|--stop" >&2
    exit 1
    ;;
esac

exit 0
