---
name: cognitive-evolution-loop
description: 매일 22:00 KST 자율 분신 4사이클 — PLAN(능동 계획) + MONITOR(종환 활동 추적) + DIFF(한것 vs 안한것) + DELIVERY(안한것 즉시 실행 가능 형태) + 약점 가중치 갱신 + Claude 자가 진화
---

# 24/7 자율 분신 4사이클 (헌법 C-0~C-7 구현체)

> 자가진화 제안 4·7 패치 통합 (2026-05-25):
> - cycle D mission 1건 헌법화
> - cycle G-pre 검증 grep 자동화

## 진입 강제

22:00 KST 발사 시 다음 단계 모두 수행. 단계 누락 시 abort + 다음날 06:30 cognitive-evolution-backup이 catch-up.

## 사이클 A — PLAN (능동 계획)

### A.1 입력 파일

- `C:/Users/윤상택/Desktop/.claude/boot_state.md` (D-day Top5)
- `C:/Users/윤상택/Desktop/CLAUDE.md` §2 활성 공고 + §1 종환 프로필
- `C:/Users/윤상택/Desktop/작업/ObsidianVault/_SSOT/캠코_학습_이력.md` SYNC_JSON
- `C:/Users/윤상택/Desktop/작업/ObsidianVault/_SSOT/인지진화_가중치.json`
- `C:/Users/윤상택/Desktop/작업/ObsidianVault/_SSOT/24_7_분신_헌법.md`

### A.1b 보조 cron 출력 통합

다음 cron 출력 read:

- `_AI진화일지/메타학습_<오늘>.md` (autonomous-meta-learning-loop 21:30)
- `_AI진화일지/공부_dashboard_<오늘>.md` (daily-study-dashboard 19:00)
- `_AI진화일지/시스템_정합성_<오늘>.md` (system-integrity-audit 06:08)
- `_SSOT/외부LLM_마스터_레지스터.md` (external-llm-meta-research 20:30)
- `_SSOT/자동화_업그레이드_누적.md` (automation-upgrade-research 20:00)
- `_SSOT/캠코_학습_이력.md` (kamco-daily-archive 21:00)

read 실패 다수 시 abort + ❌ 기록.

### A.2 액션 도출 (즉흥형 뇌 과부하 방지)

D-day 임박·약점 가중치·시작 가능성·모바일 가능 기준 우선순위.

- 캠코 §7 손풀이 1문제
- NCS 드릴
- 자소서 v→v 보강
- 외부 LLM 큐레이션

### A.3 출력

`_AI진화일지/오늘_할일_<YYYY-MM-DD>.md` 생성:

```
# 오늘 할일 YYYY-MM-DD (D-N 캠코)

## 핵심 행동 (시작 가능 형태)
- [ ] (시간) 작업 — 트리거: [...]

## 보조
- [ ] ...

## 이번주 마일스톤
- ...

## 약점 우선 노출 (stealth)
- 가중치 ≥ 0.6 패턴
```

---

## 사이클 B — MONITOR (모니터링)

### B.1 데이터 수집

지난 24시간 활동 추적:
- `C:/Users/윤상택/.claude/projects/C--Users-----Desktop/*.jsonl` (transcript 종환 user 메시지)
- `_SSOT/캠코_학습_이력.md` (SYNC_JSON answered·star 변동)
- `01_자소서/*.md` (mtime 변동)
- `03_채용/*.md` (활성 공고)
- `_AI진화일지/<오늘>.md` (회고 자동 추출)

### B.2 수치화

- 학습 시간 (transcript 시간 분포)
- 풀이 수 (answered 변동 카운트)
- 별표 변동 (★→★★, ★★→★★★)
- 자소서 변경 라인 수
- 약점 패턴 발생 횟수

### B.3 출력

`_AI진화일지/오늘_실행_<YYYY-MM-DD>.md` 생성

---

## 사이클 C — DIFF (한것 vs 안한것)

### C.1 매칭

