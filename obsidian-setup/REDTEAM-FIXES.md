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

## 남은 검증 불가 항목

브라우저/Claude/Obsidian 없이는 100% 검증 못 함. 실제 셋업 시 다음 항목 추가 확인 권장:

- Web Clipper `{{"prompt"}}` syntax가 실제 Interpreter UI와 일치하는지
- Dataview의 `split(file.folder, "/")[0]` 컴파일 여부
- Templater의 `tp.file.find_tfile()` API 시그니처 (버전에 따라 다를 수 있음)
- 5개 community 템플릿 import 시 schema validation error 여부
