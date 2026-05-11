# Windows 셋업 체크리스트

> 위에서부터 순서대로. 각 단계는 약 5~20분. 전체 약 2~3시간.
> 6번(CLAUDE.md 작성)이 가장 오래 걸리고 가장 중요하다. 시간을 아끼지 말 것.

## ⚡ TL;DR — 30분 미니멀 셋업

시간 없으면 이것만:

1. Obsidian 설치 → vault 만들기 (1번~2번)
2. 이 키트 클론 → `templates/CLAUDE.md`를 vault 루트에 복사하고 5분만 채우기 (3번~6번)
3. `templates/`와 `starter-notes/`, `inbox-init/`를 vault에 복사 (5번)
4. Templater 플러그인 1개만 설치 (8번 중)
5. Claude Code 설치 + `/plugin marketplace add kepano/obsidian-skills` + `/plugin install obsidian@obsidian-skills` (10번)
6. Claude에 첫 질문: "내 vault의 4개 시드 노트에서 못 본 패턴을 찾아줘"

여기서부터 vault가 살아남. 나머지(MCP, Web Clipper, Git, 자동화)는 나중에 한 단계씩.

## 🎯 어떤 Claude를 쓰는가? (트랙 결정)

이 키트는 두 가지 Claude 클라이언트를 지원. 본인 환경에 따라 선택:

| | **Claude Code** (터미널) | **Claude Cowork / Desktop** (앱) |
|---|---|---|
| `kepano/obsidian-skills` (10번) | ✅ 사용 | ❌ 건너뛰기 (Cowork 미지원) |
| MCP 서버 (11번) | ✅ `~/.claude/mcp.json` | ✅ `%APPDATA%\Claude\claude_desktop_config.json` |
| Custom Instructions 위치 | `~/.claude/CLAUDE.md` | 앱 **Settings → User Preferences** 필드 |
| vault CLAUDE.md (6번) | 양쪽 모두 동일 | 양쪽 모두 동일 |
| Web Clipper (9.5번) | 양쪽 모두 동일 | 양쪽 모두 동일 |
| 프롬프트 사용 | 양쪽 모두 동일 (복사 붙여넣기) | 양쪽 모두 동일 |
| Vault 구조/템플릿/시드 | 양쪽 모두 동일 | 양쪽 모두 동일 |

> **Cowork 사용자**는 10번을 통째로 건너뛰고 11번에서 config 파일 경로만 다르게. 실용적 차이는 거의 없음 — Cowork는 MCP가 obsidian-skills의 기능을 대부분 커버.

> **둘 다 쓰는 경우**: 같은 vault에 양쪽 모두 연결 가능. MCP config만 각각 등록. 두 클라이언트 사이 충돌 없음.

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

## 5. 템플릿/시드/초기 파일 복사

PowerShell에서 (대체로 robocopy가 안전):
```powershell
$KIT = "$env:USERPROFILE\ubermensch\obsidian-setup"
$VAULT = "$env:USERPROFILE\Google Drive\Vault\brain"

# 템플릿 (note 양식)
robocopy "$KIT\templates" "$VAULT\templates" /E /XD webclipper-templates

# 시드 노트 (4개) → inbox/로
robocopy "$KIT\starter-notes" "$VAULT\inbox"

# inbox 초기 누적 파일 (decisions.md, action-tracker.md)
robocopy "$KIT\inbox-init" "$VAULT\inbox"

# Vault 루트 파일
Copy-Item "$KIT\templates\CLAUDE.md" "$VAULT\CLAUDE.md"
Copy-Item "$KIT\templates\home.md"  "$VAULT\home.md"
```

체크:
- [ ] `vault/templates/` 안에 daily-note.md, zettel.md, literature.md, moc.md, project.md, home.md 6개
- [ ] `vault/inbox/`에 시드 4개(001~004) + `decisions.md` + `action-tracker.md`
- [ ] `vault/CLAUDE.md`와 `vault/home.md`가 루트에 있음

## 6. ★ CLAUDE.md 채우기 (가장 중요)

> 이게 가장 오래 걸린다. 30분~1시간을 투자할 가치가 있다. CLAUDE.md 품질 = Claude 답변 품질.

