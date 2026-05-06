#!/usr/bin/env bash
#
# quick-mcp-tunnel.sh
#
# mcp-obsidian (STDIO) → supergateway (SSE) → cloudflared tunnel (공개 HTTPS).
# 출력된 URL을 claude.ai → Settings → Connectors에 등록하면, 웹 채팅에서
# 이 볼트를 직접 읽고 쓸 수 있다.
#
# 사용법:
#   1) 같은 디렉터리의 .env.example을 .env로 복사하고 값 채우기
#      (OBSIDIAN_API_KEY는 Obsidian의 Local REST API 플러그인 설정에서 복사)
#   2) Obsidian이 켜져 있고 Local REST API 플러그인이 활성화되어 있을 것
#   3) ./scripts/quick-mcp-tunnel.sh 실행
#
# 의존성: uvx (또는 pipx), npx, cloudflared
#   - uvx:        curl -LsSf https://astral.sh/uv/install.sh | sh
#   - cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
#
# Ctrl-C로 종료하면 두 프로세스 모두 정리된다.

set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly ENV_FILE="${REPO_ROOT}/.env"
readonly DEFAULT_PORT=8765

# ── 1. 의존성 체크 ──────────────────────────────────────────────
need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: '$1' 명령이 필요합니다. 설치 후 다시 시도하세요." >&2
    [[ -n "${2:-}" ]] && echo "  설치: $2" >&2
    exit 1
  fi
}

need uvx        "curl -LsSf https://astral.sh/uv/install.sh | sh"
need npx        "Node.js 설치 (https://nodejs.org)"
need cloudflared "https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"

# ── 2. 설정 로딩 ───────────────────────────────────────────────
if [[ ! -f "${ENV_FILE}" ]]; then
  echo "ERROR: ${ENV_FILE} 가 없습니다." >&2
  echo "  cp .env.example .env 후 값 채우기." >&2
  exit 1
fi

# .env에 정의된 값을 export. 기존 환경변수는 덮어쓰지 않음.
set -a
# shellcheck disable=SC1090
source "${ENV_FILE}"
set +a

: "${OBSIDIAN_API_KEY:?OBSIDIAN_API_KEY 가 .env에 설정되지 않았습니다}"
OBSIDIAN_HOST="${OBSIDIAN_HOST:-127.0.0.1}"
OBSIDIAN_PORT="${OBSIDIAN_PORT:-27124}"
MCP_PORT="${MCP_PORT:-${DEFAULT_PORT}}"

# ── 3. Obsidian Local REST API 헬스 체크 ──────────────────────
if ! curl -s -k -o /dev/null -w "%{http_code}" \
     "https://${OBSIDIAN_HOST}:${OBSIDIAN_PORT}/" \
     -H "Authorization: Bearer ${OBSIDIAN_API_KEY}" | grep -q '^2'; then
  echo "WARN: Obsidian Local REST API에 접속할 수 없습니다." >&2
  echo "  - Obsidian이 실행 중인지" >&2
  echo "  - Local REST API 플러그인이 활성화되어 있는지" >&2
  echo "  - .env의 OBSIDIAN_HOST/PORT/API_KEY가 맞는지 확인하세요." >&2
  echo "  계속 진행은 하지만, 연결이 안 될 가능성이 높습니다." >&2
  sleep 2
fi

# ── 4. 프로세스 정리 trap ──────────────────────────────────────
SUPERGW_PID=""
CLOUDFLARED_PID=""

cleanup() {
  echo ""
  echo "[quick-mcp-tunnel] 종료 중..."
  [[ -n "${SUPERGW_PID}" ]]    && kill "${SUPERGW_PID}"    2>/dev/null || true
  [[ -n "${CLOUDFLARED_PID}" ]] && kill "${CLOUDFLARED_PID}" 2>/dev/null || true
  wait 2>/dev/null || true
  echo "[quick-mcp-tunnel] 정리 완료."
}
trap cleanup EXIT INT TERM

# ── 5. supergateway로 mcp-obsidian을 SSE로 띄우기 ─────────────
echo "[1/3] supergateway로 mcp-obsidian을 SSE로 노출 (port ${MCP_PORT})..."
npx -y supergateway \
  --stdio "uvx mcp-obsidian" \
  --port "${MCP_PORT}" \
  --baseUrl "http://localhost:${MCP_PORT}" \
  --ssePath /sse \
  --messagePath /message \
  > /tmp/supergateway.log 2>&1 &
SUPERGW_PID=$!

# 기동 대기
for _ in {1..20}; do
  if curl -s -o /dev/null -w "%{http_code}" "http://localhost:${MCP_PORT}/sse" | grep -q '^2'; then
    break
  fi
  sleep 0.5
done

if ! kill -0 "${SUPERGW_PID}" 2>/dev/null; then
  echo "ERROR: supergateway 기동 실패. 로그:" >&2
  cat /tmp/supergateway.log >&2
  exit 1
fi
echo "      supergateway 기동됨 (PID ${SUPERGW_PID}), 로그: /tmp/supergateway.log"

# ── 6. cloudflared로 공개 HTTPS URL 만들기 ────────────────────
echo "[2/3] cloudflared 터널 생성..."
CF_LOG=$(mktemp)
cloudflared tunnel --no-autoupdate --url "http://localhost:${MCP_PORT}" \
  > "${CF_LOG}" 2>&1 &
CLOUDFLARED_PID=$!

# 공개 URL 추출 (cloudflared가 stderr로 출력)
PUBLIC_URL=""
for _ in {1..30}; do
  PUBLIC_URL=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "${CF_LOG}" | head -n1 || true)
  [[ -n "${PUBLIC_URL}" ]] && break
  sleep 1
done

if [[ -z "${PUBLIC_URL}" ]]; then
  echo "ERROR: cloudflared 공개 URL을 받지 못했습니다. 로그:" >&2
  cat "${CF_LOG}" >&2
  exit 1
fi

# ── 7. 안내 출력 ───────────────────────────────────────────────
cat <<EOF

[3/3] 준비 완료!

  공개 URL :  ${PUBLIC_URL}/sse
  로컬 포트 :  ${MCP_PORT}
  로그      :  /tmp/supergateway.log, ${CF_LOG}

claude.ai 등록:
  1) https://claude.ai 우상단 프로필 → Settings → Connectors → Add custom connector
  2) Name:  ubermensch-vault
     URL :  ${PUBLIC_URL}/sse
  3) (선택) Authorization 헤더:  Bearer ${OBSIDIAN_API_KEY}
  4) 저장 후 새 채팅에서 connector 활성화

이 셸을 종료(Ctrl-C)하면 터널이 닫혀 URL이 만료됩니다.
영구 URL이 필요하면 cloudflared 명명된 터널(named tunnel)을 사용하세요.
EOF

# ── 8. 무한 대기 (Ctrl-C로 종료) ───────────────────────────────
wait "${CLOUDFLARED_PID}"
