# _CLAUDE.md — 볼트 운영 매뉴얼

이 파일은 이 볼트에서 작업하는 모든 Claude 세션이 가장 먼저 읽는 문서다. 이 볼트의 모든 읽기·쓰기를 구속하는 규칙을 담는다. 당신이 Claude라면, 다른 작업보다 먼저 이 파일을 따라야 한다.

> 프론트매터 키(`date`, `type`, `tags`, `ai-first` 등)는 영어로 유지한다. Obsidian, MCP 서버, Dataview 같은 도구가 표준 키를 기대하기 때문이다. 값과 본문은 한글로 쓴다.

## 1. 우선순위

이 파일이 스킬 기본값을 덮어쓴다. 이 파일이 침묵하는 영역에서만 스킬 기본값이 적용된다. 이 파일과 어느 스킬 문서가 충돌하면, 이 볼트 안에서는 이 파일이 이긴다.

## 2. AI-first 프리앰블 — 모든 노트의 첫머리

모든 노트는 프론트매터 직후에 `## For future Claude` 블록으로 시작한다. 3줄 구성:

```
## For future Claude

이 노트는 [YYYY-MM-DD]에 저장된 [주제]에 대한 [타입] 노트다. [핵심 목적].
[선택: 신선도 주의, 신뢰도 한정, 범위 제한.]
```

미래의 Claude 세션이 이 노트만 단독으로 끌어와도(주변 맥락 0인 상태) 이게 무엇이고 왜 쓰였는지 이해할 수 있도록 만드는 장치다.

## 3. 공통 프론트매터 — 모든 노트

모든 노트는 최소한 다음 YAML 프론트매터를 가진다:

```yaml
---
date: YYYY-MM-DD       # 생성일 또는 마지막 수정일
type: <노트-타입>       # 4번 섹션의 스키마 중 하나
tags: [<type>, ...]    # 타입을 태그에 반드시 포함; 소문자
ai-first: true         # 규칙 준수 플래그
---
```

`ai-first: true`는 준수 신호다. 이 플래그가 없는 노트는 레거시로 간주하고 재작성 대상으로 표시한다.

## 4. 타입별 추가 프론트매터 스키마

공통 블록 위에 다음 필드를 더한다.

| 타입 | 추가 필드 |
|---|---|
| `daily` | `mood: ""` (선택), `energy: ""` (선택) |
| `project` | `updated: YYYY-MM-DD`, `status: active\|planning\|completed\|archived\|on-hold`, `related-people: []`, `related-projects: []` |
| `person` | `updated: YYYY-MM-DD`, `role: ""`, `company: "[[Companies/...]]"`, `relationship: weak\|medium\|strong`, `last-interaction: YYYY-MM-DD`, `related-projects: []` |
| `idea` | `status: captured\|exploring\|graduated\|shelved`, `related-projects: []` |
| `task` | `status: in-progress\|done\|waiting\|cancelled`, `priority: high\|medium\|low`, `due: YYYY-MM-DD`, `related-projects: []`, `related-people: []` |
| `decision` | `related-projects: []`, `confidence: stated\|high\|medium\|speculation`, `sources: []` |
| `devlog` | `project: "[[Projects/...]]"`, `related-people: []` |
| `review` | `period-start: YYYY-MM-DD`, `period-end: YYYY-MM-DD`, `period: weekly\|monthly\|quarterly` |
| `adr` | `decision: ""`, `status: proposed\|accepted\|superseded`, `related-projects: []`, `supersedes: "[[Knowledge/ADR-...]]"` (선택) |

애매하면 `type: knowledge`로 두고, 노트가 자기완결적이도록 필요한 필드를 추가한다.

## 5. 신선도 마커 (recency markers)

외부 출처의 모든 주장에는 인라인 날짜와 출처를 붙인다:

```
- Mem0가 2,400만 달러 시리즈 A를 유치 (as of 2026-04, mem0.ai/blog/series-a)
- Anthropic이 네이티브 메모리 출시 (as of 2026-02, anthropic.com/news/memory)
```

패턴: `(as of YYYY-MM, source-url)`. URL은 그대로 보존 — 단축 금지, 의역 금지. 재검증 가능성이 핵심이다.

## 6. 신뢰도 (confidence)

사소하지 않은 주장에는 다음 중 하나를 붙인다:

- `stated` — 출처가 직접 인용 또는 주장한 것
- `high` — 독립적인 복수 출처가 일치
- `medium` — 단일 출처지만 그럴듯함
- `speculation` — 작성자의 추론, 출처 없음

인라인 형태: `(confidence: medium)`. 프론트매터 형태: `confidence: high`. 노트 전체의 신뢰도는 프론트매터에, 개별 주장 단위는 인라인에 적는다.

## 7. 위키링크 — 필수

모든 엔티티 참조는 `[[폴더/이름]]` 문법을 쓴다. 예:

- `[[People/Eugeniu Ghelbur]]`
- `[[Projects/Ubermensch]]`
- `[[Companies/Anthropic]]`
- `[[Knowledge/Bi-temporal-facts]]`

