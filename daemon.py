#!/usr/bin/env python3
"""
백그라운드 데몬 - 사람이 직접 켜지 않아도 자동으로 동작한다.

크론 없이 자체적으로 매시간 반복한다.
nohup으로 띄우면 터미널을 꺼도 계속 돌아간다.

동작 방식:
1. setup_cron.sh 로 한 번 띄우면 끝
2. 매시간(3600초) 자동으로 깨어남
3. 태스크 큐 확인 → 있으면 처리
4. 예약된 정기 작업 실행
5. 다시 잠들기 → 반복

사용법:
    ./setup_cron.sh          # 백그라운드 시작
    ./setup_cron.sh stop     # 중지
    ./setup_cron.sh status   # 상태 확인
"""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
import fcntl
import time
import atexit
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 path에 추가
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.roles import get_default_team, ROLE_PRESETS
from config.settings import SystemConfig, DebateConfig, RefinementConfig, TaskWatcherConfig
from core.refinement import RefinementLoop
from tasks.watcher import TaskQueue, Task, TaskStatus, TaskPriority

# === 설정 ===
LOCK_FILE = PROJECT_ROOT / ".daemon.lock"
PID_FILE = PROJECT_ROOT / ".daemon.pid"
LOG_DIR = PROJECT_ROOT / "logs"
SCHEDULES_FILE = PROJECT_ROOT / "schedules.json"
INTERVAL_SECONDS = 3600  # 매시간

LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "daemon.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("daemon")


# === 중복 실행 방지 ===

class SingleInstance:
    """Lock file + PID file로 중복 실행 방지"""

    def __init__(self):
        self.lockfile = open(LOCK_FILE, "w")
        self.locked = False

    def acquire(self) -> bool:
        try:
            fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lockfile.write(str(os.getpid()))
            self.lockfile.flush()
            self.locked = True
            # PID 파일도 별도 기록 (상태 확인용)
            with open(PID_FILE, "w") as f:
                f.write(str(os.getpid()))
            return True
        except BlockingIOError:
            return False

    def release(self):
        if self.locked:
            fcntl.flock(self.lockfile, fcntl.LOCK_UN)
            self.lockfile.close()
            for f in (LOCK_FILE, PID_FILE):
                try:
                    f.unlink()
                except FileNotFoundError:
                    pass


# === 예약 작업 관리 ===

def load_schedules() -> list[dict]:
    """예약된 정기 작업 로드"""
    if not SCHEDULES_FILE.exists():
        default_schedules = [
            {
                "id": "health_check",
                "name": "시스템 상태 점검",
                "description": "현재 시스템의 상태를 점검하고 개선점을 찾아라.",
                "interval_hours": 24,
                "last_run": None,
                "enabled": True,
                "team": ["architect", "critic"],
            },
        ]
        save_schedules(default_schedules)
        return default_schedules

    with open(SCHEDULES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_schedules(schedules: list[dict]):
    with open(SCHEDULES_FILE, "w", encoding="utf-8") as f:
        json.dump(schedules, f, ensure_ascii=False, indent=2)


def is_schedule_due(schedule: dict) -> bool:
    if not schedule.get("enabled", True):
        return False

    last_run = schedule.get("last_run")
    if last_run is None:
        return True

    interval = schedule.get("interval_hours", 24)
    last_dt = datetime.fromisoformat(last_run)
    elapsed = (datetime.now() - last_dt).total_seconds() / 3600
    return elapsed >= interval


# === 파일 읽기 ===

def read_source_files(file_paths: list[str]) -> str:
    """현재 브랜치의 소스 파일들을 읽어서 하나의 텍스트로 합친다."""
    parts = []
    for rel_path in file_paths:
        full_path = PROJECT_ROOT / rel_path
        if not full_path.exists():
            parts.append(f"\n--- {rel_path} (파일 없음) ---\n")
            continue
        try:
            content = full_path.read_text(encoding="utf-8")
            parts.append(f"\n--- {rel_path} ---\n```python\n{content}\n```\n")
        except Exception as e:
            parts.append(f"\n--- {rel_path} (읽기 실패: {e}) ---\n")
    return "\n".join(parts)


def read_branch_files(branch: str, file_paths: list[str]) -> str:
    """다른 git 브랜치에 있는 파일들을 읽어온다.
    이전 작업 브랜치의 코드를 에이전트가 볼 수 있게 해준다."""
    import subprocess
    parts = []
    for rel_path in file_paths:
        try:
            result = subprocess.run(
                ["git", "show", f"{branch}:{rel_path}"],
                capture_output=True, text=True, cwd=str(PROJECT_ROOT),
            )
            if result.returncode == 0:
                content = result.stdout
                ext = Path(rel_path).suffix
                lang = {"py": "python", ".md": "markdown", ".json": "json",
                         ".sh": "bash", ".bat": "batch"}.get(ext, "")
                parts.append(f"\n--- [{branch}] {rel_path} ---\n```{lang}\n{content}\n```\n")
            else:
                parts.append(f"\n--- [{branch}] {rel_path} (없음) ---\n")
        except Exception as e:
            parts.append(f"\n--- [{branch}] {rel_path} (읽기 실패: {e}) ---\n")
    return "\n".join(parts)


def list_branch_files(branch: str) -> list[str]:
    """브랜치의 전체 파일 목록을 가져온다."""
    import subprocess
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", branch],
        capture_output=True, text=True, cwd=str(PROJECT_ROOT),
    )
    if result.returncode == 0:
        return result.stdout.strip().split("\n")
    return []


