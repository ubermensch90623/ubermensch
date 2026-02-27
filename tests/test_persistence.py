"""TeamPersistence 유닛 테스트."""

import json
from pathlib import Path

import pytest

from ubermensch.core.message import SharedTask, TaskStatus
from ubermensch.core.persistence import TeamPersistence


@pytest.fixture
def tmp_persistence(tmp_path: Path):
    return TeamPersistence(base_dir=tmp_path)


class TestSaveConfig:
    def test_save_team_config(self, tmp_persistence: TeamPersistence):
        path = tmp_persistence.save_team_config(
            team_name="test-team",
            model="claude-sonnet-4-20250514",
            members=[
                {"name": "alice", "type": "SecurityReviewerAgent", "system_prompt": "..."},
                {"name": "bob", "type": "DebuggerAgent", "system_prompt": "..."},
            ],
        )
        assert path.exists()
        config = json.loads(path.read_text())
        assert config["name"] == "test-team"
        assert len(config["members"]) == 2
        assert config["members"][0]["name"] == "alice"

    def test_save_creates_directory(self, tmp_persistence: TeamPersistence):
        tmp_persistence.save_team_config("new-team", "model", [])
        team_dir = tmp_persistence.base_dir / "new-team"
        assert team_dir.is_dir()

    def test_save_overwrites(self, tmp_persistence: TeamPersistence):
        tmp_persistence.save_team_config("t", "v1", [{"name": "old"}])
        tmp_persistence.save_team_config("t", "v2", [{"name": "new"}])
        config = tmp_persistence.load_team_config("t")
        assert config["model"] == "v2"
        assert config["members"][0]["name"] == "new"


class TestSaveTasks:
    def test_save_tasks(self, tmp_persistence: TeamPersistence):
        tasks = [
            SharedTask(id="t1", title="First", status=TaskStatus.COMPLETED, result="done"),
            SharedTask(id="t2", title="Second", status=TaskStatus.PENDING, priority=5),
            SharedTask(
                id="t3",
                title="Third",
                status=TaskStatus.FAILED,
                error="broken",
                depends_on=["t1"],
            ),
        ]
        path = tmp_persistence.save_tasks("test-team", tasks)
        assert path.exists()
        data = json.loads(path.read_text())
        assert len(data) == 3
        assert data[0]["status"] == "completed"
        assert data[2]["depends_on"] == ["t1"]

    def test_save_task_with_non_serializable_result(self, tmp_persistence: TeamPersistence):
        """직렬화 불가능한 result는 str로 변환."""
        tasks = [SharedTask(id="t1", title="Obj", result=object())]
        path = tmp_persistence.save_tasks("team", tasks)
        data = json.loads(path.read_text())
        assert isinstance(data[0]["result"], str)


class TestLoadConfig:
    def test_load_config(self, tmp_persistence: TeamPersistence):
        tmp_persistence.save_team_config("t", "model", [{"name": "a"}])
        config = tmp_persistence.load_team_config("t")
        assert config is not None
        assert config["name"] == "t"
        assert config["members"][0]["name"] == "a"

    def test_load_config_not_found(self, tmp_persistence: TeamPersistence):
        assert tmp_persistence.load_team_config("nonexistent") is None


class TestLoadTasks:
    def test_load_tasks(self, tmp_persistence: TeamPersistence):
        original = [
            SharedTask(
                id="t1",
                title="Task",
                description="Desc",
                status=TaskStatus.IN_PROGRESS,
                assigned_to="agent1",
                depends_on=["t0"],
                created_by="lead",
                priority=7,
                result={"key": "value"},
            ),
        ]
        tmp_persistence.save_tasks("t", original)
        loaded = tmp_persistence.load_tasks("t")

        assert loaded is not None
        assert len(loaded) == 1
        task = loaded[0]
        assert task.id == "t1"
        assert task.title == "Task"
        assert task.description == "Desc"
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.assigned_to == "agent1"
        assert task.depends_on == ["t0"]
        assert task.created_by == "lead"
        assert task.priority == 7
        assert task.result == {"key": "value"}

    def test_load_tasks_not_found(self, tmp_persistence: TeamPersistence):
        assert tmp_persistence.load_tasks("nonexistent") is None


class TestManagement:
    def test_list_teams_empty(self, tmp_persistence: TeamPersistence):
        assert tmp_persistence.list_teams() == []

    def test_list_teams(self, tmp_persistence: TeamPersistence):
        tmp_persistence.save_team_config("alpha", "m", [])
        tmp_persistence.save_team_config("beta", "m", [])
        teams = tmp_persistence.list_teams()
        assert set(teams) == {"alpha", "beta"}

    def test_team_exists(self, tmp_persistence: TeamPersistence):
        assert not tmp_persistence.team_exists("nope")
        tmp_persistence.save_team_config("exists", "m", [])
        assert tmp_persistence.team_exists("exists")

    def test_delete_team(self, tmp_persistence: TeamPersistence):
        tmp_persistence.save_team_config("doomed", "m", [])
        assert tmp_persistence.delete_team("doomed") is True
        assert not tmp_persistence.team_exists("doomed")

    def test_delete_nonexistent(self, tmp_persistence: TeamPersistence):
        assert tmp_persistence.delete_team("nope") is False


class TestSaveTeamIntegration:
    def test_save_team_object(self, tmp_persistence: TeamPersistence):
        """AgentTeam 객체를 직접 저장하는 통합 테스트."""
        from unittest.mock import MagicMock

        # AgentTeam-like mock
        mock_team = MagicMock()
        mock_team.name = "my-team"
        mock_team.model = "claude-sonnet-4-20250514"

        agent1 = MagicMock()
        agent1.name = "reviewer"
        agent1.system_prompt = "Review code"
        type(agent1).__name__ = "SecurityReviewerAgent"

        mock_team._teammates = {"reviewer": agent1}
        mock_team.task_list.all_tasks = [
            SharedTask(id="t1", title="Review", status=TaskStatus.COMPLETED),
        ]

        config_path, tasks_path = tmp_persistence.save_team(mock_team)
        assert config_path.exists()
        assert tasks_path.exists()

        config = tmp_persistence.load_team_config("my-team")
        assert config["members"][0]["name"] == "reviewer"
        assert config["members"][0]["type"] == "SecurityReviewerAgent"
