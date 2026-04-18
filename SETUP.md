# 집 노트북(Windows) 원격 접속 + 자동 푸시 설정 가이드

외출 중 집 노트북의 Claude Code 작업 상태를 확인/이어받을 수 없었던 상황 재발 방지용 **3중 백업** 구축 가이드.

집 도착하면 **1 → 0 → 5 → 2 → 3 → 4** 순서로 진행. 각 단계에 **확인(Verify)** 이 포함돼 있으니 건너뛰지 말 것.

---

## 0. 사전 준비 체크 (모든 원격 접속의 공통 전제)

이게 안 돼 있으면 SSH·Chrome Remote Desktop 모두 실패한다.

### 0-1. Windows 사용자 계정 비밀번호
- **비번 없는 계정은 SSH 접속이 기본 차단**되고 Chrome Remote Desktop 로그인도 막힘.
- Microsoft 계정 로그인 시 PIN만 쓰는 경우도 **실제 비밀번호 따로 설정** 필요.
- 설정: `Ctrl+Alt+Del` → 암호 변경 → (현재 빈 값일 수 있음) → 신규 암호 지정.

### 0-2. 절전/화면/덮개 설정
```
설정 > 시스템 > 전원 및 배터리 > 화면 및 절전
- 화면 끄기: 안 함 (또는 30분)
- 절전 모드: 안 함

제어판 > 전원 옵션 > "덮개를 닫을 때의 동작 선택"
- 전원 연결 시: 아무 작업도 안 함
- 배터리 사용 시: 아무 작업도 안 함
```
덮고 외출해도 꺼지지 않게.

### 0-3. Wake on LAN은 쓰지 말 것
공유기·ISP에 따라 불안정. 대신 **항상 켜두기 + Tailscale**이 훨씬 안정적.

---

## 1. Claude Code 웹 전환 (가장 먼저, 기기 무관)

어떤 기기에서도 지금 바로 가능:

1. 브라우저에서 `https://claude.ai/code` 접속
2. GitHub 계정으로 로그인 → `ubermensch90623/ubermensch` 연결
3. `claude/resume-local-work-EiJIa` 브랜치에서 이어서 작업
4. **이후 장시간 작업은 웹에서** 시키기

### 주의
- 웹 세션도 레포 기반이므로 로컬에만 있던 파일은 보이지 않는다.
- **자동 푸시 훅(5번)을 먼저 켜놓는 것**이 웹 전환의 전제.

---

## 2. Windows OpenSSH 서버 설치

### 2-1. 관리자 PowerShell
```powershell
# 설치
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# 서비스 기동 및 자동시작
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# 방화벽 규칙 (이미 있으면 에러 무시)
if (-not (Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' `
        -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
}

# (선택) 기본 셸을 PowerShell로 변경 — Claude Code를 SSH로 실행할 때 편함
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell `
    -Value "C:\Program Files\PowerShell\7\pwsh.exe" -PropertyType String -Force
# pwsh 없으면: "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
```

### 2-2. Verify
```powershell
Get-Service sshd           # Status: Running 확인
Get-NetTCPConnection -LocalPort 22   # LISTEN 확인
```
같은 PC에서 테스트: `ssh <사용자>@localhost` → 비번 입력 → 프롬프트 뜨면 성공.

### 주의
- **ISP가 인바운드 22번 포트를 막는 경우가 흔함** → 공인 IP로 직접 SSH는 가급적 하지 말고 **Tailscale(3번) 경유**를 쓸 것.
- Windows Defender 말고 다른 보안 프로그램(V3, 알약 등) 있으면 방화벽 별도 허용 필요.

---

## 3. Tailscale + SSH (실용성 최고)

공인 IP·포트포워딩 없이 어디서든 집 PC 접속.

### 3-1. 집 노트북
1. `https://tailscale.com/download/windows` 설치
2. 로그인 (Google/GitHub/Microsoft 계정)
3. Tailscale 관리 콘솔(`https://login.tailscale.com/admin/machines`) 에서:
   - **MagicDNS 활성화** (Settings → DNS → MagicDNS: ON). 활성 안 하면 호스트네임 못 쓰고 IP만 써야 함.
   - 해당 기기의 **Key Expiry 비활성화** (기기 행 ⋯ → Disable key expiry). 안 하면 90일 후 갑자기 끊김.
4. 트레이 아이콘 → 할당 이름/IP 확인 (예: `my-laptop.tail-XXXX.ts.net` 또는 `100.x.x.x`)

### 3-2. 외부 기기 (폰/다른 PC)
1. 같은 Tailscale 계정으로 앱 설치·로그인
2. 터미널: `ssh <Windows사용자>@my-laptop` (MagicDNS) 또는 `ssh <Windows사용자>@100.x.x.x`
3. 비번 입력 → 프롬프트 성공

### 3-3. Tailscale SSH (선택, 비번 불필요)
```
집 노트북 트레이 > Tailscale > Settings > "Run Tailscale SSH Server" 활성화
```
이후 외부에서 `tailscale ssh <사용자>@my-laptop` 으로 접속하면 OS 비번 대신 Tailscale 계정 인증으로 자동 승인. **편하지만 2FA 꼭 켤 것.**

### 3-4. Verify
- 폰 LTE(와이파이 끄고)에서 SSH 접속 성공
- 접속 후 `cd C:\path\to\ubermensch && git log -3` 로 레포 접근 확인

