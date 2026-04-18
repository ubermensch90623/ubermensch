# 집 노트북(Windows) 원격 접속 + 자동 푸시 설정 가이드

외출 중 집 노트북에 작업 시켜놓고 확인 불가능했던 상황 재발 방지용 3중 백업 구축 가이드.

집 도착하면 **1 → 5 → 3 → 4** 순서로 진행하면 30분 내 완료.

---

## 1. Claude Code 웹 (가장 먼저, 기기 무관)

어떤 기기에서도 바로:

1. 브라우저에서 `https://claude.ai/code` 접속
2. GitHub 계정으로 로그인 → `ubermensch90623/ubermensch` 연결
3. `claude/resume-local-work-EiJIa` 브랜치에서 이어서 작업
4. 이후 장시간 작업은 **웹에서** 시키기

---

## 2. Windows 사전 설정 (집 도착 후)

### 2-1. 절전/화면 설정
```
설정 > 시스템 > 전원 및 절전
- 화면 끄기: 안 함
- 절전 모드: 안 함
- (노트북) 커버 닫을 때 동작: 아무것도 안 함
```

### 2-2. OpenSSH 서버 설치 (관리자 PowerShell)
```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```
확인: `Get-Service sshd` → Running

---

## 3. Tailscale + SSH (실용성 최고)

### 3-1. 집 노트북
1. `https://tailscale.com/download/windows` 설치
2. 로그인 (Google/GitHub 계정)
3. 트레이 아이콘 → Connect → 할당 이름 확인 (예: `my-laptop`)

### 3-2. 외부 기기 (폰/PC)
1. 같은 Tailscale 계정으로 앱 설치
2. 터미널: `ssh <Windows사용자>@my-laptop`
3. 접속 성공 시 `claude` 실행, `git push` 등 전부 가능

### 3-3. Tailscale SSH (비번 불필요, 선택)
```
트레이 > Tailscale > Settings > Tailscale SSH 활성화
```

---

## 4. Chrome Remote Desktop (GUI 원격)

1. 집 노트북 Chrome: `https://remotedesktop.google.com/access`
2. "원격 액세스 설정" → 확장 설치 → MSI 설치
3. 컴퓨터 이름 + **6자리 PIN** 설정
4. 폰/외부 PC: 같은 구글 계정으로 접속 → PIN 입력 → GUI 조작

---

## 5. 자동 git push 훅 (재발 방지 핵심)

**이미 이 레포에 설정돼 있음**: `.claude/settings.json`

Claude Code가 이 레포에서 세션 종료할 때마다:
1. 변경사항 전부 stage
2. 변경 있으면 자동 커밋
3. 현재 브랜치로 `git push`

### 다른 레포에도 적용하려면

프로젝트 루트에 `.claude/settings.json` 생성:
```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "cd \"$CLAUDE_PROJECT_DIR\" && git add -A && (git diff --cached --quiet || (git commit -m \"auto: claude session snapshot\" && git push origin HEAD))"
          }
        ]
      }
    ]
  }
}
```

또는 전역 적용: `C:\Users\<사용자>\.claude\settings.json` 에 동일 내용.

**주의**: `.env`, 자격증명 등 민감 파일이 커밋되지 않도록 `.gitignore` 필수 정비.

---

## Verification 체크리스트

집 도착 후 순서대로:

- [ ] 노트북 덮고 10분 후에도 다른 기기에서 핑 가능
- [ ] 다른 기기에서 `ssh user@my-laptop` 성공
- [ ] 폰 LTE(와이파이 끄고)에서도 Tailscale 접속 성공
- [ ] 폰에서 Chrome Remote Desktop 화면 보이고 조작 가능
- [ ] Claude Code에서 더미 파일 생성 → 세션 종료 → GitHub에 자동 커밋 확인
- [ ] 외부 기기에서 SSH 접속해 `git log` 로 진행 상황 확인
