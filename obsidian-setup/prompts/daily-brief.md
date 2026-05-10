# Daily Brief Prompt

> 매일 아침 실행. Claude Code에 그대로 붙여넣기.
> 또는 N8N으로 6am 자동화 (`07-automation-future.md` 참고).

---

You are reading my Obsidian knowledge vault. Read everything in `/inbox` from
the last 24 hours and everything in `/notes` from the last 7 days. Also read
`CLAUDE.md` at the vault root for context about who I am and what I'm working on.

Then do three things:

## CONNECTIONS

Find the 3 most interesting connections between recent captures and older
notes I probably have not noticed. Be specific. Quote the relevant passages.
Use `[[wikilink]]` format to reference the exact notes.

## PATTERN

Identify one pattern across everything I have been reading this week. What is
my brain clearly working on even if I have not said it explicitly? Ground this
in specific note titles, not abstract themes.

## QUESTION

Give me one question worth sitting with today based on the pattern you
identified. Not a task. A question. The question should be specific enough
that I can make progress on it today, but open enough that it doesn't have a
trivial answer.

---

Write this as a clean markdown file formatted for Obsidian. Save it to
`/inbox/brief-{{today's date in YYYY-MM-DD}}.md`.

Use this structure:

```markdown
---
date: YYYY-MM-DD
tags:
  - daily-brief
---

# Daily Brief — {date}

## 🔗 CONNECTIONS

### 1. [[note-A]] ↔ [[note-B]]
> "passage from note A"
> "passage from note B"
**Why this matters**: ...

### 2. ...

### 3. ...

## 🌊 PATTERN

You are clearly working on [pattern]. Evidence:
- [[note-1]] — ...
- [[note-2]] — ...
- [[note-3]] — ...

## ❓ QUESTION

> [The question]

Why this question now: ...
Where to start: ...
```

---

규칙:
- 동기부여 문구 금지
- 일반론 금지
- 모든 주장은 [[wikilink]]로 vault 노트 인용
- 답이 없으면 솔직히 "지난 7일 노트가 너무 적어 패턴 식별 불가" 같이 말할 것
