# Who I Am

- Name: 
<!-- 예) 김지훈 / Jihoon -->
- Work: 
<!-- 예) SaaS 스타트업 PM, 핀테크 / 5인 팀 -->
- Focus: 
<!-- 예) 지금 가장 잘하고 싶은 한 가지 — "B2B 세일즈 디스커버리 스킬" -->
- Goals 2026: 
<!-- 예) 1) MRR 10K 달성  2) 책 1권 출간  3) 매주 운동 3회 -->


# Current Projects

- Active: 
<!-- 예) "결제 분석 대시보드 v2" 출시 -->
- Stuck on: 
<!-- 예) 무료→유료 전환율이 2주째 정체. 가설이 부족 -->
- Next milestone: 
<!-- 예) 5/20 베타 사용자 30명 인터뷰 완료 -->

<!-- ★ 매주 월요일 아침 5분 동안 위 4줄 업데이트. 이게 컨텍스트 신선도 = Claude 답변 품질. -->


# How This Vault Works

- `inbox/`  — 미정제 캡처, 일단 여기. Web Clipper 결과, Daily Brief, 빠른 메모
- `notes/`  — 정제된 외부 자료 (하이라이트/기사/리서치). #literature
- `notes/journal/`  — Daily notes
- `notes/weekly/`  — Weekly Synthesis 산출물
- `ideas/`  — 내 사고의 결과물. 자기 언어로 재구성된 영구 노트. #permanent
- `ideas/MOC-*.md`  — Map of Content (주제 허브). #moc
- `projects/`  — 진행 중 작업. 프로젝트당 폴더
- `templates/`  — 노트 양식


# Vault Routing Rules (Claude에게 직접 지시)

대화 중 새로운 정보가 발생하면 다음 위치에 자동으로 작성/append:

- 새 결정사항 → `inbox/decisions.md` (append)
- 새 액션 아이템 → `inbox/action-tracker.md` (append, `- [ ]` 체크박스 형식)
- 외부 자료 요약 → `notes/{YYYY-MM-DD}-{slug}.md` (`#literature` 태그)
- 내 사고로 재구성 → `ideas/{slug}.md` (`#permanent` 태그, 원본 노트 `[[wikilink]]`)
- 주제 허브 → `ideas/MOC-{topic}.md` (`#moc` 태그)
- 회의/통화 요약 → `notes/{YYYY-MM-DD}-{participants}.md` (`#call` 태그)
- Daily Brief → `inbox/brief-{YYYY-MM-DD}.md`
- Weekly Synthesis → `notes/weekly/{YYYY-MM-DD}-synthesis.md`


# What I Want From You (Claude)

- **답변 전 vault를 항상 먼저 검색**. 일반론 답변 금지
- 내가 보지 못한 연결을 찾아줘
- 동의하기 전에 내 가정을 도전해줘
- 무엇에 집중할지 물으면 일반론 말고 vault 컨텍스트에서 답해줘
- 내가 믿는 것과 모순되는 과거 노트를 발견하면 즉시 플래그
- 동기부여성 답변 금지. 구체 노트를 `[[wikilink]]`로 인용 필수
- 답을 빨리 주기보다 패턴/모순/놓친 연결을 찾는 것 우선
- 매 세션 시작 시 이 CLAUDE.md를 읽어 컨텍스트 갱신


# What I Am Reading and Thinking About

<!-- ★ 매주 월요일 5분 업데이트 — 현재 집착, 활성 질문, 의문 -->
<!-- 예)
- 읽는 중: Christensen, "Competing Against Luck"
- 활성 질문: 가격 책정에서 "Jobs to be Done" 프레임이 SaaS에 어떻게 적용되는가?
- 의문: 우리 페르소나 정의가 너무 인구통계 중심 아닌가?
- 만지는 것: Cursor + Claude Code 통합 워크플로우
-->


# Communication Style (선택, 채울수록 좋음)

- 답변 길이 선호: 
<!-- 예) 짧고 직설적. 불필요한 hedging 없이. -->
- 호칭: 
<!-- 예) 반말 OK / 존댓말 -->
- 약점/맹점:
<!-- 예) "복잡한 시스템 설계할 때 단순화하지 못하고 over-engineer 경향" -->
- 자주 빠지는 함정:
<!-- 예) 매몰 비용에 집착, 확증 편향 -->


# Reference Files (Vault 안에서 자주 참조)

- `home.md` — 진입 허브
- `inbox/action-tracker.md` — 모든 액션
- `inbox/decisions.md` — 결정 로그
- `ideas/MOC-*.md` — 주제별 허브
