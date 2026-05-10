# Windows 셋업 체크리스트

> 위에서부터 순서대로. 각 단계는 약 5~20분. 전체 약 2~3시간.
> 6번(CLAUDE.md 작성)이 가장 오래 걸리고 가장 중요하다. 시간을 아끼지 말 것.

## 사전 준비

- [ ] Windows 10/11
- [ ] Google 계정 + Google Drive (또는 Dropbox/OneDrive)
- [ ] (옵션) Anthropic 계정 — Web Clipper AI Interpreter용
- [ ] (옵션) GitHub 계정 — git 백업용

---

## 1. Obsidian 설치

- [ ] PowerShell에서: `winget install Obsidian.Obsidian`
- [ ] 또는 https://obsidian.md/download 에서 인스톨러 다운로드
- [ ] 첫 실행 시 "Create new vault" 선택 (다음 단계에서 위치 지정)

## 2. Vault 위치 결정 (중요)

- [ ] Google Drive 폴더 안에 둘 위치 결정: `%USERPROFILE%\Google Drive\Vault\brain`
- [ ] (Cottrell 팁) 클라우드 폴더 안에 두면 모든 기기에서 같은 vault 사용 가능
- [ ] Obsidian에서 "Create new vault" → 위 경로 지정 → vault 이름 `brain`

> **주의**: `.obsidian/` 폴더(설정)도 같이 동기화됨. 다른 기기에서 다른 플러그인 설정을 원하면 별도 vault 권장.

## 3. 이 셋업 키트 클론

- [ ] PowerShell:
```powershell
cd %USERPROFILE%
git clone <이 레포 주소> ubermensch
cd ubermensch\obsidian-setup
```
- [ ] 이 폴더를 별도 파일 탐색기 창으로 열어두기 (자주 참고)

## 4. Vault에 5폴더 + CLAUDE.md 만들기

Vault 루트에서 다음 폴더 생성:

```
brain/
├── CLAUDE.md          (다음 단계에서 작성)
├── home.md            (templates/home.md 복사)
├── inbox/
├── notes/
│   └── journal/       (Daily notes용 하위 폴더)
├── ideas/
├── projects/
├── templates/         (이 키트의 templates/ 내용 복사)
└── attachments/       (이미지 등)
```

- [ ] Obsidian 좌측 사이드바에서 폴더 생성 또는 파일 탐색기에서 직접 생성

## 5. 템플릿/시드 복사

- [ ] 이 키트의 `templates/` 내용 → vault의 `templates/`로 복사
- [ ] 이 키트의 `starter-notes/` 5개 파일 → vault의 `inbox/`로 복사
- [ ] 이 키트의 `templates/CLAUDE.md` → vault 루트로 복사
- [ ] 이 키트의 `templates/home.md` → vault 루트로 복사

## 6. ★ CLAUDE.md 채우기 (가장 중요)

> 이게 가장 오래 걸린다. 30분~1시간을 투자할 가치가 있다. CLAUDE.md 품질 = Claude 답변 품질.

- [ ] Obsidian에서 vault 루트의 `CLAUDE.md` 열기
- [ ] `<!-- 예) ... -->` 주석은 그대로 두되, 위 빈 줄에 본인 정보 작성
- [ ] **Who I Am** 섹션 완성: 이름, 일, Focus(한 가지), Goals 2026(3개)
- [ ] **Current Projects** 섹션: Active, Stuck on, Next milestone
- [ ] **What I Am Reading and Thinking About** 섹션: 현재 집착/질문 3~5개
- [ ] 저장 후 다시 읽어보며 솔직한지 점검 (가장 부족한 부분이 가장 중요)
- [ ] **매주 월요일 아침 5분** 일정 등록 — CLAUDE.md 업데이트 시간

## 7. Obsidian 기본 설정

- [ ] **Settings → Files & Links**
  - Default location for new notes: `inbox`
  - Use [[Wikilinks]]: ON
  - New link format: Shortest path when possible
  - Detect all file extensions: OFF
- [ ] **Settings → Daily notes**
  - Date format: `YYYY-MM-DD`
  - Template file location: `templates/daily-note.md`
  - New file location: `notes/journal`
