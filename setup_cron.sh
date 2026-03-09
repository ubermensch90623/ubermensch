#!/bin/bash
#
# 크론 예약 설정 스크립트
# 매시간 자동으로 데몬을 실행하도록 크론탭에 등록한다.
#
# 사용법:
#   chmod +x setup_cron.sh
#   ./setup_cron.sh          # 크론 등록
#   ./setup_cron.sh remove   # 크론 해제
#   ./setup_cron.sh status   # 상태 확인

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
DAEMON_SCRIPT="$PROJECT_DIR/daemon.py"
CRON_LOG="$PROJECT_DIR/logs/cron.log"
CRON_MARKER="# ubermensch-agent-daemon"

mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/tasks/queue"
mkdir -p "$PROJECT_DIR/tasks/results"

# Python 경로 탐색
PYTHON_BIN=""
for p in python3 python; do
    if command -v "$p" &>/dev/null; then
        PYTHON_BIN="$(command -v "$p")"
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "오류: Python을 찾을 수 없습니다."
    exit 1
fi

# ANTHROPIC_API_KEY 확인
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "경고: ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다."
    echo "  export ANTHROPIC_API_KEY='your-key'"
    echo "  크론에서도 이 키가 필요합니다."
fi

install_cron() {
    # 기존 등록 제거 후 재등록
    (crontab -l 2>/dev/null | grep -v "$CRON_MARKER") | crontab - 2>/dev/null || true

    # 매시간 0분에 실행
    CRON_LINE="0 * * * * cd $PROJECT_DIR && ANTHROPIC_API_KEY=\"\${ANTHROPIC_API_KEY:-$ANTHROPIC_API_KEY}\" $PYTHON_BIN $DAEMON_SCRIPT >> $CRON_LOG 2>&1 $CRON_MARKER"

    (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -

    echo "크론 등록 완료!"
    echo ""
    echo "  스케줄: 매시간 0분"
    echo "  스크립트: $DAEMON_SCRIPT"
    echo "  로그: $CRON_LOG"
    echo ""
    echo "확인: crontab -l"
    echo "해제: $0 remove"
}

remove_cron() {
    (crontab -l 2>/dev/null | grep -v "$CRON_MARKER") | crontab - 2>/dev/null || true
    echo "크론 해제 완료."
}

show_status() {
    echo "=== Ubermensch 데몬 상태 ==="
    echo ""

    # 크론 등록 확인
    if crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
        echo "크론: 등록됨"
        crontab -l 2>/dev/null | grep "$CRON_MARKER"
    else
        echo "크론: 미등록"
    fi
    echo ""

    # Lock 파일 확인
    if [ -f "$PROJECT_DIR/.daemon.lock" ]; then
        PID=$(cat "$PROJECT_DIR/.daemon.lock" 2>/dev/null)
        if kill -0 "$PID" 2>/dev/null; then
            echo "데몬: 실행 중 (PID: $PID)"
        else
            echo "데몬: 미실행 (stale lock)"
        fi
    else
        echo "데몬: 미실행"
    fi
    echo ""

    # 대기 태스크 수
    PENDING=$(find "$PROJECT_DIR/tasks/queue" -name "*.json" 2>/dev/null | wc -l)
    echo "대기 태스크: ${PENDING}개"

    # 최근 로그
    if [ -f "$CRON_LOG" ]; then
        echo ""
        echo "=== 최근 로그 (마지막 10줄) ==="
        tail -10 "$CRON_LOG"
    fi
}

case "${1:-install}" in
    install)
        install_cron
        ;;
    remove)
        remove_cron
        ;;
    status)
        show_status
        ;;
    *)
        echo "사용법: $0 {install|remove|status}"
        exit 1
        ;;
esac
