# Philosophy — 왜 이렇게 만드는가

## 한 문장 요약

> Vault의 목표는 **조직화가 아니라 인지(cognition)**다. 정보를 저장하는 vault는 죽은 묘지일 뿐이고, 시스템은 매일 당신에게 **말을 걸어와야** 한다.

## 세 가지 실패 모드 (CyrilXBT)

대부분의 second brain이 실패하는 이유:

1. **캡처 마찰** — 추가가 10초를 넘으면 인지 부하 아래서 무너진다
2. **연결 레이어 부재** — 노트들이 고립된 채로만 쌓인다
3. **돌아올 이유 없음** — vault가 먼저 인사이트를 푸시하지 않으면 결국 안 연다

> "A second brain that never talks back is not a second brain. It is a very organized way to forget things." — CyrilXBT

이 키트는 세 가지 모두를 해결한다:
- **캡처**: Web Clipper + AI Interpreter로 10초 미만
- **연결**: Claude가 vault 전체를 읽고 패턴 찾음
- **돌아옴**: Daily Brief가 매일 아침 vault에 먼저 도착해 있음

## 4-Layer 아키텍처 (Dwivedi / CyrilXBT 공통)

```
┌─────────────────────────────────────────┐
│  Layer 4: Intelligence (Claude)         │  ← 패턴, 모순, 시너지 발견
├─────────────────────────────────────────┤
│  Layer 3: Memory (Obsidian)             │  ← 영구 컨텍스트 저장
├─────────────────────────────────────────┤
│  Layer 2: Automation (Pipeline)         │  ← N8N, MCP, Web Clipper
├─────────────────────────────────────────┤
│  Layer 1: Capture (Web Clipper, etc.)   │  ← 마찰 0의 입력
└─────────────────────────────────────────┘
```

각 레이어는 하나의 역할만. 겹치지 않음. 단방향 흐름.

이 키트의 매핑:
- **L1 Capture**: Obsidian Web Clipper (+ 미래의 Telegram bot/Whisper)
- **L2 Automation**: Smart Rules, AI Interpreter, Obsidian Git
- **L3 Memory**: Vault (5폴더, Google Drive 안)
- **L4 Intelligence**: Claude Code + kepano/obsidian-skills + MCP + CLAUDE.md

## 5-Piece 시스템 (Cottrell)

운영 관점에서 같은 그림을 5조각으로:

1. **Obsidian** — 무료, 평문 마크다운, 평생 lock-in 없음
2. **Capture → Drive** — 통화/하이라이트/음성이 자동으로 클라우드 폴더에
3. **Obsidian MCP** — Claude가 vault를 직접 read/write
4. **Claude Cowork + MCP connectors** — Slack, Calendar, Gmail 등으로 확장
5. **Custom Instructions 한 줄** — "답변 전 항상 vault 검색" — 이게 전부 묶는 풀

## CLAUDE.md가 가장 중요한 파일인 이유

> "Most people use AI like a temp worker with amnesia." — Cottrell
> "The most important file in this entire system is not your notes. It's CLAUDE.md." — Dwivedi

Claude는 매 세션이 처음이다. 컨텍스트가 없으면:
- 답이 일반론적이다
- 본인 상황을 모르는 답이 나온다
- 매번 본인 소개를 다시 해야 한다

CLAUDE.md가 있으면:
- 모든 세션의 시작점이 동일
- "당신을 몇 달 알아온 동료"처럼 답함
- vault 라우팅 규칙도 여기에 적어두면 Claude가 새 노트 위치도 알아서 결정

## "Vault should talk back" — Daily Brief / Weekly Synthesis

CyrilXBT의 핵심 컨트리뷰션:

### Daily Brief (매일 아침)
Claude가 지난 24시간의 inbox + 지난 7일의 notes를 읽고:
- **CONNECTIONS**: 못 본 연결 3개
- **PATTERN**: 무의식적으로 작업 중인 주제
- **QUESTION**: 오늘 앉아서 생각할 가치 있는 질문 하나

### Weekly Synthesis (매주 월요일 15분)
Claude가 vault 전체를 읽고:
- **EMERGING THESIS**: 명시하지 않았지만 형성 중인 입장
- **CONTRADICTIONS**: 과거 신념과 충돌하는 최근 저장물
- **KNOWLEDGE GAPS**: 안 읽고 있는데 읽어야 할 관점
- **ONE ACTION**: 가장 레버리지 큰 하나의 행동

이 두 가지가 vault를 살아있게 만든다.

## 폴더 단순함의 원칙 (CyrilXBT)

> "Every complex folder structure eventually collapses under its own weight."

→ **5폴더만**:
- `inbox/` — 미정제, 일단 여기
- `notes/` — 정제된 외부 자료
- `ideas/` — 내 사고
- `projects/` — 진행 중 작업
- `templates/` — 양식

규칙: "어디 둘지 헷갈리면 inbox."

Zettelkasten의 fleeting/literature/permanent는 **폴더 대신 태그**로:
- `#fleeting` — 휘발성 메모
- `#literature` — 외부 출처
- `#permanent` — 자기 언어로 재구성

## "Context is the moat" (Dwivedi)

> "The actual moat in the AI era is not prompts, not tools, not models. **Context.**"

매일 0에서 시작하는 사람 vs 6개월 누적 컨텍스트로 시작하는 사람.
이 격차는 더 열심히 해서 따라잡을 수 없다. **일찍 시작해야만** 좁힐 수 있다.

## 시작 규모: 5개 노트 (Dwivedi / CyrilXBT 공통)

완벽한 셋업을 기다리지 마라:

> "Start with five notes tonight. The vault does the rest." — CyrilXBT

5개:
- 기억할 가치 있는 아이디어 5개
- 자꾸 돌아오는 질문 5개
- 잃고 싶지 않은 인사이트 5개

그리고 Claude에게 한 문장:
> "What patterns do you see that I'm missing?"

이 키트의 `starter-notes/`가 정확히 이 5개를 제공한다.

## 컴파운딩 효과

- **1개월**: 유용한 도구로 느껴짐
- **3개월**: 지능적으로 느껴짐 — 8주 전 노트를 정확히 끌어옴
- **6개월**: 거의 unfair — 본인이 잊은 약속, 모순된 신념을 vault가 기억함

이 격차는 조용히 백그라운드에서 쌓인다.
대부분의 사람은 그 가치를 따라잡기 힘들 만큼 늦어진 뒤에야 깨닫는다.

## 이 키트의 약속

- **마찰 0** 캡처 (Web Clipper)
- **단순한 구조** (5폴더)
- **풍부한 컨텍스트** (CLAUDE.md)
- **매일 말 거는** vault (Daily Brief)
- **검증된 도구들** (kepano/obsidian-skills + MCP)

당신의 역할은 시스템을 유지하는 게 아니라 **생각하는 것**이다.
