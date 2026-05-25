<#
.SYNOPSIS
종환 PC를 모바일 Claude Code 앱에서 24시간 원격 제어 가능하게 유지.

.DESCRIPTION
`claude remote-control` 프로세스를 영구 유지. crash·timeout(10분 네트워크 단절)·
종료 시 자동 재시작. 출근 후 직장 모바일에서 desktop 세션 connect → 명령 →
PC에서 즉시 실행.

.PARAMETER SessionName
모바일 앱에 표시될 세션 이름. 기본 "Jonghwan PC (24h)".

.PARAMETER LogDir
재시작 로그 저장. 기본 ~\.hermes\logs\.

.PARAMETER MinRestartInterval
재시작 최소 간격(초). 너무 빠른 crash loop 방지. 기본 10초.

.EXAMPLE
.\claude_remote_control_loop.ps1
.\claude_remote_control_loop.ps1 -SessionName "Jonghwan PC"

.NOTES
배치: C:\Users\윤상택\.hermes\scripts\claude_remote_control_loop.ps1
Task Scheduler logon trigger로 부팅 후 자동 시작 (setup_remote_control.ps1 참고).
sleep 차단 필수: powercfg /change standby-timeout-ac 0
#>

param(
    [string]$SessionName = "Jonghwan PC (24h)",
    [string]$LogDir = "$env:USERPROFILE\.hermes\logs",
    [int]$MinRestartInterval = 10
)

$ErrorActionPreference = "Continue"
chcp 65001 | Out-Null
$env:PYTHONIOENCODING = "utf-8"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$LogFile = Join-Path $LogDir "claude_remote_control_loop.log"
$HeartbeatFile = Join-Path $LogDir "claude_remote_control_heartbeat.log"

function Write-Log($msg) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | $msg"
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
    Write-Host $line
}

# claude CLI 존재 확인
$claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
if (-not $claudeCmd) {
    Write-Log "❌ claude CLI 없음. npm i -g @anthropic-ai/claude-code 또는 설치 경로 PATH 확인."
    exit 1
}

# remote-control 서브명령 존재 확인 (claude --help 출력에 'remote-control' 포함 검사)
$helpOut = & claude --help 2>&1 | Out-String
if ($helpOut -notmatch "remote-control") {
    Write-Log "⚠️  claude --help에 remote-control 없음. CLI 버전 업그레이드 필요할 수 있음."
    Write-Log "   (계속 진행 — 명령 자체가 실패하면 loop가 5초 후 재시도)"
}

Write-Log "==== claude_remote_control_loop 시작 ===="
Write-Log "SessionName: $SessionName"
Write-Log "LogDir     : $LogDir"
Write-Log "MinRestart : ${MinRestartInterval}s"

$consecutiveFailures = 0
$lastStartTime = [datetime]::MinValue

while ($true) {
    $now = Get-Date
    $sinceLastStart = ($now - $lastStartTime).TotalSeconds
    if ($sinceLastStart -lt $MinRestartInterval) {
        $sleep = [int]($MinRestartInterval - $sinceLastStart)
        Write-Log "쿨다운 ${sleep}s 대기 (재시작 너무 빠름)"
        Start-Sleep -Seconds $sleep
    }

    # 5회 연속 빠른 실패 시 백오프 (5분)
    if ($consecutiveFailures -ge 5) {
        Write-Log "⚠️  연속 실패 ${consecutiveFailures}회 — 5분 백오프"
        Start-Sleep -Seconds 300
        $consecutiveFailures = 0
    }

    $lastStartTime = Get-Date
    Write-Log "claude remote-control --name '$SessionName' 실행"
    Add-Content -Path $HeartbeatFile -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | START" -Encoding UTF8

    try {
        & claude remote-control --name $SessionName 2>&1 | ForEach-Object {
            Add-Content -Path $LogFile -Value "  $_" -Encoding UTF8
        }
        $exitCode = $LASTEXITCODE
    } catch {
        Write-Log "예외: $_"
        $exitCode = -1
    }

    $duration = ((Get-Date) - $lastStartTime).TotalSeconds
    Add-Content -Path $HeartbeatFile -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | END exit=$exitCode duration=${duration}s" -Encoding UTF8

    if ($duration -lt 30) {
        $consecutiveFailures += 1
        Write-Log "⚠️  세션 ${duration}s 만에 종료 (exit $exitCode) — 연속 실패 ${consecutiveFailures}회"
    } else {
        $consecutiveFailures = 0
        Write-Log "세션 종료 (exit $exitCode, ${duration}s 작동) — 즉시 재시작"
    }
}
