# DeepTutor Project

## Overview
DeepTutor는 에이전트 기반 AI 개인화 학습 플랫폼입니다.
- **Backend**: Python 3.11 + FastAPI (포트 8001)
- **Frontend**: Next.js 16 + React 19 (포트 3782)
- **실행**: Docker Compose (`docker compose up -d`)

## Quick Reference

### 서비스 시작/중지
```bash
docker compose up -d          # 시작
docker compose down            # 중지
docker compose logs -f         # 로그
docker compose up -d --build   # 재빌드
```

### 환경 설정
- `.env` 파일에 API 키 설정 필수 (`.env.example` 참고)
- `LLM_API_KEY` — LLM 서비스 키 (필수)
- `EMBEDDING_API_KEY` — 임베딩 서비스 키 (필수)

### 접속
- Frontend: http://localhost:3782
- Backend API: http://localhost:8001

## Architecture
```
deeptutor/          # Python backend (FastAPI)
  agents/           # Agent orchestration
  api/              # API endpoints (WebSocket + REST)
  capabilities/     # Level 2 — multi-step agent pipelines (chat, deep_solve, deep_question)
  tools/            # Level 1 — single-function tools (rag, web_search, code_execution)
  plugins/          # Playground plugins (deep_research)
  knowledge/        # Knowledge base & RAG
  services/         # Business logic
  tutorbot/         # Autonomous tutor agents
deeptutor_cli/      # CLI entry point
web/                # Next.js frontend
scripts/            # Utility scripts
tests/              # Test suite
```

## Key Files
| File | Purpose |
|------|---------|
| `docker-compose.yml` | Production orchestration |
| `.env` | API keys and configuration (gitignored) |
| `.env.example` | Template for .env |
| `deeptutor/api/main.py` | FastAPI app entry point |
| `deeptutor/runtime/orchestrator.py` | ChatOrchestrator — unified agent entry |
| `web/` | Next.js frontend |

## Data Persistence
- `data/user/` — 사용자 설정, 워크스페이스, 메모리 (Docker volume)
- `data/knowledge_bases/` — 업로드된 문서 & RAG 인덱스 (Docker volume)
- 이 디렉토리들은 Docker volume으로 마운트되어 컨테이너 재시작 후에도 유지됨

## Session Startup
새 세션에서 `./scripts/session_check.sh`를 실행하면:
1. `.env` 파일 존재 확인
2. Docker 서비스 상태 확인
3. 필요시 자동 시작
