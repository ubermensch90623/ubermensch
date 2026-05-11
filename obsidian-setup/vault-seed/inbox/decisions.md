---
tags:
  - log/decisions
---

# 🧭 Decisions Log

> Claude와 본인이 내린 결정들이 시간순으로 누적. 최신이 위.

---

## 2026-05-11 — Cowork Global Instructions UI 경로/명칭 확정 #project/vault-setup

- **컨텍스트**: Cowork 통합 트랙이 추정 기반이었음. Anthropic 공식 문서로 대조 필요
- **결정**: Cowork는 **Claude Desktop의 기능**(별도 앱 X), Custom Instructions 필드 = **Settings → Cowork → Global Instructions**, MCP config UI = **Settings → Developers → Edit Config**
- **대안**: "Settings → User Preferences" (틀린 이름), 별도 앱으로 안내 (오해 유발)
- **이유**: 공식 지원 문서 (support.claude.com) 검증
- **재검토 조건**: Cowork가 GA되면 UI 변경 가능성. 분기마다 재확인
- **관련 노트**: [[two-claude-md-pattern]] · [[MOC-vault-setup]]

## 2026-05-11 — MCP 연결 검증 방법 = 🔨 hammer 아이콘 #project/vault-setup

- **컨텍스트**: Claude Desktop/Cowork에서 MCP 작동 여부를 자연어 질문으로만 안내했었음
- **결정**: 새 채팅창 하단의 **🔨 hammer 아이콘**에 도구 개수가 표시되는 것이 일차 검증. 아이콘 자체가 없으면 MCP 미연결
- **대안**: "내 vault의 X를 읽어줘"로만 검증 (간접적, 모호)
- **이유**: 공식 문서가 hammer 아이콘을 명시적 verification 방법으로 안내
- **관련 노트**: [[MOC-vault-setup]] · [[4-layer-pkm-architecture]]

## 2026-05-11 — Seamless 메커니즘 = session-bridge.md + SESSION PROTOCOL #project/vault-setup

- **컨텍스트**: "새 세션 열면 어제 작업이 이어지는가?" 질문. 자동 컨텍스트 로딩이 "희망"이 아니라 "강제"여야 함
- **결정**: `inbox/session-bridge.md`를 단기 기억 메커니즘으로 신설. CLAUDE.md 최상단에 **SESSION PROTOCOL** 4단계(A/B/C/D) 강제 섹션. Custom Instructions가 매 세션 시작 시 이를 트리거
- **대안**: Custom Instructions만으로 행동 유도 (실패율 높음), Claude의 자체 기억 의존 (없음)
- **이유**: CyrilXBT/Cottrell 모두 "vault should talk back" 강조. Memory 메커니즘 없이는 "search engine with persona"로 퇴화
- **재검토 조건**: 3회 이상 Seamless 테스트 실패 시 메커니즘 재설계
- **관련 노트**: [[session-bridge-mechanism]] · [[cognition-vs-organization]] · [[MOC-vault-setup]]

## 2026-05-11 — Custom Instructions 자가 강제 프로토콜로 강화 #project/vault-setup

- **컨텍스트**: 1차 버전은 "Claude가 잘 해주길 희망"하는 구조
- **결정**: `~/.claude/CLAUDE.md`와 Cowork Global Instructions가 vault CLAUDE.md의 SESSION PROTOCOL을 매번 호출하도록 강화. MCP 실패 시 즉시 사용자 알림 의무화
- **대안**: 부드러운 가이드라인 (검증 불가)
- **이유**: 시스템이 사용자의 기억력에 의존하면 한 주 내에 무너짐. 프로토콜이 시스템을 강제해야 함
- **관련 노트**: [[session-bridge-mechanism]] · [[two-claude-md-pattern]]

## 2026-05-11 — Windows 자동실행 + 주간 Task Scheduler 알림 #project/vault-setup

- **컨텍스트**: MCP는 Obsidian이 켜져 있어야 작동. 사용자가 Obsidian 실행을 잊으면 시스템 죽음. CLAUDE.md도 stale해지면 답변 품질 추락
- **결정**: 체크리스트 11.5 신설. Obsidian을 Windows 시작 프로그램 등록 + 매주 월요일 9am Task Scheduler 알림 (CLAUDE.md 업데이트)
- **대안**: 수동 의존 (실패 보장)
- **관련 노트**: [[session-bridge-mechanism]] · [[MOC-vault-setup]]

## 2026-05-11 — kepano/obsidian-skills 설치는 2개 명령 #project/vault-setup

- **컨텍스트**: 1차 버전은 `/plugin marketplace add`만 안내 → 스킬 비활성
- **결정**: `marketplace add` + **`/plugin install obsidian@obsidian-skills`** 두 명령 모두 실행
- **이유**: kepano 공식 README 검증
- **관련 노트**: [[4-layer-pkm-architecture]]

## 2026-05-11 — mcp-obsidian = Python(uvx) 패키지 #project/vault-setup

- **컨텍스트**: 1차 버전은 `npx -y mcp-obsidian`으로 안내 (틀림)
- **결정**: `uvx mcp-obsidian` 사용. 사전에 `winget install astral-sh.uv` 필요. config 환경변수는 `OBSIDIAN_API_KEY`, `OBSIDIAN_HOST`, `OBSIDIAN_PORT`
- **이유**: MarkusPfundstein/mcp-obsidian 공식 README 검증
- **재검토 조건**: 다른 MCP 서버(obsidian-mcp-tools 등) 도입 시 재평가
- **관련 노트**: [[4-layer-pkm-architecture]]

