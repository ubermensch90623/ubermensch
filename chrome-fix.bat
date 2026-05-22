@echo off
chcp 65001 >nul
title Chrome 시작 페이지 자동 수정

echo.
echo ============================================
echo  Chrome 시작 페이지 자동 수정 도구
echo ============================================
echo.
echo 이 도구는 다음 작업을 합니다:
echo   1. Chrome 종료
echo   2. 시작 페이지 설정을 "새 탭" 으로 초기화
echo   3. 모든 Chrome 프로필에 적용
echo.
echo 북마크, 비밀번호, 방문 기록은 건드리지 않습니다.
echo.
pause

echo.
echo [1/3] Chrome 종료 중...
taskkill /F /IM chrome.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/3] Chrome 설정 수정 중...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference = 'Continue';" ^
  "$userData = Join-Path $env:LOCALAPPDATA 'Google\Chrome\User Data';" ^
  "if (-not (Test-Path $userData)) {" ^
  "  Write-Host '  Chrome 설치를 찾을 수 없습니다.' -ForegroundColor Red;" ^
  "  exit 1" ^
  "}" ^
  "$profiles = Get-ChildItem $userData -Directory | Where-Object { $_.Name -eq 'Default' -or $_.Name -like 'Profile *' };" ^
  "$fixed = 0;" ^
  "foreach ($p in $profiles) {" ^
  "  $prefsPath = Join-Path $p.FullName 'Preferences';" ^
  "  if (-not (Test-Path $prefsPath)) { continue }" ^
  "  try {" ^
  "    Copy-Item $prefsPath ($prefsPath + '.bak') -Force;" ^
  "    $json = Get-Content $prefsPath -Raw -Encoding UTF8 | ConvertFrom-Json;" ^
  "    if (-not $json.PSObject.Properties['session']) {" ^
  "      $json | Add-Member -NotePropertyName session -NotePropertyValue ([PSCustomObject]@{}) -Force" ^
  "    }" ^
  "    $json.session | Add-Member -NotePropertyName startup_urls -NotePropertyValue @() -Force;" ^
  "    $json.session | Add-Member -NotePropertyName restore_on_startup -NotePropertyValue 5 -Force;" ^
  "    $json | ConvertTo-Json -Depth 100 -Compress | Set-Content $prefsPath -Encoding UTF8 -NoNewline;" ^
  "    Write-Host ('  - ' + $p.Name + ': 완료 (백업: Preferences.bak)') -ForegroundColor Green;" ^
  "    $fixed = $fixed + 1" ^
  "  } catch {" ^
  "    Write-Host ('  - ' + $p.Name + ': 오류 - ' + $_.Exception.Message) -ForegroundColor Yellow" ^
  "  }" ^
  "}" ^
  "Write-Host '';" ^
  "Write-Host ('[3/3] 처리 완료: ' + $fixed + '개 프로필') -ForegroundColor Cyan"

echo.
echo ============================================
echo  완료! Chrome 다시 실행해보세요.
echo ============================================
echo.
echo 만약 다시 jjanggame.co.kr 이 뜬다면:
echo  1. Chrome 확장 프로그램에 의심스러운 것이 있는지 확인
echo  2. 작업 관리자 ^> 시작프로그램 탭에 이상한 것이 있는지 확인
echo  3. Malwarebytes 같은 무료 백신으로 검사
echo.
pause
