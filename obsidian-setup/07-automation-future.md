# 다음 단계 자동화 (Future Automation)

> 이 키트는 Capture 레이어 기본을 Web Clipper로 완성한다.
> 추가 자동화는 vault가 자리 잡은 후(2~4주) 도입 권장.

## 4-Layer 진행 상황

| Layer | 이 키트 상태 | 다음 단계 |
|---|---|---|
| L1 Capture | ✅ Web Clipper (글/X/유튜브) | + N8N Telegram bot, Whisper, 통화 전사 |
| L2 Automation | ✅ Smart Rules, AI Interpreter | + N8N 라우팅, 스케줄 |
| L3 Memory | ✅ Vault (5폴더, Google Drive) | + 정기 lint, archive |
| L4 Intelligence | ✅ Claude Code + MCP | + Daily Brief 자동화, Slack/Calendar MCP |

## 추가 자동화 옵션 (난이도 순)

### 1. Daily Brief 6am 자동 실행 (가장 큰 ROI)

**왜**: 매일 아침 vault가 먼저 말 걸어옴 (CyrilXBT 핵심).

**필요한 것**:
- N8N (셀프호스팅 또는 cloud)
- Anthropic API 키 (Web Clipper와 같은 거 재사용)
- Obsidian MCP (이미 셋업됨)

**워크플로우**:
```
Cron Trigger (매일 06:00)
  → Read Files (vault의 inbox/ + notes/ 지난 7일)
  → Claude API (prompts/daily-brief.md의 프롬프트)
  → Write File (inbox/brief-{date}.md)
  → (옵션) Email 또는 Slack 알림
```

N8N 미사용 시 대안:
- Windows Task Scheduler + PowerShell + curl로 Claude API 호출
- Anthropic SDK Python 스크립트 + Windows 작업 스케줄러

### 2. N8N Telegram Bot — 즉시 캡처

**왜**: 모바일에서 떠오른 아이디어를 메시지 한 번으로 vault에.

**셋업** (30분, CyrilXBT 원본):
1. BotFather에서 봇 생성 → 토큰 발급
2. N8N에 새 워크플로우:

```
Node 1: Telegram Trigger
  - event: message
  - chat_id: <your_chat_id>

Node 2: Code (format note)
  - filename: inbox/{{$now.format("yyyy-MM-dd-HHmmss")}}-quick-capture.md
  - content:
    # Quick Capture
    {{$json.message.text}}

    ---
    Source: Telegram
    Date: {{$now.format("yyyy-MM-dd HH:mm")}}

Node 3: Write File to Obsidian vault
  - path: C:/Users/<USER>/Google Drive/Vault/brain/inbox/
  - operation: create
```

3. 봇과 첫 메시지로 chat_id 확인 (`/start`)
4. N8N 활성화 → 텔레그램에서 메시지 보내면 vault에 자동 생성

### 3. Whisper 음성 받아쓰기

**왜**: 운전 중/산책 중 떠오른 아이디어를 음성으로.

**옵션 A: OpenAI Whisper API (간단, $0.006/분)**
- Telegram 봇에 음성 파일 보냄
- N8N이 음성 받아서 Whisper API 호출
- 받아쓰기 결과를 vault inbox로

**옵션 B: 로컬 Whisper (무료, GPU 권장)**
- `whisper.cpp` 또는 `faster-whisper` 설치
- 폴더 watch → 새 mp3 파일이 들어오면 자동 받아쓰기
- 결과를 vault로

**옵션 C: macOS Shortcuts / Windows 음성 인식 (가장 간단)**
- OS 내장 받아쓰기 → 클립보드 → 자주 쓰는 스니펫

### 4. 통화 전사 자동 라우팅 (Cottrell)

**왜**: 회의/통화에서 결정/액션을 잊지 않게.

**필요한 도구**:
- Fathom / Otter / Fireflies / Krisp — 통화 전사
- Zapier / Make / N8N — Google Drive로 라우팅
- Claude (MCP) — 전사 읽고 vault에 정리

