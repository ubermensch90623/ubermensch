---
date: 2026-05-06
type: guide
tags: [guide, sync, setup]
ai-first: true
---

## For future Claude

이 노트는 2026-05-06에 저장된 동기화 설정 가이드다. 이 볼트를 Claude Code, Claude Desktop, claude.ai 웹 채팅에서 모두 같은 영구 메모리로 쓰기 위한 방법을 정리한다.
한 번 설정해두면 어떤 Claude 표면에서든 같은 볼트를 읽고 쓸 수 있어서 세션 간 맥락이 끊기지 않는다.

# 동기화 가이드 — Claude의 모든 채팅에서 같은 볼트 쓰기

## 핵심 원리

볼트(이 폴더)가 **영구 메모리**다. Claude 자체는 세션마다 잊는다. 그래서 모든 Claude 표면이 이 볼트를 읽고 쓰도록 "다리(bridge)"를 깐다. 다리의 종류만 표면별로 다르다.

```
              ┌─────────────────┐
              │  Obsidian Vault │  ← 영구 메모리 (이 폴더)
              │   /vault        │
              └────────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐   ┌─────▼─────┐  ┌─────▼──────┐
   │ Claude  │   │  Claude   │  │ claude.ai  │
   │  Code   │   │  Desktop  │  │    웹      │
   │         │   │           │  │            │
   │파일시스템│   │  로컬 MCP  │  │ 원격 MCP   │
   │ 직접    │   │  서버     │  │ Connector │
   └─────────┘   └───────────┘  └────────────┘
```

## 표면별 설정

### 1) Claude Code (CLI/IDE)

가장 쉽다. **별도 설정 없음.** Claude Code는 작업 디렉터리의 파일시스템에 직접 접근한다. 이 저장소를 클론하고 Claude Code를 실행하면 끝.

```bash
git clone <repo-url> ubermensch
cd ubermensch
claude
```

Claude는 `vault/_CLAUDE.md`를 읽고 규칙대로 노트를 읽고 쓴다. 추가 설정을 원하면 프로젝트 루트에 `CLAUDE.md`를 만들어 "이 디렉터리의 `vault/`가 Obsidian 볼트다"라고 명시할 수 있다.

### 2) Claude Desktop

로컬 MCP 서버를 설치한다. 두 가지 옵션:

#### 옵션 A — `mcp-obsidian` (Markus Pfundstein, REST API 기반)

Obsidian의 **Local REST API** 커뮤니티 플러그인이 필요하다.

1. Obsidian에서 Settings → Community plugins → Browse → **Local REST API** 설치 및 활성화
2. 플러그인 설정에서 API 키 복사 (기본 호스트 `127.0.0.1`, 기본 포트 `27124`)
3. `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) 또는 `%APPDATA%/Claude/claude_desktop_config.json` (Windows) 편집:

```json
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "uvx",
      "args": ["mcp-obsidian"],
      "env": {
        "OBSIDIAN_API_KEY": "<복사한_API_키>",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27124"
      }
    }
  }
}
```

4. Claude Desktop 재시작. 사용 가능한 도구: `list_files_in_vault`, `get_file_contents`, `search`, `patch_content`, `append_content`, `delete_file`.

#### 옵션 B — Filesystem MCP (Obsidian 플러그인 없이)

Obsidian이 켜져 있을 필요 없음. 단순 파일시스템 접근.

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/절대/경로/ubermensch/vault"]
    }
  }
}
```

장점: 가볍다. 단점: Obsidian의 검색/그래프 기능을 우회하기 때문에 search 효율이 옵션 A보다 떨어진다.

### 3) claude.ai 웹 채팅 (가장 중요한 부분)

2026년 3월부터 claude.ai는 **Custom Connectors via Remote MCP**를 지원한다. Free 플랜은 1개, 유료 플랜은 여러 개 연결 가능.

핵심 함정: claude.ai의 클라우드 서버에서 당신의 MCP 서버로 인터넷을 통해 접속한다. 즉, 로컬 `localhost:27124`로는 안 된다. **공개 URL이 필요하다.**

#### 권장 경로 — Cloudflare Tunnel + mcp-obsidian

1. 위 (2-A)대로 로컬에 `mcp-obsidian` + Local REST API 플러그인 세팅 완료
2. `mcp-obsidian`을 SSE/HTTP 모드로 노출 (저장소 README의 `--transport sse` 옵션 참고)
3. Cloudflare Tunnel 설치: `brew install cloudflared` 또는 [공식 가이드](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)
4. 터널 실행: `cloudflared tunnel --url http://localhost:8000` → 공개 HTTPS URL을 받는다
5. claude.ai 우상단 프로필 → **Settings → Connectors → Add custom connector**
6. 이름: `ubermensch-vault`, URL: 위에서 받은 공개 URL, 인증: Bearer 토큰(Local REST API 키)
7. 새 채팅에서 connector를 활성화하면, claude.ai가 볼트를 직접 읽고 쓸 수 있다

대안 — **ClaudeSync** (단방향, 더 간단): [jahwag/ClaudeSync](https://github.com/jahwag/ClaudeSync) 파이썬 도구가 로컬 폴더를 claude.ai Project의 지식 파일로 자동 업로드한다. 단점: claude.ai → 볼트 쓰기는 안 됨, 읽기만.

### 4) 여러 기기 사이의 동기화

볼트가 git 저장소에 있으니 git이 자연스러운 동기화 계층이다.

```bash
# 작업 시작 시
git pull origin claude/obsidian-second-brain-99bMG

# 작업 중간 (또는 Claude가 노트를 추가한 뒤)
git add vault/
git commit -m "vault: <요약>"
git push
```

자동화하고 싶으면 cron이나 launchd로 5분마다 `git pull && git push` 돌리는 스크립트를 두면 된다. 단, 두 기기가 동시에 쓰면 충돌이 나니 주의.

Obsidian Sync(유료) 또는 iCloud/Dropbox에 `vault/`를 놓으면 git 없이도 동기화되지만, 이력 추적은 git이 더 깔끔하다.

## 추천 조합

당신의 사용 패턴에 따라:

| 패턴 | 추천 |
|---|---|
| 거의 Claude Code에서만 작업 | (1)만 — 추가 설정 0 |
| Claude Code + Claude Desktop을 같이 씀 | (1) + (2-A) |
| claude.ai 웹에서 모바일/외부에서도 쓰고 싶음 | (1) + (2-A) + (3) — Cloudflare Tunnel 경로 |
| 가볍게 읽기만 필요 | (1) + (3) ClaudeSync |
| 여러 기기 사용 | 위 조합 + (4) git 동기화 |

## 다음 단계 (이 저장소 로드맵)

지금은 볼트 스켈레톤만 있다. 다음 컷에서 추가될 것:

- `commands/` — `/save`, `/daily`, `/world` 같은 슬래시 명령
- `hooks/` — PostCompact 백그라운드 에이전트 (컨텍스트 압축 시 자동으로 볼트에 인사이트 저장)
- `scripts/setup.sh` — Claude Desktop config 자동 편집
- `scripts/quick-mcp-tunnel.sh` — Cloudflare Tunnel 한 줄로 띄우는 헬퍼

이것들이 들어오면 위 설정 중 일부가 더 자동화된다.
