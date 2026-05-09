#!/usr/bin/env bash
# study-evolve install — 5단계, ~1분 소요
#
# 동작:
#   1. Python ≥3.10 확인
#   2. .venv 가상환경 생성 (이미 있으면 재사용)
#   3. requirements.txt 의존성 설치
#   4. data/ 폴더 + CSV 헤더 생성 (init)
#   5. 57개 테스트 실행으로 정상 작동 검증
#
# 사용:
#   bash bin/install.sh                  # 기본
#   bash bin/install.sh --no-venv        # venv 없이 시스템 pip 사용
#   bash bin/install.sh --no-tests       # 테스트 건너뛰기 (빠른 설치)
#   bash bin/install.sh --with-sample    # 설치 후 샘플 데이터 생성

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

USE_VENV=1
RUN_TESTS=1
LOAD_SAMPLE=0

for arg in "$@"; do
    case "$arg" in
        --no-venv) USE_VENV=0 ;;
        --no-tests) RUN_TESTS=0 ;;
        --with-sample) LOAD_SAMPLE=1 ;;
        -h|--help)
            sed -n '2,15p' "$0"
            exit 0
            ;;
        *) echo "알 수 없는 옵션: $arg"; exit 2 ;;
    esac
done

echo "[1/5] Python ≥3.10 확인"
if ! command -v python3 >/dev/null 2>&1; then
    echo "  ✗ python3 명령을 찾을 수 없습니다. Python 3.10+ 설치 후 재시도."
    exit 1
fi
PY_VERSION=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    echo "  ✗ Python 3.10 이상 필요 (현재: $PY_VERSION)"
    exit 1
fi
echo "  ✓ Python $PY_VERSION"

if [ "$USE_VENV" -eq 1 ]; then
    echo "[2/5] 가상환경 (.venv) 준비"
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        echo "  ✓ .venv 새로 생성"
    else
        echo "  ✓ .venv 이미 존재 (재사용)"
    fi
    PIP=".venv/bin/pip"
    PY=".venv/bin/python"
else
    echo "[2/5] venv 건너뜀 (시스템 Python 사용)"
    PIP="python3 -m pip"
    PY="python3"
fi

echo "[3/5] 의존성 설치"
$PIP install -q -U pip
$PIP install -q -r requirements.txt
echo "  ✓ pandas, tabulate"

echo "[4/5] 데이터 폴더 초기화"
$PY main.py init >/dev/null
echo "  ✓ data/records.csv, data/review_schedule.csv"

if [ "$RUN_TESTS" -eq 1 ]; then
    echo "[5/5] 검증 — 57개 테스트 실행"
    if $PY -m unittest discover tests >/dev/null 2>&1; then
        echo "  ✓ 모든 테스트 통과"
    else
        echo "  ✗ 테스트 실패. 다음으로 자세히 확인:"
        echo "     $PY -m unittest discover tests -v"
        exit 1
    fi
else
    echo "[5/5] 테스트 건너뜀 (--no-tests)"
fi

if [ "$LOAD_SAMPLE" -eq 1 ]; then
    echo
    echo "[추가] 샘플 데이터 생성"
    $PY main.py sample
fi

echo
echo "════════════════════════════════════════════════"
echo "  ✓ 설치 완료 ($ROOT)"
echo "════════════════════════════════════════════════"
echo
echo "  사용 방법 (venv 활성화):"
if [ "$USE_VENV" -eq 1 ]; then
    echo "    source .venv/bin/activate"
    echo "    python main.py add"
    echo
    echo "  또는 wrapper로 어디서든:"
    echo "    bin/study-evolve add"
    echo "    PATH=\"\$PATH:$ROOT/bin\"  # ~/.bashrc에 추가하면 'study-evolve add' 직접 호출"
else
    echo "    python3 main.py add"
fi
echo
echo "  Obsidian 자동 통합 (선택):"
echo "    bash bin/setup-shell.sh ~/Documents/MyVault          # 안내만 출력"
echo "    bash bin/setup-shell.sh ~/Documents/MyVault --apply  # ~/.bashrc 자동 추가"
echo
echo "  다음 명령:"
echo "    bin/study-evolve sample            # 샘플 17건 생성"
echo "    bin/study-evolve recommend         # 내일 학습 추천"
echo "    bin/study-evolve sync-vault --vault PATH  # Obsidian 통합"
