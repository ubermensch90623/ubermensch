"""LearningAgentCorp 조직 관리 테스트."""

from __future__ import annotations

import pytest

from ubermensch.agents.corp.organization import (
    HIRING_PRIORITY,
    TEAM_CONFIGS,
    LearningAgentCorp,
    _get_agent_factory,
)
from ubermensch.agents.corp.c_suite import CEOAgent, CTOAgent, COOAgent, CFOAgent, CMOAgent
from ubermensch.agents.corp.data_team import PlumberAgent, DataRedTeamAgent
from ubermensch.core.base_agent import BaseAgent


class TestHiring:
    """채용 프로세스 테스트."""

    def test_hire_single_agent(self, corp: LearningAgentCorp):
        agent = PlumberAgent()
        corp.hire(agent)
        assert corp.headcount == 1
        assert "plumber" in corp.agent_names
        assert corp.get_agent("plumber") is agent

    def test_hire_duplicate_replaces(self, corp: LearningAgentCorp):
        a1 = PlumberAgent()
        a2 = PlumberAgent()
        corp.hire(a1)
        corp.hire(a2)
        assert corp.headcount == 1
        assert corp.get_agent("plumber") is a2

    def test_fire_agent(self, corp: LearningAgentCorp):
        agent = PlumberAgent()
        corp.hire(agent)
        fired = corp.fire("plumber")
        assert fired is agent
        assert corp.headcount == 0
        assert corp.get_agent("plumber") is None

    def test_fire_nonexistent_returns_none(self, corp: LearningAgentCorp):
        assert corp.fire("nonexistent") is None

    def test_hire_wave_1(self, corp: LearningAgentCorp):
        hired = corp.hire_wave(1)
        names = [a.name for a in hired]
        assert "plumber" in names
        assert "data_redteam" in names
        assert corp.headcount == 2

    def test_hire_wave_2(self, corp: LearningAgentCorp):
        hired = corp.hire_wave(2)
        names = [a.name for a in hired]
        assert "tracker" in names
        assert corp.headcount == 1

    def test_hire_wave_skips_already_hired(self, corp: LearningAgentCorp):
        corp.hire(PlumberAgent())
        hired = corp.hire_wave(1)
        # plumber 이미 있으므로 data_redteam만 채용
        names = [a.name for a in hired]
        assert "plumber" not in names
        assert "data_redteam" in names
        assert corp.headcount == 2

    def test_hire_wave_invalid(self, corp: LearningAgentCorp):
        assert corp.hire_wave(0) == []
        assert corp.hire_wave(99) == []

    def test_hire_all(self, corp: LearningAgentCorp):
        hired = corp.hire_all()
        assert len(hired) == len(_get_agent_factory())
        assert corp.headcount == len(_get_agent_factory())

    def test_hire_all_idempotent(self, corp: LearningAgentCorp):
        corp.hire_all()
        count = corp.headcount
        corp.hire_all()  # 두 번째 호출 - 추가 채용 없음
        assert corp.headcount == count


class TestTeamBuilding:
    """팀 빌드 테스트."""

    def test_build_data_team_with_full_staff(self, full_corp: LearningAgentCorp):
        config = TEAM_CONFIGS[0]  # 데이터팀
        team = full_corp.build_team(config)
        assert team is not None
        assert "plumber" in team.teammate_names
        assert "data_redteam" in team.teammate_names

    def test_build_team_without_leader_returns_none(self, corp: LearningAgentCorp):
        config = TEAM_CONFIGS[0]
        # 리더(plumber) 없이 빌드 시도
        team = corp.build_team(config)
        assert team is None

    def test_build_team_partial_members(self, corp: LearningAgentCorp):
        # 리더만 있고 멤버 없는 경우에도 팀 빌드 가능
        corp.hire(PlumberAgent())
        config = TEAM_CONFIGS[0]
        team = corp.build_team(config)
        assert team is not None
        assert "plumber" in team.teammate_names
        # classifier, inspector는 없으므로 포함 안 됨
        assert "classifier" not in team.teammate_names

    def test_build_all_teams(self, full_corp: LearningAgentCorp):
        teams = full_corp.build_all_teams()
        assert len(teams) == len(TEAM_CONFIGS)


class TestAgentFactory:
    """에이전트 팩토리 테스트."""

    def test_factory_creates_all_40_agents(self):
        factory = _get_agent_factory()
        # C-Suite 5 + 데이터 4 + 학습 5 + 분석 5 + 피드백 5
        # + 연구 5 + 업데이트 4 + 외교 4 + 채용 3 = 40
        assert len(factory) == 40

    def test_factory_creates_correct_types(self):
        factory = _get_agent_factory()
        model = "claude-sonnet-4-20250514"

        assert isinstance(factory["ceo"](model), CEOAgent)
        assert isinstance(factory["cto"](model), CTOAgent)
        assert isinstance(factory["coo"](model), COOAgent)
        assert isinstance(factory["cfo"](model), CFOAgent)
        assert isinstance(factory["cmo"](model), CMOAgent)
        assert isinstance(factory["plumber"](model), PlumberAgent)
        assert isinstance(factory["data_redteam"](model), DataRedTeamAgent)

    def test_all_factory_agents_are_base_agent(self):
        factory = _get_agent_factory()
        model = "claude-sonnet-4-20250514"
        for name, create in factory.items():
            agent = create(model)
            assert isinstance(agent, BaseAgent), f"{name} is not a BaseAgent"


class TestHiringPriority:
    """채용 우선순위 테스트."""

    def test_hiring_priority_has_7_waves(self):
        assert len(HIRING_PRIORITY) == 7

    def test_wave_1_is_data_pipeline(self):
        assert "plumber" in HIRING_PRIORITY[0]
        assert "data_redteam" in HIRING_PRIORITY[0]

    def test_all_priority_agents_exist_in_factory(self):
        factory = _get_agent_factory()
        for wave in HIRING_PRIORITY:
            for name in wave:
                assert name in factory, f"{name} not in factory"


class TestCorpStatus:
    """조직 현황 테스트."""

    def test_empty_corp_status(self, corp: LearningAgentCorp):
        status = corp.status()
        assert "총 인원: 0명" in status

    def test_partial_corp_status(self, corp: LearningAgentCorp):
        corp.hire_wave(1)
        status = corp.status()
        assert "총 인원: 2명" in status

    def test_full_corp_status(self, full_corp: LearningAgentCorp):
        status = full_corp.status()
        assert "C-Suite: 5/5명 배치" in status


class TestTeamConfigs:
    """팀 구성 정보 테스트."""

    def test_8_teams_configured(self):
        assert len(TEAM_CONFIGS) == 8

    def test_all_teams_have_redteam(self):
        for config in TEAM_CONFIGS:
            assert config.redteam is not None, f"{config.name} has no redteam"

    def test_all_teams_have_parent(self):
        valid_parents = {"ceo", "cto", "coo", "cfo", "cmo"}
        for config in TEAM_CONFIGS:
            assert config.parent in valid_parents, (
                f"{config.name} has invalid parent: {config.parent}"
            )

    def test_no_duplicate_members_across_configs(self):
        all_members: list[str] = []
        for config in TEAM_CONFIGS:
            all_members.append(config.lead)
            all_members.extend(config.members)
            if config.redteam:
                all_members.append(config.redteam)
        assert len(all_members) == len(set(all_members)), "Duplicate members found"
