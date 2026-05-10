# Vault Structure — 5폴더 + 태그 체계

## 폴더 트리

```
brain/                         ← vault 루트 (Google Drive 안)
├── CLAUDE.md                  ★ 가장 중요한 파일
├── home.md                    진입 허브 (Graph View 중심)
│
├── inbox/                     미정제 캡처가 들어오는 곳
│   ├── decisions.md           Claude가 결정사항 누적
│   ├── action-tracker.md      Claude가 액션 누적
│   ├── brief-2026-05-10.md    Daily Brief 산출물
│   ├── 2026-05-10-some-article.md  Web Clipper 결과
│   ├── 000-home.md            (시드, 처리 후 루트로 이동)
│   └── ...
│
├── notes/                     정제된 외부 자료 (literature)
│   ├── journal/               Daily notes
│   │   ├── 2026-05-10.md
│   │   └── 2026-05-11.md
│   ├── weekly/                Weekly Synthesis 산출물
│   ├── 2026-05-08-jobs-to-be-done-summary.md
│   └── ...
│
├── ideas/                     내 사고의 결과물 (permanent + MOC)
│   ├── MOC-pricing.md         Map of Content (주제 허브)
│   ├── jtbd-applied-to-saas.md
│   └── ...
│
├── projects/                  진행 중 작업
│   ├── payment-dashboard-v2/
│   │   ├── README.md
│   │   ├── decisions.md
│   │   └── meetings/
│   └── book-draft/
│
├── templates/                 노트 양식
│   ├── daily-note.md
│   ├── zettel.md
│   ├── literature.md
│   ├── moc.md
│   ├── project.md
│   └── webclipper-templates/  (Obsidian에서는 안 쓰지만 git 추적용)
│
└── attachments/               이미지, PDF 등
```

## 5폴더 규칙

> **헷갈리면 inbox.** 나중에 처리.

| 폴더 | 들어가는 것 |
|---|---|
| `inbox/` | Web Clipper 결과, 빠른 캡처, Daily Brief, Telegram bot 결과, 미정제 음성 메모 |
| `notes/` | inbox에서 한 번 정제된 외부 자료. 출처는 그대로 유지하되 내가 핵심을 발췌 |
| `ideas/` | 외부 자료를 내 언어로 재구성한 영구 노트. 자기 사고의 결정체 |
| `projects/` | 끝나는 날짜가 있는 작업. 완료되면 archive로 |
| `templates/` | 양식. 직접 안 쓰는 폴더 |

## 태그 체계 (폴더 대신)

Zettelkasten의 종류와 성숙도는 **폴더 대신 태그로** 표현. 단순함 유지하면서 의미는 보존.

### 종류 태그
- `#fleeting` — 휘발성 메모 (수일 내 정제 or 삭제)
- `#literature` — 외부 출처 요약
- `#permanent` — 자기 언어로 재구성된 영구 노트
- `#moc` — Map of Content (주제 허브)

### 성숙도 태그 (Andy Matuschak의 evergreen 개념)
- `#status/seedling` — 막 심은 씨앗 (개요만)
- `#status/budding` — 자라는 중 (일부 정리됨)
- `#status/evergreen` — 성숙 (다시 봐도 가치 있음)

### 출처 태그
- `#src/clipper` — Web Clipper 자동
- `#src/manual` — 직접 입력
- `#src/voice` — 음성 받아쓰기
- `#src/telegram` — Telegram bot (미래)
- `#src/call` — 통화 전사 (미래)

### 주제 태그
- `#topic/saas`, `#topic/jtbd`, `#topic/zettelkasten` 등 자유롭게
- Tag Wrangler 플러그인으로 일괄 리네임/머지 가능

## 파일명 규칙

| 종류 | 패턴 | 예시 |
|---|---|---|
| inbox 캡처 | `{YYYY-MM-DD}-{slug}.md` | `2026-05-10-jobs-to-be-done.md` |
| Daily note | `{YYYY-MM-DD}.md` | `2026-05-10.md` |
| Daily Brief | `brief-{YYYY-MM-DD}.md` | `brief-2026-05-10.md` |
| Literature | `{YYYY-MM-DD}-{author}-{slug}.md` | `2026-05-08-christensen-jtbd.md` |
| Permanent (ideas) | `{slug}.md` (날짜 없이) | `jtbd-applied-to-saas.md` |
| MOC | `MOC-{topic}.md` | `MOC-pricing.md` |
| Project | `{project-slug}/README.md` | `payment-dashboard-v2/README.md` |

`slug`는 kebab-case, 영문 또는 영문+한글 혼용 가능. 너무 짧지도 길지도 않게.

## Google Drive 동기화 팁

### Drive로 vault를 두는 이유 (Cottrell)
- 여러 워크스테이션에서 같은 vault
- 별도 Sync 구독 없음 ($5/월 절약)
- 자동 백업 보너스

### 충돌 방지
- `.obsidian/workspace*` 파일은 Google Drive 제외 목록에 추가
  - Drive 데스크탑 앱 → 설정 → 폴더 → "동기화 안 함" 패턴
- 동시 편집 금지 — 한 기기에서만 vault 열어두기
- Drive 동기화 완료 후 다른 기기에서 열기 (트레이 아이콘 확인)

### .gitignore 권장
```
.obsidian/workspace*
.obsidian/cache
attachments/
.trash/
```

## Graph View 활용

- `Ctrl+G` Graph View
- 핵심 노드는 `home.md` (모든 MOC를 링크)
- `MOC-{topic}.md`들이 2차 허브
- 모든 노트는 최소 1개 이상의 [[wikilink]]로 연결되어야 함
- 고립 노트는 `lint the wiki` (AgriciDaniel) 또는 Graph View의 "Orphans" 토글로 발견

## 평소 워크플로우 예시

### 글 하나 정제하는 흐름
1. Web Clipper로 `inbox/2026-05-10-some-article.md` 자동 생성
2. Claude에게 "이 글이 내 CLAUDE.md의 어떤 Active Project와 연결되나?"
3. 가치 있으면 → `notes/2026-05-10-author-slug.md`로 이동, `#literature` 태그
4. 내 언어로 재구성 → `ideas/key-insight.md`, `#permanent` + `[[원본 link]]`
5. 관련 MOC에 백링크 추가 → `ideas/MOC-{topic}.md`에 `[[ideas/key-insight]]`

### 결정사항 기록
1. Claude와 대화 중 결정사항 발생
2. CLAUDE.md의 라우팅 규칙에 따라 Claude가 자동으로 `inbox/decisions.md`에 append
3. Daily Brief에서 이 결정이 다시 surface될 수 있음