- [ ] **Settings → Templates** (core plugin)
  - Template folder location: `templates`

## 8. 커뮤니티 플러그인 설치

- [ ] **Settings → Community plugins → Turn on community plugins**
- [ ] **Browse** 후 다음 검색하여 설치 + 활성화:
  - [ ] **Dataview** (blacksmithgu) — vault를 DB처럼 쿼리
  - [ ] **Templater** (SilentVoid13) — 강력한 템플릿 엔진
  - [ ] **Periodic Notes** — Daily/Weekly notes 통합
  - [ ] **Tag Wrangler** — 태그 일괄 리네임/머지
  - [ ] **Excalidraw** — 다이어그램/마인드맵
  - [ ] **Style Settings** — 테마 세부 조정
  - [ ] **Obsidian Git** — 자동 백업
  - [ ] **Local REST API** — MCP 연결용 (11번에서 사용)

> 자세한 추천 레포 목록은 `08-curated-repos.md`.

## 9. Obsidian Git 셋업

- [ ] PowerShell에서 vault 루트로:
```powershell
cd "%USERPROFILE%\Google Drive\Vault\brain"
git init
echo ".obsidian/workspace*" > .gitignore
echo "attachments/" >> .gitignore
git add .
git commit -m "initial vault"
```
- [ ] (옵션) GitHub에 private repo 만들고 `git remote add origin ...` → `git push -u origin main`
- [ ] Obsidian Git 플러그인 설정:
  - Vault backup interval: 30 (분마다 자동 커밋)
  - Auto pull interval: 60

## 9.5. ★ Web Clipper 설치 (자동 캡처)

- [ ] Chrome / Firefox / Edge / Safari 스토어에서 **"Obsidian Web Clipper"** 검색 → 설치
- [ ] 확장 아이콘 우클릭 → Options
- [ ] **General**:
  - Vault: `brain`
  - Default folder: `inbox/`
  - Filename: `{{date|date:"YYYY-MM-DD"}}-{{title|slugify}}`
- [ ] **Templates** → Import 클릭 → 이 키트의 `templates/webclipper-templates/`의 JSON 5개 모두 import:
  - default-article.json
  - twitter-thread.json
  - youtube.json
  - github-readme.json
  - research-paper.json
- [ ] **Smart Rules**:
  - `*.twitter.com, *.x.com` → twitter-thread
  - `*.youtube.com, youtu.be` → youtube
  - `*.github.com` → github-readme
  - `arxiv.org, *.nature.com, *.scholar.google.com` → research-paper
  - (기본) → default-article
- [ ] **Interpreter** (옵션, 강력 추천) — `05-web-clipper.md`의 API 키 가이드 따라 셋업
- [ ] **단축키**: 브라우저 확장 설정에서 `Alt+Shift+O` (Windows) 또는 `Cmd+Shift+O` (Mac)로 바인딩
- [ ] 테스트: 아무 글에서 단축키 → vault의 `inbox/`에 파일 생성 확인

## 10. ★ Claude Code 통합

- [ ] https://claude.ai/code 에서 Claude Code 설치
- [ ] 터미널에서 `claude` 실행 → 인증
- [ ] **Plugin marketplace에서 kepano/obsidian-skills 추가**:
```
/plugin marketplace add kepano/obsidian-skills
```
- [ ] 설치 후 `/plugin list`로 확인 — 5개 스킬(`obsidian-markdown`, `obsidian-bases`, `json-canvas`, `obsidian-cli`, `defuddle`) 표시
- [ ] **Custom Instructions 한 줄** 추가 (Claude Code 설정 또는 `~/.claude/CLAUDE.md`에):
```
Before answering any question, always search the Obsidian vault at
C:\Users\<USERNAME>\Google Drive\Vault\brain for relevant notes.
Use what you find to inform your response.
Save new decisions to inbox/decisions.md and new actions to inbox/action-tracker.md.
Always cite vault notes using [[wikilinks]].
```

## 11. (권장) Obsidian MCP 연결

- [ ] Obsidian에서 **Local REST API** 플러그인 활성화 (8번에서 설치함)
- [ ] **Settings → Local REST API**
  - Enable HTTPS: ON
  - Copy API Key (긴 문자열)
