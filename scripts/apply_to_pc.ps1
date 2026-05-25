<#
.SYNOPSIS
종환 윈도우 PC에 이 레포의 자가진화 머지 7건 + 인프라 변경을 한 번에 적용.

.DESCRIPTION
PR #6 머지 후 PC 도착 시 1줄 실행. 모든 변경 전 .bak 생성. dry-run 기본.

.PARAMETER Apply
실제로 적용. 미지정 시 dry-run (어떤 명령이 실행될지만 출력, 파일 변경 X).

.PARAMETER RepoRoot
이 레포 clone 경로. 기본 = 현재 디렉토리.

.PARAMETER Step
특정 단계만 실행. 1=hooks·2=skill·3=patch·4=cron·5=verify. 미지정 시 전체.

.EXAMPLE
.\scripts\apply_to_pc.ps1                        # dry-run 전체 (안전)
.\scripts\apply_to_pc.ps1 -Apply                 # 전체 실제 적용
.\scripts\apply_to_pc.ps1 -Apply -Step 1         # hooks 3개만 적용
.\scripts\apply_to_pc.ps1 -Apply -Step 4         # cron 등록만
#>

param(
    [switch]$Apply = $false,
    [string]$RepoRoot = (Get-Location).Path,
    [int]$Step = 0
)

$ErrorActionPreference = "Stop"
chcp 65001 | Out-Null
$env:PYTHONIOENCODING = "utf-8"

$User = "윤상택"
$Home = "C:\Users\$User"
$DesktopHooks = "$Home\Desktop\.claude\hooks"
$ClaudeSkills = "$Home\.claude\skills"
$HermesMVP = "$Home\Desktop\HERMES"
$Vault = "$Home\Desktop\작업\ObsidianVault\_SSOT"

function Run($desc, $action) {
    if ($Apply) {
        Write-Host "[APPLY] $desc" -ForegroundColor Green
        & $action
    } else {
        Write-Host "[DRY-RUN] $desc" -ForegroundColor Yellow
    }
}