### 주의
- Tailscale 서비스가 재부팅 후 자동 시작되는지 확인: `services.msc` → Tailscale → 자동
- **절대 Tailscale 계정 비번만 쓰지 말고 2FA**를 켤 것. 털리면 내 PC 그대로 털림.

---

## 4. Chrome Remote Desktop (GUI 원격, 보조)

### 4-1. 설치
1. 집 노트북 Chrome에서 `https://remotedesktop.google.com/access` 접속
2. "원격 액세스 설정" → Chrome 확장 설치 → 호스트 MSI 설치
3. 컴퓨터 이름 + **6자리 PIN** 설정

### 4-2. 연결 테스트
폰/외부 PC에서 같은 구글 계정으로 같은 URL → 노트북 선택 → PIN 입력 → 화면 조작.

### 주의
- **Windows 계정 비번이 없으면 연결돼도 잠금화면 못 뚫고 튕김** (0-1 전제).
- Chrome이 **로그인 상태로 유지돼야** 호스트 살아 있음. 다른 사람이 Chrome 로그아웃하면 원격 접속 불가.
- 모니터 꺼진 상태에서 조작 시 간혹 검은 화면만 보임 → 0-2 절전 해제 설정 필수.

---

## 5. 자동 git push 훅 (재발 방지 핵심)

**이미 이 레포에 설치됨**:
- `.claude/settings.json` — Stop 훅 등록 (타임아웃 45초)
- `.claude/hooks/auto-push.sh` — 방어적 푸시 스크립트
- `.gitignore` — 시크릿·OS 부스러기 차단

### 동작
Claude Code 세션이 종료될 때마다:
1. 현재 브랜치 확인 (`main`, `master`, `release/*` 등 보호 브랜치면 스킵)
2. 변경사항 stage → 시크릿 의심 파일(`.env`, `*.pem`, `id_rsa` 등)이 있으면 **중단하고 un-stage**
3. 없으면 `auto: claude session snapshot <UTC timestamp>` 메시지로 커밋
4. 30초 타임아웃 걸린 `git push` 실행
5. 실패해도 세션은 정상 종료 (stderr 로그에 원인 남김)

### 설계 이유
| 문제 | 대응 |
|---|---|
| 인증 프롬프트로 훅 무한 대기 | `GIT_TERMINAL_PROMPT=0` + `timeout 30` |
| main/master 브랜치 보호 규칙 거부 | 보호 브랜치면 조기 종료 |
| 시크릿 실수 커밋 | staged 파일명 정규식 차단 + `.gitignore` |
| git identity 미설정으로 커밋 실패 | `claude@local` / `Claude Code` 자동 지정 |
| 네트워크 실패 조용히 삼킴 | stderr에 명시적 로그 |
| 훅 실패로 세션 못 끝남 | 스크립트는 항상 `exit 0` |

### 다른 레포에도 적용하려면

그 레포 루트에 이 레포의 `.claude/` 디렉토리와 `.gitignore` 를 복사해 넣거나, 전역 적용:
```
C:\Users\<사용자>\.claude\settings.json
```
에 동일한 `hooks` 블록 추가. 단, 전역 적용하면 **모든 레포에서 자동 커밋·푸시**가 돌므로 원치 않는 레포에서도 영향 받는 것 주의.

### Verify
```powershell
# 더미 변경 후 Claude 세션 종료 시뮬
cd C:\path\to\ubermensch
echo test >> SCRATCH.md
# Claude Code 실행 → 아무 작업 없이 /exit
claude
```
GitHub에서 `claude/resume-local-work-EiJIa` 브랜치에 `auto: claude session snapshot …` 커밋이 올라왔는지 확인.

### 주의
- **현재 훅은 feature 브랜치에서만 동작** — `main`에서 바로 작업하면 자동 푸시 안 됨 (의도된 동작).
- 시크릿 차단은 **파일명 기반**이라 완벽하지 않음. 파일 내용에 API 키를 박아 놓으면 못 잡는다. `git secrets` 같은 도구 병용 권장.
- pre-commit 훅이 있는 레포에서 훅이 느리거나 실패하면 자동 스냅샷도 실패(경고 로그 남김, 세션은 정상 종료).

---

## 최종 시나리오 테스트

집에서 **다 설정한 직후** 한 번 리허설:

1. 집 노트북에서 `claude` 실행 → 간단한 파일 수정 시키고 `/exit`
2. 폰에서 Tailscale 켜고 `ssh user@my-laptop` → `cd` → `git log -1` 로 snapshot 커밋 보이는지
3. 폰 브라우저로 `github.com/ubermensch90623/ubermensch/commits/claude/resume-local-work-EiJIa` → 같은 커밋 확인
4. 노트북 덮고 10분 후 다시 폰에서 SSH/Chrome RD 접속 가능한지

네 가지 다 되면 외출해도 안심.

---

## 우선순위 요약

| 순위 | 작업 | 소요 | 비고 |
|---|---|---|---|
| 1 | Claude Code 웹 | 2분 | 지금 당장, 기기 무관 |
| 2 | 0번 (사용자 비번·절전) | 5분 | 모든 원격의 전제 |
| 3 | 5번 이미 적용됨 — `git pull` 해서 받기 | 1분 | 재발 방지 핵심 |
| 4 | 2·3번 SSH + Tailscale | 20분 | 실용성 최고 |
| 5 | 4번 Chrome Remote Desktop | 10분 | GUI 필요할 때만 |
