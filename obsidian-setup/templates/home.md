---
tags:
  - moc
---

# 🏠 Home

> Vault 진입 허브. Graph View의 중심 노드. 모든 길은 여기서 시작.

## 📌 Start Here (첫 셋업 시드)

> 이 vault를 처음 만들었을 때 채우는 4개 시드 노트. 채우면서 자신의 사고를 정의한다.

- [[001-why-this-vault-exists]] — 왜 이 vault를 만드는가
- [[002-how-i-want-to-think]] — 어떤 사고방식을 키우고 싶나
- [[003-current-obsessions]] — 지금 집착하는 것들
- [[004-open-questions]] — 답을 찾고 있는 질문들

> Claude에게 첫 질문: "이 4개 노트에서 내가 못 본 패턴이 뭐야?"

## 🧠 핵심 파일

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

- 새 노트: `Ctrl+N` (inbox/에 생성됨)
- 오늘 daily note: Settings → Hotkeys에서 "Daily notes: Open today's note"에 `Ctrl+Shift+D` 바인딩 권장
- Daily Brief 실행: Claude Code에서 `prompts/daily-brief.md`
- Pattern Finder: Claude Code에 `prompts/pattern-finder.md` 붙여넣기

## 🔗 외부 리소스

- [Obsidian Help](https://help.obsidian.md)
- [이 키트의 README](../README.md)
