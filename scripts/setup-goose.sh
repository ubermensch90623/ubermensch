#!/usr/bin/env bash
# Goose AI 에이전트 자동 설치 스크립트
# 사용법: bash scripts/setup-goose.sh [--provider PROVIDER] [--api-key KEY]
set -euo pipefail

GOOSE_BIN=""
LOG_FILE="/tmp/goose-setup.log"

# 기본 LLM 설정
PROVIDER="${GOOSE_PROVIDER:-}"
API_KEY="${GOOSE_API_KEY:-}"

# 인자 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        --provider) PROVIDER="$2"; shift 2 ;;
        --api-key) API_KEY="$2"; shift 2 ;;
        *) echo "알 수 없는 옵션: $1"; exit 1 ;;
    esac
done

echo "======================================"
echo "  Goose AI 에이전트 설치"
echo "======================================"
echo ""

# 1. 이미 설치되어 있는지 확인
check_existing() {
    if command -v goose &>/dev/null; then
        GOOSE_BIN="$(command -v goose)"
        echo "[OK] Goose가 이미 설치되어 있습니다: $GOOSE_BIN"
        goose version 2>/dev/null || true
        return 0
    fi
    return 1
}

# 2. OS 감지 및 설치
install_goose() {
    local OS
    OS="$(uname -s)"

    echo "[1/3] Goose 설치 중..."

    case "$OS" in
        Darwin*)
            if command -v brew &>/dev/null; then
                echo "  Homebrew로 설치합니다..."
                brew install goose 2>&1 | tail -3
            else
                echo "  curl 설치 스크립트를 사용합니다..."
                curl -fsSL https://github.com/block/goose/releases/latest/download/download_cli.sh | bash 2>&1 | tail -5
            fi
            ;;
        Linux*)
            echo "  curl 설치 스크립트를 사용합니다..."
            curl -fsSL https://github.com/block/goose/releases/latest/download/download_cli.sh | bash 2>&1 | tail -5
            ;;
        *)
            echo "[ERROR] 지원하지 않는 OS입니다: $OS"
            exit 1
            ;;
    esac

    # PATH 확인
    if command -v goose &>/dev/null; then
        GOOSE_BIN="$(command -v goose)"
    elif [ -f "$HOME/.goose/bin/goose" ]; then
        GOOSE_BIN="$HOME/.goose/bin/goose"
        export PATH="$HOME/.goose/bin:$PATH"
    elif [ -f "$HOME/.local/bin/goose" ]; then
        GOOSE_BIN="$HOME/.local/bin/goose"
        export PATH="$HOME/.local/bin:$PATH"
    fi

    echo "[2/3] 설치 확인..."
    if [ -n "$GOOSE_BIN" ] && "$GOOSE_BIN" version &>/dev/null; then
        echo "[OK] Goose 설치 성공!"
        "$GOOSE_BIN" version
    else
        echo "[ERROR] Goose 설치에 실패했습니다."
        echo "  수동 설치: https://github.com/block/goose/releases"
        exit 1
    fi
}

# 3. LLM 제공자 설정
configure_provider() {
    if [ -z "$PROVIDER" ]; then
        echo ""
        echo "[참고] LLM 제공자가 설정되지 않았습니다."
        echo "  Goose 첫 실행 시 대화형으로 설정할 수 있습니다."
        echo "  또는 환경변수로 설정:"
        echo "    export GOOSE_PROVIDER=openai"
        echo "    export GOOSE_API_KEY=sk-..."
        return 0
    fi

    echo "[3/3] LLM 제공자 설정 중..."

    # 환경변수로 설정 (Goose가 자동으로 읽음)
    local PROFILE_FILE="$HOME/.bashrc"
    if [ -f "$HOME/.zshrc" ]; then
        PROFILE_FILE="$HOME/.zshrc"
    fi

    # 기존 설정이 없으면 추가
    if ! grep -q "GOOSE_PROVIDER" "$PROFILE_FILE" 2>/dev/null; then
        {
            echo ""
            echo "# Goose AI 에이전트 설정"
            echo "export GOOSE_PROVIDER=\"$PROVIDER\""
            if [ -n "$API_KEY" ]; then
                echo "export GOOSE_API_KEY=\"$API_KEY\""
            fi
        } >> "$PROFILE_FILE"
        echo "[OK] LLM 설정 완료: $PROVIDER"
    else
        echo "[OK] 기존 LLM 설정이 있습니다."
    fi
}

# 4. NCS 학습 레시피 복사
setup_recipes() {
    local SCRIPT_DIR
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    local RECIPE_DIR="$SCRIPT_DIR/recipes"

    if [ -d "$RECIPE_DIR" ] && ls "$RECIPE_DIR"/*.yaml &>/dev/null 2>&1; then
        echo ""
        echo "NCS 학습 레시피 확인:"
        for recipe in "$RECIPE_DIR"/*.yaml; do
            echo "  - $(basename "$recipe")"
        done
        echo "[OK] 레시피 사용법: goose run --recipe recipes/<파일명>.yaml"
    fi
}

# 메인 실행
main() {
    if check_existing; then
        echo "설치를 건너뜁니다."
    else
        install_goose
    fi

    configure_provider
    setup_recipes

    echo ""
    echo "======================================"
    echo "  설치 완료!"
    echo "======================================"
    echo ""
    echo "  사용법:"
    echo "  - Claude에게 'Goose로 공부 도와줘' 라고 말하세요"
    echo "  - Claude에게 'Goose 레시피 실행해줘' 라고 말하세요"
    echo "  - Claude에게 'Goose 상태 확인' 이라고 말하세요"
    echo ""
    echo "  직접 사용:"
    echo "  - goose session                    # 대화 세션 시작"
    echo "  - goose run --recipe <파일>.yaml   # 레시피 실행"
    echo ""
}

main
