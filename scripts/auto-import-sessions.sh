#!/usr/bin/env bash
# Claude Code Stop hook: 세션이 끝날 때 자동으로 jsonl 로그를
# vault/Sessions/로 임포트한다.
#
# ~/.claude/settings.json의 Stop hooks 배열에 등록되어 매 세션 종료마다
# 실행된다. 이 저장소가 아닌 다른 프로젝트에서 실행될 때는 조용히 종료한다.
#
# 로그: /tmp/auto-import-sessions.log

set -u

readonly REPO="/home/user/ubermensch"
readonly LOG="/tmp/auto-import-sessions.log"

# 이 저장소가 없거나 vault가 없으면 조용히 종료
[[ -d "${REPO}/vault" ]] || exit 0
[[ -x "${REPO}/scripts/import-claude-code-sessions.py" ]] || exit 0

# 백그라운드로 임포트 (hook이 사용자 응답 시간을 늘리지 않게)
{
  echo ""
  echo "=== $(date -Iseconds) ==="
  cd "${REPO}" && python3 scripts/import-claude-code-sessions.py --skip-active 0
} >> "${LOG}" 2>&1 &

exit 0
