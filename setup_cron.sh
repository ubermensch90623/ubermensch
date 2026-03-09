#!/bin/bash
#
# 데몬 관리 스크립트
# 크론 없이 nohup으로 백그라운드 실행. 매시간 자동 반복.
#
# 사용법:
#   ./setup_cron.sh          # 시작
#   ./setup_cron.sh stop     # 중지
#   ./setup_cron.sh status   # 상태 확인
#   ./setup_cron.sh restart  # 재시작
#   ./setup_cron.sh logs     # 로그 보기

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
DAEMON_SCRIPT="$PROJECT_DIR/daemon.py"
PID_FILE="$PROJECT_DIR/.daemon.pid"
LOG_FILE="$PROJECT_DIR/logs/daemon.log"

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

is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

start_daemon() {
    if is_running; then
        PID=$(cat "$PID_FILE")
        echo "이미 실행 중입니다. (PID: $PID)"
        echo "  상태 확인: $0 status"
        echo "  재시작:    $0 restart"
        return 1
    fi

    # ANTHROPIC_API_KEY 확인
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo "경고: ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다."
        echo "  export ANTHROPIC_API_KEY='your-key'"
        echo ""
    fi

    echo "데몬 시작 중..."
    cd "$PROJECT_DIR"
    nohup "$PYTHON_BIN" "$DAEMON_SCRIPT" >> "$LOG_FILE" 2>&1 &
    DAEMON_PID=$!

    # 시작 확인
    sleep 1
    if kill -0 "$DAEMON_PID" 2>/dev/null; then
        echo "$DAEMON_PID" > "$PID_FILE"
        echo ""
        echo "==================================="
        echo "  데몬 시작 완료! (PID: $DAEMON_PID)"
        echo "==================================="
        echo ""
        echo "  매시간 자동으로 태스크를 처리합니다."
        echo "  터미널을 닫아도 계속 동작합니다."
        echo ""
        echo "  작업 추가: python main.py add \"할 일\" -p high"
        echo "  상태 확인: $0 status"
        echo "  로그 보기: $0 logs"
        echo "  중지:      $0 stop"
    else
        echo "오류: 데몬 시작 실패. 로그를 확인하세요:"
        echo "  tail -20 $LOG_FILE"
        return 1
    fi
}

stop_daemon() {
    if ! is_running; then
        echo "실행 중인 데몬이 없습니다."
        return 0
    fi

    PID=$(cat "$PID_FILE")
    echo "데몬 종료 중... (PID: $PID)"
    kill "$PID" 2>/dev/null

    # 종료 대기 (최대 10초)
    for i in $(seq 1 10); do
        if ! kill -0 "$PID" 2>/dev/null; then
            echo "데몬 종료 완료."
            rm -f "$PID_FILE"
            return 0
        fi
        sleep 1
    done

    # 강제 종료
    echo "강제 종료 중..."
    kill -9 "$PID" 2>/dev/null
    rm -f "$PID_FILE"
    echo "데몬 강제 종료 완료."
}

show_status() {
    echo "=== Ubermensch 데몬 상태 ==="
    echo ""

    if is_running; then
        PID=$(cat "$PID_FILE")
        echo "상태: 실행 중 (PID: $PID)"

        # 프로세스 시작 시간
        if command -v ps &>/dev/null; then
            START=$(ps -o lstart= -p "$PID" 2>/dev/null || echo "알 수 없음")
            echo "시작: $START"
        fi
    else
        echo "상태: 중지됨"
    fi
    echo ""

    # 대기 태스크 수
    PENDING=$(find "$PROJECT_DIR/tasks/queue" -name "*.json" 2>/dev/null | wc -l)
    RESULTS=$(find "$PROJECT_DIR/tasks/results" -name "*.json" 2>/dev/null | wc -l)
    echo "대기 태스크: ${PENDING}개"
    echo "완료된 결과: ${RESULTS}개"

    # 최근 로그
    if [ -f "$LOG_FILE" ]; then
        echo ""
        echo "=== 최근 로그 (마지막 10줄) ==="
        tail -10 "$LOG_FILE"
    fi
}

show_logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -50 "$LOG_FILE"
    else
        echo "로그 파일이 없습니다."
    fi
}

case "${1:-start}" in
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    restart)
        stop_daemon
        sleep 1
        start_daemon
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "사용법: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
