#!/usr/bin/env bash
# CatchMe AI 메모리 시스템 자동 설치 스크립트
# 사용법: bash scripts/setup-catchme.sh [--provider PROVIDER] [--api-key KEY] [--model MODEL]
set -euo pipefail

CATCHME_DIR="$HOME/catchme-install"
CONDA_ENV="catchme"
CATCHME_REPO="https://github.com/HKUDS/catchme.git"
LOG_DIR="$CATCHME_DIR/logs"

# 기본 설정
PROVIDER="${CATCHME_PROVIDER:-ollama}"
API_KEY="${CATCHME_API_KEY:-}"
API_URL="${CATCHME_API_URL:-}"
MODEL="${CATCHME_MODEL:-gemma3:4b}"

# 인자 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        --provider) PROVIDER="$2"; shift 2 ;;
        --api-key) API_KEY="$2"; shift 2 ;;
        --api-url) API_URL="$2"; shift 2 ;;
        --model) MODEL="$2"; shift 2 ;;
        *) echo "알 수 없는 옵션: $1"; exit 1 ;;
    esac
done

echo "======================================"
echo "  CatchMe AI 메모리 시스템 설치"
echo "======================================"
echo ""

# 1. conda 확인
check_conda() {
    if command -v conda &>/dev/null; then
        echo "[OK] conda 발견: $(conda --version)"
        return 0
    fi

    echo "[!] conda가 설치되어 있지 않습니다. Miniconda를 설치합니다..."
    local MINICONDA_DIR="$HOME/miniconda3"
    local INSTALLER

    case "$(uname -s)" in
        Linux*)  INSTALLER="Miniconda3-latest-Linux-x86_64.sh" ;;
        Darwin*) INSTALLER="Miniconda3-latest-MacOSX-$(uname -m).sh" ;;
        *)       echo "[ERROR] 지원하지 않는 OS입니다."; exit 1 ;;
    esac

    curl -fsSL "https://repo.anaconda.com/miniconda/$INSTALLER" -o /tmp/miniconda.sh
    bash /tmp/miniconda.sh -b -p "$MINICONDA_DIR"
    rm /tmp/miniconda.sh

    export PATH="$MINICONDA_DIR/bin:$PATH"
    conda init bash 2>/dev/null || true
    echo "[OK] Miniconda 설치 완료"
}

# 2. CatchMe 이미 설치되어 있는지 확인
check_existing() {
    if conda run -n "$CONDA_ENV" catchme --help &>/dev/null 2>&1; then
        echo "[OK] CatchMe가 이미 설치되어 있습니다."
        return 0
    fi
    return 1
}

# 3. CatchMe 클론 및 설치
install_catchme() {
    echo ""
    echo "[1/4] CatchMe 소스 코드 다운로드..."
    if [ -d "$CATCHME_DIR" ]; then
        echo "  기존 디렉토리 발견. 업데이트합니다..."
        cd "$CATCHME_DIR" && git pull origin main 2>/dev/null || true
    else
        git clone "$CATCHME_REPO" "$CATCHME_DIR"
    fi

    echo "[2/4] Python 환경 생성 (conda env: $CONDA_ENV)..."
    if conda env list | grep -q "^$CONDA_ENV "; then
        echo "  기존 환경 발견. 재사용합니다."
    else
        conda create -n "$CONDA_ENV" python=3.11 -y
    fi

    echo "[3/4] CatchMe 설치 중..."
    conda run -n "$CONDA_ENV" pip install -e "$CATCHME_DIR" 2>&1 | tail -5

    echo "[4/4] 설치 확인..."
    if conda run -n "$CONDA_ENV" catchme --help &>/dev/null 2>&1; then
        echo "[OK] CatchMe 설치 성공!"
    else
        echo "[ERROR] CatchMe 설치에 실패했습니다."
        exit 1
    fi
}

