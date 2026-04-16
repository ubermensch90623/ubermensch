# 경연(經筵) 안건서 — LLM / Harness / Wiki 전수조사 및 온고지신 업그레이드

> 개최일: 2026-04-16
> 안건: 사용자 지시 "모든 설치된 github에서 llm wiki, harness 등등 싹다 전수조사해서 바꿀건 바꿔 무조건 다 바꾸지 말고 온고지신으로"
> 프로세스: C-4 경연 거버넌스. 박사팀 안건 정리 → 사용자 판결.
> ⚠ 모든 분석은 C-0 준수 (출처 URL 동반, 단정 금지, 격리 원칙).

## 1. 현재 설치 상태 (Inventory, 2026-04-16)

| 구성 | 위치 | 상태 | 유지 가치 |
|---|---|---|---|
| `~/.claude/settings.json` | 로컬 | 최소 구성 (Stop hook + Skill 권한) | **유지 권장** (작동 중, 간결) |
| Stop hook `stop-hook-git-check.sh` | `~/.claude/stop-hook-git-check.sh` | git 미커밋/untracked 차단 | **유지 필수** (C-0 데이터 유실 방지) |
| Skill `session-start-hook` | `~/.claude/skills/session-start-hook` | 설치되어 있음. 내용 미확인 | **검토 권장** (프로젝트 맞춤 확장 가능) |
| MCP 서버 | 설정에 없음 | 내장 GitHub MCP 만 활용 중 | 현 상태 유지 (추가 도입은 중대사) |
| 프로젝트별 `.claude/` | `/home/user/ubermensch/.claude` 없음 | — | CLAUDE.md 로 대체 중 (충분) |

## 2. GitHub 공개 OSS 조사 결과 (2026-04-16 WebSearch)

### A. Claude Code 생태계 큐레이션
- [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) — skills·hooks·slash-commands·agent orchestrators 큐레이션
- [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit) — 135 agents, 35 skills, 176+ plugins
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) — 1000+ skills
- [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) — 100+ 전문 서브에이전트

### B. Agent 하네스 (user 가 언급한 "harness")
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) — "agent harness performance optimization system. Skills, instincts, memory, security, research-first development"
  - Claude Code Hackathon (Cerebral Valley × Anthropic, 2026-02) 산물
  - 1282 tests, 98% 커버리지, 102 정적 분석 규칙
  - **매우 관련**. 우리 프로젝트의 "에이전트 인프라" 개선 후보

### C. Claude Code 시스템 프롬프트 공개 (메타 통찰)
- [Piebald-AI/claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts) — Claude Code 자체의 system prompt + 24 built-in 도구 설명 + 서브에이전트 프롬프트 공개 (v2.1.107, 2026-04-13 기준)
  - 가치: 에이전트 프롬프트 설계 시 참고 가능 (표준 패턴 학습)

### D. LLM 평가 하네스 (평가·채점 메타)
- [EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) — 범용 LLM 평가 프레임워크
  - 한국어 태스크 지원: **haerae, kmmlu, kobest, kormedmcqa, paws-x, csatqa**
  - NCS·공기업 필기 태스크는 **없음** (공개 기준)
