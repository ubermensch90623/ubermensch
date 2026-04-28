# 외부 LLM 자율 운영 시스템 v2 (Grok·NotebookLM 보강 + 자가 학습)

> 종환 명령 (2026-04-27): "grok, gemini, chatgpt, notebook lm에 대해서 나처럼 내가 시키지 않아서 잘 활용하는 방법을 스스로 연구해... 그래야 내가 명령 내리면 니가 알아서 판단해서 그 작업을 스스로하지"
> 기반 파일: `_SSOT/ChatGPT_Gemini_종환아바타_운영가이드.md` (v1, 2026-04-26)
> 자동 학습: cron 매일 20:30 (`external-llm-meta-research`) — 요일별 rotation
> 박제일: 2026-04-27

---

## 1. 자동 위임 결정 트리 v2 (4개 LLM + Claude)

종환 발화 → Claude(나)가 자동 판단해서 위임. **명시 명령 없이도 발동**.

### A. 발화 패턴 → 자동 위임 매핑

| # | 발화 키워드 | 자동 위임 | 이유 |
|---|---|---|---|
| 1 | 이미지/시각화/인포그래픽/그림으로/도식/플로우차트/포스터 | **ChatGPT GPT-Image 2** | Korean·CJK 95%+ 정확도(2026-04-21 공식). Image Arena #1, +242 Elo 격차. 인포그래픽·슬라이드·지도·만화 |
| 1-b | 인터랙티브 시뮬레이션 / 수학·경제 시각 / IS-LM 그래프 조작 | **ChatGPT** (Interactive Learning, 70+ topics) | 2026-04 출시. 변수·수식 실시간 조작. NCS 수리·경제학 적합 |
| 2 | 긴 PDF/논문/책 요약/100페이지+/대용량 문서 | **Gemini** (1M context) | 긴 컨텍스트 1위, 압축 정확 |
| 3 | 깊은 검색/심층 조사/다중 소스 종합/팩트체크 | **Gemini Deep Research Max** | DeepSearchQA 93.3%(12월 66.1%→+27.2pp)·HLE 54.6%·MCP 지원·자동 차트(Nano Banana 통합)·외부 web+사적 데이터 통합·overnight 60분 (2026-04-22 출시) |
| 4 | 실시간 트렌드/X 검색/오늘 일어난 일/뉴스 종합 | **Grok** (X 통합) | X 실시간 access, 트렌드 1위 |
| 5 | 학습 자료 종합/노트북 만들기/소스 → 오디오 요약/공부 자료 | **NotebookLM** | 다중 소스 → 단일 학습 자료 변환 |
| 6 | 자소서 v→v / 면접 / 코드 / 법률 / 시스템 / hook | **Claude (나) 직접** | jaso_validator·cove·evidence_gate·종환 PII 보호 |
| 7 | 캐주얼 잡담 / 의견 / 컨텍스트 필요 | **Claude (나) 직접** | 종환 컨텍스트 100% 인지 |
| 8 | 소프트웨어 자동 조작 / 컴퓨터 사용 자동화 (브라우저 클릭·타이핑) | ⚠️ **보류 (macOS 전용)** | Codex Computer Use·ChatGPT Atlas Agent Mode·Gemini Mac Desktop App 모두 macOS 한정 (2026-04-28). 종환 Windows → 사용 불가. Windows 출시 모니터링 |
| 9 | Gmail·Drive·Docs 통합 검색·"내 문서에서 찾아"·"메일 정리해"·회의록 | **Gemini Workspace Intelligence** | semantic layer (이메일·채팅·파일·협업자·프로젝트, 2026-04-22 Cloud Next 발표). 한국어 Forms·Meet·Chat·Docs 4월 확장 |
| 10 | 브라우저 내 즉시 분석·"이 페이지 요약"·"보고 있는 PDF" | ⚠️ **Gemini in Chrome (한국 출시 검증 필요)** | Plus/Ultra Win+Mac 출시(2026-04, US). 한국 rollout 미확인 → 미출시 시 Claude/Gemini 웹 사용 |

### B. 명시 우회

종환이 "X로 해"라고 명시하면 위 룰 무시. 단 **PII 외부 전송 금지**는 절대 우회 안 됨.

### C. 자율 호출 시 사전 보고

