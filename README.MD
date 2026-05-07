# ubermensch

[`eugeniughelbur/obsidian-second-brain`](https://github.com/eugeniughelbur/obsidian-second-brain)을 모델로 만든 개인용 세컨드 브레인. 장기적으로는 Obsidian 볼트 위에 얹는 Claude Code 스킬(슬래시 명령, 훅, 스케줄 에이전트)로 자라날 예정이다.

이번 첫 컷은 의도적으로 최소다 — 볼트에 쓰는 모든 Claude 세션을 구속하는 **볼트 스켈레톤**과 **운영 매뉴얼**까지만. 명령이나 자동화는 다음 컷.

## 구성

- `vault/` — Obsidian 볼트. Obsidian에서 이 폴더를 열어 사용한다.
  - `vault/_CLAUDE.md` — 운영 매뉴얼. 모든 Claude 세션이 가장 먼저 읽는다.
  - `vault/SYNC.md` — Claude Code, Claude Desktop, claude.ai 웹과 볼트를 동기화하는 방법.
  - `vault/Home.md`, `SOUL.md`, `CRITICAL_FACTS.md`, `index.md`, `log.md` — 루트 레벨 볼트 파일.
  - `vault/Templates/` — 타입별 노트 템플릿. 복사해서 쓰고 원본은 수정하지 않는다.
  - `vault/{Daily,Projects,People,Companies,Ideas,Tasks,Dev Logs,Reviews,Boards,Knowledge,Sessions}/` — 노트 폴더.
- `scripts/quick-mcp-tunnel.sh` — claude.ai 웹에 볼트를 연결하는 원격 MCP 터널 헬퍼.
- `scripts/import-claude-code-sessions.py` — `~/.claude/projects/*.jsonl`을 `vault/Sessions/`로 임포트.
- `scripts/import-claude-ai-export.py` — claude.ai 공식 데이터 export(zip)를 `vault/Sessions/claude-ai/`로 임포트.
- `scripts/fetch-claude-ai.py` — sessionKey 쿠키로 claude.ai 내부 API에서 모든 대화를 직접 가져와 `vault/Sessions/claude-ai/`에 저장 (가장 자동, 비공식).
- `scripts/auto-import-sessions.sh` — Claude Code Stop hook용. 세션 종료 시 자동 임포트.
- `.env.example` — 스크립트가 읽는 환경변수 템플릿.

## 사용법

1. `vault/`를 Obsidian(또는 마크다운 에디터)에서 볼트로 연다.
2. `vault/_CLAUDE.md`를 읽고 규칙을 익힌다.
3. `SOUL.md`와 `CRITICAL_FACTS.md`를 본인 정보로 채운다.
4. `vault/SYNC.md`를 따라 사용 중인 Claude 표면(Code/Desktop/웹)에 볼트를 연결한다.
5. `Templates/`에서 복사해 노트를 쓰기 시작한다.

## 로드맵

- [x] 볼트 스켈레톤 + `_CLAUDE.md`
- [x] 동기화 가이드 (`SYNC.md`)
- [x] claude.ai 웹용 원격 MCP 터널 헬퍼 (`scripts/quick-mcp-tunnel.sh`)
- [x] 과거 대화 임포터 (Claude Code 세션 + claude.ai 웹 export)
- [ ] 핵심 명령 (`/save`, `/daily`, `/world`)
- [ ] 사고 도구 (challenge / emerge / connect)
- [ ] 리서치 툴킷 (x / web / youtube)
- [ ] 스케줄 에이전트 + PostCompact 훅

## 크레딧

패턴과 규칙은 [`eugeniughelbur/obsidian-second-brain`](https://github.com/eugeniughelbur/obsidian-second-brain) (MIT)에서 가져와 한국어와 본 저장소 맥락에 맞게 다듬었다. 원문 코드를 그대로 복사하지는 않았고, 구조와 규칙의 형태만 옮겼다.