def read_branch_key_files(branch: str, max_files: int = 15) -> str:
    """브랜치의 주요 파일들을 자동으로 읽어온다.
    .py, .md, .json 파일 위주로 최대 max_files개."""
    all_files = list_branch_files(branch)
    if not all_files:
        return f"\n(브랜치 {branch}에서 파일을 찾을 수 없음)\n"

    # 중요한 파일 우선 선택
    priority_files = []
    other_files = []
    for f in all_files:
        name = Path(f).name.lower()
        if name in ("claude.md", "readme.md", "pyproject.toml", "package.json"):
            priority_files.append(f)
        elif f.endswith((".py", ".md", ".json")) and not f.endswith(".gitkeep"):
            other_files.append(f)

    selected = priority_files + other_files[:max_files - len(priority_files)]

    parts = [f"\n=== 브랜치: {branch} (전체 {len(all_files)}개 파일, 주요 {len(selected)}개 표시) ===\n"]
    parts.append("전체 파일 목록: " + ", ".join(all_files[:30]))
    if len(all_files) > 30:
        parts.append(f"  ... 외 {len(all_files) - 30}개")
    parts.append("")
    parts.append(read_branch_files(branch, selected))
    return "\n".join(parts)


def build_review_prompt(description: str, file_paths: list[str] | None,
                        branches: list[str] | None = None) -> str:
    """예약 작업의 설명 + 실제 코드를 합쳐서 전체 프롬프트를 만든다.
    branches가 있으면 다른 브랜치의 코드도 읽어서 포함한다."""
    prompt_parts = [description]

    if file_paths:
        code_text = read_source_files(file_paths)
        prompt_parts.append(f"\n\n=== 현재 브랜치 검토 대상 코드 ===\n{code_text}")

    if branches:
        for branch in branches:
            branch_text = read_branch_key_files(branch)
            prompt_parts.append(branch_text)

    return "\n".join(prompt_parts)


# === 메인 데몬 로직 ===

def create_config() -> SystemConfig:
    return SystemConfig(
        debate=DebateConfig(max_rounds=3, consensus_threshold=0.75),
        refinement=RefinementConfig(max_iterations=2, quality_threshold=0.8),
        task_watcher=TaskWatcherConfig(enabled=True),
    )


def process_task(config: SystemConfig, task: Task) -> str:
    team = get_default_team()

    if task.team:
        team = [
            ROLE_PRESETS[r] for r in task.team if r in ROLE_PRESETS
        ] or get_default_team()

    loop = RefinementLoop(config, team)
    result = loop.run(task.description)
    return result.final_output


def run_cycle(config: SystemConfig) -> int:
    """한 사이클 실행. 처리된 태스크 수 반환."""
    queue = TaskQueue()
    processed = 0

    # 1. 큐에 있는 대기 태스크 처리
    pending = queue.get_pending_tasks()
    if pending:
        logger.info(f"대기 태스크 {len(pending)}개 발견")
        for task in pending:
            logger.info(f"처리 중: [{task.priority.value}] {task.title}")
            queue.update_status(task.id, TaskStatus.IN_PROGRESS)
            try:
                output = process_task(config, task)
                queue.update_status(task.id, TaskStatus.COMPLETED)
                queue.save_result(task.id, {
                    "task_id": task.id,
                    "task_title": task.title,
                    "output": output[:5000],
                    "success": True,
                })
                processed += 1
                logger.info(f"완료: {task.title}")
            except Exception as e:
                queue.update_status(task.id, TaskStatus.FAILED)
                queue.save_result(task.id, {
                    "task_id": task.id,
                    "error": str(e),
                    "success": False,
                })
                logger.error(f"실패: {task.title} - {e}")
    else:
        logger.info("대기 태스크 없음")

    # 2. 예약된 정기 작업 확인
    schedules = load_schedules()
    for schedule in schedules:
        if is_schedule_due(schedule):
            logger.info(f"예약 작업 실행: {schedule['name']}")
            # 파일/브랜치가 지정되어 있으면 실제 코드를 읽어서 붙인다
            full_description = build_review_prompt(
                schedule["description"],
                schedule.get("files"),
                schedule.get("branches"),
            )
            task = Task(
                id=f"sched_{schedule['id']}_{datetime.now().strftime('%Y%m%d%H')}",
                title=schedule["name"],
                description=full_description,
                priority=TaskPriority.MEDIUM,
                team=schedule.get("team"),
            )
            try:
                output = process_task(config, task)
                queue.save_result(task.id, {
                    "task_id": task.id,
                    "task_title": task.title,
                    "output": output[:5000],
                    "success": True,
                    "type": "scheduled",
                })
                schedule["last_run"] = datetime.now().isoformat()
                processed += 1
                logger.info(f"예약 작업 완료: {schedule['name']}")
            except Exception as e:
                logger.error(f"예약 작업 실패: {schedule['name']} - {e}")

    save_schedules(schedules)

    # 3. 사이클 결과를 읽기 쉬운 리포트로 저장
    if processed > 0:
        generate_report(queue)

    return processed


