# setup.ps1 — 데스크탑(Windows PowerShell) 원클릭 검증 스크립트
# 목적: 동작 점검만. 설치 작업 없음 (stdlib-only).

$ErrorActionPreference = "Stop"

Write-Host "=== ubermensch 프로젝트 로컬 검증 ==="
Write-Host ""

# 1. Python 확인 (Windows 는 py launcher 우선)
$PY = $null
foreach ($cmd in @("py -3", "python", "python3")) {
    try {
        $out = & cmd.exe /c "$cmd --version 2>&1"
        if ($LASTEXITCODE -eq 0) { $PY = $cmd; break }
    } catch {}
}

if (-not $PY) {
    Write-Host "[ERR] Python 3 이 설치되어 있지 않습니다. https://www.python.org/downloads/ 에서 설치 후 재시도." -ForegroundColor Red
    exit 1
}

$VER = & cmd.exe /c "$PY -c ""import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"""
Write-Host "[OK] Python $VER 발견 ($PY)"

$parts = $VER -split '\.'
$MAJOR = [int]$parts[0]
$MINOR = [int]$parts[1]
if ($MAJOR -lt 3 -or ($MAJOR -eq 3 -and $MINOR -lt 9)) {
    Write-Host "[ERR] Python 3.9 이상 필요." -ForegroundColor Red
    exit 1
}

# 2. 한글 콘솔 대비 (UTF-8)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

# 3. Git 상태
if (Test-Path .git) {
    $BRANCH = git rev-parse --abbrev-ref HEAD
    Write-Host "[OK] Git repo ($BRANCH)"
    if ($BRANCH -ne "claude/fix-handwriting-recognition-J9xJq") {
        Write-Host "[WARN] 브랜치 확인 필요 (현재: $BRANCH)" -ForegroundColor Yellow
    }
} else {
    Write-Host "[WARN] Git repo 아님"
}

# 4. 테스트
Write-Host ""
Write-Host "=== unittest ==="
& cmd.exe /c "$PY -m unittest discover tests"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERR] 테스트 실패" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] 테스트 통과"

# 5. CLI 스모크
Write-Host ""
Write-Host "=== CLI 동작 확인 ==="
& cmd.exe /c "$PY -m exam_analyzer --version"
& cmd.exe /c "$PY -m exam_analyzer --no-color analyze --agency `"서민금융진흥원`" --date 2026-04-15 --section `"직업기초능력평가:19.33:40:40`" --section `"직무수행능력평가:38.76:60:60`" --cutoff 64.48"

Write-Host ""
& cmd.exe /c "$PY -m exam_analyzer --no-color corpus stats"

Write-Host ""
Write-Host "=== 완료 ==="
Write-Host "다음: Claude Code 로 이 폴더 열고 'CLAUDE.md + docs/readiness_checklist.md 읽어' 라고 요청."
Write-Host "상세: docs/desktop_setup.md"
