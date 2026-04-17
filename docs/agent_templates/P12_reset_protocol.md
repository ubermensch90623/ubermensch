# P12 CEO RESET 프로토콜 — 결정적 규칙

> SC2 지적(2026-04-18) 반영: RESET 판정이 "재량" 이 아닌 "결정적·반복가능" 규칙으로 명시.
> 헌법 C-0 ("명시·반복가능") 원칙 정렬.

## 1. RESET 의미

- 현재 진행 중인 M(마일스톤) 전체를 폐기하고 M0 부터 재시작.
- 자율모드에서는 **즉시 실행 금지** — `docs/m3_5_gate_log.md` 에 기록하고 사용자 복귀 시 AskUserQuestion(C-4 경연) 으로 판결.
- 유인모드에서는 사용자가 직접 판결.

## 2. RESET 트리거 조건 (3종, 결정적)

다음 **어느 하나라도** 충족하면 RESET 후보로 승격:

### T1. 실제 기출 원문 인용 부재
- `harness/data/restored/c0_passed.jsonl` 의 `source_type in {"official_released","ebook","primary"}` 항목 수가 **MIN_REAL_EXAM_REFS (=5)** 미만
- AND 해당 M 이 복원률 카운트를 시작하는 단계 (M3.5 이후)

### T2. C-0 격리율 임계 초과
- `c0_failed.jsonl` 라인수 / (`c0_passed.jsonl` + `c0_failed.jsonl`) ≥ **0.30** (30%)
- 단, 총 처리 claim < 20 이면 유예 (표본 부족)

### T3. 동일 claim 격리 루프
- 같은 `claim_id` 가 lineage 상에서 **"collected → c0_passed → quarantined" 또는 "c0_passed → quarantined"** 패턴을 **3 라운드 이상 반복**
- 이는 수집·검증 방법 자체에 체계적 결함이 있다는 신호

### T4 (SC1/SC2 합의). 수석위원 상충 누적
- SC1 PASS vs SC2 REJECT (또는 그 반대) 가 **같은 주제에 3회 연속** 발생
- 제3 수석위원 소집으로 해결 안 되면 RESET 검토

## 3. RESET 판정 절차

```
1. P12 가 자동으로 T1~T4 스캔 (매 M 진입·종료 시, 또는 명시 호출)
2. 하나라도 HIT → verdict = "RESET_CANDIDATE"
3. 자율모드: docs/m3_5_gate_log.md + docs/session_log.md append
4. 유인모드: AskUserQuestion 으로 사용자에게 3 옵션 제시
   (A) 전면 RESET → M0 재시작
   (B) GATED 증분 → 블로커 해소 후 부분 재수집
   (C) 하이브리드 → 코드·UI 유지, 데이터만 재수집
```

## 4. 판정 기록 형식 (append-only)

```markdown
## YYYY-MM-DDTHH:MM:SSZ — P12 RESET 스캔
- T1 real_exam_refs: N / 5 → HIT/MISS
- T2 quarantine_rate: X% → HIT/MISS
- T3 loop_offenders: [claim_id, ...]
- T4 sc_conflict_rounds: N
- verdict: PASS | RESET_CANDIDATE | GATED
- autonomous_note: "사용자 복귀 시 AskUserQuestion 위임" (해당 시)
```

## 5. RESET 이후 의무

- C-9 기록관(P10) 이 이전 라운드의 장점·단점 `docs/meta_overseer/pre_reset_YYYY-MM-DD.md` 에 기록
- P11 태상위원이 rebirth 주기에 해당 RESET 사유 반영
- 재시작 M0 프롬프트에 "이전 RESET 교훈 3줄" 선행 삽입 (C-7 진화 루프)

## 6. 금지

- 사용자 판결 없이 자동 RESET 실행 (C-4 위반)
- 인기영합 이유 (사용자가 싫어할 것 같아서) 로 RESET 회피 (C-6 위반)
- T1~T4 이외의 재량적 사유로 RESET 판정
- P12 혼자 RESET 후 숨김 (C-11 실패 수용 원칙 위반)
