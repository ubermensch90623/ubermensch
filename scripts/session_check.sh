#!/bin/bash
# ============================================
# DeepTutor Session Startup Check
# ============================================
# 새 Claude Code / Cowork 세션에서 자동 실행
# 환경 상태를 체크하고 DeepTutor CLI를 준비합니다.

set -e
cd "$(dirname "$0")/.."
PROJECT_ROOT="$(pwd)"

echo "=========================================="
echo "  DeepTutor Session Check"
echo "=========================================="

# 1. .env 파일 체크
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "[OK] .env file found"

    if grep -q "your-.*-key-here\|sk-xxx" "$PROJECT_ROOT/.env" 2>/dev/null; then
        echo "[!!] .env contains placeholder API keys"
        echo "     Edit .env and replace with real API keys"
        echo "     Required: LLM_API_KEY, EMBEDDING_API_KEY"
    else
        echo "[OK] .env appears configured"
    fi
else
    echo "[!!] .env file not found — creating from template"
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    echo "     Created .env from .env.example"
    echo "     Edit .env and add your API keys before starting"
fi

# 2. DeepTutor CLI 설치 확인 & 자동 설치
if command -v deeptutor &> /dev/null; then
    echo "[OK] DeepTutor CLI installed"
else
    echo "[--] DeepTutor CLI not found — installing..."
    pip install -r "$PROJECT_ROOT/requirements/cli.txt" -q 2>&1 | tail -1
    pip install -e "$PROJECT_ROOT" -q 2>&1 | tail -1
    if command -v deeptutor &> /dev/null; then
        echo "[OK] DeepTutor CLI installed successfully"
    else
        echo "[!!] DeepTutor CLI installation failed"
    fi
fi

# 3. Docker 확인 (optional — CLI works without Docker)
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        CONTAINER_STATUS=$(docker compose ps --format "{{.State}}" 2>/dev/null || echo "none")
        if echo "$CONTAINER_STATUS" | grep -q "running"; then
            echo "[OK] DeepTutor Docker is running"
            echo "     Frontend: http://localhost:${FRONTEND_PORT:-3782}"
            echo "     Backend:  http://localhost:${BACKEND_PORT:-8001}"
        else
            echo "[--] DeepTutor Docker not running (CLI mode available)"
        fi
    fi
fi

# 4. 데이터 디렉토리 상태
if [ -d "$PROJECT_ROOT/data/knowledge_bases" ]; then
    KB_COUNT=$(ls -d "$PROJECT_ROOT/data/knowledge_bases"/*/ 2>/dev/null | wc -l)
    echo "[OK] Knowledge bases: $KB_COUNT found"
fi

echo ""
echo "=========================================="
echo "  Ready! Use DeepTutor:"
echo "    deeptutor chat start          # 대화형 학습"
echo "    deeptutor run chat \"질문\"     # 한 번 질문"
echo "    deeptutor run deep_solve \"문제\" # 심층 풀이"
echo "    deeptutor kb list             # 지식 베이스 목록"
echo "=========================================="
