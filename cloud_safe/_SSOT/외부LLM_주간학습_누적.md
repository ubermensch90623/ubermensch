---
type: ssot
created: 2026-04-29
status: ledger
cluster: external_llm
entry_order: 4
role: 주간 ledger — cron이 매일 append
auto_appended_by: external-llm-meta-research (매일 20:30)
retention: 일요일 retrospective 후 다음 주 ISO week로 롤오버
---

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
| 04-29 (수) | Grok | **Grok 4.3 Beta** (4/17, native video + slide creation in chat, SuperGrok Heavy $300/월)·**grok-voice-think-fast-1.0** (4/23, 다단계 voice 워크플로우, STT/TTS 25개 언어 GA, TTS $4.20/1M chars)·**Remote MCP Tools GA** (Grok이 외부 MCP 서버 연결, server_url+Bearer, 다중 서버 지원, native SDK + OpenAI Responses API + Voice Agent API)·**Multi-agent (Grok 4.20)** 4 agents 내부 debate (시스템 C 3agent_protocol과 평행 진화)·**GitHub MCP 서버** merterbak/Grok-MCP·Bob-lance/grok-mcp(PyPI) | ✅ "긴 비디오 native 분석"→Grok 4.3 즉시 갱신, "X 트렌드/X 실시간"→DeepSearch baseline 강화. Post-freeze 큐: "면접 STAR 음성 연습"→Voice Think Fast 1, "Grok→Claude MCP 호출"→Remote MCP Tools | ⏳ |
| 04-30 (목) | NotebookLM | ❌ **silent fail** — `_AI진화일지/외부LLM_학습_2026-04-30.md` 산출물 부재. cron 미실행 또는 검색 0건 silent skip. 동일 날짜 daily/시스템_정합성 파일은 존재 → external-llm-meta-research 단독 실패. boot_state·verify_overnight_fires hook 점검 큐 | ❌ 트리 영향 없음 (§2 NotebookLM 4/26 박제 시점 유지) | — |
| 05-01 (금) | 통합 갱신 audit | 월~목 4일치 통합 audit 완료. 4/29 Grok v2.3 변경 이력 누락 소급 기록. 4/30 NotebookLM 결손 박제. 위임 트리 모순 0건 (영역 분리 확인). freeze 5/16 보호 — 신규 도입 0건 | ✅ §1 트리 충돌 없음 확인 + v2.4 audit entry 신설 (`외부_LLM_자율운영_시스템_v2.md`) | — |
| 05-02 (토) | Claude | (자기 자신 진화 + 4개 LLM 비교) | ⏳ | ⏳ |
| 05-03 (일) | retrospective | 1주일치 효과 측정 | ⏳ | — |

---

## 2026-W19 (2026-05-04 ~ 2026-05-10) — 캠코 D-5 보호 모드

| 일자 | LLM | 핵심 신기능 | §1 트리 갱신 | 효과 (1주 후) |
|---|---|---|---|---|
| 05-04 (월) | ChatGPT | GPT-5.5 (4/23 정식, Plus 자동 승급)·Workspace Agents (5/6 무료 종료)·Super App 통합·Codex 90+ plugins·Advanced Account Security (6/1 Trusted Access)·Outlook 공유 메일 위임. **자가학습 큐 2건 처리 완료** (DALL-E 3 deprecate 5/12 + Custom GPT vs scheduled task 비용) | ❌ 즉시 갱신 0건 (freeze 5/16 보호) — Workspace Agents·Custom GPT 분신 등 4건 보류 큐 추가 | ⏳ |
| 05-05 (화) | Gemini | ⏳ pending | ⏳ | ⏳ |
| 05-06 (수) | Grok | ⏳ pending | ⏳ | ⏳ |
| 05-07 (목) | NotebookLM | ⏳ pending | ⏳ | ⏳ |
| 05-08 (금) | 통합 갱신 audit | ⏳ pending | ⏳ | — |
| 05-09 (토) | Claude (자기 자신) | 🔥 캠코 필기 당일 — 학습 skip 또는 시험 후 야간 진행 | ⏳ | ⏳ |
| 05-10 (일) | retrospective | 1주일치 효과 측정 | ⏳ | — |

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
| **xAI Remote MCP Tools** (Grok→Claude 호출) | 2026-04-29 | 종환 휴대폰 발화→Grok→Claude recruitment-scanner/econ-daily-quiz 호출 가능. 분신 통합도 ↑. 종환 PII 정책 재검증 필요 | 5/16 freeze 해제 후 |
| **grok-voice-think-fast-1.0** 한국어 검증 | 2026-04-29 | 25개 언어 GA — 한국어 명시 미확인. 면접 STAR 음성 인식 정확도 측정 필요 | 5/16 freeze 해제 후 |
| **merterbak/Grok-MCP** (Claude→Grok 호출) | 2026-04-29 | Claude Code 내 Grok agentic tool calling + image/video gen 호출 가능 | 5/16 freeze 해제 후 |
| **SuperGrok Heavy ($300/월) ROI 측정** | 2026-04-29 | Grok 4.3 native video + slide creation 활용도 vs 가격. 종환 자소서/NCS 영역 향상도 측정 | 5/16 freeze 해제 후 |
| **Workspace Agents (5/6 무료 종료, credit-based 시작)** | 2026-05-04 | 종환 single user enterprise 한정 — 직접 활용 X. 단 외부 협업 시 ROI 가능성. credit 단가 명시 추적 큐 | 5/16 freeze 해제 후 |
| **Custom GPT "종환 분신" 생성 ROI** | 2026-05-04 | Plus 무료 기능. Claude·Gemini·Grok 분신 가이드와 통합 가능성. 분신 응답 vs Claude 직접 응답 시간/품질 측정 필요 | 5/16 freeze 해제 후 |
| **Advanced Account Security 옵트인** | 2026-05-04 | 6/1 Trusted Access for Cyber 강제 — 일반 Plus는 강제 X. phishing-resistant sign-in 옵트인 효과·session 단축 영향 측정 | 5/16 freeze 해제 후 종환 직접 결정 |
| **Outlook 공유 메일/캘린더 위임** | 2026-05-04 | 종환 회사 Microsoft 365 환경 가능성 — 확인 필요. 채용 자동화는 Claude 측 처리 (recruitment-scanner) → 직접 활용 0이지만 회사 업무 효율화 가능 | 종환 직접 회사 환경 확인 |

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