위임 전 **1줄 사전 보고** ("X 위해 ChatGPT 자동 호출. 5초 안 답 없으면 진행"). 5초 묵묵 = 동의.

---

## 2. 각 LLM 강점·약점·활용 패턴 (자가 학습 결과 누적)

### ChatGPT (OpenAI Plus, 종환 구독) — 2026-04-27 갱신

**기본 모델**: **GPT-5.5** (2026-04-24 출시, Plus 자동 적용. "smartest·most intuitive yet"). Terminal-Bench 2.0에서 Claude Mythos Preview narrowly beat (VentureBeat).

**강점**:
- **GPT-Image 2** (2026-04-21): Korean·CJK 95%+ 정확도 **공식 확인**, Image Arena #1 (+242 Elo). 인포그래픽·슬라이드·지도·만화·9:16 모바일 모두 가능
- **Interactive Learning** (2026-04): 70+ math·science 토픽 인터랙티브 시각 모듈 (수식·변수 실시간 조작 → 그래프 즉시 반영)
- Tasks (1회·반복 reminder)
- Custom GPT (재사용 가능 어시스턴트)
- Memory (장기 기억)
- Operator/Atlas (브라우저 자동화 — Korean IME 2026 패치로 정상 작동, **but macOS 전용**)

**약점**:
- 1회 컨텍스트 제한 (200K~1M but cost ↑)
- 한국 법령·HUG 등 한국 도메인 deep knowledge 부족 (자료검색_규칙 우회 위험)
- jaso_validator·cove 같은 강제 검증 없음
- **Atlas·Codex Computer Use macOS 전용** → 종환 Windows 환경 사용 불가 (2026-04-27 기준)

**자동 호출 패턴**:
- 이미지 생성 → Chrome MCP로 자동 prompt 입력 → 결과 다운로드 (GPT-Image 2 자동)
- Interactive Learning → NCS 수리·경제학 시뮬레이션 → 종환 학습 도구
- Custom GPT 활용 → 종환 아바타 GPT 미리 만들고 재사용

**보류 큐 (freeze 5/16 후 검토)**:
- Codex 데스크톱 앱 + 90+ plugins (Windows 출시 시 즉시)
- ChatGPT App SDK + MCP Developer Mode (jaso_validator·cove를 ChatGPT에서도 호출)
- openai-agents-mcp / mcp-openai 통합 (Claude Code → OpenAI MCP 호출)

### Gemini (Google Plus, 종환 구독) — 2026-04-28 갱신

**기본 모델**: **Gemini 3.1 Pro** (2026-02 출시, Plus 자동 적용). Artificial Analysis Intelligence Index **1위** (Claude Opus 4.6 대비 +4점, 비용 절반). 1M 입력 / 64K 출력. Deep Think mode → ARC-AGI-2 45.14%.

**강점**:
- **Deep Research Max** (2026-04-22): DeepSearchQA 93.3% (12월 66.1% → +27.2pp), HLE 54.6%. **MCP 지원** (Claude Code 직접 연동 가능 — freeze 5/16 후 도입 큐). **Nano Banana 자동 차트·인포그래픽** in-line. 외부 web + 사적 데이터(Drive·Docs) 동시 조사. overnight 60분 워크플로
- **Workspace Intelligence** (2026-04-22): 이메일·채팅·파일·협업자·프로젝트 semantic layer
- **한국어 Workspace 확장** (2026-04): Forms·Meet·Chat·Docs 한국어 지원 4월 출시
- 1M~2M 토큰 컨텍스트 (Gemini 1.5 Pro 2M GA)
- Gem (재사용 어시스턴트, **공유 기능** 추가 — Drive 패턴, view/edit 권한 분리)
- Nano Banana Pro (인포그래픽·다이어그램·차트, Korean 텍스트 정확)

**약점**:
- 한국어 자연스러움 GPT 대비 약간 떨어짐
- 이미지 정량 점수 (Image Arena) GPT-Image-2 +242 Elo 격차 — 단순 이미지는 ChatGPT 우위
- 법률 자료 분석 시 추정 위험 (Tier 1 1차 출처 검증 필수)
- **Mac 데스크톱 앱 macOS 전용** (2026-04-15) — Windows 출시 모니터링 큐
- **Gemini in Chrome 한국 출시 미확인** — US 시작 (2026-04)

