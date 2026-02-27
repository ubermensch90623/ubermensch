"""에이전트 유닛 테스트 - LLM 호출 모킹."""

from __future__ import annotations

import pytest

from ubermensch.core.message import AgentMessage, TaskStatus
from ubermensch.agents.corp.c_suite import CEOAgent, CTOAgent, COOAgent, CFOAgent, CMOAgent
from ubermensch.agents.corp.data_team import (
    PlumberAgent, ClassifierAgent, InspectorAgent, DataRedTeamAgent,
)
from ubermensch.agents.corp.learning_team import (
    ReviewSchedulerAgent, QuizMasterAgent, ExplainerAgent,
    CommuteSchedulerAgent, LearningRedTeamAgent,
)
from ubermensch.agents.corp.analytics_team import (
    TrackerAgent, DiagnosticianAgent, ValidatorAgent,
    PredictorAgent, AnalyticsRedTeamAgent,
)
from ubermensch.agents.corp.feedback_team import (
    BurnoutWatcherAgent, HabitDesignerAgent, SystemImproverAgent,
    DebateModeratorAgent, FeedbackRedTeamAgent,
)
from ubermensch.agents.corp.research_team import (
    StrategistAgent, PasserProfilerAgent, TrendAnalystAgent,
    AIResearcherAgent, ResearchRedTeamAgent,
)
from ubermensch.agents.corp.update_team import (
    StrategyUpdaterAgent, SystemPatcherAgent, ContentUpdaterAgent,
    UpdateRedTeamAgent,
)
from ubermensch.agents.corp.diplomacy_team import (
    GeminiDiplomatAgent, NotionDiplomatAgent, ResponseIntegratorAgent,
    CrossCheckerAgent,
)
from ubermensch.agents.corp.recruitment_team import (
    RecruiterAgent, CapabilityEvaluatorAgent, RecruitmentRedTeamAgent,
)


ALL_AGENT_CLASSES = [
    # C-Suite
    CEOAgent, CTOAgent, COOAgent, CFOAgent, CMOAgent,
    # 데이터팀
    PlumberAgent, ClassifierAgent, InspectorAgent, DataRedTeamAgent,
    # 학습팀
    ReviewSchedulerAgent, QuizMasterAgent, ExplainerAgent,
    CommuteSchedulerAgent, LearningRedTeamAgent,
    # 분석팀
    TrackerAgent, DiagnosticianAgent, ValidatorAgent,
    PredictorAgent, AnalyticsRedTeamAgent,
    # 피드백팀
    BurnoutWatcherAgent, HabitDesignerAgent, SystemImproverAgent,
    DebateModeratorAgent, FeedbackRedTeamAgent,
    # 연구팀
    StrategistAgent, PasserProfilerAgent, TrendAnalystAgent,
    AIResearcherAgent, ResearchRedTeamAgent,
    # 업데이트팀
    StrategyUpdaterAgent, SystemPatcherAgent, ContentUpdaterAgent,
    UpdateRedTeamAgent,
    # 외교팀
    GeminiDiplomatAgent, NotionDiplomatAgent, ResponseIntegratorAgent,
    CrossCheckerAgent,
    # 채용팀
    RecruiterAgent, CapabilityEvaluatorAgent, RecruitmentRedTeamAgent,
]


class TestAgentInstantiation:
    """모든 에이전트가 올바르게 생성되는지 테스트."""

    def test_total_agent_count(self):
        assert len(ALL_AGENT_CLASSES) == 40

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES)
    def test_agent_creates_without_error(self, agent_cls):
        agent = agent_cls()
        assert agent.name
        assert agent.system_prompt
        assert agent.model == "claude-sonnet-4-20250514"

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES)
    def test_agent_custom_model(self, agent_cls):
        agent = agent_cls(model="claude-haiku-4-5-20251001")
        assert agent.model == "claude-haiku-4-5-20251001"

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES)
    def test_agent_system_prompt_in_korean(self, agent_cls):
        agent = agent_cls()
        assert "한국어" in agent.system_prompt


class TestAgentExecution:
    """에이전트 실행 테스트 (LLM 모킹)."""

    @pytest.mark.asyncio
    async def test_plumber_execute(self, mock_anthropic):
        agent = PlumberAgent()
        result = await agent.run(
            AgentMessage(
                task="Keep 노트 파이프라인 설계",
                context={"notes": [], "pipeline_status": "정상"},
            )
        )
        assert result.status == TaskStatus.COMPLETED
        assert result.data is not None

    @pytest.mark.asyncio
    async def test_data_redteam_execute(self, mock_anthropic):
        agent = DataRedTeamAgent()
        result = await agent.run(
            AgentMessage(
                task="파이프라인 설계 검증",
                context={"work_item": "test", "work_type": "pipeline"},
            )
        )
        assert result.status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_ceo_tf_request(self, mock_anthropic):
        agent = CEOAgent()
        result = await agent.run(
            AgentMessage(
                task="데이터 파이프라인 장애 발생",
                context={
                    "type": "tf_request",
                    "active_tfs": 0,
                    "available_agents": ["plumber", "data_redteam"],
                },
            )
        )
        assert result.status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_ceo_priority_decision(self, mock_anthropic):
        agent = CEOAgent()
        result = await agent.run(
            AgentMessage(
                task="학습팀 vs 분석팀 우선순위",
                context={"type": "priority", "department_status": {}},
            )
        )
        assert result.status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_review_scheduler_execute(self, mock_anthropic):
        agent = ReviewSchedulerAgent()
        result = await agent.run(
            AgentMessage(
                task="오늘의 복습 리스트 생성",
                context={
                    "study_history": ["NCS 수리 5문제"],
                    "available_hours": 2,
                    "weak_areas": ["비율", "탄력성"],
                },
            )
        )
        assert result.status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_quiz_master_execute(self, mock_anthropic):
        agent = QuizMasterAgent()
        result = await agent.run(
            AgentMessage(
                task="취약 영역 문제 출제",
                context={
                    "weak_areas": ["수요탄력성"],
                    "difficulty": "중",
                    "count": 3,
                    "subject": "경제학",
                },
            )
        )
        assert result.status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_burnout_watcher_execute(self, mock_anthropic):
        agent = BurnoutWatcherAgent()
        result = await agent.run(
            AgentMessage(
                task="번아웃 위험도 점검",
                context={
                    "streak_days": 5,
                    "weekly_hours": [2, 1.5, 0, 0, 3, 2, 1],
                    "accuracy_trend": [0.7, 0.65, 0.6],
                },
            )
        )
        assert result.status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_cross_checker_execute(self, mock_anthropic):
        agent = CrossCheckerAgent()
        result = await agent.run(
            AgentMessage(
                task="AI 크로스체크 최종 검증",
                context={
                    "integrated_conclusion": "Claude와 Gemini 답변 일치",
                    "original_question": "수요탄력성 계산",
                    "participating_ais": ["claude", "gemini"],
                },
            )
        )
        assert result.status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_recruitment_redteam_execute(self, mock_anthropic):
        agent = RecruitmentRedTeamAgent()
        result = await agent.run(
            AgentMessage(
                task="신규 '오답노트 자동생성관' 채용 검토",
                context={
                    "existing_capabilities": ["classifier", "explainer"],
                    "reason": "오답 데이터 자동 정리 필요",
                },
            )
        )
        assert result.status == TaskStatus.COMPLETED