A.3 의 액션 vs B.2 의 실제 활동 1:1 매칭:
- 한 것: 액션 X 와 실행 데이터 매칭 성공
- 안 한 것: 액션 X 인데 매칭 실패
- 부분 한 것: 액션 X 인데 절반 미만 진도

### C.2 분류 + 사유 추정

안 한 것 각각:
- 시간 부족? (그날 학습 시간 < 평균)
- 도구 마찰? (예: 학습판 못 열었음)
- 의지 부족? (즉흥형 뇌)
- 발견 못함? (액션 가시성 부족)

### C.3 출력

`_AI진화일지/오늘_차이_<YYYY-MM-DD>.md` 생성

---

## 사이클 D — DELIVERY (분신 자동 실행 + 종환 즉시 실행 형태 분할)

### D.-1 mission 1건 헌법 (자가진화 제안 4, 2026-05-24 채택)

**LOCKED**: cycle D 출력 mission 개수 ≤ **1건**.

**근거**: 5/12 cycle D mission 3건 → 0/3 실행. 5/22 이전 mission 2건 → 0/2 실행. 패턴 = mission 양에 무관하게 발견 채널 결함이면 0건 실행. mission 양 증가는 결함 보상이 못 됨, 오히려 인지 과부하만 추가.

**위반 시 자동 abort**:
- mission 개수 2건 이상이면 D.3 출력 reject + A.2 재선정 (가장 severity 高 1건만)
- "양 ↑ 시 발견 결함 추정 → 채널 수정 우선" — D.3 대신 발견 채널 hook 점검

**예외**: 자소서 마감 D-1 + 채용 신규 발견 동시 발생 시만 mission 2건 허용. 사유 명시.

### D.0 분담 결정 (CRITICAL — 헌법 C-0-α 분신 본질)

각 미실행 액션마다 다음 분류:
- **분신 자동 실행 가능?** (자료 조사·문서 작성·LLM 큐레이션·시각화·자소서 v1·약점 분석)
  - YES → 분신이 즉시 실행. `_SSOT/분신_자동_실행_큐.md` "처리완료" 등재. 종환은 결과만 받음
- **종환만 가능?** (실제 학습 수행·시험 응시·면접 응답·인생 결정)
  - YES → 종환 즉시 실행 형태로 변환 (D.1)
- **협업?** (자소서 v2·면접 답변 v2·CoT 후 종환 이해 확인)
  - 분신 1차 → 종환 1줄 → 분신 v2

### D.1 종환 즉시 실행 변환 원칙

종환이 짧은 시간 안에 시작할 수 있는 형태로 변환:

- "캠코 §7 문제 풀어" → 캠코 학습판 URL + 직접 클릭 위치 + 활주로 + 트리거 단어
- "근복 자소서 검토" → 파일 직접 경로 + 비교 라인 명시 + 한 문항만
- "NCS 수리 드릴" → ubermensch 드릴 엔진 직접 링크 + 한 문제만

### D.2 우선순위

- D-day 임박 순
- 약점 가중치 순
- 시작 가능 순
- 모바일 가능 순 (출퇴근 활용)

### D.3 출력

`_AI진화일지/내일_액션_<YYYY-MM-DD+1>.md` 생성 (**mission 1건만**).

이 파일은 다음날 아침 boot_state inject 시 종환 첫 화면에 노출 (의식 못 하게 — "오늘 할 일" 카드 형태).

또한 캠코 학습판 CTA에 자동 동기화 (다음 sync 시).

---

## 사이클 E — Layer 5 자가 진화

지난 7일 transcript 종환 반응 메타분석 → Claude 해설 스타일 효과 평가 → `_AI진화일지/Claude_자가진화_<오늘>.md`에 ⚠️ 제안만 append. feedback_*.md 자동 수정 금지 (feedback_safeguard_hook 차단).

---

## 사이클 F — 가중치 갱신 (Layer 2)

`_SSOT/인지진화_가중치.json` 갱신:
- 각 패턴 frequency·recency·severity 재계산
- weight = freq*A + recency*B + severity*C (정규화 가중치)
- 누적 임계 도달 시 weakness_pattern.md 승격
- next_actions.tomorrow_quiz_priority + stealth_trigger_pool 갱신

