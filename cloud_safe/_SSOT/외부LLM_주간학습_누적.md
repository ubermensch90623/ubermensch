# 외부 LLM 주간 학습 누적 ledger

> 자동 cron `external-llm-meta-research` 매일 20:30 결과를 누적.
> 일요일 retrospective에서 효과 측정 + 다음 주 위임 트리 조정 제안.
> 양식: 일자 | LLM | 핵심 신기능 | 위임 트리 갱신 | 효과 (1주 후 fill-in)

---

## 2026-W18 (2026-04-27 ~ 2026-05-03)

| 일자 | LLM | 핵심 신기능 | §1 트리 갱신 | 효과 (1주 후) |
|---|---|---|---|---|
| 04-27 (월) | ChatGPT | GPT-5.5 (4/24)·GPT-Image 2 한글 95%+ 공식(4/21)·Interactive Learning 70+ topics·Codex Computer Use macOS(4/16)·Atlas Korean IME 정상(macOS) | ✅ 1행 갱신, 1-b 추가, 8행 macOS 보류 명시 | ⏳ |
| 04-28 (화) | Gemini | **Gemini 3.1 Pro** (Artificial Analysis Index 1위, vs Claude Opus 4.6 +4점·비용 1/2)·**Deep Research Max** (4/22, DeepSearchQA 93.3%·MCP·자동 차트·외부+사적 데이터)·**Workspace Intelligence** (4/22, semantic layer)·**한국어 Workspace 4월 확장** (Forms·Meet·Chat·Docs)·**Gemini in Chrome Win+Mac** (4월 US, 한국 미확인)·**Mac Desktop App macOS 전용** (4/15)·Nano Banana Pro 인포그래픽·Gem 공유 기능 | ✅ 3행 갱신(Deep Research Max), 8행 보강, 9행 신설(Workspace Intelligence), 10행 신설(Chrome 검증 필요), §2 Gemini 전면 갱신 | ⏳ |
| 04-29 (수) | Grok | (예정) | ⏳ | ⏳ |
| 04-30 (목) | NotebookLM | (예정) | ⏳ | ⏳ |
| 05-01 (금) | 통합 갱신 | (월~목 4일치 통합) | ⏳ | — |
| 05-02 (토) | Claude | (자기 자신 진화 + 4개 LLM 비교) | ⏳ | ⏳ |
| 05-03 (일) | retrospective | 1주일치 효과 측정 | ⏳ | — |

---

## 누적 보류 큐 (freeze 5/16 후 검토)

| 도구 | 발견일 | 결정 사유 | 검토 일정 |
|---|---|---|---|
| Codex 데스크톱 앱 + 90+ plugins | 2026-04-27 | macOS 전용 → Windows 출시 모니터링 | 5/16 freeze 해제 후 |
| ChatGPT App SDK + MCP Developer Mode | 2026-04-27 | Claude jaso_validator를 ChatGPT 측에서도 호출 가능성 | 5/16 freeze 해제 후 |
| openai-agents-mcp / mcp-openai | 2026-04-27 | Claude Code → OpenAI MCP 통합 | 5/16 freeze 해제 후 |
| ChatGPT Atlas (macOS 전용) | 2026-04-27 | 종환 Mac 도입 의향 시 우선순위 1위 | 종환 결정 대기 |
| **salviz/gemini-mcp-server** (23 tools, 우선순위 1) | 2026-04-28 | Claude Code → Gemini Deep Research Max 직접 호출 (DeepSearchQA 93.3% 활용) | 5/16 freeze 해제 후 1순위 |
| pminervini/deep-research-mcp (multi-provider) | 2026-04-28 | OpenAI + Gemini + Open Deep Research 통합 wrapper | 5/16 freeze 해제 후 2순위 |
| capyBearista/gemini-researcher (free tier proxy) | 2026-04-28 | 비용 0 우회 (종환 Plus 구독 한도 초과 시) | 5/16 freeze 해제 후 |
| Gemini in Chrome 한국 출시 모니터링 | 2026-04-28 | Plus/Win/한국 동시 충족 시 §1 트리 10행 활성화 | Google 한국 rollout 대기 |
| Mac Gemini Desktop App Windows 출시 | 2026-04-28 | macOS 전용 → 종환 Windows 차단 | Google 발표 대기 |
| Subscription Plus → Pro/Ultra 매핑 | 2026-04-28 | 4/11 재구조화로 종환 기존 구독 자동 이전 여부 불명 | 종환 직접 확인 |

---

## 자동 위임 트리 변경 이력

- **2026-04-27 v2.1**:
  - 1행: 이미지/시각화 → ChatGPT GPT-Image 2 (Korean 95%+ 공식 확인, Image Arena #1 +242 Elo)
  - 1-b 신설: 인터랙티브 시뮬레이션 → ChatGPT Interactive Learning (70+ math·science)
  - 8행 신설: 컴퓨터 사용 자동화 → ⚠️ macOS 전용 보류 (Codex CU·Atlas Agent 모두 macOS 한정)

- **2026-04-28 v2.2**:
  - 3행 갱신: 깊은 검색 → Gemini Deep Research → **Deep Research Max** (DeepSearchQA 93.3%, MCP 지원, 자동 차트, 외부 web + 사적 데이터, 2026-04-22 출시)
  - 8행 보강: macOS 전용 LLM 도구에 Gemini Mac Desktop App (4/15) 추가
  - 9행 신설: Gmail·Drive·Docs 통합 검색 → Gemini Workspace Intelligence (2026-04-22 Cloud Next 발표)
  - 10행 신설: 브라우저 내 즉시 분석 → Gemini in Chrome (한국 출시 검증 필요, US Plus/Ultra만 출시)
  - §2 Gemini 섹션 전면 갱신: 기본 모델 = Gemini 3.1 Pro, 한국어 Workspace 4월 확장, Gem 공유

---

박제일: 2026-04-27 (첫 cron 실행)
마지막 갱신: 2026-04-28 (Gemini, v2.2)
다음 갱신: 2026-04-29 (수요일 Grok)