- **2026-04-29 v2.3**:
  - "긴 유튜브/비디오 native 분석" 신설 → **Grok 4.3 Beta** (4/17 native video understanding 출시)
  - "X 트렌드/X 실시간/X 변호사 발화" baseline 강화 → **Grok DeepSearch** (r/grok 4월 사례 — 웹+X 동시 검색, Perplexity 유사 구조화 출력)
  - Post-freeze 큐 4건 신설: Remote MCP Tools, grok-voice-think-fast-1 한국어 검증, merterbak/Grok-MCP, SuperGrok Heavy ROI
  - 시스템 C 3agent_protocol과 Grok 4.20 multi-agent 평행 진화 발견 (외부 검증)

- **2026-05-01 v2.4 (Friday integration audit)**:
  - 월~목 4일치 통합 감사 완료 — 위임 트리 모순 0건 (LLM 영역 분리 확인)
  - 4/29 Grok v2.3 변경 이력 SSOT v2.md에 소급 박제 (이전 누락분 보정)
  - **결손 진단**: 4/30 NotebookLM cron silent fail — 산출물 부재. boot_state·verify_overnight_fires hook 점검 큐로 위임
  - **freeze 5/16 보호**: 신규 LLM 구독·API 도입 0건. 누적 보류 큐 14건 5/17 ROI 측정 대기 유지
  - SSOT v2 변경 이력에 v2.4 audit entry 신설 (`외부_LLM_자율운영_시스템_v2.md` §변경 이력)
  - 종환 보고 트리거: ❌ 미발동 (중요 신기능 0건, audit는 silent 박제)

- **2026-05-04 v2.5 (W19 1일차 ChatGPT)**:
  - §1 자동 위임 트리 즉시 갱신 0건 (freeze 5/16 보호 정상 작동, 캠코 D-5 보호 모드)
  - 자가학습 큐 §4-A 2건 처리 완료:
    - DALL-E 3 deprecate 5/12 → chatgpt-image-latest 자동 alias 이전, 종환 영향 NONE
    - Custom GPT vs scheduled task → Plus($20)에 Custom GPT 포함, scheduled task 종환 박은 게 stale 다수 → 신규 X, 종환 직접 정리 우선
  - 누적 보류 큐 4건 신설: Workspace Agents (5/6 무료 종료) · Custom GPT 분신 ROI · Advanced Account Security 옵트인 · Outlook 공유 메일 위임
  - GPT-5.5 (4/23) 종환 ChatGPT UI 자동 승급 — 자소서 톤 baseline 측정은 5/16 freeze 후 (캠코 D-5 보호)
  - 종환 보고 트리거: ❌ 미발동 (중요 baseline 승격 0건, 모두 보류 큐 적재)

---

박제일: 2026-04-27 (첫 cron 실행)
마지막 갱신: 2026-05-01 (Friday audit, v2.4)
다음 갱신: 2026-05-02 (토요일 Claude 자기 진화 + 4개 LLM 비교)