**워크플로우**:
```
[통화] → [전사 도구] → [Zapier watches] → [Google Drive /Transcripts/]
                                                 ↓
                                          [Claude Cowork (MCP)]
                                                 ↓
                            [extracts summary + decisions + actions]
                                                 ↓
                              [writes to vault: notes/, inbox/decisions.md,
                               inbox/action-tracker.md]
```

**Custom Instructions 추가**:
```
When processing a transcript from Google Drive /Transcripts/:
1. Read full transcript
2. Extract: summary (3 bullets), all decisions made, all action items (owner + deadline)
3. Write summary to notes/{date}-{participants}.md with #call tag
4. Append decisions to inbox/decisions.md
5. Append actions to inbox/action-tracker.md with [ ] checkbox
6. Move processed transcript to /Transcripts/processed/
```

### 5. Readwise → Obsidian (선택)

**왜**: Kindle 하이라이트, Twitter 북마크, Instapaper 등을 한 곳으로.

**상태**: Web Clipper로 대부분 대체 가능. Kindle 사용자가 아니면 필요성 낮음.

**셋업**:
1. Readwise 계정 ($8/월)
2. Readwise 공식 Obsidian 플러그인 설치
3. Settings에서 vault의 `notes/highlights/` 경로 지정
4. 자동 동기화 (매일)

### 6. Slack / Gmail / Calendar MCP (Claude Cowork 방향)

**왜**: vault + Slack + 캘린더 + 메일을 Claude가 통합 조회.

**셋업**:
- Claude Cowork (Anthropic 데스크탑 앱)
- 각 도구의 MCP 커넥터 활성화:
  - Google Drive
  - Google Calendar
  - Gmail
  - Slack
  - ClickUp / Linear / Jira (선택)

**효과**:
- "이번 주 뭐 있어?" → Calendar + vault의 projects 컨텍스트
- "client X 관련 최근 동향" → Slack + Gmail + vault notes 통합

## 우선순위 권장

vault 사용 2주 후 도입 순서:

1. **Daily Brief 자동화** (가장 큰 행동 변화)
2. **Telegram bot** (모바일 캡처 갭 해소)
3. **Whisper** (운전/산책 중 캡처)
4. **Slack/Calendar MCP** (업무용)
5. **통화 전사** (회의가 많은 경우만)
6. **Readwise** (Kindle 사용자만)

## 비용 추정 (월간)

| 항목 | 무료 | 유료 |
|---|---|---|
| Obsidian | ✅ | (Sync $5) |
| Claude API (Daily Brief + Web Clipper) | | ~$5~15 |
| N8N | 셀프호스팅 ✅ | Cloud $20 |
| Telegram Bot | ✅ | |
| Whisper (로컬) | ✅ | |
| Whisper (API) | | $1~5 |
| 통화 전사 (Fathom 무료 플랜) | ✅ 제한적 | $25+ |
| Readwise | | $8 |
| Zapier (Free plan, 100 tasks/월) | ✅ | $20+ |
| **최소 구성 합계** | $0 | ~$5~15 |
| **풀 구성 합계** | | $50~80 |

## 자동화 안티패턴

피할 것:

- ❌ vault에 들어오기 전에 너무 많이 변환 — raw를 우선 저장, 정제는 나중
- ❌ 모든 캡처에 AI Interpreter 적용 — 빠르고 싸지만 누적되면 비싸짐. 가치 있는 것만
- ❌ 자동화 자체가 새로운 일이 되는 것 — "도구 만지는 시간 > 생각하는 시간"이면 잘못된 방향
- ❌ Vault를 자동으로 정제 — Claude가 inbox를 자동 분류하게 두지 말 것. 인간의 큐레이션이 핵심 가치

## 다음에 읽을 것

- N8N Telegram → Obsidian 워크플로우 템플릿 (CyrilXBT 공유 예정)
- Anthropic API Cookbook의 RAG/Claude over docs 예제
- Karpathy의 "The art of the LLM wiki"