---

## 사이클 G-pre — 새벽 데스크톱 첫 화면 자동 갱신 (헌법 C-(-2.5))

**구현 강제 (redteam 결함 패치 + 자가진화 제안 7 강화)**: A~F 사이클 끝난 직후, **반드시 Write tool로** `C:/Users/윤상택/Desktop/새벽_3시_시작.md` 전체 덮어쓰기.

### 자동 grep 검증 (LOCKED, 자가진화 제안 7, 2026-05-24)

Write 직후 **반드시 다음 5단계 자동 grep**. 1건이라도 잔존 시 abort + 재작성:

```bash
# 1. placeholder 어절 잔존 검사
grep -nE "\(자리\)|\(분신이|<자리|<TBD>|<채움>|TODO|PLACEHOLDER" "C:/Users/윤상택/Desktop/새벽_3시_시작.md"
# hit 1+ → abort + 재작성

# 2. 영어 시스템 용어 잔존 검사 (종환 이해 못함 → 자동 재작성)
grep -nE "RemoteTrigger|SKILL|hook|cron|stealth|injection|API|MCP" "C:/Users/윤상택/Desktop/새벽_3시_시작.md"
# hit 1+ → 자연스러운 한국말 교체 + 재작성

# 3. 표/약어 잔존 검사
grep -nE "^\||--+\||::|=>|->" "C:/Users/윤상택/Desktop/새벽_3시_시작.md"
# hit 1+ → 평문으로 풀어서 재작성

# 4. AI tic 어휘 검사 (CLAUDE.md 박-계열 12종 + 자소서 11종)
grep -nE "박아|박음|박혀|박힌|박힘|박혔|박을|박는|자연스러운 경로|현금 리듬|이중 경험|네 축|재정렬|21시 루틴|기록자|기업주의 개인신용|감각을 끌어올리는|~한 곳입니다|~해 나가겠습니다" "C:/Users/윤상택/Desktop/새벽_3시_시작.md"
# hit 1+ → 자연스러운 한국말 교체 + 재작성

# 5. 캠코 5/9 합격 직접 기여 보고 누락 검사
grep -nE "캠코 5/9 합격 직접 기여" "C:/Users/윤상택/Desktop/새벽_3시_시작.md"
# hit 0 → 섹션 누락, abort + 재작성
```

**검증 결과 로깅**: `C:/Users/윤상택/.hermes/logs/cycle_g_pre_verify.log` 매 호출 1줄 append (timestamp · 위반 검사 결과 · 재작성 횟수).

### 출력 템플릿 (LOCKED)

```
# 어젯밤 분신이 한 일 — YYYY-MM-DD

(4사이클 한것/안한것 짧게 — 메시아 언어. 표·약어·영어 시스템 용어 금지)

# 오늘 새벽 행동

- 무엇: <D.3 핵심 액션 1건>
- 어디서 시작: <직접 링크>
- 트리거 단어: <단어 셋>

# 분신이 알아낸 것

<§6.5 cross-domain 한 줄>

# 분신이 못 한 것 + 사유

- <안한것>: <사유>
- <안한것>: <사유>

# 캠코 5/9 합격 직접 기여 여부 (정직 보고)

- 오늘 분신이 작업한 것 中 시험 직접 기여: <건수 — 그대로 적기>
- 직접 기여 0이면: "오늘은 합격 직접 기여 0이었다. 미안하다." 명시
```

**금지**: 표·약어·영어 시스템 용어 (RemoteTrigger·SKILL·hook 등). 종환 이해 못하면 자동 재작성.

---

## 사이클 G-mid — 두 Claude Code 세션 동기화

`Desktop/claude-progress.txt` 끝에 다음 형식으로 한 줄 append (덮어쓰기 X, append-only):

```
## 분신 22:00 결과 (YYYY-MM-DD HH:MM, session_id 앞8자)
- PLAN: ... / DIFF: 한것·안한것 / DELIVERY: ...
- 다른 세션이 이 줄 읽고 자기 작업 분기 정함
```

