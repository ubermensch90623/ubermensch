#!/usr/bin/env bash
set -euo pipefail

# gbrain 설치/초기화 스크립트
# 참고: https://github.com/garrytan/gbrain
#
# 동작:
#   1) bun이 없으면 안내하고 종료
#   2) ~/src/gbrain 에 clone (이미 있으면 pull)
#   3) bun install && bun link 로 전역 `gbrain` 명령 등록
#   4) `gbrain init` 안내 (대화형이라 자동화하지 않음)

GBRAIN_DIR="${GBRAIN_DIR:-$HOME/src/gbrain}"
REPO_URL="https://github.com/garrytan/gbrain.git"

if ! command -v bun >/dev/null 2>&1; then
  echo "bun이 설치되어 있지 않습니다. 먼저 설치하세요: https://bun.sh"
  echo "  curl -fsSL https://bun.sh/install | bash"
  exit 1
fi

mkdir -p "$(dirname "$GBRAIN_DIR")"

if [ -d "$GBRAIN_DIR/.git" ]; then
  echo "[gbrain] 기존 클론 업데이트: $GBRAIN_DIR"
  git -C "$GBRAIN_DIR" pull --ff-only
else
  echo "[gbrain] clone: $REPO_URL -> $GBRAIN_DIR"
  git clone "$REPO_URL" "$GBRAIN_DIR"
fi

cd "$GBRAIN_DIR"
echo "[gbrain] bun install"
bun install
echo "[gbrain] bun link (전역 gbrain 명령 등록)"
bun link

echo
echo "설치 완료. 이어서 다음을 직접 실행하세요:"
echo "  gbrain init                       # 최초 1회, API 키 입력 프롬프트가 뜹니다"
echo "  gbrain import ~/notes/            # 기존 마크다운/노트 인덱싱"
echo "  gbrain query \"무슨 주제가 있지?\"  # 동작 확인"
echo
echo "Claude Code에서 MCP로 쓰려면 이 레포의 .mcp.json 이 이미 준비되어 있습니다."
echo "Claude Code를 재시작하면 자동으로 gbrain MCP 서버에 연결됩니다."
