"""Team config persistence - JSON 기반 팀 설정 저장/복원."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ubermensch.core.message import SharedTask, TaskStatus

logger = logging.getLogger(__name__)

DEFAULT_TEAMS_DIR = Path.home() / ".ubermensch" / "teams"


class TeamPersistence:
    """팀 설정과 태스크 상태를 JSON 파일로 영속화합니다.

    저장 구조:
        base_dir/
        └── {team_name}/
            ├── config.json      # 팀 구성 (멤버 목록, 모델 등)
            └── tasks.json       # 태스크 리스트 스냅샷

    사용 예:
        persistence = TeamPersistence()

        # 저장
        persistence.save_team(team)

        # 복원
        config = persistence.load_team_config("my-team")
        tasks = persistence.load_tasks("my-team")
    """

    def __init__(self, base_dir: Path | str | None = None) -> None:
        self.base_dir = Path(base_dir) if base_dir else DEFAULT_TEAMS_DIR

    def _team_dir(self, team_name: str) -> Path:
        return self.base_dir / team_name

    # --- 저장 ---

    def save_team_config(
        self,
        team_name: str,
        model: str,
        members: list[dict[str, str]],
    ) -> Path:
        """팀 구성을 config.json에 저장합니다.

        Args:
            team_name: 팀 이름
            model: 사용 중인 모델
            members: [{"name": "...", "type": "...", "system_prompt": "..."}]

        Returns:
            저장된 파일 경로
        """
        team_dir = self._team_dir(team_name)
        team_dir.mkdir(parents=True, exist_ok=True)

        config = {
            "name": team_name,
            "model": model,
            "members": members,
        }

        config_path = team_dir / "config.json"
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2))
        logger.info(f"Team config saved: {config_path}")
        return config_path

    def save_tasks(
        self,
        team_name: str,
        tasks: list[SharedTask],
    ) -> Path:
        """태스크 리스트를 tasks.json에 저장합니다."""
        team_dir = self._team_dir(team_name)
        team_dir.mkdir(parents=True, exist_ok=True)

        task_dicts = []
        for task in tasks:
            d = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "assigned_to": task.assigned_to,
                "depends_on": task.depends_on,
                "created_by": task.created_by,
                "priority": task.priority,
                "error": task.error,
            }
            # result는 직렬화 가능한 경우만 저장
            try:
                json.dumps(task.result)
                d["result"] = task.result
            except (TypeError, ValueError):
                d["result"] = str(task.result) if task.result is not None else None

            task_dicts.append(d)

        tasks_path = team_dir / "tasks.json"
        tasks_path.write_text(json.dumps(task_dicts, ensure_ascii=False, indent=2))
        logger.info(f"Tasks saved: {tasks_path} ({len(task_dicts)} tasks)")
        return tasks_path

    def save_team(self, team: Any) -> tuple[Path, Path]:
        """AgentTeam 전체를 저장합니다 (config + tasks).

        Args:
            team: AgentTeam 인스턴스

        Returns:
            (config_path, tasks_path)
        """
        members = [
            {
                "name": agent.name,
                "type": type(agent).__name__,
                "system_prompt": agent.system_prompt,
            }
            for agent in team._teammates.values()
        ]

        config_path = self.save_team_config(team.name, team.model, members)
        tasks_path = self.save_tasks(team.name, team.task_list.all_tasks)
        return config_path, tasks_path

    # --- 로드 ---

    def load_team_config(self, team_name: str) -> dict[str, Any] | None:
        """팀 구성을 로드합니다."""
        config_path = self._team_dir(team_name) / "config.json"
        if not config_path.exists():
            logger.warning(f"Team config not found: {config_path}")
            return None

        config = json.loads(config_path.read_text())
        logger.info(f"Team config loaded: {config_path}")
        return config

    def load_tasks(self, team_name: str) -> list[SharedTask] | None:
        """태스크 리스트를 로드합니다."""
        tasks_path = self._team_dir(team_name) / "tasks.json"
        if not tasks_path.exists():
            logger.warning(f"Tasks not found: {tasks_path}")
            return None

        task_dicts = json.loads(tasks_path.read_text())
        tasks = []
        for d in task_dicts:
            task = SharedTask(
                id=d["id"],
                title=d["title"],
                description=d.get("description", ""),
                status=TaskStatus(d["status"]),
                assigned_to=d.get("assigned_to"),
                depends_on=d.get("depends_on", []),
                created_by=d.get("created_by", ""),
                priority=d.get("priority", 0),
                result=d.get("result"),
                error=d.get("error"),
            )
            tasks.append(task)

        logger.info(f"Tasks loaded: {tasks_path} ({len(tasks)} tasks)")
        return tasks

    # --- 관리 ---

    def list_teams(self) -> list[str]:
        """저장된 팀 목록을 반환합니다."""
        if not self.base_dir.exists():
            return []
        return [
            d.name
            for d in self.base_dir.iterdir()
            if d.is_dir() and (d / "config.json").exists()
        ]

    def delete_team(self, team_name: str) -> bool:
        """팀 데이터를 삭제합니다."""
        team_dir = self._team_dir(team_name)
        if not team_dir.exists():
            return False

        import shutil

        shutil.rmtree(team_dir)
        logger.info(f"Team deleted: {team_dir}")
        return True

    def team_exists(self, team_name: str) -> bool:
        """팀 데이터가 존재하는지 확인합니다."""
        return (self._team_dir(team_name) / "config.json").exists()