평문 이름은 그래프를 끊는다. 대상 스텁이 아직 없으면 **만든다** — 프론트매터와 프리앰블만 있는 최소 노트라도 만들어 링크가 해소되게 한다. 미래의 Claude는 링크 없는 곳을 건너갈 수 없다.

## 8. 전파(propagation) — 모든 쓰기는 여러 페이지를 건드린다

노트 하나만 단독으로 쓰는 것은 볼트 부패다. 의미 있는 쓰기 한 번에 다음도 같이 갱신한다:

- `Home.md` — 변경이 대시보드 관련일 때 (활성 프로젝트, 오늘의 초점, 미해결 질문)
- `Boards/` — 칸반에서 추적되는 상태가 바뀔 때
- `Daily/<오늘>.md` — 오늘 기록할 가치가 있는 사건일 때
- `index.md` — 새로운 노트 타입이나 카테고리가 도입될 때
- `log.md` — 의미 있는 쓰기마다 `YYYY-MM-DD HH:MM | actor | summary` 한 줄 추가

볼트는 그래프다. 쓰기는 파일 추가가 아니라 그래프 변형이다.

## 9. 명명 규칙과 스타일

- **헤더**: 자연스러운 한국어 문장체 (`## 무엇을 하는가`).
- **이모지**: 볼트 출력에 쓰지 않는다. 스킬에 포함된 명시적 UI 요소에서만 허용.
- **em-dash (`—`)**: 사용자에게 보이는 산문에 쓰지 않는다. 일반 하이픈에 띄어쓰기를 쓰거나 문장을 재구성한다.
- **날짜**: 메타데이터는 ISO `YYYY-MM-DD`. `오늘`, `어제`, `지난주` 같은 상대 표현은 메타데이터에 절대 쓰지 않는다.
- **태그**: 영문 소문자, 다단어는 kebab-case. 노트의 `type`은 항상 태그에 포함.
- **파일명**: 사람이 읽기 좋게. 일일 노트는 ISO 날짜 (`Daily/2026-05-06.md`).
- **YAML 문자열**: 특수문자나 선두 기호가 있으면 큰따옴표로 감싼다.

## 10. 안티패턴

| 패턴 | 문제 |
|---|---|
| `date: today` | 나중에 읽으면 의미 없음. `YYYY-MM-DD`를 쓴다. |
| 날짜 없는 단언 | "X가 1위" — 언제 1위인가? |
| 출처 URL 누락 | 재검증 불가. 감사 추적 단절. |
| 위키링크 대신 평문 이름 | 그래프 탐색 불가. |
| 구조 없는 산문 | 불릿과 헤더가 검색에 더 잘 잡힌다. |
| `ai-first: true` 누락 | 비준수 신호. 레거시 노트로 간주. |
| 고립 노트 | 모든 노트는 최소 한 노트와 양방향 또는 단방향 링크가 있어야 한다. |
| "위에서 언급한", "아래에서" | 자기완결적이지 않다. 미래의 Claude는 한 번에 한 노트씩 끌어온다. |

## 11. 폴더 지도

| 폴더 | 용도 | 기본 `type` |
|---|---|---|
| `Daily/` | 하루 한 파일, `YYYY-MM-DD.md`, 그날 일어난 일의 로그 | `daily` |
| `Projects/` | 활성/보관 프로젝트당 파일 하나 | `project` |
| `People/` | 사람당 파일 하나, 이름으로 | `person` |
| `Companies/` | 회사당 파일 하나 | `company` |
| `Ideas/` | 캡처된 아이디어. 준비되면 프로젝트로 졸업 | `idea` |
| `Tasks/` | 프로젝트 자체 목록에 묶이지 않는 단독 태스크 | `task` |
| `Dev Logs/` | 개발 일지, 기술 결정, 디버그 세션 | `devlog` |
| `Reviews/` | 주간/월간/분기 회고 | `review` |
| `Boards/` | 칸반 보드 (체크박스 마크다운 또는 Kanban 플러그인) | (혼합) |
| `Knowledge/` | 정제된 지속 지식: ADR, 원칙, 프레임워크 | `knowledge` 또는 `adr` |
| `Templates/` | 타입별 템플릿. 복사해서 쓰고 원본은 수정하지 않는다. | (템플릿) |

## 12. 루트 레벨 볼트 파일

- `Home.md` — 대시보드. 활성 프로젝트, 오늘의 초점, 최근 결정, 미해결 질문.
- `SOUL.md` — 정체성, 가치관, 일하는 방식, 장기 목표. "당신이 누구인가" 파일.
- `CRITICAL_FACTS.md` — 항상 참인 사실. 약 120 토큰 이하로 유지. 모든 Claude 컨텍스트에 로드된다.
- `index.md` — 노트 카탈로그. 자동 유지.
- `log.md` — 감사 기록. append-only.
- `SYNC.md` — Claude Code, Claude Desktop, claude.ai 웹과 이 볼트를 동기화하는 방법.
