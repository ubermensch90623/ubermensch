---
name: 3-Agent Harness Protocol (모방판)
description: Anthropic Three-Agent Harness 패턴을 freeze 안에서 Agent tool로 모방
type: system-protocol
version: 1.0
created: 2026-04-26
references:
  - https://www.infoq.com/news/2026/04/anthropic-three-agent-harness-ai/
  - https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
  - https://arxiv.org/pdf/2511.13646  (LIVE-SWE-AGENT 77.4% SWE-Bench)
---

# 3-Agent Harness Protocol (모방판)

> **목적**: "보고만 하고 실행 안 함" 메타패턴 차단. 자소서·분석 작업 시 자동으로 Planner → Generator → Evaluator 분리.
> **freeze 준수**: 신규 프레임워크 0개. 기존 Agent tool로 모방.
> **언제 적용**: 자소서 v1·분석 보고·복합 채용 조사. 단순 답변·조회는 적용 안 함.

---

## 트리거 (자동 적용 대상)

다음 작업 발화 시 이 프로토콜을 자동 적용:
- "자소서 v1/v2/... 작성"
- "탈락 원인 분석"
- "배점 추정"
- "기관 비교"
- "면접 예상 답변"
- "필기 학습 자료 생성"

---

## 3단계 분리

### 1) Planner (Agent: general-purpose 또는 Plan)
**역할**: 작업 범위·팩트 의존성·블로커 식별. 코드/본문 작성 금지.
**산출물**:
- 문항별 요구 글자수·키워드 (자소서)
- 검증 필요한 팩트 N건 (URL·grep 매칭 계획 포함)
- 종환 측 팩트(이미 알려진 것)와의 정합 체크리스트

### 2) Generator (메인 세션 또는 Agent: brand-voice:content-generation)
**역할**: Planner 산출물을 받아 본문 생성.
**제약**:
- Planner가 검증한 팩트만 사용
- 자소서면 `_SSOT/자소서_피드백_누적.md`의 절대 규칙 + 금칙어 준수
- 분석/보고면 모든 단정에 출처 인라인 첨부

### 3) Evaluator (Agent: quality-assurance 또는 자체)
**역할**: Generator 출력을 종환에게 노출하기 전 자가 검증.
**필수 통과 게이트**:
- 자소서: `python3 작업/agent-memory/jaso_validator.py <파일>` exit 0
- 본문 작성: `cove_critic_hook` 검증 질문 5개에 답변
- 분석/보고: `evidence_gate` BLOCK 없음 + 독립 도메인 2개+ 매칭
- 모두 통과 시에만 종환에게 v1 노출

---

## 호출 방법 (메인 세션이 따라야 할 표준)

```
Step 1) Agent tool로 Planner 호출
        prompt: "이 작업의 범위·팩트 의존성·블로커를 분리해 보고."
Step 2) Planner 산출물 받아서 메인이 Generator 수행
        (또는 Agent tool 한번 더 호출)
Step 3) Agent tool로 Evaluator 호출
        prompt: "다음 본문이 [jaso_validator | cove | evidence_gate] 통과하는가? 위반 항목 N개 보고."
Step 4) Evaluator NO → Generator 재실행 (피드백 반영)
        Evaluator OK → 종환에게 노출
```

---

## 금지

- Planner 단계 스킵 후 바로 Generator
- Evaluator 통과 전 종환에게 v1 노출
- "통과 가정" — 실제 hook/validator 실행해야 통과
- 같은 Agent 인스턴스에서 3단계 순차 실행 (편향)

---

## 측정 지표

| 지표 | baseline | 목표 |
|---|---|---|
| 자소서 v1 노출 전 자가 review 통과 비율 | 0% (4/22 IBK D-0) | 100% |
| 분석/보고 시 evidence_gate BLOCK 회수 | 측정 안 됨 | 0회 |
| Planner 단계 스킵률 | 측정 안 됨 | <10% |

---

## 향후 확장 (freeze 5/16 후)

- 정식 harness CLI 구축 (Bash 진입점 1개)
- Planner/Generator/Evaluator 각각 다른 LLM 인스턴스 (sonnet · opus · haiku 분담)
- LIVE-SWE-AGENT 자기 진화 패턴 도입 (실패 케이스 → 도구 자동 갱신)