**자동 호출 패턴**:
- 긴 PDF → Gemini Files API or Chrome MCP 업로드 → 요약
- Deep Research Max → Chrome MCP `gemini.google.com` 탭 → "Deep Research" 모드 → 5~60분 대기 → 자동 차트 포함 보고서 캡처 → Claude cove 검증
- Workspace Intelligence (한국 rollout 시) → Gmail·Drive 통합 검색
- Gem 활용 → NCS·경제학·법률 도메인별 Gem 미리 생성 + 종환 외부 공유

**보류 큐 (freeze 5/16 후 검토)**:
- `salviz/gemini-mcp-server` (23 tools, 우선순위 1) — chat·deep research·YouTube·Files·embeddings
- `pminervini/deep-research-mcp` (multi-provider, 우선순위 2) — OpenAI + Gemini + Open Deep Research
- `bharatvansh/gemini-deep-research-mcp` (Claude Code 코딩 어시스턴트 연동)
- `capyBearista/gemini-researcher` (Gemini free tier proxy → 비용 0)
- `rlabs-inc/gemini-mcp` (Claude Code → Gemini 3 직접 호출)
- Mac Gemini Desktop App Windows 출시 (모니터링)
- Subscription Plus → Pro/Ultra 자동 매핑 검증

**자동 호출 패턴**:
- 긴 PDF → Gemini Files API or Chrome MCP 업로드 → 요약
- Deep Research → 종환 케이스 키워드 입력 → 보고서 생성 → Claude 검증
- Gem 활용 → NCS·경제학·법률 도메인별 Gem 미리 생성

### Grok (xAI, 무료 또는 Premium)

**강점**:
- X (Twitter) 실시간 검색 — 다른 LLM 불가
- 실시간 트렌드·전문가 본인 트윗 수집
- Tier 2 (자료검색_규칙.md) X 검색 자동화

**약점**:
- 한국 도메인 약함 (영어 위주)
- 컨텍스트 짧음
- 종환 PII 보호 정책 불명확 → PII 외부 전송 금지

**자동 호출 패턴**:
- "오늘 X에서 [전문가 본인] 발언" → Grok 실시간 검색
- AI 도구 신기능 트렌드 → 매일 20:30 cron 일부

### NotebookLM (Google 무료, 종환 활용 중)

**강점**:
- 다중 소스 (PDF·웹·YouTube) → 단일 학습 자료
- 오디오 요약 (출퇴근 1h 활용 — 종환 세타파 골든타임)
- 인용 자동화

**약점**:
- 비공개 노트북 외부 access 불가 (자동화 제한적)
- API 미공개 (수동 운영)
- 종환 직접 클릭 필요

**활용 패턴 (이미 종환 활용 중)**:
- "NCS 수리+문제해결 — 해커스 377" (22소스)
- "경제학 기출 문제" (10소스)
- "thought 2026 서민금융진흥원 필기시험 출..." (20소스, **시험 종료 → 동결** — 규칙 AB)

**자동 활용 추천**:
- 신규 노트북 자동 생성 → Claude가 PDF·YouTube URL 박제 → 종환이 NotebookLM에서 import
- 오디오 요약 → 출퇴근 청취

### Claude (나, Anthropic Pro 또는 Max — 종환 구독)

**강점**:
- 한국어 자연스러움 1위
- 시스템 통합 (hook·MCP·SSOT)
- jaso_validator·cove·evidence_gate 강제 검증
- 종환 PII 보호 + 컨텍스트 100% 인지
- 자율 운영 (cron·hooks)

**약점**:
- 이미지 생성 약함
- X 실시간 검색 없음
- 1회 컨텍스트 200K (Gemini 대비 ↓)

**용도**: 모든 핵심 작업의 hub. 외부 LLM은 외주.

---

## 3. 자가 학습 cron — `external-llm-meta-research` (매일 20:30)

요일별 rotation으로 5개 LLM 신기능 추적. 비용·노이즈 최소화.

