# Remote Control 셋업 SOP — 직장 모바일 ↔ 종환 PC 24시간

> **시나리오**: PC 24시간 켜둠 → 출근 → 직장 모바일 Claude Code 앱 → "Jonghwan PC (24h)" 세션 tap → 명령 → PC에서 즉시 실행 → 결과는 vault/GD에 저장 → 모바일에서 GD로 확인.

---

## 동작 원리 (공식 문서: https://code.claude.com/docs/en/remote-control)

```
[종환 모바일 (직장)]                  [Anthropic Cloud API]                  [종환 PC (집, 24h)]
   Claude Code 앱           ←HTTPS poll→     세션 registry      ←HTTPS outbound→     claude remote-control
                                                                                        ↑
                                                                              PowerShell loop이 영구 유지
                                                                              (crash 시 5초 후 재시작)
```

- PC가 **outbound HTTPS only** (inbound 포트 X) — 방화벽·공유기 설정 불필요
- 네트워크 단절 10분 이상 → timeout → 프로세스 종료 → loop 재시작
- PC sleep 차단 필수 (`powercfg /change standby-timeout-ac 0`)

---

## 셋업 (PC에서 1회, 약 2분)

### 1. 사전 요구

- Windows 10/11
- Claude Code CLI 설치 확인:
  ```powershell
  claude --version
  # 없으면: npm i -g @anthropic-ai/claude-code
  ```
- ubermensch 레포 clone:
  ```powershell
  cd C:\Users\윤상택
  git clone https://github.com/ubermensch90623/ubermensch.git
  cd ubermensch
  ```

### 2. dry-run으로 안전 확인

```powershell
.\scripts\setup_remote_control.ps1
```

`[DRY-RUN]` 항목들 검토. 어떤 명령이 실행될지 미리 봄.

### 3. 실제 적용

```powershell
.\scripts\setup_remote_control.ps1 -Apply
```

자동 진행:
1. `powercfg` 4개 (standby·hibernate·monitor sleep 차단, hibernate off)
2. `claude_remote_control_loop.ps1` → `~\.hermes\scripts\` 복사
3. Task Scheduler `Hermes_ClaudeRemoteControl_Autostart` 등록 (logon trigger, HIGHEST 권한)
4. 즉시 1회 실행

### 4. 검증 (30초 대기 후)

```powershell
# heartbeat 확인 (START 라인 1+개)
Get-Content $env:USERPROFILE\.hermes\logs\claude_remote_control_heartbeat.log -Tail 5

# Task Scheduler 등록 확인
schtasks /query /tn Hermes_ClaudeRemoteControl_Autostart
```

모바일 Claude Code 앱 → sessions → **"Jonghwan PC (24h)"** 표시 확인.

---

## 모바일 사용 (직장에서)

1. **Claude Code 앱** 열기 (iOS/Android)
2. Sessions 목록에서 `Jonghwan PC (24h)` tap
3. 텍스트 박스에 명령:
   - `/ncs-tutor` → NCS 1문제 풀이판 생성
   - `/jaso-reviewer` → 자소서 검토
   - `오늘 인지진화 가중치 갱신해줘` → cycle E 트리거
4. PC에서 즉시 실행 → vault에 결과 저장 → GD mirror 30분 cycle로 모바일 GD 앱에서 확인 가능

### 자주 쓰는 명령 (출퇴근 시나리오)

| 시각 | 명령 | 효과 |
|---|---|---|
| 07:20 출근 | `오늘 1문제` | NCS 약점 1문제 풀이판 → preview HTML → 모바일 학습 |
| 12:30 점심 | `자소서 KEPCO v2 검토` | jaso_validator gate 통과 후 핸드오프 |
| 17:30 퇴근 직전 | `오늘 학습 회고 + 내일 P0 액션` | cycle B+D 트리거 |
| 22:00 (자동) | `cron 자동 발화` | cognitive-evolution-loop 4사이클 |

---

## 트러블슈팅

### "연결 해제됨" 표시

원인:
1. PC sleep / power off → `powercfg` 적용 안 됐을 수 있음, 재확인:
   ```powershell
   powercfg /query SCHEME_CURRENT SUB_SLEEP
   # STANDBYIDLE = 0x00000000 확인
   ```
2. `claude remote-control` 프로세스 종료 → loop이 재시작했는지 heartbeat 로그 확인
3. 인터넷 단절 10분 이상 → 복구 시 loop이 자동 재시작 (heartbeat에서 END·START 짝 확인)
4. Task Scheduler 비활성 → `schtasks /query /tn Hermes_ClaudeRemoteControl_Autostart`

### Loop이 너무 빨리 재시작 (CPU 100%)

`claude_remote_control_loop.ps1`에 안전장치 박혀 있음:
- 30초 미만 종료 시 "연속 실패" 카운트
- 5회 연속 실패 시 5분 백오프

그래도 안 되면: `claude --help`에 `remote-control` 명령 존재 확인. 없으면 CLI 버전 업그레이드:
```powershell
npm i -g @anthropic-ai/claude-code@latest
```

### 모바일 앱에 세션 안 보임

1. Anthropic 계정 동일 확인 (PC `claude /login`과 모바일 앱 같은 계정)
2. PC 재로그인:
   ```powershell
   claude /login
   ```
3. Task 수동 실행:
   ```powershell
   schtasks /run /tn Hermes_ClaudeRemoteControl_Autostart
   ```

### 한글경로 UnicodeError

PowerShell 콘솔에:
```powershell
chcp 65001
$env:PYTHONIOENCODING = "utf-8"
```

설정해도 안 되면 Windows 시스템 locale UTF-8 활성:
설정 → 시간 및 언어 → 언어 → 관리 언어 설정 → 시스템 로캘 변경 → "Beta: 세계 언어 지원을 위한 Unicode UTF-8 사용" 체크 → 재부팅

---

## 보안 주의

- `claude remote-control`은 **모바일에서 PC의 모든 파일·명령 접근 가능**. 분실 시 즉시 anthropic 토큰 회수.
- 종환 PC `~/.claude/settings.json` permissions가 그대로 적용됨 — Bash·Edit·Write 다 allow 상태라 신중.
- 민감 파일(`.credentials.json` 등) Claude가 안 건드리도록 명시. CLAUDE.md `Do NOT` 섹션에 추가 권장.

---

## 자동화 추가 (선택)

### A. 매일 05:00 — 학습판 자동 생성 (모바일에서 일어나자마자 확인)

```powershell
schtasks /create /tn Hermes_MorningQuiz `
  /tr "powershell -NoProfile -Command claude /ncs-tutor '오늘 약점 1문제 풀이판 생성'" `
  /sc daily /st 05:00 /rl HIGHEST
```

### B. 매시간 — vault → GD mirror (이미 MEMORY.md `gd-mirror-30m` 있으면 skip)

종환의 기존 `gd_mirror.ps1` 사용.

### C. 매일 22:00 — cognitive-evolution-loop 자동 발화

종환의 기존 cron `ab8935cf9923` 또는 PowerShell loop으로 이미 설정됨.
