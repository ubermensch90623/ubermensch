---
created: 2026-05-10
tags:
  - log/actions
---

# ✅ Action Tracker

> 모든 액션 아이템이 모이는 단일 파일. 프로젝트별 폴더에 흩어진 액션들의 마스터 인덱스.
> Claude가 통화/회의/세션 후 새 액션을 자동으로 여기에 append.

## 작성 형식

```markdown
- [ ] [YYYY-MM-DD] 액션 내용 — owner — due:YYYY-MM-DD — [[관련-노트]] #project/foo
```

체크박스, 생성일, 액션 자체, 책임자, 마감일, 관련 노트, 프로젝트 태그.

## Open Actions

<!-- Claude가 새 액션을 여기에 append. 완료되면 [x] 처리하고 아래 섹션으로 이동. -->

- [ ] [2026-05-10] CLAUDE.md를 본인 정보로 완성 — me — due:2026-05-11 — [[CLAUDE]] #project/vault-setup
- [ ] [2026-05-10] 시드 노트 4개(001~004) 본인 컨텍스트로 채우기 — me — due:2026-05-11 — [[001-why-this-vault-exists]] #project/vault-setup
- [ ] [2026-05-10] Claude에게 첫 패턴 분석 요청 — me — due:2026-05-12 — [[home]] #project/vault-setup

## 자동 쿼리 — 마감 임박

```dataview
TASK
FROM "inbox/action-tracker"
WHERE !completed AND contains(text, "due:")
SORT due ASC
```

## 자동 쿼리 — 프로젝트별 미완료

```dataview
TASK
FROM "inbox/action-tracker"
WHERE !completed
GROUP BY filter(file.tags, (t) => startswith(t, "#project"))
```

## Completed (Archive)

<!-- 완료된 액션은 여기로. 한 달 이상 된 건 분기 회고 시 정리. -->

---

<!--
이 파일이 비대해지면 분기마다 Completed 섹션을 잘라서 notes/archive/{quarter}-actions.md로.
-->
