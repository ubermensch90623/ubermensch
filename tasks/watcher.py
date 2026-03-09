"""
태스크 감시자 - 할 일이 생기면 자동으로 에이전트 시스템을 가동한다.

감시 방법:
1. 파일 기반: 지정 디렉토리에 태스크 파일이 생기면 처리
2. 스케줄 기반: 주기적으로 실행
3. 이벤트 기반: 외부 트리거 (webhook 등)
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from enum import Enum

from config.settings import SystemConfig, TaskWatcherConfig

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Task:
    """처리할 태스크"""
    id: str
    title: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = ""
    team: list[str] | None = None  # 사용할 에이전트 역할 리스트

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class TaskQueue:
    """태스크 큐 - 파일 기반 태스크 관리"""

    def __init__(self, queue_dir: str = "./tasks/queue"):
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir = self.queue_dir.parent / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def add_task(self, task: Task) -> str:
        """태스크 추가"""
        filepath = self.queue_dir / f"{task.id}.json"
        data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority.value,
            "status": task.status.value,
            "created_at": task.created_at,
            "team": task.team,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"태스크 추가됨: {task.id} - {task.title}")
        return str(filepath)

    def get_pending_tasks(self) -> list[Task]:
        """대기 중인 태스크 조회 (우선순위 순)"""
        tasks = []
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
        }

        for filepath in self.queue_dir.glob("*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("status") == TaskStatus.PENDING:
                    tasks.append(Task(
                        id=data["id"],
                        title=data["title"],
                        description=data["description"],
                        priority=TaskPriority(data.get("priority", "medium")),
                        status=TaskStatus(data["status"]),
                        created_at=data.get("created_at", ""),
                        team=data.get("team"),
                    ))
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"태스크 파일 파싱 실패: {filepath} - {e}")

        tasks.sort(key=lambda t: priority_order.get(t.priority, 99))
        return tasks

    def update_status(self, task_id: str, status: TaskStatus):
        """태스크 상태 업데이트"""
        filepath = self.queue_dir / f"{task_id}.json"
        if not filepath.exists():
            logger.warning(f"태스크 파일 없음: {task_id}")
            return

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["status"] = status.value
        data["updated_at"] = datetime.now().isoformat()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_result(self, task_id: str, result: dict):
        """태스크 결과 저장"""
        filepath = self.results_dir / f"{task_id}_result.json"
        result["completed_at"] = datetime.now().isoformat()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)


class TaskWatcher:
    """
    태스크 감시자.
    큐를 주기적으로 확인하고 새 태스크가 있으면 콜백을 호출한다.
    """

    def __init__(self, config: TaskWatcherConfig, on_task: callable):
        self.config = config
        self.on_task = on_task
        self.queue = TaskQueue(config.watch_paths[0] if config.watch_paths else "./tasks/queue")
        self._running = False

    def start(self):
        """감시 시작 (블로킹)"""
        if not self.config.enabled:
            logger.info("태스크 감시자 비활성화 상태")
            return

        self._running = True
        logger.info(
            f"태스크 감시 시작 (간격: {self.config.poll_interval_seconds}초)"
        )

        while self._running:
            try:
                self._check_and_process()
            except Exception as e:
                logger.error(f"태스크 처리 중 오류: {e}", exc_info=True)

            time.sleep(self.config.poll_interval_seconds)

    def stop(self):
        """감시 중지"""
        self._running = False
        logger.info("태스크 감시 중지")

    def run_once(self):
        """한 번만 확인하고 처리 (테스트/수동 실행용)"""
        self._check_and_process()

    def _check_and_process(self):
        """대기 태스크 확인 및 처리"""
        pending = self.queue.get_pending_tasks()
        if not pending:
            return

        logger.info(f"대기 태스크 {len(pending)}개 발견")

        for task in pending:
            logger.info(f"태스크 처리 시작: [{task.priority.value}] {task.title}")
            self.queue.update_status(task.id, TaskStatus.IN_PROGRESS)

            try:
                result = self.on_task(task)
                self.queue.update_status(task.id, TaskStatus.COMPLETED)
                self.queue.save_result(task.id, {
                    "task_id": task.id,
                    "task_title": task.title,
                    "output": str(result) if result else "완료",
                    "success": True,
                })
                logger.info(f"태스크 완료: {task.title}")
            except Exception as e:
                self.queue.update_status(task.id, TaskStatus.FAILED)
                self.queue.save_result(task.id, {
                    "task_id": task.id,
                    "task_title": task.title,
                    "error": str(e),
                    "success": False,
                })
                logger.error(f"태스크 실패: {task.title} - {e}")