- [ ] Obsidian에서 vault 루트의 `CLAUDE.md` 열기
- [ ] `<!-- 예) ... -->` 주석은 그대로 두되, 위 빈 줄에 본인 정보 작성
- [ ] **Who I Am** 섹션 완성: 이름, 일, Focus(한 가지), Goals 2026(3개)
- [ ] **Current Projects** 섹션: Active, Stuck on, Next milestone
- [ ] **What I Am Reading and Thinking About** 섹션: 현재 집착/질문 3~5개
- [ ] 저장 후 다시 읽어보며 솔직한지 점검 (가장 부족한 부분이 가장 중요)
- [ ] **매주 월요일 아침 5분** 일정 등록 — CLAUDE.md 업데이트 시간

## 7. Obsidian 기본 설정 (Core)

- [ ] **Settings → Files & Links**
  - Default location for new notes: `inbox`
  - Use [[Wikilinks]]: ON
  - New link format: Shortest path when possible
  - Detect all file extensions: OFF
- [ ] **Settings → Daily notes** (Core plugin)
  - Date format: `YYYY-MM-DD`
  - Template file location: `templates/daily-note.md`
  - New file location: `notes/journal`
- [ ] **Settings → Templates** (Core plugin)
  - Template folder location: `templates`

> Templater 설정은 다음 단계에서 플러그인 설치 후.

## 8. 커뮤니티 플러그인 설치

- [ ] **Settings → Community plugins → Turn on community plugins**
- [ ] **Browse** 후 다음 검색하여 설치 + 활성화:
  - [ ] **Dataview** (blacksmithgu) — vault를 DB처럼 쿼리
  - [ ] **Templater** (SilentVoid13) — 강력한 템플릿 엔진 (이 키트 템플릿 작동에 필수)
  - [ ] **Periodic Notes** — Daily/Weekly notes 통합
  - [ ] **Tag Wrangler** — 태그 일괄 리네임/머지
  - [ ] **Excalidraw** — 다이어그램/마인드맵
  - [ ] **Style Settings** — 테마 세부 조정
  - [ ] **Obsidian Git** — 자동 백업
  - [ ] **Local REST API** — MCP 연결용 (11번에서 사용)

> 자세한 추천 레포 목록은 `08-curated-repos.md`.

## 8.5. Templater 설정 (★ 이 키트 템플릿 작동 필수)

설치 직후 반드시 설정. 안 하면 `<% tp.date.now(...) %>`가 그대로 글자로 남음.

- [ ] **Settings → Templater**
  - **Template folder location**: `templates`
  - **Trigger Templater on new file creation**: **ON** (★ 필수)
  - **Folder Templates** 매핑 추가 (자동 적용):
    - `notes/journal` → `templates/daily-note.md`
    - `ideas` → `templates/zettel.md`
    - `notes` → `templates/literature.md` (옵션 — Web Clipper는 직접 자기 템플릿 씀)
    - `projects` → `templates/project.md`
- [ ] **단축키 등록** (Settings → Hotkeys):
  - `Templater: Open Insert Template modal` → `Alt+E` (기존 Folder Templates 외에 수동 삽입할 때)
  - `Daily notes: Open today's daily note` → `Ctrl+Shift+D`

### Templater가 트리거되는 3가지 경로
1. **자동** — Folder Templates에 매핑된 폴더에 새 파일 생성 시
2. **수동** — `Alt+E`로 어떤 템플릿이든 삽입
3. **재실행** — `Templater: Replace templates in the active file` 명령으로 기존 파일에 다시 적용

## 9. Obsidian Git 셋업

- [ ] PowerShell에서 vault 루트로:
```powershell
cd "$env:USERPROFILE\Google Drive\Vault\brain"
git init
```
- [ ] **`.gitignore` 작성** — PowerShell의 `echo`는 UTF-16LE를 만들어서 git이 못 읽음. `Set-Content -Encoding utf8` 사용:
```powershell
Set-Content -Encoding utf8 .gitignore @"
# Obsidian local state (per-machine)
.obsidian/workspace
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/cache
.obsidian/graph.json

# Attachments (large binaries)
attachments/

# OS
.DS_Store
Thumbs.db

# Trash
.trash/

# Sensitive (절대 커밋 금지)
.obsidian/plugins/obsidian-local-rest-api/data.json
"@
```
> 처음에는 `.obsidian/` 전체를 무시하다가 안정되면 위처럼 선택적으로 풀어도 됨.

