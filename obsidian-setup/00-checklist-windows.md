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

| | **Claude Code** (터미널/CLI) | **Claude Desktop + Cowork** (데스크탑 앱) |
|---|---|---|
| 요구 사항 | 무료 가능 | **Pro/Max/Team/Enterprise 유료 플랜 필수** (Cowork) |
| `kepano/obsidian-skills` (10번) | ✅ 사용 | ❌ 건너뛰기 (Cowork 미지원) |
| MCP 서버 (11번) | ✅ `%USERPROFILE%\.claude\mcp.json` | ✅ `%APPDATA%\Claude\claude_desktop_config.json` (또는 앱의 Settings → Developers → Edit Config) |
| Custom Instructions 위치 | `~/.claude/CLAUDE.md` | 앱 **Settings → Cowork → Global Instructions** |
| MCP 연결 검증 | `/mcp` 명령 | 새 채팅 하단 **🔨 hammer 아이콘**에 도구 개수 |
| vault CLAUDE.md (6번) | 양쪽 모두 동일 | 양쪽 모두 동일 |
| Web Clipper (9.5번) | 양쪽 모두 동일 | 양쪽 모두 동일 |
| 프롬프트 사용 | 양쪽 모두 동일 (복사 붙여넣기) | 양쪽 모두 동일 |

> **Cowork 사용자**는 10번을 통째로 건너뛰고 10-Cowork로 → 11번에서 config 경로만 다르게. 실용 차이는 거의 없음 — Cowork는 MCP가 obsidian-skills 기능을 대부분 커버.

> **둘 다 쓰는 경우**: 같은 vault에 양쪽 연결 가능. MCP config만 각각 등록. 두 클라이언트 사이 충돌 없음 (Obsidian Git이 자동 커밋으로 보호).

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

# inbox 누적 파일 — 두 가지 옵션 중 선택:

# 옵션 A: 빈 템플릿 (깨끗한 시작)
robocopy "$KIT\inbox-init" "$VAULT\inbox"

# 옵션 B (★ 권장): 오늘 셋업 세션의 영구 기억 포함
# decisions 15개 + actions 12개 + ideas 7개. 첫날부터 풍부한 컨텍스트.
robocopy "$KIT\vault-seed\inbox" "$VAULT\inbox"
robocopy "$KIT\vault-seed\ideas" "$VAULT\ideas"

