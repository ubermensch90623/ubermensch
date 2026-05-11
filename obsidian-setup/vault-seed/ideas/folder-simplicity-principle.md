---
aliases:
  - five folders
  - folder simplicity
  - structure collapse
created: 2026-05-11
tags:
  - permanent
  - status/evergreen
---

# Folder Simplicity Principle

> 복잡한 폴더 구조는 결국 무너진다. 단순함이 지속성을 만든다.
> CyrilXBT의 핵심 통찰. 모든 PKM 시스템 설계의 기본 제약.

## 핵심 주장

폴더가 많을수록 캡처 시 "이거 어디 넣지?" 결정이 누적. 결정 피로가 임계점을 넘으면 사용자가 캡처 자체를 포기. 시스템 죽음.

해결: **5폴더 + 풍부한 태그**.

## 5폴더 구조

```
Vault/
├── CLAUDE.md
├── home.md
├── inbox/         (미정제 캡처 — 일단 여기)
├── notes/         (정제된 외부 자료 — #literature)
├── ideas/         (내 사고 — #permanent)
├── projects/      (진행 중 작업)
├── templates/
└── attachments/
```

**규칙**: 어디 넣을지 모르면 → `inbox/`. 5초 안에 결정 안 나면 inbox로. 정제는 나중.

## Zettelkasten 정신은 폴더가 아님

전통 Zettelkasten은 fleeting / literature / permanent / structure 4종으로 노트를 나눈다. 많은 가이드가 이걸 폴더로 만든다 (`zettel/fleeting/`, `zettel/literature/`, ...).

이게 함정. Zettelkasten은 **사고 방식**이지 **폴더 구조**가 아니다. 같은 효과를 태그로 얻을 수 있다:
- `#fleeting` — 휘발성 (며칠 내 정제 or 삭제)
- `#literature` — 외부 출처 요약
- `#permanent` — 자기 언어로 재구성
- `#moc` — Map of Content

폴더는 단순화하고 태그는 풍부하게. 이게 modern Zettelkasten의 일반적 형태.

## 성숙도 태그 추가

같은 #permanent 안에서도 성숙도가 다름:
- `#status/seedling` — 막 심은 씨앗 (방금 작성)
- `#status/budding` — 자라는 중 (여러 번 수정)
- `#status/evergreen` — 성숙 (안정적, 자주 인용됨)

이 성숙도가 Dataview로 자동 추적 가능. 폴더로 처리하면 이동시킬 때마다 깨진다 ([[linkrot-prevention]]).

## 왜 폴더가 무너지는가

복잡한 계층 구조의 실패 패턴:
1. 처음엔 깔끔 — `projects/active/`, `projects/archive/`, `notes/research/`, `notes/captures/`
2. 1개월 후 — "이거 active인가 archive인가?" 결정 마찰
3. 2개월 후 — 일부 노트가 잘못된 폴더에. 검색 실패
4. 3개월 후 — 사용자가 캡처를 미루기 시작
5. 결국 — vault가 묘지가 됨 ([[cognition-vs-organization]])

태그는 다중 분류 가능, 폴더는 단일. 정보는 본질적으로 다차원. 단일 분류 강제 = 정보 손실.

## 검증: 폴더 추가 의향이 들 때

새 폴더 만들고 싶을 때 자기 질문:
- "이 폴더 안에 들어갈 노트가 10개 이상이 될 것인가?"
- "태그로는 처리 불가능한가?"
- "이 폴더가 6개월 후에도 의미 있을 것인가?"

3개 다 Yes면 폴더. 하나라도 No면 태그.

## 예외

- `inbox/` — 임시 staging이라 별도 폴더 정당화
- `notes/journal/` — daily notes는 시간순 정렬 + 별도 plugin 설정 때문에 폴더 필요
- `notes/weekly/` — 동일
- `projects/<name>/` — 프로젝트당 폴더는 OK (각 프로젝트가 자체 attachments/decisions 가질 수 있어)

## 관련 노트

- [[MOC-vault-setup]] (주제 허브)
- [[cognition-vs-organization]] (왜 단순화가 인지로 이어지는가)
- [[4-layer-pkm-architecture]] (Layer 3 설계 근거)
- [[linkrot-prevention]] (폴더 이동이 링크를 깨는 메커니즘)

## 출처

- CyrilXBT 원문: "Every complex folder structure eventually collapses under its own weight"
- Sönke Ahrens, "How to Take Smart Notes" (전통 Zettelkasten)
- 본인 + 이 키트의 [[decisions#2026-05-11 — PKM 방법론 = Zettelkasten 사고 + CyrilXBT 5폴더]]

## 미해결

- 5폴더가 임계 수를 넘는 vault에서도 유효한가? (10,000+ 노트)
- 회사/팀 vault에서는 권한 분리 위해 더 많은 폴더 필요할 수 있음 — 그 경우 어떻게?
