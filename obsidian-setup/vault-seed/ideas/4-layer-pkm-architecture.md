---
aliases:
  - 4-layer architecture
  - PKM layers
  - capture-pipeline-memory-intelligence
created: 2026-05-11
tags:
  - permanent
  - status/evergreen
---

# 4-Layer PKM Architecture

> 정보를 인지로 바꾸는 단방향 파이프. 각 레이어는 정확히 하나의 일만 한다.
> Dwivedi/Cottrell/CyrilXBT 세 글의 공통 골격. 셋이 같은 결론에 도달했다는 점이 신호.

## 핵심 아이디어

**대부분의 second brain이 실패하는 이유**: 입력 설계는 있지만 출력 설계가 없다. 정보를 모으지만 인지가 안 생긴다. → [[cognition-vs-organization]]

해결: 정보의 흐름을 4개 분리된 레이어로 만든다. 각 레이어가 한 가지만 잘하면 시스템이 컴파운드한다.

## 레이어 구조

### Layer 1: Capture (마찰 0초)
- 도구: Obsidian Web Clipper / Whisper / Telegram bot / Readwise
- 역할: 정보를 분류/태깅 없이 빠르게 vault의 `inbox/`로 떨어뜨림
- 규칙: 10초 넘는 capture는 무너진다 (CyrilXBT). 분류는 나중

### Layer 2: Pipeline (자동 라우팅)
- 도구: N8N / Zapier / AI Interpreter
- 역할: 캡처된 raw를 정제된 형태로 변환하여 `inbox/` → 적절한 폴더로
- 예: Web Clipper의 AI Interpreter가 클립 순간 요약/태그 생성

### Layer 3: Memory (Obsidian Vault)
- 도구: Obsidian + 5폴더 → [[folder-simplicity-principle]]
- 역할: 영구 컨텍스트 저장. 변하지 않는 ground truth
- 폴더: `inbox/`, `notes/`, `ideas/`, `projects/`, `templates/` + `CLAUDE.md`

### Layer 4: Intelligence (Claude)
- 도구: Claude Code or Claude Desktop+Cowork
- 역할: vault를 읽고 패턴/모순/연결 surface
- 진입점: CLAUDE.md → [[two-claude-md-pattern]]
- 세션 간 연결: [[session-bridge-mechanism]]

## 왜 이게 작동하나

각 레이어가 다른 레이어의 문제를 해결:
- Capture가 빠르면 Memory가 풍성해진다
- Pipeline이 자동이면 Memory가 깔끔해진다
- Memory가 풍성+깔끔하면 Intelligence가 강력해진다
- Intelligence가 패턴을 surface하면 Capture 방향성이 생긴다

순환이 형성되면 vault가 매주 똑똑해진다. CyrilXBT: "At 6 months it feels almost unfair."

## 셋업 키트와의 연결

이 4 레이어는 키트의 7개 가이드 문서로 분해됨:
- Layer 1: `05-web-clipper.md`
- Layer 2: `07-automation-future.md` (다음 단계)
- Layer 3: `02-vault-structure.md` + 모든 템플릿
- Layer 4: `04-claude-integration.md` + `06-agricidaniel-wiki.md`

## 관련 노트

- [[MOC-vault-setup]] (주제 허브)
- [[cognition-vs-organization]] (Layer 4의 진짜 목적)
- [[session-bridge-mechanism]] (Layer 4 안의 메모리 메커니즘)
- [[folder-simplicity-principle]] (Layer 3 설계 원칙)
- [[two-claude-md-pattern]] (Layer 4 진입점 구조)

## 출처

- Dwivedi의 원래 4-layer 정의 (Capture/Automation/Memory/Intelligence)
- Cottrell의 5-piece 구체화 (Obsidian/Transcription/MCP/Cowork/Custom Instructions)
- CyrilXBT의 운영 매뉴얼 (Daily Brief/Weekly Synthesis)

## 미해결

- Layer 2 (Pipeline) 자동화를 언제 도입할지: 현재는 수동. N8N 셋업은 [[action-tracker]] 후속
- Layer 4의 Claude 자체가 진화하면 Layer 3 구조도 재설계해야 할 수 있음