- [lbox-kr/lm-evaluation-harness-kbl](https://github.com/lbox-kr/lm-evaluation-harness-kbl) — 한국 법조 평가 벤치마크 (KBL, 2510 examples, 법무 domain)
  - 가치: 서민금융 법령 영역과 **일부 중첩 가능성**. 참고 자료로 유용.

### E. 한국어 NLP 리소스
- [datanada/Awesome-Korean-NLP](https://github.com/datanada/Awesome-Korean-NLP)
- [insikk/awesome-korean-nlp](https://github.com/insikk/awesome-korean-nlp)
- [ko-nlp/Open-korean-corpora](https://github.com/ko-nlp/Open-korean-corpora)
- 가치: KINFA 전용 데이터는 없으나 **법률 코퍼스·일반 한국어 NLP 리소스** 로 간접 도움

### F. Claude Code 베스트 프랙티스
- [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice)
- [ChrisWiles/claude-code-showcase](https://github.com/ChrisWiles/claude-code-showcase)
- [FlorianBruniaux/claude-code-ultimate-guide](https://github.com/FlorianBruniaux/claude-code-ultimate-guide)
- [levnikolaevich/claude-code-skills](https://github.com/levnikolaevich/claude-code-skills)
- 가치: 우리 프로젝트의 skill / hook / CLAUDE.md 구조 비교·보강 기준

## 3. 박사팀 분석 — 변경 후보 (온고지신)

### 🟢 유지 (안정 작동, 변경 불요)
- `~/.claude/settings.json` 현 구성 (Stop hook + Skill 권한)
- Stop hook 스크립트 (git 체크) — 프로젝트 C-0 준수에 직결
- 프로젝트 내 CLAUDE.md 구조 (C-0~C-5 헌법 + 상세 지침)
- corpus 모듈 자체 (이미 격리·혈통 추적 설계)

### 🟡 검토·부분 도입 후보
- **O1. `everything-claude-code` 의 agent harness 패턴** 일부 차용 (예: memory·instincts 개념)
  - 리스크: 큰 의존성 도입. 우리 stdlib-only 원칙과 충돌 여지
  - 기회: P1~P9 에이전트 오케스트레이션 체계화
- **O2. `claude-code-system-prompts` 참고하여 서브에이전트 프롬프트 개선**
  - 리스크: 없음 (참고용 읽기만)
  - 기회: 현재 P9 템플릿 등 품질 향상
- **O3. Korean lm-evaluation-harness-kbl** 법률 태스크를 참고하여 corpus 의 "법률 영역 문항 구조" 보강
  - 리스크: 없음 (참고 자료 수준)
  - 기회: 서민금융 법령 관련 문항 분류 체계 정교화

### 🔴 신중·거부 권장
- **X1. `awesome-claude-code-toolkit` 135 agents 전체 도입**: 과잉. 우리 프로젝트 7 페르소나로 충분.
- **X2. MCP 서버 신규 설치 (예: filesystem, github)**: GitHub MCP 는 이미 내장. 추가 도입은 복잡도 증가 대비 이득 불분명.
- **X3. 외부 의존성(pip install) 대량 도입**: stdlib-only 원칙 유지. 꼭 필요한 것만 중대사로 별도 승인.

## 4. 수석위원 SC1·SC2 사전 검토 (가상 심사)

### SC1 의견
> 현재 설치된 인프라는 안정 작동 중. 과도한 교체는 C-0 스노우볼 유발 위험 (새 도구가 검증되지 않았으므로).
> 권고: 🟢 유지 다수 + 🟡 중 O2(참고용 읽기) 만 즉시 반영. O1·O3 은 사용자 우선순위 확인 후.

### SC2 의견
> C-5 (생성 원리 상호 의심) 이행 관점에서 외부 에이전트 패턴을 도입할 땐 **해당 에이전트의 추론 메커니즘** 까지 감사해야 함.
> `everything-claude-code` 는 테스트 커버리지 98% 주장이나 우리 프로젝트와 유즈케이스가 다름. 직접 도입 보다 **설계 영감** 만 차용 권고.

### 두 수석위원 합의
- 🟢 전부 유지
- 🟡 O2 채택 (참고 읽기, 위험 0)
- 🟡 O1·O3 는 **사용자 판결** 후 진행
- 🔴 거부

## 5. 사용자 판결 필요 사항 (경연 옵션)

### 옵션 A — 최소 개입 (보수)
- 현재 인프라 유지
- O2 만 참고 읽기로 반영 (서브에이전트 프롬프트 품질 개선에 활용)
- 작업: 즉시 가능. 외부 의존성 0.

### 옵션 B — 중간 개입 (선별 도입)
- 옵션 A + **O3 lm-eval-harness-kbl 태스크 구조** 를 corpus 의 법률 영역 분류 체계에 반영
- O1 (everything-claude-code 의 memory·instincts 개념) 은 우리 CLAUDE.md 와 호환 부분만 설계 영감 차용 (코드 복사 X)
- 작업: 설계 문서 작업 + 경미한 구조 보강. 외부 의존성 0.

### 옵션 C — 공격적 도입 (리스크 有)
- 옵션 B + 외부 하네스 부분 코드 차용 (라이선스 확인 후)
- 일부 MCP 서버 추가 (예: filesystem MCP 로 로컬 파일 직접 접근 개선)
- 작업: 외부 의존성 도입. C-4 중대사 재승인 필요.

### 수석위원 권고
**옵션 A 또는 B**. 옵션 C 는 스노우볼 리스크 큼 (새 도구의 추론 메커니즘 전수 감사 필요).

## 6. 비결정 항목 (사용자 추가 지시 시 반영)
- 특정 skill/subagent 를 우리 `~/.claude/skills/` 에 설치 여부 — 사용자 요청 있을 때만.
- Korean NLP 리소스 중 특정 데이터셋 반입 여부 — 구체적 필요 발생 시 별도 경연.

## 7. 산출물 (이 경연의 출력)
- 본 안건서 (`docs/gyeongyeon/2026-04-16_llm-harness-wiki-전수조사.md`)
- 사용자 판결 후 → 판결 내용 + 실행 결과 이 파일 말미에 추기
