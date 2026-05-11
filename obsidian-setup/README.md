# Obsidian + Claude PKM 셋업 키트 (Windows)

> 로컬 PC에서 Obsidian + Claude를 인지(cognition) 증폭기로 셋업하기 위한 완성 키트.
> Zettelkasten 사고 방식 + 5폴더 구조 + Claude MCP 통합 + Web Clipper 자동 캡처.

## 이 키트가 만들어주는 것

- **Vault**: 5개 폴더로 단순하게 시작하는 평생 가는 vault
- **CLAUDE.md**: Claude를 인지 파트너로 만드는 컨텍스트 파일
- **Daily Brief / Weekly Synthesis**: vault가 매일 말을 걸어오게 만드는 프롬프트
- **Web Clipper + AI Interpreter**: 글/X/유튜브를 자동으로 정제하여 vault에 저장
- **Claude Code 통합**: kepano/obsidian-skills + MCP로 Claude가 vault 직접 read/write

## 빠른 시작 (요약)

1. `00-checklist-windows.md`를 위에서부터 순서대로 따라가세요.
2. 막히면 해당 항목의 참고 문서로 점프 (각 항목에 링크 있음).
3. 완벽한 셋업을 기다리지 마세요. **5개 시드 노트로 오늘 바로 시작**할 수 있습니다.

## 파일 안내

| 파일 | 용도 |
|---|---|
| `00-checklist-windows.md` | ★ 메인 체크리스트. 여기부터 시작 |
| `01-philosophy.md` | 왜 이렇게 만드는가 (Dwivedi/Cottrell/CyrilXBT 통합 철학) |
| `02-vault-structure.md` | 5폴더 구조 + 태그 체계 + Google Drive 팁 |
| `03-shortcuts-windows.md` | Windows 단축키 치트시트 |
| `04-claude-integration.md` | kepano/skills + MCP + Custom Instructions |
| `05-web-clipper.md` | ★ Web Clipper + AI Interpreter (API 키 가이드) |
| `06-agricidaniel-wiki.md` | 자동 wiki 시스템 옵션 (`/wiki`, `ingest`, `/autoresearch`) |
| `07-automation-future.md` | N8N/Telegram/Whisper 등 다음 단계 자동화 |
| `08-curated-repos.md` | 큐레이션된 Obsidian GitHub 레포 20선 |
| `templates/` | Vault에 복사할 노트 템플릿 (CLAUDE.md 포함) |
| `templates/webclipper-templates/` | Web Clipper용 JSON 템플릿 5개 |
| `starter-notes/` | 4개 시드 노트 (Why/How/Obsessions/Questions). vault의 `inbox/`로 복사 |
| `inbox-init/` | `decisions.md` + `action-tracker.md` 초기 헤더. vault의 `inbox/`로 복사 |
| `prompts/` | Daily Brief / Weekly Synthesis / Pattern Finder + **Session Start / Session End** 프롬프트 |

## 두 가지 트랙

### 트랙 A: 미니멀 (권장 — 처음 1~2주)
이 키트만으로 운영. 5폴더 + 시드 5개 + Web Clipper + Claude Code/MCP.

### 트랙 B: 풀스택 (익숙해진 후)
[AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) 추가 머지 — `/wiki`, `ingest`, `/autoresearch` 등 자동 wiki 시스템. 자세한 통합은 `06-agricidaniel-wiki.md`.

## 핵심 원칙

1. **인지가 목적이지 조직화가 아니다** — vault는 묘지가 아니라 증폭기여야 한다 (Dwivedi)
2. **캡처 마찰 < 10초** — 10초 넘으면 인지 부하 아래서 무너진다 (CyrilXBT)
3. **5폴더 + 태그** — 복잡한 폴더 구조는 결국 무너진다 (CyrilXBT)
4. **CLAUDE.md가 가장 중요한 파일** — 컨텍스트 없는 AI는 검색엔진일 뿐 (Dwivedi/Cottrell)
5. **Vault should talk back** — 매일 아침 vault가 먼저 말을 건다 (CyrilXBT)
6. **5개 노트로 시작** — 완벽한 셋업은 영원히 오지 않는다 (Dwivedi/CyrilXBT)
7. **세션은 휘발성, vault는 영구** — 매 세션 종료 시 `session-bridge.md`로 다음 세션에 다리 놓기. 이게 seamless의 핵심

## 참고 출처

- Nainsi Dwivedi, "Your Obsidian Vault Is Probably Dead"
- Fraser Cottrell, "Claude + Obsidian = A true AI employee"
- CyrilXBT, "How to Build an Obsidian Knowledge Vault That Gets Smarter Every Day"
- [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) (Obsidian CEO Stephan Ango)
- [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)
