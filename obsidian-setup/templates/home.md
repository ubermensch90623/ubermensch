---
tags:
  - moc
---

# 🏠 Home

> Vault 진입 허브. Graph View의 중심 노드.

## 🧠 핵심

- [[CLAUDE.md]] — Claude 컨텍스트 (★ 매주 월요일 업데이트)
- [[inbox/action-tracker]] — 진행 중 액션
- [[inbox/decisions]] — 결정 로그

## 📚 주제 허브 (MOC)

<!-- 새 MOC 만들 때마다 여기 추가 -->
- 

## 🚀 활성 프로젝트

<!-- projects/ 하위 폴더 링크 -->
- 

## 📓 최근

```dataview
TABLE file.mtime AS "수정"
FROM "notes" OR "ideas" OR "inbox"
WHERE !contains(file.path, "templates")
SORT file.mtime DESC
LIMIT 10
```

## 📊 Vault 통계

```dataview
TABLE length(rows) AS Count
FROM ""
WHERE !contains(file.path, "templates") AND !contains(file.path, ".obsidian")
GROUP BY split(file.folder, "/")[0] AS Folder
SORT Count DESC
```

## ⚡ 빠른 작업

- 새 영구 노트: `Ctrl+N` (inbox/에 생성됨)
- 오늘 daily note: `Ctrl+Shift+D` (커스텀 바인딩)
- Daily Brief 실행: Claude Code에서 `prompts/daily-brief.md`
- Pattern Finder: Claude Code에 `prompts/pattern-finder.md` 붙여넣기

## 🔗 외부 리소스

- [Obsidian Help](https://help.obsidian.md)
- [이 키트의 README](../README.md)
