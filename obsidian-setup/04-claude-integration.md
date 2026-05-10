# Claude Integration — 3 레이어

Claude를 Obsidian과 연결하는 3가지 방법. 위에서 아래로 갈수록 강력해진다.

## 레이어 1: kepano/obsidian-skills (필수, 5분)

[obsidian-skills](https://github.com/kepano/obsidian-skills) — Obsidian CEO Stephan Ango가 만든 Claude Code 에이전트 스킬 팩 (30k★).

### 설치

```
/plugin marketplace add kepano/obsidian-skills
```

또는 수동:
```bash
npx skills add https://github.com/kepano/obsidian-skills
```

### 제공 스킬 5개

| 스킬 | 기능 |
|---|---|
| `obsidian-markdown` | Obsidian Flavored Markdown 작성 — wikilinks, embeds, callouts |
| `obsidian-bases` | Obsidian Bases (DB 뷰) 생성/편집 |
| `json-canvas` | JSON Canvas 파일 (다이어그램) 생성/편집 |
| `obsidian-cli` | Obsidian CLI로 vault 조작 |
| `defuddle` | 웹 페이지에서 깨끗한 마크다운 추출 |

### 사용 예시 (Claude Code에서)
```
"내 vault에 'Jobs to be Done 정리' MOC를 만들고
관련된 notes 5개를 wikilink로 연결해줘"
```
→ kepano/obsidian-skills의 `obsidian-markdown`이 자동 호출되어 적절한 형식으로 작성.

## 레이어 2: Obsidian MCP 서버 (권장, 10분)

Claude가 vault를 **직접** read/write/move/search. Copy-paste 없어짐.

### 옵션 비교

| MCP 서버 | 특징 | 권장 상황 |
|---|---|---|
| `MarkusPfundstein/mcp-obsidian` | REST API 기반. 가장 널리 쓰임 | 일반적인 경우 — **권장** |
| `iansinnott/obsidian-claude-code-mcp` | WebSocket 기반, Claude Code 자동 발견 | Claude Code 사용자 |
| `jacksteamdev/obsidian-mcp-tools` | 시맨틱 검색 + Templater 프롬프트 | 고급 — Templater 활용 시 |

### 셋업 (MarkusPfundstein/mcp-obsidian 기준)

**1. Obsidian Local REST API 플러그인 활성화**
- Settings → Community plugins → Browse → "Local REST API" 설치
- Enable HTTPS: ON
- API Key 복사 (긴 문자열)
- 포트 확인: HTTPS는 27124, HTTP는 27123

**2. MCP 설정 파일 편집**
`~/.claude/mcp.json` (없으면 생성):
```json
{
  "mcpServers": {
    "obsidian-vault": {
      "command": "npx",
      "args": ["-y", "mcp-obsidian"],
      "env": {
        "OBSIDIAN_API_KEY": "여기에_API_KEY_붙여넣기",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27124"
      }
    }
  }
}
```

**3. Claude Code 재시작**

**4. 확인**
```
/mcp
```
→ `obsidian-vault: connected` 표시되면 성공.

```
"내 vault의 CLAUDE.md를 읽어줘"
```
→ 파일 내용 출력되면 완전 작동.

### Self-signed 인증서 문제

Local REST API의 HTTPS는 self-signed 인증서. Node가 거부하면:
- `NODE_TLS_REJECT_UNAUTHORIZED=0` 환경변수 (로컬만 권장)
- 또는 HTTP 27123 사용 (보안 약간 떨어짐, 로컬만이면 OK)

## 레이어 3: Custom Instructions (가장 중요한 한 줄)

> "That single instruction means Claude reads your vault before every reply." — Cottrell

### 어디에 넣나
- Claude Code: `~/.claude/CLAUDE.md` 또는 settings의 system prompt
- Claude.ai Projects: Project Instructions 필드
- Claude Cowork: User Preferences

### 정확한 문구 (복사해서 사용)

```
Before answering any question, always search the Obsidian vault at
C:\Users\<USERNAME>\Google Drive\Vault\brain for relevant notes.
Use what you find to inform your response.

Vault routing rules:
- New decisions → inbox/decisions.md (append)
- New action items → inbox/action-tracker.md (append)
- External source summaries → notes/{date}-{slug}.md with #literature tag
- My own synthesized thinking → ideas/{slug}.md with #permanent tag
- Topic hubs → ideas/MOC-{topic}.md with #moc tag

Always cite vault notes using [[wikilinks]].
Read vault/CLAUDE.md at the start of every session for context.
Do not give generic answers — ground every response in vault content.
Challenge my assumptions when they conflict with my own past notes.
```

### 효과
- 매 질문마다 자동으로 vault 검색
- 답변에 본인 노트가 [[wikilink]]로 인용됨
- Claude가 새 결정/액션을 알아서 vault에 기록
- 일반론 답변 사라짐 — 본인 컨텍스트로 답함

## 통합 워크플로우 예시

### "이번 주 뭐가 가장 중요해?"
1. Claude Code에 입력
2. Custom Instructions → vault 검색 자동
3. MCP → vault의 `projects/`와 `inbox/action-tracker.md` 직접 읽음
4. kepano/obsidian-skills → MOC 형식으로 답변 작성
5. CLAUDE.md의 Goals/Current Projects 컨텍스트로 우선순위 매김
6. 답변에 `[[payment-dashboard-v2/decisions]]` 같은 인용 포함
7. 결정사항을 `inbox/decisions.md`에 append

이 모든 게 한 질문으로.

### "지난주 통화 전사 중 client X 관련된 거 요약해줘"
1. MCP가 `notes/` 또는 `inbox/` 검색
2. 관련 transcripts 발견
3. 요약 + 액션 아이템 추출
4. 결과를 `projects/client-x/2026-W19-summary.md`로 작성
5. `inbox/action-tracker.md`에 새 액션 append

## 트러블슈팅

| 증상 | 원인 / 해결 |
|---|---|
| `/mcp` 명령이 obsidian-vault를 못 찾음 | mcp.json 경로 확인. `~/.claude/` 또는 Claude Code 설정 위치 |
| MCP 연결되지만 read 실패 | Local REST API 플러그인 활성화 / API Key 일치 확인 |
| HTTPS 인증서 오류 | HTTP 27123으로 변경 또는 인증서 신뢰 |
| Claude가 vault 검색을 안 함 | Custom Instructions가 등록 안 됨. `~/.claude/CLAUDE.md` 확인 |
| 답변이 일반론적 | vault의 CLAUDE.md 부실. 6번 단계 다시 |
| Claude가 새 파일 작성 시 위치 잘못됨 | Vault Routing Rules가 CLAUDE.md에 없거나 모호함 |

## 다음 단계

이 3레이어가 단단해지면 → `06-agricidaniel-wiki.md`로 자동 wiki 시스템 추가.
