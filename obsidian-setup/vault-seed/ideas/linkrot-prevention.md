---
aliases:
  - linkrot
  - link integrity
  - broken links
  - connection preservation
created: 2026-05-11
tags:
  - permanent
  - status/evergreen
---

# Linkrot Prevention — 연결점이 풀어지지 않게

> "어제 옵시디언 연결점 풀어진 거 보고 놀랐다" — 실제 사용자 경험.
> Linkrot은 wikilink가 끊기는 현상. 방치하면 [[cognition-vs-organization|vault가 묘지로]] 향하는 가장 빠른 길.

## 왜 링크가 풀어지나 (원인)

| 원인 | 결과 | 빈도 |
|---|---|---|
| **파일 이름 변경** (OS 파일 탐색기로) | 모든 `[[old-name]]` 깨짐 | 매우 흔함 |
| **파일 이동** (다른 폴더로) | 경로 기반 링크 깨짐 | 흔함 |
| **파일 삭제** | 모든 인용처가 빨간색 | 흔함 |
| **Obsidian "Update links on rename" 비활성** | rename해도 링크 자동 업데이트 안 됨 | 셋업 실수 |
| **동기화 충돌** | `file (1).md` 같은 중복 파일 생성, 원본 링크는 새 파일 못 찾음 | Google Drive 멀티 디바이스 시 |
| **Wikilink 오타** | 처음부터 끊긴 링크 | 사람 실수 |
| **Aliases 미설정** | 별명으로 인용한 게 끊김 | 자주 |
| **Templater 잘못된 렌더링** | `<% tp.file.title %>`이 빈 문자열로 → 헤딩 없는 파일 | 드물지만 치명적 |

## 6중 방어선

### 1. Obsidian 설정 (필수)

- [ ] **Settings → Files & Links → "Automatically update internal links"**: **ON** (★ 가장 중요)
- [ ] **Settings → Files & Links → "Use [[Wikilinks]]"**: **ON**
- [ ] **Settings → Files & Links → "New link format"**: **Shortest path when possible**
- [ ] **Settings → Files & Links → "Detect all file extensions"**: OFF

이 4개 중 첫 번째가 핵심. 켜져 있으면 Obsidian 안에서 rename 시 모든 인용처가 자동 갱신.

### 2. Aliases — 모든 핵심 노트에 별명 부여

frontmatter:
```yaml
aliases:
  - decisions
  - decisions log
  - 결정 로그
```

효과: 파일명을 `decisions.md`로 두든 `decision-log.md`로 두든 `[[decisions]]`로 인용 가능. 이름이 진화해도 인용이 안 깨짐.

이 키트의 모든 idea/inbox 노트는 aliases 보유.

### 3. OS 파일 시스템에서 rename/move 금지

**규칙**: vault 안의 파일은 **Obsidian 안에서만** 이름 변경/이동.
- File Explorer로 rename → 링크 깨짐 (Obsidian이 모름)
- Git mv → 동일하게 깨짐
- Obsidian "Rename" 명령 → 자동 업데이트 작동

### 4. 동기화 충돌 모니터링

Google Drive는 충돌 시 `file (1).md`, `file conflict copy.md` 생성. 이게 vault 어딘가에 누적되면 원본은 변하지 않았는데 새 파일이 생겨 링크가 분기.

- [ ] 주 1회 vault 루트에서 검색: `conflict copy` / `(1)` / `(2)` 같은 파일명
- [ ] 발견 시 즉시 비교 후 삭제 또는 머지
- [ ] 더 안전한 방법: Obsidian Sync($5/월) 사용 — 충돌 처리가 명시적

### 5. Orphan / Broken Link Dataview (자동 추적)

`home.md` 또는 `MOC-vault-setup.md`에 다음 쿼리 추가:

```dataview
TABLE WITHOUT ID
  file.link AS "Note",
  length(file.outlinks) AS "Outlinks",
  length(file.inlinks) AS "Inlinks"
FROM ""
WHERE !contains(file.path, "templates") AND !contains(file.path, ".obsidian")
  AND length(file.inlinks) = 0
SORT file.mtime DESC
```

→ 아무도 인용 안 하는 orphan 노트 목록. 매주 점검.

깨진 wikilink 찾기:
```dataview
LIST
FROM ""
WHERE !contains(file.path, "templates")
FLATTEN file.outlinks AS outlink
WHERE !outlink.file
```

### 6. 주간 점검 의식 (5분, 월요일)

매주 월요일 [[CLAUDE.md|CLAUDE.md 갱신]]과 함께 5분:
1. home.md / MOC-vault-setup.md 열기
2. Orphan 쿼리 결과 보기 → 인용처 추가하거나 archive
3. 깨진 wikilink 쿼리 → 빨간 글씨 모두 수정
4. 동기화 충돌 파일 검색 → 정리

## Claude에게 시키는 자동화

CLAUDE.md의 라우팅 규칙에 추가:
- 새 파일 생성 시 항상 frontmatter에 `aliases` 포함
- 새 wikilink는 가능하면 aliases를 사용 (파일명 변경에 강건)
- 매주 월요일 Weekly Synthesis 실행 시 orphan/broken-link 점검 포함

## "어제 연결점 풀어진 사건" 회피 시나리오

가능성 높은 원인 추적:
1. **Google Drive 충돌** — 다른 기기에서 같은 파일 편집 후 동기화 충돌
2. **OS rename** — 파일 탐색기로 이름 바꿈
3. **Obsidian 설정 OFF** — Update links 기능 비활성
4. **vault 폴더 이동** — vault 자체 위치 변경

→ 6중 방어선 1, 2, 3, 4번이 이걸 모두 막음. [[action-tracker]] 7번 액션이 핵심.

## 관련 노트

- [[MOC-vault-setup]] (주제 허브)
- [[folder-simplicity-principle]] (폴더 이동이 링크 깨는 메커니즘)
- [[cognition-vs-organization]] (linkrot이 vault를 묘지로 만드는 경로)
- [[session-bridge-mechanism]] (bridge의 wikilink가 끊기면 seamless 실패)
- [[two-claude-md-pattern]] (CLAUDE.md 안의 wikilink 보호)

## 출처

- 이 키트의 [[decisions]] 라운드 — 사용자 보고 "옵시디언 연결점 풀어진 거 보고 놀랐다"
- Obsidian 공식 docs (Files & Links 설정)
- Dataview docs (orphan/broken-link 쿼리 패턴)

## 미해결

- Obsidian Sync vs Google Drive 충돌율 정량 비교 (체감만 있고 데이터 없음)
- 큰 vault에서 orphan 쿼리가 느려질 가능성 — 인덱싱 최적화 필요?
- AI가 자동으로 orphan을 재연결하는 시스템 가능한가? (예: 의미 유사도로 자동 wikilink 제안)
