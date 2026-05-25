<#
.SYNOPSIS
종환 PC에 모바일 Claude Code 원격 제어 환경 1줄 셋업.

.DESCRIPTION
실행 순서:
  1. powercfg sleep·hibernate·display 차단 (AC 전원)
  2. ~/.hermes/scripts/claude_remote_control_loop.ps1 배치
  3. Windows Task Scheduler logon trigger 등록 (재부팅 후 자동)
  4. 즉시 1회 실행 → 모바일 앱에서 "Jonghwan PC (24h)" 세션 확인

.PARAMETER Apply
실제 적용. 미지정 시 dry-run.

.PARAMETER RepoRoot
이 ubermensch 레포 clone 경로. 기본 현재 디렉토리.

.PARAMETER SessionName
모바일 앱 표시명. 기본 "Jonghwan PC (24h)".

.EXAMPLE
.\setup_remote_control.ps1                  # dry-run
.\setup_remote_control.ps1 -Apply           # 실제 적용

.NOTES
종환 PC에서 1회만 실행. 적용 후:
- 출근 → 모바일 Claude Code 앱 → desktop sessions → "Jonghwan PC (24h)" tap → 명령
- PC는 24시간 켜져 있어야 함 (sleep 차단 자동 적용됨)
- crash 시 5초 후 자동 재시작
#>

param(
    [switch]$Apply = $false,
    [string]$RepoRoot = (Get-Location).Path,
    [string]$SessionName = "Jonghwan PC (24h)"
)

$ErrorActionPreference = "Stop"
chcp 65001 | Out-Null
$env:PYTHONIOENCODING = "utf-8"

$ScriptsDest = "$env:USERPROFILE\.hermes\scripts"
$LoopScript = Join-Path $ScriptsDest "claude_remote_control_loop.ps1"
$TaskName = "Hermes_ClaudeRemoteControl_Autostart"

function Run($desc, $action) {
    if ($Apply) {
        Write-Host "[APPLY] $desc" -ForegroundColor Green
        & $action
    } else {
        Write-Host "[DRY-RUN] $desc" -ForegroundColor Yellow
    }
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " setup_remote_control ($(if ($Apply) {'APPLY'} else {'DRY-RUN'}))" -ForegroundColor Cyan
Write-Host " RepoRoot   : $RepoRoot" -ForegroundColor Cyan
Write-Host " SessionName: $SessionName" -ForegroundColor Cyan
Write-Host " Task name  : $TaskName" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# 사전 검증
if (-not (Test-Path "$RepoRoot\scripts\claude_remote_control_loop.ps1")) {
    Write-Error "$RepoRoot\scripts\claude_remote_control_loop.ps1 없음. -RepoRoot 옵션 확인."
    exit 1
}

$claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
if (-not $claudeCmd) {
    Write-Warning "claude CLI 없음. npm i -g @anthropic-ai/claude-code 또는 https://code.claude.com/docs 참고."
    if ($Apply) { exit 1 }
}

# 1. Sleep / Hibernate / Display 차단 (AC 전원 — DC는 노트북 배터리, 데스크톱은 무관)
Write-Host "`n[1/4] Sleep·Hibernate·Display 차단 (AC)" -ForegroundColor Cyan
Run "powercfg /change standby-timeout-ac 0" { powercfg /change standby-timeout-ac 0 }
Run "powercfg /change hibernate-timeout-ac 0" { powercfg /change hibernate-timeout-ac 0 }
Run "powercfg /change monitor-timeout-ac 0" { powercfg /change monitor-timeout-ac 0 }
Run "powercfg /hibernate off" { powercfg /hibernate off }

# 2. Loop 스크립트 배치
Write-Host "`n[2/4] claude_remote_control_loop.ps1 → $ScriptsDest" -ForegroundColor Cyan
Run "mkdir -Force $ScriptsDest" { New-Item -ItemType Directory -Force -Path $ScriptsDest | Out-Null }
Run "cp claude_remote_control_loop.ps1" {
    Copy-Item "$RepoRoot\scripts\claude_remote_control_loop.ps1" $LoopScript -Force
}

# 3. Task Scheduler 등록 (logon trigger, HIGHEST 권한, 부팅 후 자동)
Write-Host "`n[3/4] Task Scheduler 등록 ($TaskName)" -ForegroundColor Cyan
Run "schtasks /delete /tn $TaskName /f (기존 제거)" {
    schtasks /delete /tn $TaskName /f 2>$null
}
Run "schtasks /create /tn $TaskName /tr ... /sc onlogon /rl HIGHEST" {
    $action = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$LoopScript`" -SessionName `"$SessionName`""
    schtasks /create /tn $TaskName /tr $action /sc onlogon /rl HIGHEST /f
}
Run "schtasks /query /tn $TaskName 검증" {
    schtasks /query /tn $TaskName
}

# 4. 즉시 시작 (이미 logon 됐으니 수동 트리거)
Write-Host "`n[4/4] 즉시 시작 (background, 모바일 앱에서 확인 가능)" -ForegroundColor Cyan
Run "schtasks /run /tn $TaskName" {
    schtasks /run /tn $TaskName
    Write-Host "  → 30초 후 모바일 Claude Code 앱 sessions에 '$SessionName' 표시 확인" -ForegroundColor DarkGray
    Write-Host "  → 로그: $env:USERPROFILE\.hermes\logs\claude_remote_control_loop.log" -ForegroundColor DarkGray
    Write-Host "  → heartbeat: $env:USERPROFILE\.hermes\logs\claude_remote_control_heartbeat.log" -ForegroundColor DarkGray
}

Write-Host "`n================================================================" -ForegroundColor Cyan
if ($Apply) {
    Write-Host " 셋업 완료. 모바일 Claude Code 앱 sessions에서 '$SessionName' tap → 명령" -ForegroundColor Green
    Write-Host ""
    Write-Host " 검증 (이 PC):" -ForegroundColor Green
    Write-Host "   Get-Content $env:USERPROFILE\.hermes\logs\claude_remote_control_heartbeat.log -Tail 5" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host " 재부팅 후에도 자동 시작 (Task Scheduler logon trigger 등록 완료)" -ForegroundColor Green
} else {
    Write-Host " DRY-RUN 종료. 실제 적용은: -Apply" -ForegroundColor Yellow
}
Write-Host "================================================================" -ForegroundColor Cyan
