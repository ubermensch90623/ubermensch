# 유기적 학습/지식 관리 워크플로

아래는 **Google Gemini, NotebookLM, Google Keep, Notion**을 유기적으로 연결하고, **UI는 Google Antigravity**를 중심으로 사용하는 흐름을 정리한 제안입니다.

## Antigravity 데모 UI 실행

`index.html`을 브라우저로 열면 **클릭 가능한 대시보드 UI**를 확인할 수 있습니다.

```
open index.html
```

## 1) 전체 구조 요약

- **입력/캡처**: Google Keep
- **정리/요약/질문 생성**: NotebookLM + Gemini
- **지식 베이스/프로젝트 관리**: Notion
- **일상적 조작 UI**: Google Antigravity

## 2) 역할 분담 (도구별 역할)

### Google Keep (입력 허브)
- 강의/독서/아이디어의 **즉시 메모**
- 태그(예: `inbox`, `수학`, `문제풀이`)로 분류

### NotebookLM (자료 정리/학습 보조)
- PDF/노트/Keep 메모를 묶어 **요약 + 질문 생성**
- 핵심 개념을 **Q/A 카드**로 추출

### Google Gemini (정교화/자동화)
- NotebookLM 결과를 **더 구조화**
- 학습 계획, 오답 패턴 분석, 요약본 가다듬기

### Notion (영구 지식/프로젝트 관리)
- 검증된 요약본, 오답노트, 학습 체크리스트 저장
- 학습 스프린트/주간 계획 관리

### Google Antigravity (통합 UI)
- 위 모든 도구에 대한 **대시보드 역할**
- 자주 쓰는 링크/자동화 버튼을 모아놓은 홈 화면 구성

## 3) 추천 워크플로 (일일 흐름)

1. **Keep에 메모/오답 기록**
2. **NotebookLM에 자료 업로드 후 요약/질문 생성**
3. **Gemini로 요약/질문 정교화 및 난이도 분류**
4. **Notion에 최종 정리** (카드/오답노트/스프린트에 반영)
5. **Antigravity 대시보드에서 일괄 접근**

## 4) 자동화 아이디어

- **Keep → NotebookLM 자동 수집**
  - Keep에서 특정 태그(`inbox`)만 NotebookLM 입력 대상으로 사용
- **NotebookLM → Notion 자동 저장**
  - 요약 결과를 Notion 데이터베이스로 자동 전송
- **Notion → Antigravity 바로가기 구성**
  - 오늘 할 일, 복습 목록, 요약 페이지를 한 화면에서 접근

## 5) Antigravity UI 구성 예시

아래는 **Antigravity 홈 화면**을 가정한 간단한 와이어프레임입니다.

```
┌───────────────────────────────────────────────────────┐
│ 오늘의 학습 목표 (Notion DB)                            │
│ - 주간 목표: 수학 오답 복습 20문항                      │
│ - 오늘 목표: 1) 미분 오답 5문항 2) 독해 카드 10개       │
├───────────────────────────────────────────────────────┤
│ [오늘 복습 카드]   [오답노트 바로가기]   [스프린트 보드] │
├───────────────────────────────────────────────────────┤
│ 빠른 입력                                                 │
│ [Keep 메모 추가]  [NotebookLM 요약 생성]  [Gemini 질문] │
├───────────────────────────────────────────────────────┤
│ 상태 요약                                                │
│ - 대기 중 복습: 12개   - 완료: 8개   - 미해결: 3개        │
└───────────────────────────────────────────────────────┘
```

### 구성 요소 설명
- **오늘의 학습 목표**: Notion DB를 연결해 오늘 목표를 자동 표기
- **오늘 복습 카드**: Notion의 “오늘 복습” 뷰를 바로 열기
- **빠른 입력**: Keep/NotebookLM/Gemini로 즉시 이동
- **상태 요약**: 복습 진행 상황을 한눈에 확인

---

---

## 6) Antigravity 제어 가능 여부

