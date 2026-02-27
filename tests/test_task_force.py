"""TaskForceManager 테스트."""

from __future__ import annotations

import pytest

from ubermensch.agents.corp.task_force import (
    MAX_CONCURRENT_TFS,
    MAX_TF_LIFESPAN_DAYS,
    TaskForceManager,
    TaskForceRecord,
)
from ubermensch.agents.corp.data_team import PlumberAgent, DataRedTeamAgent
from ubermensch.agents.corp.analytics_team import TrackerAgent, DiagnosticianAgent


@pytest.fixture
def tf_manager() -> TaskForceManager:
    """에이전트 풀이 채워진 TaskForceManager."""
    mgr = TaskForceManager()
    mgr.register_agents([
        PlumberAgent(),
        DataRedTeamAgent(),
        TrackerAgent(),
        DiagnosticianAgent(),
    ])
    return mgr


class TestTaskForceCreation:
    """TF 편성 테스트."""

    def test_create_tf(self, tf_manager: TaskForceManager):
        team = tf_manager.create_tf(
            name="emergency-data",
            problem="데이터 파이프라인 장애",
            leader_name="plumber",
            member_names=["data_redteam"],
            goal="장애 복구",
        )
        assert team is not None
        assert tf_manager.active_count == 1
        assert "plumber" in team.teammate_names

    def test_max_concurrent_tfs(self, tf_manager: TaskForceManager):
        # TF 2개까지 가능
        tf1 = tf_manager.create_tf(
            name="tf1", problem="p1",
            leader_name="plumber", member_names=[], goal="g1",
        )
        tf2 = tf_manager.create_tf(
            name="tf2", problem="p2",
            leader_name="tracker", member_names=[], goal="g2",
        )
        assert tf1 is not None
        assert tf2 is not None
        assert tf_manager.active_count == 2

        # 3번째 TF는 거부
        tf3 = tf_manager.create_tf(
            name="tf3", problem="p3",
            leader_name="diagnostician", member_names=[], goal="g3",
        )
        assert tf3 is None
        assert tf_manager.active_count == 2

    def test_create_tf_with_unknown_leader(self, tf_manager: TaskForceManager):
        team = tf_manager.create_tf(
            name="bad", problem="test",
            leader_name="nonexistent", member_names=[], goal="test",
        )
        assert team is None

    def test_create_tf_skips_unknown_members(self, tf_manager: TaskForceManager):
        team = tf_manager.create_tf(
            name="partial", problem="test",
            leader_name="plumber",
            member_names=["data_redteam", "nonexistent_agent"],
            goal="test",
        )
        assert team is not None
        assert "plumber" in team.teammate_names
        assert "data_redteam" in team.teammate_names


class TestTaskForceDissolution:
    """TF 해산 테스트."""

    @pytest.mark.asyncio
    async def test_dissolve_tf(self, tf_manager: TaskForceManager):
        tf_manager.create_tf(
            name="temp", problem="test",
            leader_name="plumber", member_names=[], goal="test",
        )
        assert tf_manager.active_count == 1

        record = await tf_manager.dissolve_tf(
            name="temp",
            result="문제 해결됨",
            lessons="파이프라인 모니터링 강화 필요",
        )
        assert record is not None
        assert not record.active
        assert record.result == "문제 해결됨"
        assert tf_manager.active_count == 0

    @pytest.mark.asyncio
    async def test_dissolve_nonexistent_returns_none(
        self, tf_manager: TaskForceManager
    ):
        result = await tf_manager.dissolve_tf("nope", "r", "l")
        assert result is None

    @pytest.mark.asyncio
    async def test_dissolve_frees_slot(self, tf_manager: TaskForceManager):
        tf_manager.create_tf(
            name="tf1", problem="p1",
            leader_name="plumber", member_names=[], goal="g1",
        )
        tf_manager.create_tf(
            name="tf2", problem="p2",
            leader_name="tracker", member_names=[], goal="g2",
        )
        assert not tf_manager.can_create_tf()

        await tf_manager.dissolve_tf("tf1", "done", "lesson")
        assert tf_manager.can_create_tf()


class TestTaskForceRecord:
    """TF 기록 테스트."""

    def test_active_flag(self):
        record = TaskForceRecord(
            name="test", problem="p", leader="l", members=["l"], goal="g"
        )
        assert record.active

        record.resolved_at = 1.0
        assert not record.active

    def test_age_days(self):
        import time

        record = TaskForceRecord(
            name="test", problem="p", leader="l",
            members=["l"], goal="g",
            created_at=time.time() - 86400 * 3,  # 3일 전
        )
        assert 2.9 < record.age_days < 3.1


class TestTaskForceStatus:
    """TF 현황 조회 테스트."""

    def test_empty_status(self, tf_manager: TaskForceManager):
        status = tf_manager.status()
        assert "활성 TF: 0/2" in status
        assert "에이전트 풀: 4명" in status

    def test_active_tf_in_status(self, tf_manager: TaskForceManager):
        tf_manager.create_tf(
            name="data-fix", problem="파이프라인 장애",
            leader_name="plumber", member_names=["data_redteam"],
            goal="긴급 복구",
        )
        status = tf_manager.status()
        assert "TF-data-fix" in status
        assert "리더: plumber" in status

    def test_expired_tf_detection(self, tf_manager: TaskForceManager):
        import time

        tf_manager.create_tf(
            name="old", problem="p",
            leader_name="plumber", member_names=[], goal="g",
        )
        # 강제로 생성 시간을 8일 전으로 설정
        tf_manager._task_forces["old"].created_at = (
            time.time() - 86400 * 8
        )

        expired = tf_manager.get_expired_tfs()
        assert len(expired) == 1
        assert expired[0].name == "old"
