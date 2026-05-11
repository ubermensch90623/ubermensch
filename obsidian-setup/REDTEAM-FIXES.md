# 레드팀 검증 결과 및 수정 사항

> 첫 셋업 키트(commit `826ba9b`)에서 발견된 11개 이슈를 외부 도구의 실제 동작과 대조하여 수정한 기록.

## 🔴 CRITICAL (셋업 실패 방지)

### C1. Web Clipper JSON 스키마 불일치 → 수정 완료
**문제**: import해도 작동 안 함
- `schemaVersion` 필드 누락
- `context` 필드 누락
- Schema.org 변수에 `@` 누락 (`schema:VideoObject:author` → `schema:@VideoObject:author`)
- 파일명 필터 `slugify` 사용 (실제는 `safe_name`)
- Triggers를 글로브 패턴(`*.youtube.com/watch*`)으로 작성 (실제는 URL prefix)
- 날짜 properties `"type": "date"` (실제는 `"datetime"`)
- 현재 시각 `{{date}}` (실제는 `{{time}}`)

**수정**: 5개 JSON 파일 전부 재작성 (`templates/webclipper-templates/*.json`). community 템플릿의 실제 형식과 일치.

**참고**: [obsidian-community/web-clipper-templates](https://github.com/obsidian-community/web-clipper-templates)의 youtube-clipper.json raw 검증

### C2. MCP 서버 명령어 잘못됨 → 수정 완료
**문제**: `mcp-obsidian`은 Python(uvx) 패키지인데 `npx -y mcp-obsidian`/`npx -y obsidian-mcp-server`로 안내함

**수정**:
- `00-checklist-windows.md` 11번 단계: uvx 명령으로 변경, 사전에 `winget install astral-sh.uv` 추가
- `04-claude-integration.md`: 동일하게 수정 + Claude Desktop config 경로 명시

```diff
- "command": "npx",
- "args": ["-y", "obsidian-mcp-server"],
+ "command": "uvx",
+ "args": ["mcp-obsidian"],
```

### C3. kepano/obsidian-skills 설치 명령 누락 → 수정 완료
**문제**: `/plugin marketplace add kepano/obsidian-skills`만 안내 → 카탈로그 등록만 되고 스킬 비활성

**수정**: 두 번째 명령 추가
```
/plugin marketplace add kepano/obsidian-skills
/plugin install obsidian@obsidian-skills
```

## 🟠 HIGH (혼란/오작동 방지)

### H1. 템플릿 문법 혼용 (Core Templates vs Templater) → 수정 완료
**문제**: `{{date:YYYY-MM-DD}}`(core)와 `<% tp.file.title %>`(Templater)가 같은 파일에 섞임

**수정**: 5개 템플릿 모두 **Templater 문법으로 통일**:
- `daily-note.md`: `<% tp.date.now("YYYY-MM-DD") %>` 사용
- `zettel.md`, `literature.md`, `moc.md`, `project.md`: 모두 Templater
- `00-checklist`의 Templater 폴더 설정 단계 추가

### H2. daily-note.md의 깨진 embed → 수정 완료
**문제**: `![[inbox/brief-{{date:YYYY-MM-DD}}#CONNECTIONS]]` — brief가 없으면 빨간 글씨

**수정**: Templater의 `tp.file.find_tfile()`로 존재 여부 체크 후 conditional 렌더링:
```
<%* if (briefExists) { %>
![[inbox/brief-...]]
<%* } else { %>
> 오늘 Daily Brief 아직 없음. ...
<%* } %>
```

### H3. inbox/decisions.md, action-tracker.md 초기 파일 부재 → 수정 완료
**문제**: CLAUDE.md 라우팅 규칙은 이 파일들에 append하라고 함. 하지만 파일이 없어서 첫 append 시 실패 가능

**수정**: `inbox-init/` 폴더 신설, 두 파일 초기 헤더 포함하여 생성. 체크리스트 5번에서 vault로 복사하도록 추가.

### H4. home.md 중복 → 수정 완료
**문제**: `templates/home.md`와 `starter-notes/000-home.md` 둘 다 존재 → 어디 두는지 헷갈림

**수정**:
- `starter-notes/000-home.md` 삭제
- `templates/home.md`에 "📌 Start Here (시드 노트)" 섹션 추가하여 4개 시드 노트로 링크
- 체크리스트 5번에서 home.md는 vault 루트로, 시드는 inbox/로 명확히 분리

### H5. CLAUDE.md 3곳의 관계 불명확 → 수정 완료
**문제**: 키트의 templates/CLAUDE.md, vault 루트 CLAUDE.md, `~/.claude/CLAUDE.md` 3개의 역할 불명확

**수정**: `04-claude-integration.md`에 "CLAUDE.md 위치 — 헷갈리는 3개 정리" 섹션 신설. 표로 누가 읽고 언제 자동 로드되는지 명시. Claude Code는 `cd <vault>` 후 실행해야 vault CLAUDE.md가 프로젝트 컨텍스트로 로드됨을 강조.

### H6. Templater 폴더 설정 누락 → 수정 완료
**문제**: Settings → Templates만 안내, Settings → Templater 별도 설정 없음 → Templater 문법 작동 안 함

**수정**: `00-checklist-windows.md` 7번 단계에 Templater 설정 추가:
- Template folder location: `templates`
- Trigger Templater on new file creation: ON
- Folder Templates 매핑

### H7. Web Clipper AI Interpreter 모델 ID 미검증 → 수정 완료
**문제**: `claude-haiku-4-5`, `claude-sonnet-4-6` 정확한 ID가 드롭다운에 있는지 확인 안 됨

**수정**: 모델 선택을 "드롭다운에서 사용 가능한 최신 Haiku/Sonnet" 식으로 변경. Anthropic models 페이지 링크 추가.

### H8. .gitignore 부족 + PowerShell 인코딩 문제 → 수정 완료
**문제**:
- `.obsidian/workspace*` 하나만 → workspace.json, cache, graph.json 등 누락
- PowerShell `echo > file`은 UTF-16LE BOM 생성 → git 못 읽음
- API key가 들어있는 plugin data 파일 무방비

**수정**: `00-checklist-windows.md` 9번 단계 전면 재작성:
- `Set-Content -Encoding utf8` 사용
- 무시 패턴 확장: workspace, workspace.json, workspace-mobile.json, cache, graph.json, .DS_Store, Thumbs.db, .trash/
- **API key 파일 명시적 제외**: `.obsidian/plugins/obsidian-local-rest-api/data.json`

## 🟡 MEDIUM / 🟢 LOW (이번에 일부 반영)

| 이슈 | 처리 |
|---|---|
| M1. Google Drive 공백 경로 | 체크리스트에서 `"..."` quote 사용 강조 |
| M2. Self-signed cert | `04-claude-integration.md`에서 HTTP 27123 폴백 안내 |
| M3. PowerShell UTF-16LE | H8에서 해결 |
| M4. winget 가용성 | 수동 다운로드 폴백 안내 유지 |
| M5. bash 스크립트 (AgriciDaniel) | Git Bash/WSL 안내 유지 |
| M6. Schema.org 미보장 | Twitter 템플릿에서 selectorHtml 사용 |
| M7. Dataview 쿼리 미검증 | 그대로 — 실제 실행에서 검증 필요 |
| M8. Nested 태그 검색법 | 다음 업데이트 |
| M9. Interpreter 작동 확인 | "Test connection" 단계 추가 |
| L1-L10 | 다음 업데이트 (낮은 우선순위) |

## 확인 방법

수정이 실제로 작동하는지는 로컬 PC에서 다음으로 검증:

1. **Web Clipper 템플릿 import**: Options → Templates → Import → 5개 JSON → 에러 없이 로드되면 OK
2. **AI Interpreter 동작**: 아무 글에서 클립 → vault에 "AI Summary" 섹션이 한국어 불릿으로 채워지면 OK
3. **MCP 연결**: Claude Code에서 `/mcp` → `obsidian-vault: connected` → "내 vault의 home.md를 읽어줘" → 내용 출력되면 OK
4. **kepano/obsidian-skills**: Claude Code에서 `/plugin list` → 5개 스킬 표시되면 OK
5. **Templater**: vault에서 `Ctrl+N` 후 templates/zettel.md를 Templater로 삽입 → `<% tp.file.title %>` 자리에 실제 파일명 들어가면 OK
6. **Daily note conditional embed**: 오늘 daily note 생성 → brief가 없으면 "아직 없음" 메시지, 있으면 transclude

## 2차 라운드 — HIGH 영역 후속 정리 (commit 이후)

1차 수정 후 추가로 발견된 미세 이슈 6건:

### R1. daily-note.md Templater API 오용
**문제**: `tp.file.find_tfile("inbox/brief-2026-05-10.md")` — Templater의 `find_tfile`은 **파일명만** 받음 (경로 X). 슬래시 들어간 경로를 넘기면 null만 리턴.

**수정**: `tp.app.vault.getAbstractFileByPath()` 사용 (Obsidian API 직접 호출, 경로 OK). `await`도 불필요(동기).

### R2. action-tracker.md 하드코딩된 날짜
**문제**: `[2026-05-10]`이 초기 작업 3개에 박혀있어 나중에 셋업하는 사용자에게 의미 불명

**수정**: ``[`첫 셋업일`]``로 placeholder 처리 + Templater 안내 추가

### R3. 체크리스트 7-8단계 역순
**문제**: 7단계에서 "Templater 설정 (8번에서 설치 후)"라고 안내 — 설치 전에 설정 단계가 와있어 혼란

**수정**: 7단계는 Core 설정만, 8단계 플러그인 설치, **8.5 신설** — Templater 설정 + Folder Templates 매핑 + 트리거 방식 3가지 명시

### R4. project.md의 깨진 Dataview
**문제**: `FROM "inbox/decisions"` — `inbox/decisions.md` 단일 파일을 가리키므로 `WHERE contains(file.tags, ...)`로는 항상 빈 결과

**수정**: 백링크 기반 설계로 변경. Claude가 결정 작성 시 `[[<프로젝트>]]` 백링크를 박으면 자동 추적. 액션 트래커도 동일 원리.

### R5. home.md Dataview 인덱싱
**문제**: `GROUP BY split(file.folder, "/")[0]` — Dataview에서 배열 인덱싱 `[0]` 미보장 (버전에 따라)

**수정**: `GROUP BY file.folder`로 단순화 (하위 폴더가 별도로 카운트되지만 안전). top-level 묶기 원하면 `regexreplace(file.folder, "/.*$", "")` 사용 가능 — 주석으로 안내.

### R6. 체크리스트 10단계 CLAUDE.md 2개 파일 혼동
**문제**: `~/.claude/CLAUDE.md`와 vault `CLAUDE.md`를 같은 것처럼 안내해 사용자가 덮어쓸 위험

**수정**: 표로 역할 분리 + 각 파일의 구체 내용 별도 명시 + `cd <vault> && claude` 실행 패턴 강조

## 추가 개선

- **TL;DR — 30분 미니멀 셋업**: 체크리스트 최상단에 추가. 시간 없을 때 6단계만 따라가도 vault가 살아나도록.
- **13.5 셋업 검증**: 각 컴포넌트 작동을 사용자가 직접 체크할 수 있는 9개 검증 항목 추가.

## 3차 라운드 — Cowork 실측 검증 (Claude 공식 지원 문서 대조)

Cowork 전용 트랙을 만들었지만 외부 도구 명칭/UI 경로가 추정에 가까웠음. Anthropic 공식 지원 문서로 재검증:

### F1. "Cowork"이 별도 앱이라는 오해
**문제**: 이전 문서는 "Claude Cowork / Desktop"로 묶었지만 사용자가 "둘 다 설치해야 하나?" 헷갈림

**확인**: Cowork는 **Claude Desktop 안의 기능**. 2026년 1월 research preview, 2월 Windows. **Pro/Max/Team/Enterprise 플랜 필수**.

**수정**: 매트릭스/체크리스트/통합 가이드 전반에서 "Claude Desktop + Cowork"로 통일. 플랜 요구사항 명시.

### F2. Custom Instructions 필드명 오류
**문제**: "User Preferences" 또는 "Custom Instructions" 필드라고 안내 — Cowork 실제 UI에 없음

**확인**: Cowork는 **`Settings → Cowork → Global Instructions → Edit`**. "Global Instructions"가 정확한 명칭.

**수정**: 체크리스트 10-Cowork, 매트릭스, 04-claude-integration.md 모두 수정.

### F3. MCP config UI 경로 미안내
**문제**: `%APPDATA%\Claude\claude_desktop_config.json`만 안내 — 비개발자는 경로 입력 부담

**확인**: 앱 UI에서 **`Settings → Developers → Edit Config`** 클릭하면 메모장/IDE로 자동 오픈.

**수정**: 두 경로 모두 제공.

### F4. 재시작 의미 모호
**문제**: "재시작" 안내 — 사용자가 창만 닫고 다시 열면 새 config 안 읽힘

**확인**: Claude Desktop은 트레이 백그라운드. 창 닫기 ≠ 종료. **트레이 아이콘 우클릭 → Quit** 필요.

**수정**: "앱 완전 종료" 표현 명시 + 트레이 Quit 강조.

### F5. MCP 연결 검증 방법 미안내
**문제**: 검증을 "내 vault의 CLAUDE.md 읽어줘" 같은 자연어 질문으로만 안내

**확인**: Claude Desktop/Cowork에서는 **새 채팅창 하단 🔨 hammer 아이콘**에 사용 가능한 도구 개수가 숫자로 표시됨. 아이콘 자체가 없으면 MCP 미연결.

**수정**: 매트릭스의 "MCP 연결 검증" 행 + 11번 검증 단계 + Seamless 테스트 사전 확인에 hammer 아이콘 추가.

### F6. Cowork 트러블슈팅 부재
**문제**: "Cowork 메뉴가 안 보임" 같은 흔한 증상 누락

**확인**: 무료 플랜은 Cowork 미지원 → 메뉴 자체가 없음.

**수정**: 04-claude-integration.md 트러블슈팅 표에 행 추가 + 사전 요구사항 명시.

## 남은 검증 불가 항목 (실제 PC에서만 확인 가능)

- Web Clipper `{{"prompt"}}` syntax가 실제 Interpreter UI와 일치하는지
- Templater의 `tp.app.vault.getAbstractFileByPath` 접근이 모든 Templater 버전에서 가능한지
- 5개 community 템플릿 import 시 schema validation error 여부
- Dataview `regexreplace` 함수 가용성 (특정 버전부터)
- `claude_desktop_config.json` 경로가 Windows에서 정확한지 (`%APPDATA%\Claude\`)
- kepano/obsidian-skills 마켓플레이스 명령이 현재 Claude Code 버전에서 그대로 작동하는지