# Vault 루트 파일
Copy-Item "$KIT\templates\CLAUDE.md" "$VAULT\CLAUDE.md"
Copy-Item "$KIT\templates\home.md"  "$VAULT\home.md"
```

> **옵션 B 권장 이유**: 오늘 세션에서 결정한 15개 결정과 7개 영구 사고 노트가 vault에 이미 들어가 있어, 첫 Claude 세션이 즉시 "어제 시스템을 셋업했고 X/Y/Z를 결정했다"는 컨텍스트로 시작. Graph View도 첫날부터 살아있음. [[session-bridge-mechanism]]이 즉시 작동.

체크:
- [ ] `vault/templates/` 안에 daily-note.md, zettel.md, literature.md, moc.md, project.md, home.md 6개
- [ ] `vault/inbox/`에 시드 4개(001~004) + `decisions.md` + `action-tracker.md` + **`session-bridge.md`**
- [ ] `vault/CLAUDE.md`와 `vault/home.md`가 루트에 있음
- [ ] `vault/CLAUDE.md` 최상단에 **SESSION PROTOCOL 섹션이 있음** (이게 시스템 자가 강제의 핵심)

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

- [ ] **Settings → Files & Links** (★ linkrot 방지 핵심 — [[linkrot-prevention]] 참조)
  - **Automatically update internal links**: **ON** (★ 가장 중요. 파일 이름/위치 변경 시 모든 인용처 자동 갱신)
  - Default location for new notes: `inbox`
  - Use [[Wikilinks]]: ON
  - New link format: Shortest path when possible
  - Detect all file extensions: OFF

> ⚠️ **위 첫 번째 옵션을 켜지 않으면 vault가 어느 날 갑자기 연결점이 풀어질 수 있음.** OS 파일 탐색기로 파일 이름 바꾸지 말고 항상 Obsidian 안에서 rename.
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
# Vault Bootstrap (모든 세션에 자동 적용)

내 Obsidian vault: `C:\Users\<USERNAME>\Google Drive\Vault\brain`

## 매 세션 시작 시 (사용자 첫 메시지 답변 전 반드시):

1. MCP로 `<vault>/CLAUDE.md`를 읽고 그 안의 SESSION PROTOCOL 섹션을 적용
2. `<vault>/inbox/session-bridge.md`를 읽고 직전 세션 컨텍스트 로드
3. `<vault>/inbox/action-tracker.md`의 Open Actions 인지

위 3개를 못 읽으면 즉시 사용자에게 알림: "vault MCP 연결 실패 — 답변이 일반론 수준일 수 있음"

## 매 답변마다:

- 답변에 vault 노트를 `[[wikilink]]`로 인용 (인용 없으면 컨텍스트 미사용 신호)
- 새 결정/액션/요약은 즉시 vault에 저장 (vault CLAUDE.md의 Routing Rules 따름)
- 일반론 답변 금지, 동기부여 멘트 금지

## 매 세션 종료 시:

- 사용자가 "마무리", "끝", 종료 의도 표현하면 → `prompts/session-end.md` 절차 자동 실행
- `inbox/session-bridge.md`를 이번 세션 요약으로 덮어쓰기
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

## 10-Cowork. Claude Cowork 통합 (Cowork 사용자용)

> ⚠️ **중요**: Claude Cowork는 **Claude Desktop 앱 안의 기능**입니다 (별도 앱 아님).
> 2026년 1월 research preview 출시, 2월에 Windows 지원. **Pro/Max/Team/Enterprise 유료 플랜 필요**.

- [ ] Claude Desktop 앱 설치 후 로그인 (https://claude.ai/download)
- [ ] **Settings → Cowork → Global Instructions → Edit** 클릭 후 다음 붙여넣기 (Claude Code용과 동일):

```markdown
# Vault Bootstrap (모든 대화에 자동 적용)

내 Obsidian vault: `C:\Users\<USERNAME>\Google Drive\Vault\brain`

## 매 대화 시작 시 (사용자 첫 메시지 답변 전 반드시):

1. MCP로 `<vault>/CLAUDE.md`를 읽고 그 안의 SESSION PROTOCOL 섹션을 적용
2. `<vault>/inbox/session-bridge.md`를 읽고 직전 세션 컨텍스트 로드
3. `<vault>/inbox/action-tracker.md`의 Open Actions 인지

위 3개를 못 읽으면 즉시 사용자에게 알림: "vault MCP 연결 실패 — 답변이 일반론 수준일 수 있음"

## 매 답변마다:

- 답변에 vault 노트를 [[wikilink]]로 인용
- 새 결정/액션/요약은 즉시 vault에 저장
- 일반론 답변 금지, 동기부여 멘트 금지

## 매 세션 종료 시:

- 사용자가 "마무리", "끝", 종료 의도 표현하면
  → `inbox/session-bridge.md`를 이번 세션 요약으로 덮어쓰기
