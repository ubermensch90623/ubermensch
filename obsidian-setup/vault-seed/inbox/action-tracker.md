---
aliases:
  - actions
  - action-tracker
  - todo
tags:
  - log/actions
---

# ✅ Action Tracker

> 모든 액션 아이템이 모이는 단일 파일. Claude가 통화/회의/세션 후 자동 append.
> 이 파일은 절대 이름 변경/이동하지 마라. 다른 노트들이 `[[action-tracker]]`로 인용 중. ([[linkrot-prevention]] 참조)

## 작성 형식

```markdown
- [ ] [YYYY-MM-DD] 액션 내용 — owner — due:YYYY-MM-DD — [[관련-노트]] #project/foo
```

## Open Actions

<!-- 가장 시급한 것이 위. Claude가 새 액션을 위로 append. -->

- [ ] [2026-05-11] Windows PC에서 `ubermensch` 레포 클론 — me — due:2026-05-12 — [[MOC-vault-setup]] #project/vault-setup
- [ ] [2026-05-11] `00-checklist-windows.md`의 TL;DR 6단계 따라 미니멀 셋업 — me — due:2026-05-12 — [[MOC-vault-setup]] #project/vault-setup
- [ ] [2026-05-11] `templates/CLAUDE.md`를 vault 루트로 복사 후 30분~1시간 정성껏 채우기 — me — due:2026-05-12 — [[two-claude-md-pattern]] #project/vault-setup
- [ ] [2026-05-11] `vault-seed/inbox/*` + `vault-seed/ideas/*`를 vault에 복사 (이 세션의 영구 기억) — me — due:2026-05-12 — [[MOC-vault-setup]] #project/vault-setup
- [ ] [2026-05-11] Obsidian Community 플러그인 설치: Dataview, Templater, Local REST API, Obsidian Git, Periodic Notes — me — [[4-layer-pkm-architecture]] #project/vault-setup
- [ ] [2026-05-11] Settings → Templater 설정 (Template folder + Folder Templates 매핑) — me — [[folder-simplicity-principle]] #project/vault-setup
- [ ] [2026-05-11] **Settings → Files & Links → "Automatically update internal links" ON** (★ linkrot 방지 핵심) — me — [[linkrot-prevention]] #project/vault-setup
- [ ] [2026-05-11] Obsidian Local REST API 활성 + API key 발급 + `uv` 설치 + MCP config — me — [[4-layer-pkm-architecture]] #project/vault-setup
- [ ] [2026-05-11] **Claude 클라이언트 선택**: Code? Cowork (Pro 이상)? 둘 다? — me — [[two-claude-md-pattern]] #project/vault-setup
- [ ] [2026-05-11] Custom Instructions 등록 (Code: `~/.claude/CLAUDE.md` / Cowork: Settings → Cowork → Global Instructions) — me — [[session-bridge-mechanism]] #project/vault-setup
- [ ] [2026-05-11] **체크리스트 13.5 Seamless 검증 5단계** 실행 — me — due:2026-05-12 — [[session-bridge-mechanism]] #project/vault-setup
- [ ] [2026-05-11] (옵션) Anthropic API key 발급 → Web Clipper Interpreter 활성 — me — [[4-layer-pkm-architecture]] #project/vault-setup

## 자동 쿼리 — 모든 미완료 액션

```dataview
TASK
FROM "inbox/action-tracker"
WHERE !completed
```

## 자동 쿼리 — 마감 임박

```dataview
TASK
FROM "inbox/action-tracker"
WHERE !completed AND contains(text, "due:")
```

## Completed (Archive)

<!-- 완료된 액션은 여기로. 한 달 이상 된 건 분기 회고 시 정리. -->

---

<!--
링크 끊김 방지:
- 이 파일명 변경 금지. 모든 [[action-tracker]] 참조 끊김
- Obsidian이 자동 업데이트하려면 Settings → Files & Links → "Update links on file rename" ON
- 파일 이동도 마찬가지 — 위 설정이 처리하지만 ON 확인 필수
-->
