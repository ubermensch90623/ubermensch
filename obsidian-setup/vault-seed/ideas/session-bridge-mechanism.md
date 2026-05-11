---
aliases:
  - session bridge
  - seamless sessions
  - SESSION PROTOCOL
  - bridge file
created: 2026-05-11
tags:
  - permanent
  - status/evergreen
---

# Session Bridge Mechanism — Seamless의 핵심

> 새 Claude 세션이 어제 세션과 이어지는 메커니즘.
> "vault = 영구 기억, 대화 = 휘발성"이라는 비대칭을 활용한 단기 기억 다리.

## 문제

Claude는 세션 간 기억이 없다. 어제 1시간 대화하고 새 채팅 열면 어제 결정/논의 사라짐. 사용자가 매번 컨텍스트를 재주입하면 마찰이 누적되어 시스템 무너진다.

대부분의 해결책:
- ❌ Claude가 모든 대화를 자동 기억 (없음)
- ❌ 사용자가 매번 컨텍스트 붙여넣기 (마찰)
- ❌ 긴 단일 채팅 유지 (컨텍스트 윈도우 한계)

## 해법: 단기 기억 파일 + 강제 프로토콜

**핵심 디자인**:
1. **`inbox/session-bridge.md`** = 단기 기억 파일. 직전 세션의 모든 핵심을 담음
2. **CLAUDE.md 최상단 SESSION PROTOCOL** = Claude의 행동 강제 규칙 (A/B/C/D)
3. **Custom Instructions** (`~/.claude/CLAUDE.md` 또는 Cowork Global Instructions) = SESSION PROTOCOL을 트리거

이 셋이 결합되어 **희망**이 아닌 **강제**가 됨.

## 4단계 프로토콜

### A. 세션 시작
- CLAUDE.md 읽기
- session-bridge.md 읽기 ← 어제 컨텍스트 자동 로딩
- action-tracker.md Open Actions 인지
- 첫 답변 전 "내가 알고 있는 컨텍스트" 한 줄 보고

### B. 대화 중 (자동)
- 트리거 단어 감지 → 즉시 vault 저장 (`📝 saved → [[...]]`)
- 결정 → [[decisions]]에 append
- 액션 → [[action-tracker]]에 append

### C. 세션 종료
- session-bridge.md 덮어쓰기:
  - Last Session Summary (3줄)
  - Open Threads
  - Decisions Made (wikilinks)
  - Actions Added
  - Files Created/Modified
- `🌙 session bridged` 보고

### D. 신뢰 검증
- 사용자의 검증 질문(예: "내 Current Projects 그대로 읊어줘")에 일반론 금지
- MCP 실패 시 즉시 "vault 접근 불가" 솔직 보고

## 왜 작동하나

- **session-bridge.md는 덮어쓰이는 단일 파일** — 부풀어 오르지 않음
- **결정/액션은 별도 append-only 파일** — 영구 보존
- **CLAUDE.md의 PROTOCOL은 Claude가 매 세션 자동 읽음** — 사용자의 기억력 의존 X
- **검증 가능** — [[MOC-vault-setup]] 13.5 단계의 5-step Seamless Test

## 실패 모드

| 증상 | 원인 |
|---|---|
| 새 세션이 어제 모름 | session-bridge.md를 첫 read 안 함 → PROTOCOL A1~A3 누락 (Custom Instructions 점검) |
| 결정이 vault에 안 들어감 | 트리거 감지 실패 → PROTOCOL B 표현 강화 필요 |
| session-bridge.md 안 덮어쓰임 | PROTOCOL C 미트리거 → `prompts/session-end.md` 수동 사용 |
| 일반론 답변 | MCP 실패 또는 vault CLAUDE.md 부실 |

## Cottrell의 원형과 차이

Cottrell의 글은 "AI 직원" 비유로 이 메커니즘을 설명. 그러나 그는 **개념**만 제시했지 **강제 메커니즘**까지 안 짰음. 이 노트의 핵심 기여:

- Cottrell: "Memory file을 read하라고 지시"
- 이 디자인: SESSION PROTOCOL 4단계 + bridge 파일 + 검증 5-step

## 관련 노트

- [[MOC-vault-setup]] (주제 허브)
- [[two-claude-md-pattern]] (PROTOCOL이 어디 사는지)
- [[cognition-vs-organization]] (왜 bridge가 필요한가)
- [[4-layer-pkm-architecture]] (Layer 4 안의 메커니즘)
- [[linkrot-prevention]] (bridge 링크가 끊기지 않게)

## 출처

- Cottrell의 "AI employee" 메타포
- Dwivedi의 "vault that talks back" 원칙
- 본인 + Claude의 이번 세션 통합 설계

## 미해결

- 30분 침묵 자동 감지가 안 됨 — 사용자가 "마무리"라고 명시해야 PROTOCOL C 트리거
- session-bridge.md가 너무 길어지면 컨텍스트 윈도우 압박. 분기마다 archive 필요?
- 두 클라이언트(Code + Cowork)가 동시에 vault 쓸 때 충돌 방지 (현재는 Obsidian Git 자동 커밋 의존)
