# NotebookLM + Claude MCP Integration

Google NotebookLM을 Claude에 MCP(Model Context Protocol)로 연결하여,
Claude가 NotebookLM 노트북의 문서를 직접 조회하고 분석할 수 있도록 합니다.

## 구조

```
.
├── .mcp/
│   └── mcp-config.json          # MCP 서버 설정 (Claude Desktop / Cursor 등)
├── scripts/
│   └── setup.sh                 # 자동 설치 스크립트
├── package.json                 # Node.js 의존성
└── README.MD                    # 이 파일
```

## MCP 서버 비교

| 항목 | PleasePrompto/notebooklm-mcp | jacob-bd/notebooklm-mcp-cli |
|------|------------------------------|----------------------------|
| 언어 | Node.js | Python |
| 설치 | `npx notebooklm-mcp@latest` | `uv tool install notebooklm-mcp-cli` |
| 도구 수 | 16개 (full 프로필) | 29개 |
| CLI | 없음 | `nlm` CLI 포함 |
| 클라이언트 | Claude Code, Cursor, Codex, VS Code | Claude Code/Desktop, Cursor, Gemini |
| 특징 | 빠른 셋업, 프로필 기반 도구 관리 | 풍부한 CLI (노트북 생성, 팟캐스트, 퀴즈 등) |

## 빠른 시작

### 1. 자동 설치

```bash
./scripts/setup.sh
```

### 2. 수동 설치

**Option A: PleasePrompto/notebooklm-mcp (추천 - 간편)**

```bash
# Claude Code에 바로 추가
claude mcp add notebooklm -- npx notebooklm-mcp@latest

# 또는 npm으로 로컬 설치
npm install notebooklm-mcp@latest
```

**Option B: jacob-bd/notebooklm-mcp-cli (풍부한 기능)**

```bash
# 설치
uv tool install notebooklm-mcp-cli
# 또는
pip install notebooklm-mcp-cli

# Claude Code에 자동 등록
nlm setup add claude-code
```

### 3. Google 인증

```bash
# jacob-bd/notebooklm-mcp-cli 사용 시
nlm login

# PleasePrompto/notebooklm-mcp는 첫 실행 시 브라우저에서 자동 인증
```

> **보안 팁**: 자동화 용도로 별도의 Google 계정 사용을 권장합니다.

### 4. Claude Desktop 설정

`~/.config/claude/claude_desktop_config.json` 에 아래 내용을 추가합니다:

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "npx",
      "args": ["-y", "notebooklm-mcp@latest"]
    }
  }
}
```

또는 자동 설정:

```bash
nlm setup add claude-desktop
```

## 사용 예시

### Claude에서 NotebookLM 노트북 조회

```
"NotebookLM에서 내 노트북 목록을 보여줘"
"AI 연구 노트북에서 transformer 아키텍처에 대해 검색해줘"
```

### nlm CLI로 노트북 관리

```bash
# 노트북 생성
nlm notebook create "AI Research"

# 소스 추가
nlm source add <notebook-id> --url "https://arxiv.org/abs/..."

# 팟캐스트 생성
nlm audio create <notebook-id> --format deep_dive --confirm

# 퀴즈 생성
nlm quiz <notebook-id>

# 마인드맵 생성
nlm mindmap <notebook-id>
```

### MCP 프로필 설정 (PleasePrompto)

```bash
# 도구 수 줄이기 (토큰 절약)
npx notebooklm-mcp config set profile minimal    # 빠른 질문용
npx notebooklm-mcp config set profile standard   # 라이브러리 관리 추가
npx notebooklm-mcp config set profile full        # 전체 기능
```

## 참고

- 이 MCP는 29개의 도구를 제공합니다. NotebookLM을 사용하지 않을 때는 비활성화하여 컨텍스트 윈도우를 절약하세요.
- Claude Code에서 `@notebooklm-mcp`로 토글 가능합니다.
- Google이 자동화된 사용을 감지할 수 있으므로, 전용 Google 계정 사용을 권장합니다.

## 참고 자료

- [XDA: NotebookLM connects to Claude through MCP](https://www.xda-developers.com/notebooklm-connects-to-claude-through-mcp/)
- [PleasePrompto/notebooklm-mcp](https://github.com/PleasePrompto/notebooklm-mcp)
- [jacob-bd/notebooklm-mcp-cli](https://github.com/jacob-bd/notebooklm-mcp-cli)
- [Claude Code MCP Docs](https://code.claude.com/docs/en/mcp)
