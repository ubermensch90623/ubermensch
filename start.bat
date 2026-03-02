@echo off
chcp 65001 >nul
title Übermensch Demo

echo.
echo   ========================================
echo     Übermensch 실행 중...
echo   ========================================
echo.

:: Python 있는지 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo   [오류] Python이 설치되어 있지 않습니다.
    echo.
    echo   1. https://www.python.org/downloads/ 에서 다운로드
    echo   2. 설치할 때 "Add Python to PATH" 체크 필수!
    echo   3. 설치 후 이 파일을 다시 더블클릭하세요.
    echo.
    pause
    exit /b 1
)

:: 의존성 설치 (처음 한 번만)
if not exist ".installed" (
    echo   패키지 설치 중... (처음 한 번만)
    pip install -e . >nul 2>&1
    echo done > .installed
    echo   설치 완료!
    echo.
)

:: 실행
python run.py

echo.
pause
