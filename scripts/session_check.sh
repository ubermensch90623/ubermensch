#!/bin/bash
# ============================================
# DeepTutor Session Startup Check
# ============================================
# 새 Claude Code / Cowork 세션에서 자동 실행
# 환경 상태를 체크하고 필요시 서비스를 시작합니다.

set -e
cd "$(dirname "$0")/.."
PROJECT_ROOT="$(pwd)"

echo "=========================================="
echo "  DeepTutor Session Check"
echo "=========================================="

# 1. .env 파일 체크
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "[OK] .env file found"

    # API 키가 placeholder인지 확인
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

# 2. Docker 확인
if command -v docker &> /dev/null; then
    echo "[OK] Docker available"

    # Docker daemon 실행 중인지 확인
    if docker info &> /dev/null; then
        echo "[OK] Docker daemon running"

        # DeepTutor 컨테이너 상태 확인
        CONTAINER_STATUS=$(docker compose ps --format "{{.State}}" 2>/dev/null || echo "none")

        if echo "$CONTAINER_STATUS" | grep -q "running"; then
            echo "[OK] DeepTutor is running"
            echo "     Frontend: http://localhost:${FRONTEND_PORT:-3782}"
            echo "     Backend:  http://localhost:${BACKEND_PORT:-8001}"
        else
            echo "[--] DeepTutor is not running"

            # .env가 설정되어 있으면 자동 시작
            if [ -f "$PROJECT_ROOT/.env" ] && ! grep -q "your-.*-key-here\|sk-xxx" "$PROJECT_ROOT/.env" 2>/dev/null; then
                echo "     Starting DeepTutor..."
                docker compose up -d 2>&1
                echo "[OK] DeepTutor started"
                echo "     Frontend: http://localhost:${FRONTEND_PORT:-3782}"
                echo "     Backend:  http://localhost:${BACKEND_PORT:-8001}"
            else
                echo "     Configure .env first, then run: docker compose up -d"
            fi
        fi
    else
        echo "[!!] Docker daemon not running"
        echo "     Start Docker Desktop or dockerd first"
    fi
else
    echo "[!!] Docker not found"
    echo "     Install Docker: https://docs.docker.com/get-docker/"
fi

# 3. 데이터 디렉토리 상태
echo ""
if [ -d "$PROJECT_ROOT/data/user" ]; then
    echo "[OK] User data directory exists (persistent)"
else
    echo "[--] No user data yet (will be created on first run)"
fi

if [ -d "$PROJECT_ROOT/data/knowledge_bases" ]; then
    KB_COUNT=$(ls -d "$PROJECT_ROOT/data/knowledge_bases"/*/ 2>/dev/null | wc -l)
    echo "[OK] Knowledge bases: $KB_COUNT found"
else
    echo "[--] No knowledge bases yet"
fi

echo ""
echo "=========================================="
echo "  Session check complete"
echo "=========================================="
