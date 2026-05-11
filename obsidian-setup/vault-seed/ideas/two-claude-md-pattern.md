---
aliases:
  - two CLAUDE.md
  - CLAUDE.md split
  - global vs vault CLAUDE.md
created: 2026-05-11
tags:
  - permanent
  - status/evergreen
---

# Two-CLAUDE.md Pattern

> 시스템에는 CLAUDE.md가 **2개** 있다. 다른 일을 한다. 헷갈리면 둘 다 망가진다.

## 두 파일의 역할

| 위치 | 역할 | 내용 | 누가 편집 |
|---|---|---|---|
| **`<vault>/CLAUDE.md`** | **본인 데이터** + SESSION PROTOCOL | 누구, 뭘 하는지, current projects, 사고 스타일, **A/B/C/D 강제 프로토콜** | 사용자 직접 (매주 월요일 5분 갱신) |
| **`~/.claude/CLAUDE.md`** (Code) 또는 **Settings → Cowork → Global Instructions** (Cowork) | **Claude에게 주는 지시문** | vault 경로 + "vault CLAUDE.md를 매번 읽어라" 같은 메타 지시 | 사용자 한 번 작성, 거의 안 만짐 |

## 분리 이유

**섞으면 안 되는 이유**:
1. **vault CLAUDE.md는 vault와 함께 동기화/백업** — 다른 기기에서도 같은 본인 컨텍스트
2. **글로벌 CLAUDE.md는 모든 Claude 세션에 적용** — vault 안 들어가도 동작
3. **글로벌이 vault CLAUDE.md 호출 → 무한 재귀 방지** 필요 (글로벌은 "vault 읽어라"만, vault는 본인 내용만)

이 분리가 있어야 vault를 옮겨도/공유해도 본인 컨텍스트가 따라간다.

## 글로벌 CLAUDE.md의 정확한 내용

```markdown
# Vault Bootstrap (모든 세션에 자동 적용)

내 Obsidian vault: `C:\Users\<USER>\Google Drive\Vault\brain`

## 매 세션 시작 시:
1. MCP로 <vault>/CLAUDE.md 읽고 SESSION PROTOCOL 적용
2. <vault>/inbox/session-bridge.md 읽고 직전 컨텍스트 로드
3. <vault>/inbox/action-tracker.md Open Actions 인지

## 매 답변마다:
- vault 노트를 [[wikilink]]로 인용
- 새 결정/액션은 즉시 vault에 저장
- 일반론 금지

## 매 세션 종료 시:
- 사용자 "마무리" 표현 시 → session-bridge.md 덮어쓰기
```

이게 SESSION PROTOCOL 트리거. ([[session-bridge-mechanism]])

## Vault CLAUDE.md의 정확한 내용

[[MOC-vault-setup]] 참고. 구성:
- SESSION PROTOCOL (최상단, A/B/C/D 4단계)
- Who I Am (자기소개)
- Current Projects (매주 갱신)
- Vault Routing Rules
- Communication Style
- What I Am Reading and Thinking About

## 클라이언트별 위치

**Claude Code**:
- 글로벌: `~/.claude/CLAUDE.md` (또는 `%USERPROFILE%\.claude\CLAUDE.md`)
- Vault: 자동 로드되려면 `cd <vault> && claude` 실행 (current dir의 CLAUDE.md = project CLAUDE.md)

**Claude Desktop + Cowork**:
- 글로벌 자리: **Settings → Cowork → Global Instructions** (Pro 이상 필요)
- Vault: MCP가 `<vault>/CLAUDE.md`를 read

**Claude.ai 웹 (Project)**:
- 글로벌 자리: Project Instructions
- Vault: 접근 못 함 (MCP 없음)

## 흔한 실수

1. **vault CLAUDE.md만 채우고 글로벌 안 만듦** → Claude가 새 세션에서 vault CLAUDE.md 자동 안 읽음
2. **글로벌에 본인 정보 넣음** → vault CLAUDE.md와 분기. 둘이 안 맞으면 답변이 일관성 없음
3. **vault CLAUDE.md를 SESSION PROTOCOL 없이 채움** → B/C 자동 저장이 안 됨
4. **글로벌에서 vault 경로 틀림** → MCP는 동작하지만 Claude가 못 찾음

## 관련 노트

- [[MOC-vault-setup]] (주제 허브)
- [[session-bridge-mechanism]] (CLAUDE.md가 호출하는 PROTOCOL의 정체)
- [[4-layer-pkm-architecture]] (전체 구조에서의 위치)
- [[linkrot-prevention]] (CLAUDE.md 안의 wikilink가 끊기지 않게)

## 출처

- Cottrell의 "Memory file" 개념 (Cowork에서 부르는 이름)
- Dwivedi의 "CLAUDE.md is the most important file"
- 이 키트의 [[decisions#2026-05-11 — Cowork Global Instructions UI 경로/명칭 확정]]

## 미해결

- 글로벌 CLAUDE.md가 너무 길면 Cowork Global Instructions의 글자수 제한에 걸릴 가능성 (미검증)
- vault를 동시에 여러 vault로 운영하면? (예: work + personal) — 글로벌 한 개로는 충돌. vault별 라우팅 필요?