# === 리포트 생성 ===

REPORT_DIR = PROJECT_ROOT / "reports"

def generate_report(queue: TaskQueue):
    """모든 결과를 모아서 사람이 읽기 쉬운 리포트 하나로 만든다."""
    REPORT_DIR.mkdir(exist_ok=True)
    now = datetime.now()

    # 결과 파일 전부 읽기
    results = []
    for result_file in sorted(queue.results_dir.glob("*.json")):
        try:
            with open(result_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                results.append(data)
        except Exception:
            continue

    if not results:
        return

    # 최신 리포트 생성
    lines = []
    lines.append(f"# 에이전트 리뷰 리포트")
    lines.append(f"")
    lines.append(f"생성 시각: {now.strftime('%Y년 %m월 %d일 %H시 %M분')}")
    lines.append(f"총 완료 작업: {len(results)}건")
    lines.append(f"")

    # 요약 테이블
    lines.append("## 작업 목록")
    lines.append("")
    lines.append("| # | 작업 | 상태 |")
    lines.append("|---|------|------|")
    for i, r in enumerate(results, 1):
        title = r.get("task_title", r.get("task_id", "?"))
        status = "성공" if r.get("success") else "실패"
        lines.append(f"| {i} | {title} | {status} |")
    lines.append("")

    # 각 작업의 상세 결과
    lines.append("## 상세 결과")
    lines.append("")
    for i, r in enumerate(results, 1):
        title = r.get("task_title", r.get("task_id", "?"))
        lines.append(f"### {i}. {title}")
        lines.append("")
        if r.get("success"):
            output = r.get("output", "(결과 없음)")
            lines.append(output)
        else:
            error = r.get("error", "(오류 내용 없음)")
            lines.append(f"**실패 원인:** {error}")
        lines.append("")
        lines.append("---")
        lines.append("")

    report_text = "\n".join(lines)

    # 최신 리포트 (항상 같은 파일에 덮어쓰기 - 가장 최근 결과)
    latest_path = REPORT_DIR / "latest.md"
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    # 날짜별 리포트 (이력 보관)
    dated_path = REPORT_DIR / f"{now.strftime('%Y-%m-%d_%H')}.md"
    with open(dated_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    logger.info(f"리포트 생성: {latest_path}")


def run_daemon():
    """데몬 메인 루프 - 매시간 자동 반복"""
    lock = SingleInstance()

    if not lock.acquire():
        print("이미 실행 중인 데몬이 있습니다.")
        print(f"상태 확인: ./setup_cron.sh status")
        print(f"중지 후 재시작: ./setup_cron.sh stop && ./setup_cron.sh")
        return

    atexit.register(lock.release)

    # SIGTERM 시 깔끔하게 종료
    running = True

    def handle_signal(signum, frame):
        nonlocal running
        logger.info(f"시그널 {signum} 수신. 종료 중...")
        running = False

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    logger.info("=" * 50)
    logger.info(f"데몬 시작 (PID: {os.getpid()})")
    logger.info(f"반복 간격: {INTERVAL_SECONDS}초 ({INTERVAL_SECONDS // 3600}시간)")
    logger.info("=" * 50)

    config = create_config()
    if not config.api_key:
        logger.error("ANTHROPIC_API_KEY 환경변수 미설정. 종료.")
        return

    cycle = 0
    while running:
        cycle += 1
        logger.info(f"--- 사이클 #{cycle} 시작 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")

        try:
            processed = run_cycle(config)
            logger.info(f"사이클 #{cycle} 완료. 처리: {processed}건")
        except Exception as e:
            logger.error(f"사이클 #{cycle} 오류: {e}", exc_info=True)

        if not running:
            break

        logger.info(f"다음 사이클까지 {INTERVAL_SECONDS}초 대기...")

        # sleep을 작은 단위로 나눠서 시그널 반응성 확보
        for _ in range(INTERVAL_SECONDS):
            if not running:
                break
            time.sleep(1)

    logger.info("데몬 종료.")


def run_once():
    """한 번만 실행하고 종료 (테스트/수동 실행용)"""
    config = create_config()
    if not config.api_key:
        logger.error("ANTHROPIC_API_KEY 환경변수 미설정.")
        return
    processed = run_cycle(config)
    print(f"처리 완료: {processed}건")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_once()
    else:
        run_daemon()
