#!/usr/bin/env python3
"""
백그라운드 데몬 - 사람이 직접 켜지 않아도 자동으로 동작한다.

동작 방식:
1. 크론(cron)이 매시간 이 스크립트를 실행
2. 이미 실행 중이면 중복 실행 방지 (lock file)
3. 태스크 큐 확인 → 있으면 처리
4. 예약된 정기 작업 실행
5. 처리 완료 후 자동 종료 (크론이 다시 깨워줌)
"""

from __future__ import annotations

import json
import logging
import os
import sys
import fcntl
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
LOG_DIR = PROJECT_ROOT / "logs"
SCHEDULES_FILE = PROJECT_ROOT / "schedules.json"

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
    """Lock file로 중복 실행 방지"""

    def __init__(self):
        self.lockfile = open(LOCK_FILE, "w")
        self.locked = False

    def acquire(self) -> bool:
        try:
            fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lockfile.write(str(os.getpid()))
            self.lockfile.flush()
            self.locked = True
            return True
        except BlockingIOError:
            return False

    def release(self):
        if self.locked:
            fcntl.flock(self.lockfile, fcntl.LOCK_UN)
            self.lockfile.close()
            try:
                LOCK_FILE.unlink()
            except FileNotFoundError:
                pass


# === 예약 작업 관리 ===

def load_schedules() -> list[dict]:
    """예약된 정기 작업 로드"""
    if not SCHEDULES_FILE.exists():
        # 기본 예약 작업 생성
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
    """예약 작업 저장"""
    with open(SCHEDULES_FILE, "w", encoding="utf-8") as f:
        json.dump(schedules, f, ensure_ascii=False, indent=2)


def is_schedule_due(schedule: dict) -> bool:
    """예약 작업 실행 시간이 되었는지 확인"""
    if not schedule.get("enabled", True):
        return False

    last_run = schedule.get("last_run")
    if last_run is None:
        return True

    interval = schedule.get("interval_hours", 24)
    last_dt = datetime.fromisoformat(last_run)
    elapsed = (datetime.now() - last_dt).total_seconds() / 3600
    return elapsed >= interval


# === 메인 데몬 로직 ===

def create_config() -> SystemConfig:
    return SystemConfig(
        debate=DebateConfig(max_rounds=3, consensus_threshold=0.75),
        refinement=RefinementConfig(max_iterations=2, quality_threshold=0.8),
        task_watcher=TaskWatcherConfig(enabled=True),
    )


def process_task(config: SystemConfig, task: Task) -> str:
    """단일 태스크 처리"""
    team = get_default_team()

    if task.team:
        team = [
            ROLE_PRESETS[r] for r in task.team if r in ROLE_PRESETS
        ] or get_default_team()

    loop = RefinementLoop(config, team)
    result = loop.run(task.description)
    return result.final_output


def run_daemon():
    """데몬 메인 루프 (크론에 의해 매시간 호출)"""
    lock = SingleInstance()

    if not lock.acquire():
        logger.info("이미 실행 중인 인스턴스가 있음. 종료.")
        return

    atexit.register(lock.release)

    logger.info("=" * 50)
    logger.info("데몬 시작")
    logger.info("=" * 50)

    config = create_config()
    if not config.api_key:
        logger.error("ANTHROPIC_API_KEY 환경변수 미설정. 종료.")
        return

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
            task = Task(
                id=f"sched_{schedule['id']}_{datetime.now().strftime('%Y%m%d%H')}",
                title=schedule["name"],
                description=schedule["description"],
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

    logger.info(f"데몬 종료. 처리된 작업: {processed}개")
    logger.info("=" * 50)


if __name__ == "__main__":
    run_daemon()