function Backup($path) {
    if ((Test-Path $path) -and $Apply) {
        $bak = "$path.bak.$(Get-Date -Format yyyyMMdd_HHmmss)"
        Copy-Item $path $bak -Force
        Write-Host "  ↳ backup: $bak" -ForegroundColor DarkGray
    }
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " ubermensch → 종환 PC 적용 ($(if ($Apply) {'APPLY'} else {'DRY-RUN'}))" -ForegroundColor Cyan
Write-Host " RepoRoot: $RepoRoot" -ForegroundColor Cyan
Write-Host " Step    : $(if ($Step -eq 0) {'전체 (1~5)'} else {$Step})" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# 사전 검증
if (-not (Test-Path "$RepoRoot\hooks")) {
    Write-Error "$RepoRoot\hooks 없음. -RepoRoot 옵션 확인."
    exit 1
}

# 1. Stop hooks 3개 복사 (auto_morning_desktop_popup · jaso_validator · hermes_mvp_vault_sync)
if ($Step -eq 0 -or $Step -eq 1) {
    Write-Host "`n[1/5] Stop hooks 복사 → $DesktopHooks" -ForegroundColor Cyan
    Run "mkdir -Force $DesktopHooks" { New-Item -ItemType Directory -Force -Path $DesktopHooks | Out-Null }
    Run "cp auto_morning_desktop_popup.py" { Copy-Item "$RepoRoot\hooks\auto_morning_desktop_popup.py" "$DesktopHooks\" -Force }
    Run "cp jaso_validator.py" { Copy-Item "$RepoRoot\hooks\jaso_validator.py" "$DesktopHooks\" -Force }
    Run "cp hermes_mvp_vault_sync.js → HERMES 폴더" { Copy-Item "$RepoRoot\hooks\hermes_mvp_vault_sync.js" "$HermesMVP\" -Force }
    Write-Host "  → Desktop/.claude/settings.json hooks.Stop에 등록 필요 (수동, hooks/README.md 참고)" -ForegroundColor DarkGray
}

# 2. cognitive-evolution-loop SKILL 교체
if ($Step -eq 0 -or $Step -eq 2) {
    Write-Host "`n[2/5] cognitive-evolution-loop SKILL 교체 → $ClaudeSkills" -ForegroundColor Cyan
    $target = "$ClaudeSkills\cognitive-evolution-loop\SKILL.md"
    Backup $target
    Run "cp SKILL.md (cycle D.-1 + G-pre grep)" {
        New-Item -ItemType Directory -Force -Path "$ClaudeSkills\cognitive-evolution-loop" | Out-Null
        Copy-Item "$RepoRoot\.claude\skills\cognitive-evolution-loop\SKILL.md" $target -Force
    }
}

# 3. 인지진화_가중치.json patch merge (학습_displacement 추가)
if ($Step -eq 0 -or $Step -eq 3) {
    Write-Host "`n[3/5] 인지진화_가중치.json patch merge" -ForegroundColor Cyan
    $weightsJson = "$Vault\인지진화_가중치.json"
    $patchJson = "$RepoRoot\data\학습_displacement_patch.json"

    if (-not (Test-Path $weightsJson)) {
        Write-Host "  ⚠️  $weightsJson 없음. SKIP" -ForegroundColor Yellow
    } else {
        Backup $weightsJson
        Run "jq merge .patterns" {
            $weights = Get-Content $weightsJson -Raw -Encoding UTF8 | ConvertFrom-Json
            $patch = Get-Content $patchJson -Raw -Encoding UTF8 | ConvertFrom-Json
            # patch 안의 _README · _apply · _source_evidence 키는 제외
            $patternKey = "학습_displacement"
            if (-not $weights.patterns) {
                $weights | Add-Member -NotePropertyName patterns -NotePropertyValue ([pscustomobject]@{}) -Force
            }
            $weights.patterns | Add-Member -NotePropertyName $patternKey -NotePropertyValue $patch.$patternKey -Force
            $weights | ConvertTo-Json -Depth 20 | Set-Content $weightsJson -Encoding UTF8
        }
    }
}

# 4. cron 등록 (recruitment-scan-daily + cognitive-evolution catchup)
if ($Step -eq 0 -or $Step -eq 4) {
    Write-Host "`n[4/5] hermes cron 등록 (recruitment-scan-daily)" -ForegroundColor Cyan
    Run "hermes cron create recruitment-scan-daily 06:30" {
        hermes cron create `
            --name recruitment-scan-daily `
            --schedule "0 6 * * *" `
            --skill recruitment-scanner `
            --prompt "오늘 recruitment-scanner SKILL 실행. 신규 공고만 보고. 없으면 '신규 공고 없음' 1줄."
    }
    Run "hermes cron list 검증" { hermes cron list }
}

# 5. 검증 (5단계, docs/HERMES_LOCAL_SETUP.md §10 동일)
if ($Step -eq 0 -or $Step -eq 5) {
    Write-Host "`n[5/5] 적용 후 5단계 검증" -ForegroundColor Cyan
    Run "1. hermes gateway status" { hermes gateway status }
    Run "2. hermes cron list (5+개 확인)" { hermes cron list }
    Run "3. hermes personality list (4개 확인)" { hermes personality list }
    Run "4. PowerShell loop heartbeat" {
        $log = "$Home\.hermes\logs\heartbeat.log"
        if (Test-Path $log) { Get-Content $log -Tail 5 } else { Write-Host "  ⚠️ heartbeat.log 없음" }
    }
    Run "5. GD mirror 마지막 sync" {
        $mirror = "G:\내 드라이브\04_시스템\Hermes_데이터센터\02_hermes_full"
        if (Test-Path $mirror) {
            Get-Item $mirror | Select-Object LastWriteTime
        } else { Write-Host "  ⚠️ GD mirror 없음" }
    }
}

Write-Host "`n================================================================" -ForegroundColor Cyan
if ($Apply) {
    Write-Host " 적용 완료. settings.json hooks 등록은 hooks/README.md 참고." -ForegroundColor Green
    Write-Host " 백업 파일: *.bak.<timestamp>" -ForegroundColor Green
} else {
    Write-Host " DRY-RUN 종료. 실제 적용은: -Apply" -ForegroundColor Yellow
}
Write-Host "================================================================" -ForegroundColor Cyan