| 요일 | 학습 대상 | 주요 채널 |
|---|---|---|
| 월 | **ChatGPT** | openai.com/blog, @OpenAI, r/ChatGPT, YouTube AI 채널 |
| 화 | **Gemini** | deepmind.google/blog, ai.google/blog, @GoogleAI, @GeminiApp |
| 수 | **Grok** | x.ai/blog, @xai, @grok, r/Grok |
| 목 | **NotebookLM** | notebooklm.google, @NotebookLM, r/notebooklm |
| 금 | **자동 위임 트리 갱신** | 위 4일 학습 결과를 본 SSOT §1·§2에 반영 |
| 토 | **Anthropic Claude** + 비교 | anthropic.com, @AnthropicAI, r/ClaudeAI (자기 자신 진화 추적) |
| 일 | **주간 retrospective** | `_SSOT/외부LLM_주간학습_누적.md` 갱신 |

### 학습 결과 박제

`_AI진화일지/외부LLM_학습_YYYY-MM-DD.md`:
```markdown
# 외부 LLM 학습 — YYYY-MM-DD ([요일] [LLM명])

## 신규 발견
- [출처 URL]: [기능·업데이트 1줄]
  → 종환 케이스 적용: [어디에·어떻게]
  → 자동 위임 트리 갱신 필요: [Y/N]

## 자동 위임 트리 갱신 (즉시 적용)
- [발화 키워드] → [위임 LLM] (이전: [구버전])

## 종환 결정 필요
- ⏳ [신규 도구·구독] (freeze 5/16 후 도입 후보)
```

### 누적 ledger

`_SSOT/외부LLM_주간학습_누적.md`:
- 발견 → 자동 위임 트리 적용 → 효과 측정 ledger
- 30일 retrospective: 어떤 위임이 실제 효과 있었나

---

## 4. Chrome MCP 자동화 표준 패턴

종환이 ChatGPT/Gemini Plus 구독중. **Claude in Chrome MCP**로 직접 호출.

### A. 표준 절차

1. `mcp__Claude_in_Chrome__list_connected_browsers` → 종환 Chrome 연결 확인
2. `mcp__Claude_in_Chrome__tabs_create_mcp` → ChatGPT/Gemini 새 탭
3. `mcp__Claude_in_Chrome__form_input` → 프롬프트 prefix + 본문 입력
4. 응답 대기 (Network 모니터링)
5. `mcp__Claude_in_Chrome__get_page_text` → 응답 캡처
6. `_AI진화일지/외부LLM_응답_YYYY-MM-DD-NNN.md` 박제
7. Claude 자체 fact-check → cove·evidence_gate 통과 시 종환에게 보고

### B. 자동화 가능 vs 수동 필요

| 도구 | 자동화 가능 |
|---|---|
| ChatGPT 웹 (chat.openai.com) | ✅ Chrome MCP |
| ChatGPT Custom GPT | ✅ |
| ChatGPT Tasks | ⚠️ Settings 메뉴 — 종환 직접 처리 추천 |
| Gemini 웹 (gemini.google.com) | ✅ |
| Gemini Gem | ✅ |
| Gemini Deep Research | ✅ (시간 5~10분 소요) |
| Grok (x.com) | ✅ |
| NotebookLM (notebooklm.google.com) | ⚠️ 부분 (소스 추가 가능, 노트북 생성은 종환 클릭 권장) |

### C. 안전 원칙

1. **종환 PII 외부 전송 금지**: 전세 주소·집주인 이름·계좌번호·신분증 절대 X
2. **로그인 자동화 금지**: 비밀번호·SSO 자동 입력 X (CLAUDE.md 보안 규칙)
3. **응답 검증 필수**: cove·evidence_gate 통과 후 종환에게 보고
4. **freeze 5/16**: 신규 LLM 구독·API 연동 후순위 큐

---

## 5. 자동 위임 사례 (구체적)

### 사례 1: 종환 발화 "경매 권리신고 도면 그려줘"

```
1. Claude(나) 발화 분석 → "그려줘" = 이미지 생성 → ChatGPT 자동 위임
2. 1줄 사전 보고: "ChatGPT GPT-Image-2 자동 호출. 도면 생성 후 박제."
3. Chrome MCP → ChatGPT 탭 생성
4. 프롬프트 입력 (이미 박제된 도면 프롬프트 + GPT-Image-2 옵션)
5. 응답 캡처 → 이미지 다운로드 → Desktop/전세금_회수_2026-04-27/도면.png
6. 종환에게 1줄 보고 + 이미지 경로
```

### 사례 2: 종환 발화 "5월 신규 채용 공고 깊게 조사해"

