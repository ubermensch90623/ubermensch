# ubermensch — 종환 학습 분신 (Hermes Agent on Claude Code)

> **너 = Hermes Agent. 종환의 학습 분신.** 자세한 헌법은 [`CLAUDE.md`](./CLAUDE.md).

## 빠른 진입 (1초)

| 폴더 | 내용 |
|---|---|
| [`CLAUDE.md`](./CLAUDE.md) | 헌법 LOCKED 7개 · persona 4 · 박-계열 12종 금칙어 · 박사급 룰 |
| [`.claude/skills/`](./.claude/skills/) | 52개 스킬 (hermes-CCC 46 + persona 4 + notebooklm + cognitive-evolution-loop) |
| [`.claude/settings.json`](./.claude/settings.json) | autocompact 50% · MCP 5개 allow · Notion deny · SessionStart hook |
| [`hooks/`](./hooks/) | 종환 PC `Desktop/.claude/hooks/`에 갖다 둘 Stop hooks (3개) |
| [`data/`](./data/) | 인지진화_가중치.json 패치 entries |
| [`docs/`](./docs/) | HERMES_LOCAL_SETUP · RECRUITMENT_SCAN_DIAGNOSIS |
| [`scripts/session_start.sh`](./scripts/session_start.sh) | 세션 시작 시 헌법 reminder + D-day 자동 inject |
| [`scripts/setup_remote_control.ps1`](./scripts/setup_remote_control.ps1) | **PC 24h daemon 셋업** — 모바일에서 PC 원격 제어 |
| [`scripts/claude_remote_control_loop.ps1`](./scripts/claude_remote_control_loop.ps1) | claude remote-control 영구 유지 loop |
| [`docs/REMOTE_CONTROL_SETUP.md`](./docs/REMOTE_CONTROL_SETUP.md) | 직장 모바일 ↔ 종환 PC 셋업 SOP |

## 최우선 3가지 (헌법)

1. **전세 1.25억 회수** — HIGH-STAKES, D-39 임차권등기, D-101 HUG. 공식 1차 자료만
2. **서금원 정규직 전환 필기** — 7월, D-약50일. NCS:직무 = 7:3
3. **8월 하반기 채용 7곳** — KEPCO·KHNP·KDIC·HF·SGI·신보·캠코, 자소서 28건

## 슬래시 명령

```
/ncs-tutor                  NCS 박사급 튜터 (수리 1.2·통계 2.0·문제해결 1.3 약점)
/econ-professor             경제학 박사급 해설자 (13권 학습, 5단계 강제)
/jaso-reviewer              자소서 박사급 검토자 (jaso_validator gate 통과 후만 OK)
/jeonse-advisor             전세 HIGH-STAKES 자문 (공식 1차 자료만)
/notebooklm                 NotebookLM CLI 자동화 (32 소스 · 347 노트북)
/cognitive-evolution-loop   22:00 KST 4사이클 자율 분신
/hermes-route               작업 복잡도 라우팅
/hermes-memory              메모리 prefetch/sync
/hermes-persona             persona 전환
... (전체 46개 hermes-CCC + 6개 종환 자체, .claude/skills/ 참고)
```

## 자가진화 누적 (2026-05-25)

PR #6에 severity 5 P0 3건 + severity 4 P1 4건 = **7건 머지** 완료. 남은 71건은 다음 cycle E (`/cognitive-evolution-loop`)에서 자동 갱신.

| # | severity | 산출물 | PC 적용 |
|---|---|---|---|
| 1 | 5 | `hooks/auto_morning_desktop_popup.py` | Stop hook → `Desktop/.claude/hooks/` |
| 2 | 4 | `data/학습_displacement_patch.json` | `jq` merge → `_SSOT/인지진화_가중치.json` |
| 3 | 4 | `hooks/jaso_validator.py` | Stop hook → `Desktop/.claude/hooks/` |
| 4 | 4 | `cognitive-evolution-loop/SKILL.md` cycle D.-1 LOCKED | `~/.claude/skills/` 교체 |
| 5 | 5 | `hooks/hermes_mvp_vault_sync.js` | MVP `<script>` 1줄 |
| 6 | 5 | `docs/RECRUITMENT_SCAN_DIAGNOSIS.md` | cron 등록 + catch-up 룰 prepend |
| 7 | 4 | 같은 SKILL.md cycle G-pre 5단계 grep | 위와 같이 교체 |

## 환경 분리

- **종환 윈도우 PC** (`C:\Users\윤상택\`): Hermes daemon · cron 5 · PowerShell loop 4 · Task Scheduler · 한글경로
- **이 클라우드 컨테이너**: Claude Code on the web. ephemeral. GitHub MCP 단일 레포(`ubermensch90623/ubermensch`)만 허용
- 양 환경 sync: GD 5TB 데이터센터(`G:\내 드라이브\04_시스템\Hermes_데이터센터\`) 통한 mirror

상세: [`docs/HERMES_LOCAL_SETUP.md`](./docs/HERMES_LOCAL_SETUP.md)

## CI

`.github/workflows/ci.yml` — PR마다 자동 검증:
- 모든 `hooks/*.py` Python syntax
- 모든 `hooks/*.js` JS syntax (node --check)
- 모든 `data/*.json` · `.claude/settings*.json` JSON 유효성
- 모든 `.claude/skills/*/SKILL.md` frontmatter `name` + `description` 존재
- 박-계열 금칙어 12종 grep (README · docs · hooks)
