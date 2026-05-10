<%*
const today = tp.date.now("YYYY-MM-DD");
const todayLong = tp.date.now("YYYY-MM-DD dddd");
const briefPath = `inbox/brief-${today}.md`;
const briefExists = await tp.file.find_tfile(briefPath) !== null;
-%>
---
date: <% today %>
tags:
  - journal
---

# <% todayLong %>

## ☀️ Morning Brief

<%* if (briefExists) { %>
![[inbox/brief-<% today %>#CONNECTIONS]]
<%* } else { %>
> 오늘 Daily Brief가 아직 없음. `prompts/daily-brief.md` 실행하면 [[inbox/brief-<% today %>]]에 생성됨.
<%* } %>

## 🎯 Today's One Thing

> 오늘 끝내면 만족할 일 하나. (3개 아님)

- 

## 📋 Tasks

- [ ] 

## 💭 Thoughts (Fleeting)

<!-- 떠오르는 생각 즉시 메모. 정제는 나중에. -->

- 

## 📞 Meetings / Calls

- 

## 🔗 Captures

<!-- 오늘 Web Clipper로 캡처한 것 자동 표시 -->
```dataview
LIST
FROM "inbox"
WHERE startswith(file.name, "<% today %>")
```

## 🌙 End of Day

- 오늘의 결정:
- 내일로 미룬 것:
- 감사:
