# 외부 LLM 주간 학습 누적 ledger

> 자동 cron `external-llm-meta-research` 매일 20:30 결과를 누적.
> 일요일 retrospective에서 효과 측정 + 다음 주 위임 트리 조정 제안.
> 양식: 일자 | LLM | 핵심 신기능 | 위임 트리 갱신 | 효과 (1주 후 fill-in)

---

## 2026-W18 (2026-04-27 ~ 2026-05-03)

| 일자 | LLM | 핵심 신기능 | §1 트리 갱신 | 효과 (1주 후) |
|---|---|---|---|---|
| 04-27 (월) | ChatGPT | GPT-5.5 (4/24)·GPT-Image 2 한글 95%+ 공식(4/21)·Interactive Learning 70+ topics·Codex Computer Use macOS(4/16)·Atlas Korean IME 정상(macOS) | ✅ 1행 갱신, 1-b 추가, 8행 macOS 보류 명시 | ⏳ |
| 04-28 (화) | Gemini | (예정) | ⏳ | ⏳ |
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

---

## 자동 위임 트리 변경 이력

- **2026-04-27 v2.1**:
  - 1행: 이미지/시각화 → ChatGPT GPT-Image 2 (Korean 95%+ 공식 확인, Image Arena #1 +242 Elo)
  - 1-b 신설: 인터랙티브 시뮬레이션 → ChatGPT Interactive Learning (70+ math·science)
  - 8행 신설: 컴퓨터 사용 자동화 → ⚠️ macOS 전용 보류 (Codex CU·Atlas Agent 모두 macOS 한정)

---

박제일: 2026-04-27 (첫 cron 실행)
다음 갱신: 2026-04-28 (화요일 Gemini)
