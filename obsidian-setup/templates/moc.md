---
created: {{date:YYYY-MM-DD}}
tags:
  - moc
  - status/budding
---

# <% tp.file.title.replace("MOC-", "") %>

> 주제 허브. 이 주제에 관련된 모든 노트를 모은다.

## 핵심 질문

<!-- 이 주제에서 내가 답하고 싶은 질문 -->
- 

## 핵심 노트

### 영구 (#permanent)

```dataview
LIST
FROM #permanent
WHERE contains(file.outlinks, this.file.link) OR contains(this.file.outlinks, file.link)
SORT file.mtime DESC
```

### 외부 자료 (#literature)

```dataview
LIST
FROM #literature
WHERE contains(file.outlinks, this.file.link) OR contains(this.file.outlinks, file.link)
SORT file.mtime DESC
```

## 수동 큐레이션

<!-- Dataview로 자동 못 잡는 핵심 노트들 -->
- [[]]

## 미해결 질문

- 

## 인접 주제 (다른 MOC)

- [[MOC-]]
