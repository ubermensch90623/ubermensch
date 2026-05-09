#!/usr/bin/env bash
# Shell 환경변수 도우미 — Obsidian vault 자동 통합 활성화
#
# 사용:
#   bash bin/setup-shell.sh ~/Documents/MyVault           # 추가할 줄 출력만
#   bash bin/setup-shell.sh ~/Documents/MyVault --apply   # ~/.bashrc 또는 ~/.zshrc에 자동 추가
#
# 효과:
#   STUDY_EVOLVE_AUTO_SYNC=1 + OBSIDIAN_VAULT 설정 → add/done-review/sample 후 vault 자동 갱신.

set -euo pipefail

VAULT="${1:-}"
APPLY="${2:-}"

if [ -z "$VAULT" ] || [ "$VAULT" = "-h" ] || [ "$VAULT" = "--help" ]; then
    sed -n '2,12p' "$0"
    exit 0
fi

# Resolve absolute path
if [ -d "$VAULT" ]; then
    VAULT_ABS=$(cd "$VAULT" && pwd)
else
    echo "경고: vault 경로가 존재하지 않습니다: $VAULT"
    if [ "$APPLY" = "--apply" ]; then
        read -p "그래도 계속하시겠습니까? (y/n): " yn
        [ "$yn" != "y" ] && exit 1
    fi
    # Best-effort: expand ~ if any
    VAULT_ABS="${VAULT/#\~/$HOME}"
fi

LINES=$(cat <<EOF
# study-evolve auto-sync (added by bin/setup-shell.sh)
export OBSIDIAN_VAULT="$VAULT_ABS"
export STUDY_EVOLVE_AUTO_SYNC=1
EOF
)

if [ "$APPLY" = "--apply" ]; then
    # Detect rc file
    if [ -n "${ZSH_VERSION:-}" ] || [ -f "$HOME/.zshrc" ] && [ "${SHELL##*/}" = "zsh" ]; then
        RC="$HOME/.zshrc"
    else
        RC="$HOME/.bashrc"
    fi

    # Skip if already present
    if grep -q "STUDY_EVOLVE_AUTO_SYNC" "$RC" 2>/dev/null; then
        echo "이미 $RC에 STUDY_EVOLVE_AUTO_SYNC 설정이 있습니다. 수정 X."
        echo "직접 확인: grep STUDY_EVOLVE_AUTO_SYNC $RC"
        exit 0
    fi

    {
        echo
        echo "$LINES"
    } >> "$RC"
    echo "✓ $RC에 추가됨"
    echo
    echo "다음 셸에서 자동 적용. 즉시 적용하려면:"
    echo "  source $RC"
else
    echo "다음을 ~/.bashrc 또는 ~/.zshrc에 추가하세요:"
    echo
    echo "$LINES"
    echo
    echo "또는 자동 추가:"
    echo "  bash $0 $VAULT_ABS --apply"
fi