현재 저는 **Google Antigravity 자체를 직접 제어하거나 조작할 수는 없습니다.**
하지만 아래처럼 **설계/구성 안내**는 제공할 수 있습니다.

- Antigravity에 넣을 **대시보드 구성**과 **버튼 구조** 설계
- 각 버튼이 연결될 **Notion/Keep/NotebookLM/Gemini 링크 구조**
- 복습/오답 흐름을 반영한 **화면 배치 가이드**

필요하면 위 구조를 기반으로 **실제 대시보드 설계**나 **자동화 스크립트 설계**까지 구체화할 수 있습니다.

## 7) 매 시간 자동화 실행(로컬 스케줄러)

실제 서비스 연동은 API가 필요하지만, **매 시간 자동화 작업을 스스로 실행**하는 형태는 로컬 스케줄러로 구성할 수 있습니다.

### 1) 설정 파일 준비

```
cp scripts/automation-config.example.json scripts/automation-config.json
```

### 2) 자동화 스크립트 실행 테스트

```
node scripts/hourly-automation.js scripts/automation-config.json
```

### 3) 매 시간 자동 실행(cron 예시)

```
0 * * * * /usr/bin/node /workspace/ubermensch/scripts/hourly-automation.js /workspace/ubermensch/scripts/automation-config.json >> /workspace/ubermensch/automation.log 2>&1
```

> 위 스크립트는 현재 **링크/작업 목록을 로깅하는 기본 골격**이며, Notion/Google API 키를 연결하면 실제 자동화를 확장할 수 있습니다.

## 8) 실제 자동화까지 가능한 설계: 구현 경로(단계별)

아래는 **UI 링크 연결 → 데이터 동기화 → 복습 자동화 → 리포팅**까지 단계적으로 확장하는 구체적 경로입니다.

### Phase 1. 링크 연결(당일 완성)
- Antigravity 대시보드 버튼에 **실제 서비스 URL** 연결
- 클릭 시 해당 도구(Keep/NotebookLM/Gemini/Notion)의 목표 페이지로 이동
- 결과: **허브 UI 완성** (동작 확인은 브라우저에서 가능)

### Phase 2. 데이터 동기화(1~2일)
**목표**: 입력된 메모/요약을 Notion으로 자동 반영
- Keep → Notion
  - Keep API/Export/Script(가능한 방식 선택)로 메모 수집
  - Notion API로 “Inbox” DB에 자동 저장
- NotebookLM/Gemini → Notion
  - 요약 결과를 Notion “Summary” DB에 자동 추가
  - 필드: `source`, `summary`, `created_at`, `tags`
- 산출물: **자동 수집 파이프라인** (스케줄러로 주기 실행)

### Phase 3. 복습 스케줄 자동화(2~4일)
**목표**: 오답/카드 등록 시 망각곡선 기반 복습 일정 자동 계산
- Notion DB 필드 설계
  - `last_review`, `interval`, `next_review`, `status`, `difficulty`
- 규칙 예시
  - 신규 등록 → `next_review = 오늘 + 1일`
  - 성공 → `interval` 증가 (1→3→7→14→30)
  - 실패 → `interval` 축소 (다음날 재복습)
- 스케줄러가 매 시간/매일 `next_review <= 오늘` 항목을 “오늘 복습” 뷰로 이동

### Phase 4. 리포트/대시보드 자동 갱신(1~2일)
**목표**: 진행률/성과 요약 자동 생성
- 완료/대기/미해결 수치 집계
- “오늘 리포트” 섹션 자동 업데이트
- 주간 요약 메일/알림(옵션)

### 구현을 위한 최소 준비물
- Notion API Key + DB ID
- Notion DB 스키마 확정(필드 정의)
- 사용 중인 Keep/NotebookLM/Gemini 접근 경로
- 스케줄러 환경(로컬 cron 또는 서버리스)

> 원하시면 위 Phase 중 원하는 범위부터 바로 구현 가능합니다.