```

- [ ] Save → 새 대화부터 자동 적용
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

  **Claude Desktop / Cowork 사용 시**: `%APPDATA%\Claude\claude_desktop_config.json`
  - 가장 쉬운 길: 앱에서 **Settings → Developers → Edit Config** 클릭 → 메모장/IDE로 자동 열림
  - 파일이 이미 있으면 `mcpServers` 객체에 추가만. 다른 MCP 서버와 공존 가능
  - PowerShell로 직접 확인: `echo $env:APPDATA\Claude\`

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

- [ ] **앱 완전 종료 후 재시작** (이게 가장 자주 빠뜨리는 단계):
  - Claude Code: 터미널 세션 종료 → 새 터미널 열고 `claude`
  - **Claude Desktop / Cowork**: 창 닫기로는 부족. **트레이 아이콘 우클릭 → Quit**. 그래야 새 config 로드.
- [ ] **연결 확인**:
  - Claude Code: `/mcp` → `obsidian-vault: connected` 표시
  - **Claude Desktop / Cowork**: 새 대화창 하단의 **🔨 hammer 아이콘**에 도구 개수 (보통 5+) 표시. 클릭하면 `obsidian-vault`의 tool 목록. 아이콘 안 보이면 MCP 실패.
- [ ] 테스트: "내 vault의 CLAUDE.md를 읽어줘" → 파일 내용 출력되면 성공

> Self-signed 인증서 오류가 나면: `OBSIDIAN_PORT`를 `27123`(HTTP)으로 변경. 로컬 통신이므로 보안상 OK.

> 대안 MCP 서버: `iansinnott/obsidian-claude-code-mcp` (WebSocket), `jacksteamdev/obsidian-mcp-tools` (시맨틱 검색). 자세한 비교는 `04-claude-integration.md`.

## 11.4. ★ Linkrot 방지 (연결점 보존 — 어제 풀어진 사건 회피)

> 6중 방어선. 자세한 원리는 vault-seed/ideas/linkrot-prevention.md (vault에 복사 후 [[linkrot-prevention]]).

- [ ] **방어선 1**: Settings → Files & Links → **Automatically update internal links** ON (7번에서 이미 했어야 함 — 재확인)
- [ ] **방어선 2**: 모든 핵심 노트 frontmatter에 **`aliases`** 추가. 이 키트의 시드 노트들은 이미 보유. 직접 만든 노트도 같은 패턴 따라가기
- [ ] **방어선 3 (규칙)**: vault 안의 파일을 **OS 파일 탐색기로 rename/move 금지**. 항상 Obsidian 안에서.
- [ ] **방어선 4 (동기화 충돌 검사)**: 매주 vault 루트에서 `conflict copy`, `(1)`, `(2)` 파일명 검색. PowerShell:
  ```powershell
  cd "$env:USERPROFILE\Google Drive\Vault\brain"
  Get-ChildItem -Recurse -Filter "*conflict*"
  Get-ChildItem -Recurse | Where-Object { $_.Name -match "\(\d+\)" }
  ```
- [ ] **방어선 5 (Dataview orphan 추적)**: home.md에 이미 추가된 orphan 쿼리 매주 확인
- [ ] **방어선 6 (주간 의식)**: 매주 월요일 CLAUDE.md 갱신과 함께 home.md의 orphan/broken-link 5분 점검

> 어제 발생한 "연결점 풀어진 사건"의 가장 흔한 원인은 1번(Update links OFF) 또는 4번(Drive 충돌). 1번을 ON으로 확인하는 게 가장 중요.

## 11.5. ★ Seamless 보장 (자동 실행 + 주간 알림)

> 이 단계는 **"매번 수동으로 챙기는 시스템"을 "자동으로 굴러가는 시스템"으로** 바꾼다. 빼먹으면 며칠 안에 vault가 stale해진다.

### A. Obsidian Windows 시작 시 자동 실행 (필수)

MCP가 작동하려면 Obsidian이 항상 켜져 있어야 함. 부팅 시 자동 실행:

- [ ] `Win+R` → `shell:startup` 입력 → 시작 프로그램 폴더 열림
- [ ] Obsidian 바탕화면 바로가기를 이 폴더로 **드래그(복사)**
- [ ] (옵션) Obsidian Settings → About → "Launch on system startup": ON
- [ ] (옵션) Settings → About → "Hide tray icon": OFF (트레이로 백그라운드 실행)
- [ ] 재부팅 후 확인: Obsidian이 자동으로 켜져 있어야 함

### B. CLAUDE.md 주간 업데이트 알림 (Windows Task Scheduler)

매주 월요일 9am에 알림 자동 — `CLAUDE.md`를 5분 업데이트하지 않으면 답변 품질이 떨어짐:

- [ ] PowerShell 관리자 권한 실행 → 다음 명령:

```powershell
$action = New-ScheduledTaskAction `
  -Execute "powershell.exe" `
  -Argument "-WindowStyle Hidden -Command `"[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; [System.Windows.Forms.MessageBox]::Show('CLAUDE.md 업데이트 시간 (5분)`n- Current Projects 갱신`n- What I Am Reading 갱신', 'Vault Weekly Refresh', 'OK', 'Information')`""

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9am

Register-ScheduledTask `
  -TaskName "Vault Weekly CLAUDE.md Refresh" `
  -Action $action `
  -Trigger $trigger `
  -Description "매주 월요일 9am: vault CLAUDE.md 업데이트 알림"
```

### C. Daily Brief 자동 생성 (옵션, 강력 추천)

매일 아침 6am에 Claude API가 자동으로 brief를 vault에 생성하면 진짜 "talk back vault"가 됨.

- [ ] `07-automation-future.md`의 "Daily Brief 6am 자동화" 섹션 참고
- [ ] 우선은 수동으로 `prompts/daily-brief.md` 사용해도 OK. 자동화는 익숙해진 후

### D. Google Drive vs Obsidian Sync 결정

매일 여러 기기에서 작업한다면 무료 Google Drive 한계 명확:
- 동기화 지연 (Wi-Fi+충전 시에만 안정)
- 동시 편집 충돌 시 `.conflict` 파일 생성
- `.obsidian/workspace*`이 자주 충돌 → .gitignore + Drive 제외 둘 다 필요

→ **다중 기기 + 즉시 동기화가 중요하면 Obsidian Sync($5/월)** 가 가장 확실.
→ 단일 PC면 Google Drive로 충분.

- [ ] 본인 시나리오 선택 후 그에 맞게 설정

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

### ★ Seamless 검증 (가장 중요한 테스트)

이게 작동하면 키트가 완성된 것. 안 되면 SESSION PROTOCOL 미적용.

**Cowork 사용 시 사전 확인**:
- [ ] 새 채팅창 하단 **🔨 hammer 아이콘**에 도구 개수 표시 (5+ 권장). 안 보이면 MCP 미연결 → 11번 트러블슈팅
- [ ] 아이콘 클릭 → `obsidian-vault`의 list/get/search/append 등 tool 보임

**Claude Code 사용 시 사전 확인**:
- [ ] `/mcp` → `obsidian-vault: connected`

**5단계 Seamless 테스트** (Cowork든 Code든 동일):

- [ ] **세션 1**: 새 대화/세션 열고 `prompts/session-start.md` 붙여넣기 → CLAUDE.md 요약 + Open Actions + 최신 결정이 정확히 출력됨
- [ ] **세션 1 (계속)**: "OAuth를 JWT로 바꾸기로 결정했어"라고 말함 → Claude가 자동으로 `📝 saved → [[decisions#...]]` 응답. vault 파일 시스템에서 `inbox/decisions.md` 열어 실제로 추가됐는지 확인.
- [ ] **세션 1 종료**: "오늘 마무리하자"라고 말함 → Claude가 `inbox/session-bridge.md`를 덮어쓰고 `🌙 session bridged` 보고. vault의 session-bridge.md를 열어 "Last Session Summary"에 OAuth→JWT 내용 있는지 확인.
- [ ] **세션 2 (새 세션)**: 앱 완전 종료(트레이 Quit) → 다시 열기 → 새 대화 시작. 첫 메시지 없이 "지금 뭐 하고 있었지?" 질문 → Claude가 session-bridge.md를 읽고 OAuth→JWT 결정과 미완 thread를 정확히 복원
- [ ] **세션 2 (검증)**: "오늘 결정한 거 있어?" → "오늘은 아직 결정 없음. 어제 [[decisions#...OAuth-JWT]]를 결정했음" 식으로 와야 함

5개 다 통과하면 진짜 seamless. 하나라도 실패 시 어디서 깨졌는지 추적:

| 실패 지점 | 원인 | 해결 |
|---|---|---|
| 세션 1 첫 단계 (요약 출력) 실패 | MCP 미연결 또는 vault CLAUDE.md 미존재 | 🔨 아이콘 / `/mcp` 확인. CLAUDE.md 경로 확인 |
| 자동 save 실패 (📝 안 뜸) | Global Instructions / `~/.claude/CLAUDE.md`에 SESSION PROTOCOL B 누락 | 10번 또는 10-Cowork 다시 |
| 📝는 뜨는데 vault 파일에 실제로 안 들어감 | MCP write 권한 또는 Obsidian Local REST API 비활성 | 11번 재확인 |
| session-bridge 덮어쓰기 실패 | SESSION PROTOCOL C 미적용. 또는 Claude가 "마무리" 신호 인식 못 함 | `prompts/session-end.md` 수동으로 던져보기 |
| 세션 2에서 복원 실패 | Claude가 session-bridge.md를 첫 read에 안 함 | Custom Instructions A1~A3 확인. 또는 `prompts/session-start.md` 수동 |

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