- [ ] 초기 커밋:
```powershell
git add .
git commit -m "initial vault"
```
- [ ] (옵션) GitHub private repo: `git remote add origin ...` → `git push -u origin main`
- [ ] Obsidian Git 플러그인 설정:
  - Vault backup interval: 30 (분마다 자동 커밋)
  - Auto pull interval: 60

## 9.5. ★ Web Clipper 설치 (자동 캡처)

- [ ] Chrome / Firefox / Edge / Safari 스토어에서 **"Obsidian Web Clipper"** 검색 → 설치
- [ ] 확장 아이콘 우클릭 → Options
- [ ] **General**:
  - Vault: `brain`
  - Default folder: `inbox/`
  - Filename: `{{time|date:"YYYY-MM-DD"}}-{{title|safe_name|truncate:60}}`
- [ ] **Templates** → Import 클릭 → 이 키트의 `templates/webclipper-templates/`의 JSON 5개 모두 import:
  - default-article.json
  - twitter-thread.json
  - youtube.json
  - github-readme.json
  - research-paper.json
- [ ] **Smart Rules** (Triggers는 URL prefix — 와일드카드 아님):
  - `https://twitter.com/`, `https://x.com/` → twitter-thread
  - `https://www.youtube.com/watch`, `https://youtu.be/` → youtube
  - `https://github.com/` → github-readme
  - `https://arxiv.org/`, `https://www.nature.com/`, `https://scholar.google.com/` → research-paper
  - (트리거 비어있음) → default-article (fallback)
- [ ] **Interpreter** (옵션, 강력 추천) — `05-web-clipper.md`의 API 키 가이드 따라 셋업
- [ ] **단축키**: 브라우저 확장 설정에서 `Alt+Shift+O` (Windows) 또는 `Cmd+Shift+O` (Mac)로 바인딩
- [ ] 테스트: 아무 글에서 단축키 → vault의 `inbox/`에 파일 생성 확인

## 10. ★ Claude Code 통합 (Cowork 사용자는 건너뛰고 10-Cowork로)

- [ ] https://claude.ai/code 에서 Claude Code 설치
- [ ] 터미널에서 `claude` 실행 → 인증
- [ ] **Plugin marketplace에서 kepano/obsidian-skills 추가 + 설치** (두 명령 모두 필요):
```
/plugin marketplace add kepano/obsidian-skills
/plugin install obsidian@obsidian-skills
```
> ⚠️ `marketplace add`만 하면 카탈로그 등록만 되고 스킬이 활성화 안 됨. **반드시 두 번째 명령까지** 실행.
- [ ] 설치 후 `/plugin list`로 확인 — 5개 스킬(`obsidian-markdown`, `obsidian-bases`, `json-canvas`, `obsidian-cli`, `defuddle`) 표시

### ★ CLAUDE.md 두 파일의 역할 (헷갈리는 부분)

| 위치 | 역할 | 내용 |
|---|---|---|
| `<vault>/CLAUDE.md` | **본인 데이터** — 누구이고 뭘 하는지 | 6번에서 채운 그 파일 |
| `~/.claude/CLAUDE.md` (Windows: `%USERPROFILE%\.claude\CLAUDE.md`) | **Claude에게 주는 지시문** — vault를 어떻게 다뤄라 | 아래 블록 |

두 파일은 **서로 덮어쓰지 말 것**. 다른 목적.

- [ ] `%USERPROFILE%\.claude\CLAUDE.md` 파일 생성(없으면) 후 다음 내용 추가:

```markdown
# Vault Integration Instructions

내 Obsidian vault는 다음 경로에 있다:
`C:\Users\<USERNAME>\Google Drive\Vault\brain`

답변 규칙:
- 매 답변 전 vault의 CLAUDE.md를 읽어 본인 컨텍스트를 갱신할 것
- 질문과 관련된 노트를 vault에서 먼저 검색
- 답변에 vault 노트를 [[wikilink]]로 인용
- 새 결정 → inbox/decisions.md에 append (YYYY-MM-DD 헤딩, 컨텍스트/결정/이유)
- 새 액션 → inbox/action-tracker.md에 append (- [ ] [날짜] 형식)
- 외부 자료 정리 → notes/{date}-{slug}.md (#literature)
- 본인 사고 재구성 → ideas/{slug}.md (#permanent)
- 동기부여성 답변 금지. 일반론 금지. vault 컨텍스트 그라운딩 필수
- 내가 믿는 것과 모순되는 과거 노트 발견 시 즉시 플래그
```

> Claude Code는 실행 시 두 파일을 모두 읽는다:
> 1. `~/.claude/CLAUDE.md` — 글로벌 지시문 (위 블록)
> 2. `<cwd>/CLAUDE.md` — 현재 디렉토리의 프로젝트 CLAUDE.md
>
> Claude Code를 항상 vault 안에서 실행하면 vault의 CLAUDE.md가 프로젝트 CLAUDE.md로 자동 로드된다:
> ```powershell
> cd "$env:USERPROFILE\Google Drive\Vault\brain"
> claude
> ```

## 10-Cowork. Claude Cowork / Desktop 통합 (Cowork 사용자용)

> Claude Code 대신 Cowork(또는 Claude Desktop)을 쓰면 10번 대신 이 단계로.

- [ ] Claude Cowork 또는 Claude Desktop 앱 설치 후 로그인
- [ ] **앱 Settings → User Preferences (또는 Custom Instructions) 필드**에 다음 붙여넣기:

```markdown
내 Obsidian vault는 다음 경로에 있다:
`C:\Users\<USERNAME>\Google Drive\Vault\brain`

답변 규칙:
- 매 답변 전 vault의 CLAUDE.md를 읽어 본인 컨텍스트를 갱신할 것
- 질문과 관련된 노트를 vault에서 먼저 검색 (Obsidian MCP 경유)
- 답변에 vault 노트를 [[wikilink]]로 인용
- 새 결정 → inbox/decisions.md에 append (YYYY-MM-DD 헤딩, 컨텍스트/결정/이유)
- 새 액션 → inbox/action-tracker.md에 append (- [ ] [날짜] 형식)
- 외부 자료 정리 → notes/{date}-{slug}.md (#literature)
- 본인 사고 재구성 → ideas/{slug}.md (#permanent)
- 동기부여성 답변 금지. 일반론 금지. vault 컨텍스트 그라운딩 필수
- 내가 믿는 것과 모순되는 과거 노트 발견 시 즉시 플래그
```

- [ ] **kepano/obsidian-skills는 사용 안 함** — Cowork에 plugin marketplace 없음. 대신 다음 단계의 MCP가 동일한 read/write 기능을 모두 제공.

> Cowork에서 vault에 접근하는 유일한 경로는 **MCP 서버(11번)**. 11번 셋업이 더 중요해짐.

> **Claude Code와 동시 사용**: 같은 vault에 둘 다 연결 가능. MCP config만 각각 등록하면 됨. 양쪽이 vault에 동시에 쓰는 경우 Obsidian Git이 자동 커밋으로 충돌 방지.

## 11. (권장) Obsidian MCP 연결

> ⚠️ MCP 서버 `mcp-obsidian`은 **Python (uvx)** 패키지입니다. npm 아님.

- [ ] **`uv` 설치** (한 번만):
```powershell
winget install astral-sh.uv
```
설치 확인: `uvx --version`

- [ ] Obsidian에서 **Local REST API** 플러그인 활성화 (8번에서 설치함)
- [ ] **Settings → Local REST API**
  - Enable HTTPS: ON
  - Copy API Key (긴 문자열)
