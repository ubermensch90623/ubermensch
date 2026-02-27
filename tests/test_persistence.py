"""팀 설정 영속화 테스트."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ubermensch.agents.corp.organization import LearningAgentCorp
from ubermensch.core.persistence import load_corp_state, restore_corp, save_corp_state


@pytest.fixture
def tmp_state_file(tmp_path: Path) -> Path:
    return tmp_path / "test_state.json"


@pytest.fixture
def hired_corp() -> LearningAgentCorp:
    corp = LearningAgentCorp()
    corp.hire_wave(1)  # plumber + data_redteam
    corp.hire_wave(2)  # tracker
    return corp


class TestSaveState:
    """상태 저장 테스트."""

    def test_save_creates_file(self, hired_corp, tmp_state_file):
        result = save_corp_state(hired_corp, tmp_state_file)
        assert result.exists()

    def test_save_valid_json(self, hired_corp, tmp_state_file):
        save_corp_state(hired_corp, tmp_state_file)
        data = json.loads(tmp_state_file.read_text())
        assert "version" in data
        assert "deployed_agents" in data
        assert "task_force_history" in data

    def test_save_agents_count(self, hired_corp, tmp_state_file):
        save_corp_state(hired_corp, tmp_state_file)
        data = json.loads(tmp_state_file.read_text())
        assert len(data["deployed_agents"]) == 3  # plumber, data_redteam, tracker

    def test_save_agent_has_required_fields(self, hired_corp, tmp_state_file):
        save_corp_state(hired_corp, tmp_state_file)
        data = json.loads(tmp_state_file.read_text())
        agent = data["deployed_agents"][0]
        assert "name" in agent
        assert "model" in agent
        assert "class" in agent

    def test_save_model_info(self, hired_corp, tmp_state_file):
        save_corp_state(hired_corp, tmp_state_file)
        data = json.loads(tmp_state_file.read_text())
        assert data["model"] == "claude-sonnet-4-20250514"

    def test_save_empty_corp(self, tmp_state_file):
        corp = LearningAgentCorp()
        save_corp_state(corp, tmp_state_file)
        data = json.loads(tmp_state_file.read_text())
        assert len(data["deployed_agents"]) == 0

    def test_save_with_tf_history(self, hired_corp, tmp_state_file):
        # TF 편성
        hired_corp.tf_manager.create_tf(
            name="emergency",
            problem="파이프라인 장애",
            leader_name="plumber",
            member_names=["data_redteam"],
            goal="긴급 복구",
        )
        save_corp_state(hired_corp, tmp_state_file)
        data = json.loads(tmp_state_file.read_text())
        assert len(data["task_force_history"]) == 1
        assert data["task_force_history"][0]["name"] == "emergency"


class TestLoadState:
    """상태 로드 테스트."""

    def test_load_saved_state(self, hired_corp, tmp_state_file):
        save_corp_state(hired_corp, tmp_state_file)
        state = load_corp_state(tmp_state_file)
        assert len(state["deployed_agents"]) == 3

    def test_load_nonexistent_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_corp_state(tmp_path / "nonexistent.json")


class TestRestoreCorp:
    """조직 복원 테스트."""

    def test_restore_agents(self, hired_corp, tmp_state_file):
        save_corp_state(hired_corp, tmp_state_file)
        restored = restore_corp(tmp_state_file)
        assert restored.headcount == 3
        assert "plumber" in restored.agent_names
        assert "data_redteam" in restored.agent_names
        assert "tracker" in restored.agent_names

    def test_restore_agent_types(self, hired_corp, tmp_state_file):
        save_corp_state(hired_corp, tmp_state_file)
        restored = restore_corp(tmp_state_file)
        from ubermensch.agents.corp.data_team import PlumberAgent
        assert isinstance(restored.get_agent("plumber"), PlumberAgent)

    def test_restore_tf_history(self, hired_corp, tmp_state_file):
        hired_corp.tf_manager.create_tf(
            name="emergency",
            problem="test",
            leader_name="plumber",
            member_names=[],
            goal="test",
        )
        save_corp_state(hired_corp, tmp_state_file)
        restored = restore_corp(tmp_state_file)
        assert "emergency" in restored.tf_manager._task_forces

    def test_restore_full_corp(self, tmp_state_file):
        corp = LearningAgentCorp()
        corp.hire_all()
        save_corp_state(corp, tmp_state_file)

        restored = restore_corp(tmp_state_file)
        assert restored.headcount == corp.headcount

    def test_restore_preserves_model(self, tmp_state_file):
        corp = LearningAgentCorp(model="claude-haiku-4-5-20251001")
        corp.hire_wave(1)
        save_corp_state(corp, tmp_state_file)

        restored = restore_corp(tmp_state_file)
        assert restored.model == "claude-haiku-4-5-20251001"

    def test_save_restore_roundtrip(self, tmp_state_file):
        """저장 -> 복원 -> 저장이 동일한 결과를 내는지."""
        corp = LearningAgentCorp()
        corp.hire_all()
        save_corp_state(corp, tmp_state_file)
        data1 = json.loads(tmp_state_file.read_text())

        restored = restore_corp(tmp_state_file)
        save_corp_state(restored, tmp_state_file)
        data2 = json.loads(tmp_state_file.read_text())

        # 에이전트 목록이 동일해야 함
        names1 = sorted(a["name"] for a in data1["deployed_agents"])
        names2 = sorted(a["name"] for a in data2["deployed_agents"])
        assert names1 == names2