# 4. config.json 작성
write_config() {
    local CONFIG_DIR="$HOME/.catchme"
    local CONFIG_FILE="$CONFIG_DIR/config.json"

    mkdir -p "$CONFIG_DIR"

    if [ -f "$CONFIG_FILE" ]; then
        echo "[OK] 설정 파일이 이미 존재합니다: $CONFIG_FILE"
        return 0
    fi

    echo ""
    echo "설정 파일 생성 중..."

    # API URL 자동 결정
    local RESOLVED_URL="$API_URL"
    if [ -z "$RESOLVED_URL" ]; then
        case "$PROVIDER" in
            ollama)      RESOLVED_URL="http://localhost:11434/v1" ;;
            openrouter)  RESOLVED_URL="https://openrouter.ai/api/v1" ;;
            openai)      RESOLVED_URL="https://api.openai.com/v1" ;;
            anthropic)   RESOLVED_URL="https://api.anthropic.com/v1" ;;
            groq)        RESOLVED_URL="https://api.groq.com/openai/v1" ;;
            vllm)        RESOLVED_URL="http://localhost:8000/v1" ;;
            lmstudio)    RESOLVED_URL="http://localhost:1234/v1" ;;
            *)           RESOLVED_URL="" ;;
        esac
    fi

    cat > "$CONFIG_FILE" <<JSONEOF
{
    "web": {
        "host": "127.0.0.1",
        "port": 8765
    },
    "llm": {
        "provider": "$PROVIDER",
        "api_key": "$API_KEY",
        "api_url": "$RESOLVED_URL",
        "model": "$MODEL",
        "max_calls": 0,
        "max_images_per_cluster": 5
    },
    "filter": {
        "window_min_dwell": 3.0,
        "keyboard_cluster_gap": 3.0,
        "mouse_cluster_gap": 5.0
    },
    "summarize": {
        "language": "ko",
        "max_tokens_l0": 1200,
        "max_tokens_l1": 1200,
        "max_tokens_l2": 1200,
        "max_tokens_l3": 1200,
        "temperature": 0.4,
        "max_workers": 2,
        "debounce_sec": 3.0,
        "save_interval_sec": 5.0
    },
    "retrieve": {
        "max_prompt_chars": 42000,
        "max_iterations": 15,
        "max_file_chars": 8000,
        "max_select_nodes": 7,
        "max_tokens_step": 4096,
        "max_tokens_answer": 8192
    }
}
JSONEOF

    echo "[OK] 설정 파일 생성 완료: $CONFIG_FILE"
    echo "  - LLM 제공자: $PROVIDER"
    echo "  - 모델: $MODEL"
    echo "  - 요약 언어: 한국어 (ko)"
}

# 5. 플랫폼별 권한 안내
platform_notice() {
    echo ""
    case "$(uname -s)" in
        Darwin*)
            echo "======================================="
            echo "  [macOS 권한 설정 필요]"
            echo "======================================="
            echo "  시스템 설정 → 개인정보 보호 및 보안에서"
            echo "  다음 항목에 터미널/Python 접근 허용:"
            echo "  - 손쉬운 사용 (Accessibility)"
            echo "  - 입력 모니터링 (Input Monitoring)"
            echo "  - 화면 기록 (Screen Recording)"
            echo ""
            ;;
        Linux*)
            echo "[참고] Linux에서는 X11/Wayland 환경에 따라"
            echo "  추가 권한이 필요할 수 있습니다."
            echo ""
            ;;
    esac
}

# 6. 데몬 시작
start_daemon() {
    mkdir -p "$LOG_DIR"

    # 이미 실행 중인지 확인
    if conda run -n "$CONDA_ENV" catchme ram 2>/dev/null | grep -q "catchme"; then
        echo "[OK] CatchMe가 이미 실행 중입니다."
        return 0
    fi

    echo "CatchMe 데몬 시작 중..."
    nohup conda run -n "$CONDA_ENV" catchme awake > "$LOG_DIR/awake.log" 2>&1 &
    local PID=$!

    sleep 2
    if kill -0 "$PID" 2>/dev/null; then
        echo "[OK] CatchMe 데몬 시작 완료 (PID: $PID)"
        echo "  로그 위치: $LOG_DIR/awake.log"
    else
        echo "[WARN] CatchMe 데몬이 바로 종료되었습니다."
        echo "  로그를 확인하세요: $LOG_DIR/awake.log"
    fi
}

# 메인 실행
main() {
    check_conda

    if check_existing; then
        echo "설치를 건너뛰고 설정을 확인합니다."
    else
        install_catchme
    fi

    write_config
    platform_notice
    start_daemon

    echo ""
    echo "======================================"
    echo "  설치 완료!"
    echo "======================================"
    echo ""
    echo "  사용법:"
    echo "  - Claude에게 '아까 뭐 했지?' 라고 물어보세요"
    echo "  - Claude에게 '오늘 공부 뭐 했어?' 라고 물어보세요"
    echo "  - Claude에게 '공부 추천해줘' 라고 물어보세요"
    echo ""
    echo "  웹 대시보드: http://127.0.0.1:8765"
    echo "  (실행: conda run -n catchme catchme web)"
    echo ""
}

main