## 2026-05-11 — 템플릿 문법 Templater로 통일 #project/vault-setup

- **컨텍스트**: 1차 버전은 Core Templates(`{{date:YYYY-MM-DD}}`)와 Templater(`<% tp.date.now(...) %>`) 혼용 → 어느 것도 작동 안 함
- **결정**: 모든 템플릿을 Templater 문법으로 통일. Settings → Templater에서 Folder Templates 매핑 (예: `notes/journal` → `templates/daily-note.md`)
- **대안**: Core Templates 통일 (덜 강력함)
- **이유**: 조건부 embed (daily-note의 brief 존재 시만 transclude) 같은 로직 필요
- **관련 노트**: [[folder-simplicity-principle]]

## 2026-05-11 — Web Clipper JSON schema 검증 #project/vault-setup

- **컨텍스트**: 1차 버전 JSON 5개 모두 import 불가 (스키마 불일치)
- **결정**: `schemaVersion: "0.1.0"`, `context` 필드, `schema:@Type:field`(`@` 접두사), `safe_name` 필터, URL prefix triggers (글로브 X), `"type": "datetime"` 사용
- **이유**: obsidian-community/web-clipper-templates의 youtube-clipper.json raw 검증
- **관련 노트**: [[4-layer-pkm-architecture]]

## 2026-05-11 — Cowork = Claude Desktop의 기능 (Pro 이상 필요) #project/vault-setup

- **컨텍스트**: "Cowork와 Claude Desktop 둘 다 설치해야 하나?" 혼동
- **결정**: Cowork는 Claude Desktop **안의** 기능. 별도 앱 아님. **2026년 1월 research preview**, 2월 Windows. **Pro/Max/Team/Enterprise 필수**
- **이유**: support.claude.com/en/articles/13345190 검증
- **관련 노트**: [[two-claude-md-pattern]] · [[MOC-vault-setup]]

## 2026-05-11 — PKM 방법론 = Zettelkasten 사고 + CyrilXBT 5폴더 #project/vault-setup

- **컨텍스트**: Zettelkasten 전통 폴더는 12개+. 복잡해서 무너짐 (CyrilXBT 경고)
- **결정**: 폴더는 5개(`inbox/notes/ideas/projects/templates` + `CLAUDE.md`). Zettelkasten의 fleeting/literature/permanent 구분은 **태그**(`#fleeting`, `#literature`, `#permanent`)로 처리. 성숙도는 `#status/seedling|budding|evergreen`
- **대안**: 전통 Zettelkasten 폴더 구조 (붕괴 보장), PARA 폴더 (구조 다름)
- **이유**: "단순함이 지속성을 만든다" — CyrilXBT 핵심 통찰. Zettelkasten 정신은 사고 방식이지 폴더가 아님
- **관련 노트**: [[folder-simplicity-principle]] · [[4-layer-pkm-architecture]] · [[MOC-vault-setup]]

## 2026-05-11 — Vault 위치 = Google Drive 안 #project/vault-setup

- **컨텍스트**: 단일 PC면 로컬 폴더 OK. 멀티 디바이스면 동기화 필요
- **결정**: `%USERPROFILE%\Google Drive\Vault\brain`. Drive로 충돌 시 Obsidian Sync($5/월) 고려
- **이유**: Cottrell 패턴. iCloud는 Windows-only 트랙이라 의미 없음
- **관련 노트**: [[MOC-vault-setup]]

## 2026-05-11 — OS = Windows 단일, iOS 트랙 제외 #project/vault-setup

- **컨텍스트**: 사용자 선택 (트랙 결정 질문)
- **결정**: 모든 가이드는 Windows 기준. macOS/Linux/iOS 가이드 미작성
- **재검토 조건**: 사용자가 iPad/iPhone 캡처 필요해지면 별도 트랙 추가
- **관련 노트**: [[MOC-vault-setup]]

## 2026-05-11 — CLAUDE.md = 빈 칸 + 한국어 주석 예시 #project/vault-setup

- **컨텍스트**: 자기소개 필드를 어떻게 제공할지 (완전 빈 칸 / 예시 채움 / 별도 파일)
- **결정**: 필드는 비우되, 각 필드 아래 `<!-- 예) ... -->` HTML 주석으로 한국어 예시 표시. 사용자가 주석 위에 본인 내용 작성, 주석은 그대로 두거나 삭제
- **대안**: 완전 빈 칸 (가이드 없음), 가상 페르소나로 채움 (덮어쓰기 부담)
- **이유**: 학습 곡선 + 개인화 사이 균형
- **관련 노트**: [[two-claude-md-pattern]]

## 2026-05-11 — AgriciDaniel/claude-obsidian = 옵션 트랙 + 상세 가이드 #project/vault-setup

- **컨텍스트**: `/wiki`, `ingest`, `/autoresearch` 등 자동 wiki 시스템을 즉시 도입할지, 옵션으로 둘지
- **결정**: 처음 1~2주는 미니멀 트랙 운영, 익숙해진 후 옵션 B로 도입. `06-agricidaniel-wiki.md`에 두 가지 통합 옵션(별도 vault vs 머지) 상세 가이드
- **이유**: 너무 많은 자동화는 첫 셋업 학습 부담. CyrilXBT의 "5개 노트로 시작" 원칙
- **관련 노트**: [[4-layer-pkm-architecture]] · [[MOC-vault-setup]]
