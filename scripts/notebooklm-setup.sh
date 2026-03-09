#!/bin/bash
# NotebookLM MCP Integration Setup Script
# 이 스크립트는 NotebookLM MCP 서버를 Claude Code에 설정합니다.

set -e

echo "============================================"
echo "  NotebookLM MCP Integration Setup"
echo "============================================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}[1/5] 필수 도구 확인 중...${NC}"
check_tool() {
    if command -v "$1" &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} $1 $(command -v "$1")"
        return 0
    else
        echo -e "  ${RED}✗${NC} $1 not found"
        return 1
    fi
}

check_tool node
check_tool npm
check_tool npx
check_tool python3

echo ""

# Option 1: PleasePrompto/notebooklm-mcp (Node.js)
echo -e "${BLUE}[2/5] PleasePrompto/notebooklm-mcp 설치...${NC}"
if npm list notebooklm-mcp &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} notebooklm-mcp 이미 설치됨"
else
    npm install notebooklm-mcp@latest
    echo -e "  ${GREEN}✓${NC} notebooklm-mcp 설치 완료"
fi

echo ""

# Option 2: jacob-bd/notebooklm-mcp-cli (Python)
echo -e "${BLUE}[3/5] jacob-bd/notebooklm-mcp-cli 설치...${NC}"
if command -v nlm &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} notebooklm-mcp-cli 이미 설치됨"
else
    if command -v uv &> /dev/null; then
        uv tool install notebooklm-mcp-cli
    else
        pip install notebooklm-mcp-cli
    fi
    echo -e "  ${GREEN}✓${NC} notebooklm-mcp-cli 설치 완료"
fi

echo ""

# Configure Claude Code MCP
echo -e "${BLUE}[4/5] Claude Code MCP 설정...${NC}"
if command -v claude &> /dev/null; then
    echo "  Claude Code에 MCP 서버 등록 중..."
    claude mcp add notebooklm -- npx notebooklm-mcp@latest 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} Claude Code MCP 설정 완료"
else
    echo -e "  ${YELLOW}⚠${NC} Claude Code CLI를 찾을 수 없습니다."
    echo "    수동 설정이 필요합니다. README를 참고하세요."
fi

echo ""

# Setup complete
echo -e "${BLUE}[5/5] 설정 완료!${NC}"
echo ""
echo "============================================"
echo -e "${GREEN}  설정이 완료되었습니다!${NC}"
echo "============================================"
echo ""
echo "다음 단계:"
echo ""
echo -e "${YELLOW}1. Google 인증 (최초 1회):${NC}"
echo "   nlm login"
echo ""
echo -e "${YELLOW}2. Claude Desktop 설정 (선택):${NC}"
echo "   nlm setup add claude-desktop"
echo ""
echo -e "${YELLOW}3. 노트북 만들기:${NC}"
echo "   nlm notebook create \"내 연구 노트\""
echo ""
echo -e "${YELLOW}4. 소스 추가:${NC}"
echo "   nlm source add <notebook-alias> --url \"https://example.com/article\""
echo ""
echo -e "${YELLOW}5. Claude에서 사용하기:${NC}"
echo "   \"NotebookLM에서 내 노트북 목록을 보여줘\""
echo ""
