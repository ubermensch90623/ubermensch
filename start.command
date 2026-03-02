#!/bin/bash
# Mac에서 더블클릭하면 실행됩니다.

cd "$(dirname "$0")"

echo ""
echo "  ========================================"
echo "    Übermensch 실행 중..."
echo "  ========================================"
echo ""

# Python 확인
if ! command -v python3 &> /dev/null; then
    echo "  [오류] Python이 설치되어 있지 않습니다."
    echo ""
    echo "  터미널에서: brew install python3"
    echo "  또는: https://www.python.org/downloads/"
    echo ""
    read -p "  아무 키나 누르세요..."
    exit 1
fi

# 의존성 설치 (처음 한 번만)
if [ ! -f ".installed" ]; then
    echo "  패키지 설치 중... (처음 한 번만)"
    pip3 install -e . > /dev/null 2>&1
    touch .installed
    echo "  설치 완료!"
    echo ""
fi

# 실행
python3 run.py

echo ""
read -p "  아무 키나 누르세요..."
