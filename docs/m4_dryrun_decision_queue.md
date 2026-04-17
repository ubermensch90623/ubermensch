# M4 Dry-Run — 사용자 복귀 시 판결 대기 항목

> **상태**: 2026-04-18 09:10 기준 M4 진입 불가 (M3.5 게이트 RESET_CANDIDATE)
> **이유**: `data/restored/` 에 실제 캠코·수협 기출 원문 인용 0건
> **해소 조건**: B2 + B3 해소 + ebook 구매 경연 결과

---

## 1. 사용자 복귀 시 AskUserQuestion 발동 안건 (C-4 경연)

### Q1. RESET vs 증분 진행 (P12 권장: GATED 증분)
- (A) M3.5 RESET → M0 재시작 (과감, 모든 자료 B2 해소 후 재수집)
- (B) **GATED 증분 (Recommended)** — 현 상태 유지, B2·B3 해소되는 자료부터 restored 로 승격
- (C) 하이브리드 — UI·파이프라인·문서 유지, 데이터만 재수집

### Q2. ebook 구매 경연 — P4·P6 판정 상충
- (A) 번들 A: 해커스공무원 경제학 15개년 + 해커스공기업 NCS 2026 = 66,600원
  - P4 권장 / P6 반박: "해커스공무원 7급 ≠ 캠코 5급(행시급) 난이도 미스매치, 국제금융 비중 부족"
- (B) 번들 B: **정병열 경제학 미시+거시 + 해커스공기업 NCS** = 예상 85,000원 내외
  - P6 제안 / P4 우려: 정병열은 난이도 상, 종환 진도 2-3/5 로는 과중
- (C) 단계 매입: 해커스 NCS 2026 이북 (13,300원) 만 즉시, 경제학은 오프라인 서점 방문 후 종환 직판
- (D) 보류 — 보유 자료만 사용

### Q3. 블로커 B2 (캠코·수협 공식 PDF 다운로드) 실행 방식
- (A) 종환 브라우저 직접 다운로드 → harness/data/low_confidence/upload/ 저장 → P1 재파견
- (B) Claude_in_Chrome MCP 세션으로 Lead Agent 가 수행 (사용자 로그인 정보 요구)
- (C) Perplexity Deep Research 유료 구독 (신규 지출) — P15 스카우트 결과 비권장

### Q4. 블로커 B1 (data.go.kr 인증키)
- (A) 종환이 1분 소요 발급 → 환경변수 등록 → P2 재파견
- (B) 현 세션에선 포기, P14 병합 전략 (P7 §5 재파견 요청)

### Q5. 수협 선택과목 선정 (P1 HIGH confidence 5과목: 민법/회계학/경영학/수협법/상업경제)
- (A) **경영학 (Recommended)** — 캠코 경제와 컨텐츠 역출 가능, 시너지 최고
- (B) 상업경제 — 고교 과정, 난이도 평이 (P5 후기 0건 경고)
- (C) 회계학 — 투자자산운용사 자격 연계
- (D) 수협법 or 민법 — 법령 암기 노선

### Q6. CLAUDE.md 캠코 배점 수치 (60+20) 격리 처리 방식
- (A) **격리 태그 유지 (Recommended, 이미 적용)** — 정보 보존, 하류 참조 금지
- (B) 삭제 (정보 손실 리스크)
- (C) 복구 — 공식 PDF 수신 후 재확인 전 되돌림 금지

---

## 2. 현재 확정 팩트 (사용자 공유 가능 · C-0 통과)

- 캠코 2026 신입 103명, 5급 경제 19명, 접수 4/3~4/17, 필기 5/9(토), 최종 7월 (독립 4개 언론)
- 수협 2026 상반기 233명 (일반관리 209+보훈10, 기술·기능 14), 필기 5/16 서울, 최종 6/6 (독립 4개 소스)
- 수협 일반관리계 필기 = 인성 + NCS + 선택 1과목 (민법·회계학·경영학·수협법·상업경제)
- NCS 공식 10영역 (산업인력공단 1차 소스)
- 학술 5편 HIGH + KRIVET 보고서 1건 HIGH

## 3. 현재 격리 (하류 참조 금지) — 공식 재검증 필요

- 캠코 경제 60문항 80점 + NCS 20문항 20점 (CLAUDE.md 수기메모, 공식 PDF 재확인 실패)
- 캠코 출제분야 꾸르노·AC·MC·기간간최적소비·IS·PPP·리카도·먼델플레밍 (2023 후기 2차, 2024 NCS 도입 후 미상)
- 수협 NCS 100문항 + 전공 50문항 (네이버블로그 WebFetch 차단, 2026 공고 원문 재확인 필요)
- 수리 변별력 최고 → 캠코 외삽 (P13 원표본은 범용)
- 금융공공기관 3~5영역 축소 운영 → 캠코 외삽 (P3 표본 3기관, HF 2건 중복)
- P4 번들 "해커스공무원 7급" 난이도 매칭 (P6 sustain)

## 4. 세션 종료 시점 스냅샷

- 저장소: `Desktop/ubermensch/` 브랜치 `claude/fix-handwriting-recognition-J9xJq`
- 신규 디렉토리: `harness/` (backend·ui·data·tests)
- 테스트: 77 PASS
- 서버: 127.0.0.1:8765 (Python http.server)
- UI: dark 테마, 3패널 반응형, NaN 없음
- 에이전트: 기존 12종 (P1-P11+SC1/2) + P12 CEO 신규

## 5. 다음 세션 수령자 체크리스트

1. `git fetch origin claude/fix-handwriting-recognition-J9xJq && git checkout` 동일 브랜치
2. `python -m unittest discover tests && python -m unittest discover harness/tests` (77 PASS 확인)
3. `docs/session_log.md` + `docs/restoration_ecosystem_map.md` 순서로 읽기
4. Q1~Q6 사용자 판결 수령 → C-4 경연 기록 `docs/gyeongyeon/YYYY-MM-DD_M4_decisions.md`
5. 판결 후 M4 진입