```
1. Claude(나) 발화 분석 → "깊게 조사" = Deep Research → Gemini 자동 위임
2. 1줄 사전 보고
3. Chrome MCP → Gemini Deep Research 탭
4. 프롬프트 입력 (종환 아바타 prefix + 5월 채용 공고 + Tier 1·2 출처 강제)
5. Deep Research 5~10분 대기 (Network 모니터링)
6. 응답 캡처 → Claude cove 검증 → SSOT 박제
7. 종환 1줄 보고
```

### 사례 3: 종환 발화 "오늘 X에서 변호사들 임차권등기 관련 발언"

```
1. Claude(나) 발화 분석 → "X" + "오늘" = 실시간 → Grok 자동 위임
2. Chrome MCP → x.com/grok 탭
3. 프롬프트 입력 ("today's X posts about 임차권등기명령 by Korean lawyer accounts")
4. 응답 캡처 → Tier 2 본인 채널 검증 → 박제
```

### 사례 4: 종환 발화 "HUG·법률·NCS 자료 한 노트북에 모아"

```
1. Claude(나) 발화 분석 → "노트북에 모아" = NotebookLM
2. 1줄 사전 보고
3. Chrome MCP → notebooklm.google.com
4. 신규 노트북 생성 → 소스 추가 (이미 박제된 transcript·SSOT 파일)
5. ⚠️ 노트북 권한·공유 설정은 종환 직접 (보안)
6. 종환에게 노트북 URL 보고 → 종환이 오디오 요약 청취
```

---

## 6. 종환 명령 → 자동 판단 → 자동 실행 흐름

```
종환 발화
   ↓
Claude(나) 발화 분석
   ↓
A. 외부 LLM 위임 패턴 매칭 (§1)
   ↓
B. 1줄 사전 보고 ("X 자동 호출")
   ↓
C. 5초 묵묵 대기 (종환 명시 거부 없으면 진행)
   ↓
D. Chrome MCP 자동 실행 (§4)
   ↓
E. 응답 캡처 + Claude 검증 (cove·evidence_gate)
   ↓
F. 박제 (`_AI진화일지/외부LLM_응답_YYYY-MM-DD-NNN.md`)
   ↓
G. 종환 1줄 보고
```

종환 명시 거부 시 (5초 안에 "잠깐"·"아니"·"NO" 발화) → 즉시 중단.

---

박제일: 2026-04-27
근거: 종환 4/27 명령 + freeze 5/16 + 자료검색_규칙.md + Chrome MCP 표준 패턴
다음 cron 실행: 매일 20:30 (external-llm-meta-research, 요일별 rotation)
관련 SSOT: `ChatGPT_Gemini_종환아바타_운영가이드.md` v1 (이 파일이 v2 보강)

---

## 변경 이력

- **2026-04-27 v2.1**: 첫 cron 실행 결과 반영
  - §1 자동 위임 트리: 1행 GPT-Image 2 갱신, 1-b Interactive Learning 추가, 8행 macOS 전용 보류 명시
  - §2 ChatGPT 섹션: GPT-5.5 기본 모델 명시, Interactive Learning·GPT-Image 2 공식 수치 갱신, 보류 큐 신설
  - 백업: `외부_LLM_자율운영_시스템_v2.md.bak.20260427`
  - 발견 보고서: `_AI진화일지/외부LLM_학습_2026-04-27.md`

- **2026-04-28 v2.2**: Gemini 학습일 결과 반영
  - §1 자동 위임 트리:
    - 3행 → "Gemini Deep Research Max" 명시 (DeepSearchQA 93.3%·MCP·자동 차트·외부+사적 데이터, 2026-04-22)
    - 8행 → Gemini Mac Desktop App macOS 전용 추가 (4/15)
    - 9행 신설 → Gemini Workspace Intelligence (Gmail·Drive·Docs 통합 검색)
    - 10행 신설 → Gemini in Chrome (한국 출시 검증 필요)
  - §2 Gemini 섹션 전면 갱신: 기본 모델 Gemini 3.1 Pro 명시, Deep Research Max·Workspace Intelligence·한국어 확장·Nano Banana Pro·Gem 공유, 보류 큐 7개 신설
  - 백업: `외부_LLM_자율운영_시스템_v2.md.bak.20260428`
  - 발견 보고서: `_AI진화일지/외부LLM_학습_2026-04-28.md`