- [ ] **MCP 설정 파일** — 사용 중인 클라이언트에 따라 다른 경로:

  **Claude Code 사용 시**: `%USERPROFILE%\.claude\mcp.json` (없으면 생성)

  **Claude Cowork / Desktop 사용 시**: `%APPDATA%\Claude\claude_desktop_config.json`
  - 파일이 이미 있으면 `mcpServers` 객체에 추가만. 다른 MCP 서버와 공존 가능
  - PowerShell로 경로 확인: `echo $env:APPDATA\Claude\`

  **양쪽 다 쓴다면**: 두 파일에 같은 내용 등록

  내용 (양쪽 공통):
```json
{
  "mcpServers": {
    "obsidian-vault": {
      "command": "uvx",
      "args": ["mcp-obsidian"],
      "env": {
        "OBSIDIAN_API_KEY": "<여기에 복사한 키>",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27124"
      }
    }
  }
}
```

- [ ] **재시작 후 연결 확인**:
  - Claude Code: `/mcp` 명령 → `obsidian-vault: connected` 표시
  - Cowork / Desktop: 앱 재시작 → 설정의 **MCP** 또는 **Connections** 섹션에 `obsidian-vault` 활성 표시
- [ ] 테스트: "내 vault의 CLAUDE.md를 읽어줘" → 파일 내용 출력되면 성공

> Self-signed 인증서 오류가 나면: `OBSIDIAN_PORT`를 `27123`(HTTP)으로 변경. 로컬 통신이므로 보안상 OK.

> 대안 MCP 서버: `iansinnott/obsidian-claude-code-mcp` (WebSocket), `jacksteamdev/obsidian-mcp-tools` (시맨틱 검색). 자세한 비교는 `04-claude-integration.md`.

## 12. Graph View 확인

- [ ] Obsidian에서 `Ctrl+G` (Graph View)
- [ ] 5개 시드 노트가 노드로 보임
- [ ] 일부 노드끼리 `[[ ]]` 링크로 연결되어 있음 → 살아있는 vault의 시작

## 13. 첫 테스트 (Pattern Finder)

- [ ] Claude Code 또는 Claude.ai에서 이 키트의 `prompts/pattern-finder.md` 내용 붙여넣기
- [ ] Claude가 CLAUDE.md + 4개 시드 노트 기반으로 패턴 답변
- [ ] 답변이 일반론적이면 CLAUDE.md를 더 채워야 함 (6번 복귀)
- [ ] 답변이 구체적이고 [[wikilink]] 인용 포함되면 시스템 작동

## 13.5. 셋업 검증 (각 항목 직접 확인)

- [ ] **Templater 작동**: `Ctrl+Shift+N` 후 `notes/journal/test.md` 이름으로 생성 → 자동으로 daily-note 템플릿 적용, `<% tp.date.now(...) %>` 자리에 오늘 날짜가 들어가야 함. 안 되면 8.5번 설정 확인.
- [ ] **Daily-note 조건부 embed**: 오늘 daily note 생성 시 brief가 없으면 "아직 없음" 메시지, 있으면 transclude. 둘 다 정상 표시.
- [ ] **Dataview 작동**: `home.md`의 통계/최근 쿼리가 숫자/목록 표시. "Dataview block error" 보이면 플러그인 활성화 확인.
- [ ] **Web Clipper 클립**: 아무 글에서 `Alt+Shift+O` → vault의 `inbox/2026-MM-DD-{slug}.md`에 파일 생성. 한글 깨짐 없음.
- [ ] **Web Clipper AI Interpreter**: 클립된 파일의 `## AI Summary` 섹션이 한국어 불릿으로 채워져 있음. 빈 채로 남으면 Interpreter 비활성/API 키 확인.
- [ ] **kepano/obsidian-skills**: Claude Code에서 `/plugin list` → `obsidian-skills` 5개 표시.
- [ ] **MCP 연결**: Claude Code에서 `/mcp` → `obsidian-vault: connected`. "내 vault의 home.md를 읽어줘" → 내용 출력.
- [ ] **Custom Instructions 작동**: Claude Code에 일반 질문("이번 주 뭐 할까?") → 답변에 vault 노트가 `[[wikilink]]`로 인용됨. 안 되면 `~/.claude/CLAUDE.md` 확인.
- [ ] **Git 백업**: vault 루트에서 `git log` → 최소 1개 커밋 존재. Obsidian Git 플러그인 정상 동작 시 30분 후 자동 커밋 추가됨.

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
