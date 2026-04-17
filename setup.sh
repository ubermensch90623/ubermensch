#!/usr/bin/env bash
# setup.sh — 데스크탑(macOS/Linux) 원클릭 검증 스크립트
# 목적: 저장소를 클론·풀한 로컬 PC 에서 동작 점검만 수행. 설치 작업 없음 (stdlib-only).
set -euo pipefail

echo "=== ubermensch 프로젝트 로컬 검증 ==="
echo

# 1. Python 버전 확인
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "[ERR] python 3 이 설치되어 있지 않습니다. https://www.python.org/downloads/ 에서 설치 후 재시도." >&2
  exit 1
fi

PY_VERSION=$("$PY" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

echo "[OK] Python $PY_VERSION 발견 ($PY)"
if [[ "$MAJOR" -lt 3 || ( "$MAJOR" -eq 3 && "$MINOR" -lt 9 ) ]]; then
  echo "[ERR] Python 3.9 이상 필요. 현재 $PY_VERSION" >&2
  exit 1
fi

# 2. Git 상태 확인
if git rev-parse --git-dir >/dev/null 2>&1; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD)
  echo "[OK] Git repo ($BRANCH)"
  if [[ "$BRANCH" != "claude/fix-handwriting-recognition-J9xJq" ]]; then
    echo "[WARN] 현재 브랜치가 claude/fix-handwriting-recognition-J9xJq 가 아닙니다. (확인만 진행)"
  fi
else
  echo "[WARN] Git repo 아닙니다."
fi

# 3. 테스트 실행 (ubermensch 67 + harness 17 = 84 PASS 목표)
echo
echo "=== unittest 실행 (ubermensch) ==="
"$PY" -m unittest discover tests
echo "[OK] ubermensch tests 통과"

if [ -d "harness/tests" ]; then
  echo
  echo "=== unittest 실행 (harness) ==="
  "$PY" -m unittest discover harness/tests
  echo "[OK] harness tests 통과"
fi

# 4. CLI 스모크
echo
echo "=== CLI 동작 확인 ==="
"$PY" -m exam_analyzer --version || true
"$PY" -m exam_analyzer --no-color analyze \
  --agency "서민금융진흥원" --date 2026-04-15 \
  --section "직업기초능력평가:19.33:40:40" \
  --section "직무수행능력평가:38.76:60:60" \
  --cutoff 64.48 | tail -6

# 5. corpus 상태 (아직 비어있으면 정상)
echo
"$PY" -m exam_analyzer --no-color corpus stats || true

echo
echo "=== 완료 ==="
echo "다음 단계: Claude Code 앱/CLI 로 이 폴더 열고 'CLAUDE.md + docs/readiness_checklist.md 읽어' 라고 요청."
echo "상세: docs/desktop_setup.md"
