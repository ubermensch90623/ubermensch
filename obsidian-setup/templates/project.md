---
project: 
status: active
started: <% tp.date.now("YYYY-MM-DD") %>
target_done: 
tags:
  - project
---

# <% tp.file.title %>

## 목표 (Done 정의)

<!-- 이 프로젝트가 완료됐다고 말할 수 있는 구체적 조건 -->

## Why (이게 왜 중요한가)

<!-- 미래의 나에게 동기를 상기시킬 한 단락 -->

## 현재 상태

- Last touched: <% tp.date.now("YYYY-MM-DD") %>
- Next milestone: 
- Blocked on: 

## 핵심 결정사항

<!--
Claude가 결정을 inbox/decisions.md에 append할 때 헤딩 끝에 `#project/<% tp.file.title %>` 태그를 붙여야 추적 가능.
또는 아래 백링크 섹션에서 [[decisions#YYYY-MM-DD — 결정 제목]] 으로 수동 링크.
-->

### 관련 결정 (decisions.md에서 백링크)

```dataview
LIST
FROM [[decisions]]
WHERE contains(file.name, "decisions")
```

> 위 쿼리는 decisions.md가 이 프로젝트 페이지를 인용하면 떠오름. Claude에게 결정 기록 시 `[[<% tp.file.title %>]]`로 백링크 만들라고 지시.

## 액션 아이템

```dataview
TASK
FROM "inbox/action-tracker"
WHERE !completed AND contains(text, this.file.name)
```

> action-tracker.md에서 액션 줄에 `[[<프로젝트 이름>]]` 또는 `#project/<프로젝트 이름>` 포함하면 자동 표시.

## 미팅 / 통화

<!-- 이 프로젝트 관련 회의록 — [[wikilink]]로 -->
- 

## 관련 자료

### 외부 자료 (#literature)

```dataview
LIST
FROM #literature
WHERE contains(file.outlinks, this.file.link)
```

### 영구 노트 (#permanent)

```dataview
LIST
FROM #permanent
WHERE contains(file.outlinks, this.file.link)
```

## 회고

<!-- 끝나면 채울 것 — 무엇이 잘 됐고, 무엇이 안 됐고, 다음에 다르게 할 것 -->
