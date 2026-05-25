# Hermes 로컬 PC 세팅 SOP

> 윈도우 PC(`C:\Users\윤상택\`)에서 처음부터 Hermes 시스템을 구축하거나 새 노트북 복원할 때.
>
> 출처: GD `_SSOT/hermes_집도착_즉시작동.md` + `새_노트북_복원_SOP.md` (2026-05-24 sync)

---

## 0. 환경 확인 (1분)

```powershell
chcp 65001                             # UTF-8 console
$env:PYTHONIOENCODING = "utf-8"        # 한글경로 안전
python --version                       # 3.13 확인
node --version
git --version
```

## 1. Hermes Agent 본체 설치 (5분)

```powershell
# pip 설치
pip install --upgrade nous-hermes-agent

# 또는 git
git clone https://github.com/NousResearch/hermes-agent C:\Users\윤상택\.hermes
cd C:\Users\윤상택\.hermes
pip install -e .
```

## 2. OAuth Ban 우회 — openrouter API 키 (필수, 4/4 이후)

Anthropic Pro/Max OAuth로 Hermes daemon이 `claude -p` subprocess 호출 시 **2026-04-04부터 BadRequestError**. 회피 필수.

```powershell
# 옵션 A: ANTHROPIC API 키 (pay-as-you-go, console.anthropic.com)
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# 옵션 B: openrouter 경유 (Hermes 검증 ✅)
$env:OPENROUTER_API_KEY = "sk-or-..."
```

`config.yaml`:
```yaml
model: google/gemini-2.5-flash
provider: openrouter
auxiliary:
  vision:
    model: google/gemini-2.5-flash
```

## 3. hermes-CCC 설치 (Claude Code 스킬 46개, 5분)

```powershell
git clone https://github.com/AlexAI-MCP/hermes-CCC C:\Users\윤상택\hermes-CCC
cd C:\Users\윤상택\hermes-CCC
.\install.ps1
```

→ `~\.claude\skills\`에 46개 스킬 복사. Claude Code 재시작 후 슬래시 명령(`/hermes-route` 등) 활성.

## 4. Persona 4개 등록 (config.yaml)

`C:\Users\윤상택\.hermes\config.yaml`의 `agent:` 아래:

```yaml
agent:
  personalities:
    ncs_tutor: >
      너는 종환 NCS 박사급 튜터다. 수리 1.2, 통계 2.0, 문제해결 1.3 약점.
      매 문제 5초 빠른풀이 → 단계별 풀이 → 함정 식별 → 정답 순서.
      트리거 단어/공식/정의식 답안 옆 노출 금지. 한 번에 1문제만.
      평문/유니코드만 (LaTeX 금지). 종환 사고 역추적 기록부 반영.

    econ_professor: >
      너는 종환 경제학 박사급 해설자. 13권 학습 프로토콜 기반.
      개념→왜→사고추적→선지판별→헷갈리는 개념 비교 5단계 강제.
      그래프 ASCII 금지. 좌표/곡선은 Comet 프롬프트로만.
      NotebookLM/Gemini 자료 적극 인용.

    jaso_reviewer: >
      너는 종환 자소서 박사급 검토자. jaso_validator gate 통과 후만 OK.
      팩트체크(자격증/경력) → 금지어 필터 → 주어 일관성 → 3중 검토.
      캠코 실패 패턴(자격증 누락·주어혼동) 절대 재발 금지.

    jeonse_advisor: >
      너는 종환 전세금 1.25억 회수 박사급 자문. HIGH-STAKES.
      공식 1차 자료(.go.kr/HUG/법원/세무서)만. 블로그/2년 자료 절대 금지.
      추측 NEVER. 법무사 위임 + HUG 직접 방문 워크플로.
```

호출: `/personality ncs_tutor` 등.

## 5. notebooklm CLI (NotebookLM 자동화)

```powershell
pip install notebooklm-py
notebooklm login                       # 브라우저 OAuth
notebooklm list                        # 인증 확인
notebooklm language set ko
```

## 6. PATH 충돌 방지

Hermes 내부 Node가 `.hermes\node\bin\claude`를 점유 → Claude Code CLI 본체가 가려질 수 있음.

```powershell
# symlink로 Claude Code CLI 명시 우선
New-Item -ItemType SymbolicLink -Path "C:\Users\윤상택\bin\claude.cmd" -Target "<진짜 claude path>"
$env:PATH = "C:\Users\윤상택\bin;" + $env:PATH
```

## 7. cron · PowerShell loop · Task Scheduler

자율 작동 5개 cron (Hermes 본체) + 4개 PowerShell loop + Task Scheduler 1개.

| 종류 | 이름 | 주기 | 역할 |
|---|---|---|---|
| Hermes cron | `ab8935cf9923` | 30분 | vault `hermes_daily/` append |
| Hermes cron | `vault-sync-15m` | 15분 | USER/MEMORY ↔ vault 양방향 sync |
| Hermes cron | `vault-ingest-daily` | 06:30 daily | 4영역 delta → MEMORY.md |
| Hermes cron | `screen-monitor-ncs` | 30분 | 화면 캡처 + vision_analyze |
| Hermes cron | `gd-mirror-30m` | 30분 | GD 5TB 데이터센터 mirror |
| PS loop | `hermes_loop_5m_v2.ps1` | 5분 | sync · ingest · tick · heartbeat |
| PS loop | `hermes_loop_1h.ps1` | 1시간 | jeonse · ncs · jaso 스크립트 |
| PS loop | `hermes_llm_hourly_v2.ps1` | 1시간 | LLM cron 5 task |
| PS loop | `gd_mirror.ps1` | 30분 | 5 폴더 robocopy |
| Task Scheduler | `Hermes_loop_5m_autostart` | 로그온 | 재부팅 후 자동 시작 |

PS loop 등록:
```powershell
schtasks /create /tn Hermes_loop_5m_autostart /tr `
  "powershell -ExecutionPolicy Bypass -File C:\Users\윤상택\.hermes\scripts\hermes_loop_5m_v2.ps1" `
  /sc onlogon /rl HIGHEST
```

## 8. GD 데이터센터 mirror (1GB)

`G:\내 드라이브\04_시스템\Hermes_데이터센터\` (5 폴더):
- `01_vault\` (Obsidian 전체)
- `02_hermes_full\` (.hermes 풀)
- `03_claude_code\` (.claude 풀)
- `04_desktop_files\` (dashboard · 트리거)
- `05_HERMES_install\` (hermes-CCC repo)

`gd_mirror.ps1`:
```powershell
robocopy "C:\Users\윤상택\.hermes" "G:\내 드라이브\04_시스템\Hermes_데이터센터\02_hermes_full" /MIR /XD logs cache
robocopy "C:\Users\윤상택\.claude"  "G:\내 드라이브\04_시스템\Hermes_데이터센터\03_claude_code" /MIR /XD logs cache
robocopy "C:\Users\윤상택\Desktop\작업\ObsidianVault" "G:\내 드라이브\04_시스템\Hermes_데이터센터\01_vault" /MIR
```

## 9. 알려진 함정 (Windows · 한글경로)

1. `tools.memory_tool: No module named 'fcntl'` — Unix only, Windows 우회 X
2. `xterm-256color` 또는 `No Windows console found` — Hermes tool 사용 시 cmd 강제
3. `config.yaml` 한글 → UnicodeDecodeError (`hermes gateway status` 실패)
4. PowerShell 로그 cp949 일부 깨짐 — 작동 영향 X, 가독성만. UTF-8 BOM 강제 권장
5. GD 한글 폴더명 → robocopy OK, sed/awk 일부 패턴 매칭 실패
6. PC 절전·hibernate → cron 정지. `powercfg /change standby-timeout-ac 0` 필수

## 10. 검증 (도착 후 5분 안에)

```powershell
# 1. Hermes 응답 확인
hermes gateway status

# 2. cron 5개 active 확인
hermes cron list

# 3. personality 4개 등록 확인
hermes personality list

# 4. PowerShell loop 마지막 heartbeat 확인
Get-Content C:\Users\윤상택\.hermes\logs\heartbeat.log -Tail 5

# 5. GD mirror 마지막 sync 시각 확인
Get-Item "G:\내 드라이브\04_시스템\Hermes_데이터센터\02_hermes_full" | Select LastWriteTime
```

5개 다 OK = 시스템 정상.

---

## 클라우드 세션(Claude Code on the Web) 권한 확장

이 ubermensch 레포의 클라우드 세션에서 `jonghwan-claude-config` 같은 다른 깃허브 레포까지 접근하려면 환경 설정 변경 필요.

**문서**: https://code.claude.com/docs/en/claude-code-on-the-web

1. Claude Code on the Web 좌상단 환경 설정 → 이 ubermensch 환경 편집
2. **GitHub 권한**에 다음 레포 추가:
   - `ubermensch90623/jonghwan-claude-config` (private)
   - `ubermensch90623/learning-automation` (private)
   - `ubermensch90623/ncs-trainer` (public)
3. **Network policy** 검토 — Hermes 본체 받으려면 `huggingface.co`, `ollama.com` 허용 필요 (현재 차단)
4. 새 세션 시작 시 적용됨
