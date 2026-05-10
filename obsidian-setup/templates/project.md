---
project: 
status: active
started: {{date:YYYY-MM-DD}}
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

- Last touched: {{date:YYYY-MM-DD}}
- Next milestone: 
- Blocked on: 

## 핵심 결정사항

<!-- 이 프로젝트에서 내린 결정들. inbox/decisions.md에서 자동 가져오기 -->

```dataview
LIST
FROM "inbox/decisions"
WHERE contains(file.tags, "#project/" + this.file.name)
```

## 액션 아이템

```dataview
TASK
FROM "inbox/action-tracker"
WHERE !completed AND contains(text, this.file.name)
```

## 미팅 / 통화

<!-- 이 프로젝트 관련 회의록 -->
- 

## 관련 자료

### 외부 자료 (#literature)
- [[]]

### 영구 노트 (#permanent)
- [[]]

## 회고

<!-- 끝나면 채울 것 — 무엇이 잘 됐고, 무엇이 안 됐고, 다음에 다르게 할 것 -->
