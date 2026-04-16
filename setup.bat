@echo off
REM setup.bat — Windows CMD 원클릭 검증 (PowerShell 대안)
chcp 65001 >nul
setlocal

echo === ubermensch 프로젝트 로컬 검증 ===
echo.

REM Python 탐색
where py >nul 2>&1
if %errorlevel%==0 (
  set PY=py -3
) else (
  where python >nul 2>&1
  if %errorlevel%==0 (
    set PY=python
  ) else (
    echo [ERR] Python 미설치. https://www.python.org/downloads/
    exit /b 1
  )
)

%PY% --version
if errorlevel 1 exit /b 1

echo.
echo === unittest ===
%PY% -m unittest discover tests
if errorlevel 1 (
  echo [ERR] 테스트 실패
  exit /b 1
)

echo.
echo === CLI 스모크 ===
%PY% -m exam_analyzer --no-color analyze ^
  --agency "서민금융진흥원" --date 2026-04-15 ^
  --section "직업기초능력평가:19.33:40:40" ^
  --section "직무수행능력평가:38.76:60:60" ^
  --cutoff 64.48

echo.
%PY% -m exam_analyzer --no-color corpus stats

echo.
echo === 완료 ===
echo 다음: Claude Code 앱/CLI 로 이 폴더 열기. CLAUDE.md 자동 로드됨.
echo 상세: docs\desktop_setup.md
endlocal
