#!/usr/bin/env bash
# cloud_safe 분신 결과 append + push — silent fail 금지 (헌법 redteam #4)
# 사용: ./cloud_safe/append_result.sh <prefix> < 본문(stdin)
#   prefix: cloud | cloud_야간 | cloud_공고 | 세상이해_cloud
set -euo pipefail

PREFIX="${1:-cloud}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIR="$REPO/cloud_safe/_SSOT/_AI진화일지"
DATE="$(date +%Y-%m-%d)"
TIME="$(date +%H:%M)"
FILE="$DIR/${PREFIX}_${DATE}.md"

[ -d "$DIR" ] || { echo "APPEND_FAILED: DIR_NOT_FOUND $DIR"; exit 1; }

BODY="$(cat)"
[ -n "$BODY" ] || { echo "APPEND_FAILED: EMPTY_BODY"; exit 1; }

{ echo "## 클라우드 분신 결과 ($DATE $TIME KST)"; echo; echo "$BODY"; echo; } >> "$FILE" \
  || { echo "APPEND_FAILED: WRITE $FILE"; exit 1; }

cd "$REPO"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
[ "$BRANCH" = "claude/ssot-cloud-safe" ] || { echo "APPEND_FAILED: WRONG_BRANCH $BRANCH"; exit 1; }

git add "$FILE" || { echo "APPEND_FAILED: GIT_ADD"; exit 1; }
git diff --cached --quiet && { echo "APPEND_FAILED: NO_STAGED_CHANGE"; exit 1; }
git -c user.email='claude-cloud@anthropic.com' -c user.name='Claude Cloud' \
    commit -q -m "cloud_safe 분신 결과 ${DATE}" || { echo "APPEND_FAILED: COMMIT"; exit 1; }

for d in 2 4 8 16; do
  git push -u origin claude/ssot-cloud-safe -q && { echo "APPEND_OK: $FILE"; exit 0; }
  sleep "$d"
done
echo "APPEND_FAILED: PUSH (커밋은 로컬 보존됨 — 다음 실행 시 함께 push)"
exit 1