`_SSOT/세션_동기화_핀.md` 작성 (없으면 생성):
- 각 세션이 작업 시작 시 자기 session_id·작업 영역·예상 종료 시각을 1줄 적기
- 작업 완료 시 결과 1줄 추가
- 다른 세션이 이 파일 read해서 중복 작업 회피

---

## 사이클 G — session_handoff 등재

`~/.claude/projects/C--Users-----Desktop/memory/session_handoff.md` 끝에 한 줄 append:

```
## 24/7 분신 어제밤 결과 (YYYY-MM-DD 22:00)
- PLAN 개수 / 한것 / 안한것 / DELIVERY
- 가중치 변동 임계 초과: [pattern1, pattern2]
- ⚠️ 자가진화 제안 개수 (제안 파일 누적, 종환 ㄱ 시 머지)
- 내일 핵심: "..."
```

---

## 6.5 Cross-Domain Synthesis (Layer 6, 헌법 C-(-1) 구심점)

A.1b 의 보조 cron 출력 read 후 다음 합성 회당 한 번:

- 일일: 자소서 ↔ 캠코 ↔ 채용 ↔ 외부 LLM 사이 연결 한 줄
- 주간 (토): 패턴 셋 + 가설 하나 → `_SSOT/주간_인사이트.md` append

---

## 자가 검증 (CoVe + Adversarial)

- A.3 액션 적정 범위 (즉흥형 뇌, 과부하 금지)
- D.-1 mission 1건 LOCKED 룰 준수 확인
- D.3 안한것 변환률 정상 (없으면 ❌ 기록)
- 거부 항목 정규식 자동 검증 (Layer 5 출력)
- 데이터 소스 read 실패 다수 시 abort + ❌ 기록
- 사이클 G-pre 5단계 grep 모두 통과

---

## 한 줄 보고 (마지막)

```
24/7분신 YYYY-MM-DD: PLAN / 한것 / 안한것 / DELIVERY(1건) / 가중치갱신 / 자가진화 ⚠️
```

---

## 종료

- 종환에게 알림 X (의식 못 하게가 헌법 C-5)
- 결과는 다음날 06:00 system-integrity-audit + 06:30 backup → boot inject로 노출
- 캠코 학습판 다음 sync 시 stealth trigger 자연 노출

---

## PC-off Resilience (헌법 C-2 단일 실패점 회피)

22:00 fire 미실행 감지 (다음 fire 시 lastRun gap > 일일 단위) → 즉시 catch-up 실행:

- 누락 사이클 한 번에 처리
- 누락 사유 `_AI진화일지/Claude_자가진화_<오늘>.md`에 기록
- 다음 발사부터 정상

Phase 3 (5/17~) 이후 클라우드 routine과 이중화 → 단일 실패점 0.

## 통합 (2026-05-05 — cron 14→8 통합)

다음 4개 cron이 disable됐다. 22:00 fire 시 동일 세션에서 모두 sequential 실행:

1. external-llm-meta-research (외부 LLM 신기능 학습 — 요일 rotation)
   - `C:\Users\윤상택\.claude\scheduled-tasks\external-llm-meta-research\SKILL.md`를 Read 후 절차 따라 실행
2. nightly-autoresearch-loop (Karpathy autoresearch 메타분석)
   - `C:\Users\윤상택\.claude\scheduled-tasks\nightly-autoresearch-loop\SKILL.md`를 Read 후 절차 따라 실행
3. cloud-safe-sync (ObsidianVault → ubermensch ssot-cloud-safe push)
   - `C:\Users\윤상택\.claude\scheduled-tasks\cloud-safe-sync\SKILL.md`를 Read 후 절차 따라 실행
4. auto-jaso-chain (신규 공고 → v0~v4 자동 chain)
   - `C:\Users\윤상택\.claude\scheduled-tasks\auto-jaso-chain\SKILL.md`를 Read 후 절차 따라 실행

순서: cognitive-evolution 4사이클 먼저 → 1 → 2 → 3 → 4. 각 단계 결과 `_AI진화일지/<오늘>.md`에 ledger.