- [ ] `~/.claude/mcp.json` (없으면 생성) 편집:
```json
{
  "mcpServers": {
    "obsidian-vault": {
      "command": "npx",
      "args": ["-y", "obsidian-mcp-server"],
      "env": {
        "OBSIDIAN_API_KEY": "<여기에 복사한 키>",
        "OBSIDIAN_API_URL": "https://127.0.0.1:27124",
        "OBSIDIAN_VAULT_PATH": "C:/Users/<USERNAME>/Google Drive/Vault/brain"
      }
    }
  }
}
```
- [ ] Claude Code 재시작 → `/mcp` 명령으로 `obsidian-vault` 연결 확인
- [ ] 테스트: "내 vault의 CLAUDE.md를 읽어줘" → 파일 내용 출력되면 성공

> 대안 MCP 서버: `MarkusPfundstein/mcp-obsidian`, `jacksteamdev/obsidian-mcp-tools` (자세한 비교는 `08-curated-repos.md`).

## 12. Graph View 확인

- [ ] Obsidian에서 `Ctrl+G` (Graph View)
- [ ] 5개 시드 노트가 노드로 보임
- [ ] 일부 노드끼리 `[[ ]]` 링크로 연결되어 있음 → 살아있는 vault의 시작

## 13. 첫 테스트 (Pattern Finder)

- [ ] Claude Code 또는 Claude.ai에서 이 키트의 `prompts/pattern-finder.md` 내용 붙여넣기
- [ ] Claude가 CLAUDE.md + 5개 시드 노트 기반으로 패턴 답변
- [ ] 답변이 일반론적이면 CLAUDE.md를 더 채워야 함 (6번 복귀)
- [ ] 답변이 구체적이고 [[wikilink]] 인용 포함되면 시스템 작동

## 14. (옵션) AgriciDaniel/claude-obsidian 풀스택

원하면 `06-agricidaniel-wiki.md` 참고. `/wiki`, `ingest`, `/autoresearch`, `lint the wiki` 자동 명령 추가됨. 처음 1~2주는 미니멀 트랙으로 운영한 뒤 도입 권장.

## 15. (다음 단계) 자동화 레이어

`07-automation-future.md` 참고. Web Clipper로 Capture 레이어 기본은 완성됨. 추가로:
- N8N + Telegram bot — 모바일/즉시 캡처
- Whisper — 음성 → 텍스트
- 통화 전사 자동 라우팅 (Fathom + Zapier)
- Daily Brief 6am 자동화

---

## 매일 / 매주 루틴

### 매일 아침 (자동 또는 5분)
- [ ] Daily Brief 산출물(`inbox/brief-{date}.md`) 읽기 — `prompts/daily-brief.md` 수동 실행 또는 N8N 자동화

### 매주 월요일 (15분)
- [ ] CLAUDE.md의 **Current Projects** + **What I Am Reading** 섹션 업데이트
- [ ] Weekly Synthesis 실행 — `prompts/weekly-synthesis.md`
- [ ] 산출물을 `notes/weekly/{date}-synthesis.md`에 저장

### 즉시 (수시로)
- [ ] 글 읽다가 → `Alt+Shift+O`로 Web Clipper
- [ ] 아이디어 떠오르면 → `Ctrl+N`으로 inbox/ 빠른 노트
- [ ] 막히면 → Claude Code에 질문 (자동으로 vault 검색됨)

---

## 트러블슈팅

| 문제 | 해결 |
|---|---|
| Google Drive 동기화 충돌 | `.obsidian/workspace*` 파일을 `.gitignore`와 Google Drive 제외 목록에 추가 |
| Obsidian Git에서 인증 실패 | `git remote -v`로 HTTPS 확인 → Personal Access Token 사용 |
| MCP 연결 실패 | Local REST API의 HTTPS 인증서 신뢰 필요. 또는 HTTP(27123) 사용 |
| Claude 답변이 일반론적 | CLAUDE.md 부실. 6번 단계 다시 + Custom Instructions 점검 |
| Web Clipper에서 한글 깨짐 | 템플릿 properties에서 `type: text` 확인 |
