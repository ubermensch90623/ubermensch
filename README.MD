# 유기적 학습/지식 관리 워크플로

아래는 **Google Gemini, NotebookLM, Google Keep, Notion**을 유기적으로 연결하고, **UI는 Google Antigravity**를 중심으로 사용하는 흐름을 정리한 제안입니다.

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

- 상단: 오늘의 학습 목표(노션 데이터베이스 연결)
- 중앙: "오늘 복습 카드" 버튼(노션 뷰)
- 하단: Gemini/NotebookLM/Keep 바로가기

---

필요하면 위 구조를 기반으로 **실제 대시보드 설계**나 **자동화 스크립트 설계**까지 구체화할 수 있습니다.
