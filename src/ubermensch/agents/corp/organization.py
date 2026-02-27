"""Learning Agent Corp. - 전체 조직 관리."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.team import AgentTeam

from ubermensch.agents.corp.c_suite import (
    CEOAgent,
    CFOAgent,
    CMOAgent,
    COOAgent,
    CTOAgent,
)
from ubermensch.agents.corp.data_team import (
    ClassifierAgent,
    DataRedTeamAgent,
    InspectorAgent,
    PlumberAgent,
)
from ubermensch.agents.corp.learning_team import (
    CommuteSchedulerAgent,
    ExplainerAgent,
    LearningRedTeamAgent,
    QuizMasterAgent,
    ReviewSchedulerAgent,
)
from ubermensch.agents.corp.analytics_team import (
    AnalyticsRedTeamAgent,
    DiagnosticianAgent,
    PredictorAgent,
    TrackerAgent,
    ValidatorAgent,
)
from ubermensch.agents.corp.feedback_team import (
    BurnoutWatcherAgent,
    DebateModeratorAgent,
    FeedbackRedTeamAgent,
    HabitDesignerAgent,
    SystemImproverAgent,
)
from ubermensch.agents.corp.research_team import (
    AIResearcherAgent,
    PasserProfilerAgent,
    ResearchRedTeamAgent,
    StrategistAgent,
    TrendAnalystAgent,
)
from ubermensch.agents.corp.update_team import (
    ContentUpdaterAgent,
    StrategyUpdaterAgent,
    SystemPatcherAgent,
    UpdateRedTeamAgent,
)
from ubermensch.agents.corp.diplomacy_team import (
    CrossCheckerAgent,
    GeminiDiplomatAgent,
    NotionDiplomatAgent,
    ResponseIntegratorAgent,
)
from ubermensch.agents.corp.recruitment_team import (
    CapabilityEvaluatorAgent,
    RecruiterAgent,
    RecruitmentRedTeamAgent,
)
from ubermensch.agents.corp.task_force import TaskForceManager

logger = logging.getLogger(__name__)


# 채용 우선순위 (CEO 판단)
HIRING_PRIORITY = [
    # 1차: 데이터 없으면 전사 마비
    ("plumber", "data_redteam"),
    # 2차: 성과 측정 없으면 방향 상실
    ("tracker",),
    # 3차: 실제 학습 시작
    ("review_scheduler", "learning_redteam"),
    # 4차: 외부 전략 수집
    ("strategist", "research_redteam"),
    # 5차: AI 크로스 검증
    ("gemini_diplomat", "cross_checker"),
    # 6차: 지속가능성 확보
    ("burnout_watcher",),
    # 7차: 조직 자체 진화 능력
    ("recruiter", "recruitment_redteam"),
]


@dataclass
class TeamConfig:
    """팀 구성 정보."""

    name: str
    lead: str
    members: list[str]
    redteam: str | None = None
    parent: str = ""  # 상위 C-Suite


# 전체 팀 구성 정의
TEAM_CONFIGS: list[TeamConfig] = [
    TeamConfig(
        name="데이터팀",
        lead="plumber",
        members=["classifier", "inspector"],
        redteam="data_redteam",
        parent="cto",
    ),
    TeamConfig(
        name="학습팀",
        lead="review_scheduler",
        members=["quiz_master", "explainer", "commute_scheduler"],
        redteam="learning_redteam",
        parent="coo",
    ),
    TeamConfig(
        name="분석팀",
        lead="tracker",
        members=["diagnostician", "validator", "predictor"],
        redteam="analytics_redteam",
        parent="cfo",
    ),
    TeamConfig(
        name="피드백팀",
        lead="burnout_watcher",
        members=["habit_designer", "system_improver", "debate_moderator"],
        redteam="feedback_redteam",
        parent="cmo",
    ),
    TeamConfig(
        name="연구팀",
        lead="strategist",
        members=["passer_profiler", "trend_analyst", "ai_researcher"],
        redteam="research_redteam",
        parent="ceo",
    ),
    TeamConfig(
        name="업데이트팀",
        lead="strategy_updater",
        members=["system_patcher", "content_updater"],
        redteam="update_redteam",
        parent="cto",
    ),
    TeamConfig(
        name="외교팀",
        lead="gemini_diplomat",
        members=["notion_diplomat", "response_integrator"],
        redteam="cross_checker",
        parent="cto",
    ),
    TeamConfig(
        name="채용팀",
        lead="recruiter",
        members=["capability_evaluator"],
        redteam="recruitment_redteam",
        parent="ceo",
    ),
]


class LearningAgentCorp:
    """Learning Agent Corp. 전체 조직 관리.

    린스타트업 방식으로 1명씩 채용하며 검증합니다.
    각 에이전트가 실제로 가치를 만들어내는지 확인한 후 다음을 채용합니다.
    """

    def __init__(self, model: str = "claude-sonnet-4-20250514") -> None:
        self.model = model
        self._agents: dict[str, BaseAgent] = {}
        self._teams: dict[str, AgentTeam] = {}
        self.tf_manager = TaskForceManager()
        self._deployed: set[str] = set()

    def hire(self, agent: BaseAgent) -> None:
        """에이전트를 채용 (조직에 등록)합니다."""
        self._agents[agent.name] = agent
        self._deployed.add(agent.name)
        self.tf_manager.register_agent(agent)
        logger.info(f"[Corp] 채용 완료: {agent.name}")

    def fire(self, name: str) -> BaseAgent | None:
        """에이전트를 해고합니다."""
        agent = self._agents.pop(name, None)
        self._deployed.discard(name)
        if agent:
            logger.info(f"[Corp] 해고 완료: {name}")
        return agent

    def get_agent(self, name: str) -> BaseAgent | None:
        return self._agents.get(name)

    @property
    def headcount(self) -> int:
        return len(self._agents)

    @property
    def agent_names(self) -> list[str]:
        return list(self._agents.keys())

    def build_team(self, config: TeamConfig) -> AgentTeam | None:
        """팀 구성 정보로 AgentTeam을 빌드합니다."""
        # 리더 확인
        lead = self._agents.get(config.lead)
        if lead is None:
            logger.warning(f"팀 '{config.name}' 리더 '{config.lead}' 미배치")
            return None

        team = AgentTeam(name=config.name, model=self.model)
        team.spawn_teammate(lead)

        for member_name in config.members:
            member = self._agents.get(member_name)
            if member:
                team.spawn_teammate(member)

        if config.redteam:
            redteam = self._agents.get(config.redteam)
            if redteam:
                team.spawn_teammate(redteam)

        self._teams[config.name] = team
        logger.info(
            f"[Corp] 팀 빌드 완료: {config.name} "
            f"({len(team.teammate_names)}명)"
        )
        return team

    def build_all_teams(self) -> dict[str, AgentTeam]:
        """배치된 에이전트 기준으로 가능한 모든 팀을 빌드합니다."""
        for config in TEAM_CONFIGS:
            self.build_team(config)
        return dict(self._teams)

    def hire_wave(self, wave: int) -> list[BaseAgent]:
        """채용 우선순위에 따라 특정 차수의 에이전트를 채용합니다.

        Args:
            wave: 채용 차수 (1~7)

        Returns:
            채용된 에이전트 목록
        """
        if wave < 1 or wave > len(HIRING_PRIORITY):
            logger.warning(f"유효하지 않은 채용 차수: {wave}")
            return []

        agent_names = HIRING_PRIORITY[wave - 1]
        hired: list[BaseAgent] = []

        agent_factory = _get_agent_factory()

        for name in agent_names:
            if name in self._agents:
                logger.info(f"[Corp] '{name}' 이미 채용됨, 스킵")
                continue

            factory = agent_factory.get(name)
            if factory is None:
                logger.warning(f"[Corp] '{name}' 팩토리 없음")
                continue

            agent = factory(model=self.model)
            self.hire(agent)
            hired.append(agent)

        return hired

    def hire_all(self) -> list[BaseAgent]:
        """전체 에이전트를 순차 채용합니다."""
        all_hired: list[BaseAgent] = []
        agent_factory = _get_agent_factory()

        for name, factory in agent_factory.items():
            if name not in self._agents:
                agent = factory(model=self.model)
                self.hire(agent)
                all_hired.append(agent)

        return all_hired

    def status(self) -> str:
        """전사 현황 요약."""
        lines = [
            "=== Learning Agent Corp. 현황 ===",
            f"총 인원: {self.headcount}명",
            f"팀 수: {len(self._teams)}개",
        ]

        # C-Suite
        c_suite = ["ceo", "cto", "coo", "cfo", "cmo"]
        deployed_cs = [n for n in c_suite if n in self._agents]
        lines.append(f"\nC-Suite: {len(deployed_cs)}/5명 배치")

        # 팀별 현황
        for config in TEAM_CONFIGS:
            all_members = [config.lead] + config.members
            if config.redteam:
                all_members.append(config.redteam)
            deployed = [n for n in all_members if n in self._agents]
            lines.append(
                f"{config.name}: {len(deployed)}/{len(all_members)}명 배치"
            )

        # TF 현황
        lines.append(f"\n{self.tf_manager.status()}")

        return "\n".join(lines)


def _get_agent_factory() -> dict[str, Any]:
    """에이전트 이름 -> 팩토리 함수 매핑."""
    return {
        # C-Suite
        "ceo": lambda model: CEOAgent(model=model),
        "cto": lambda model: CTOAgent(model=model),
        "coo": lambda model: COOAgent(model=model),
        "cfo": lambda model: CFOAgent(model=model),
        "cmo": lambda model: CMOAgent(model=model),
        # 데이터팀
        "plumber": lambda model: PlumberAgent(model=model),
        "classifier": lambda model: ClassifierAgent(model=model),
        "inspector": lambda model: InspectorAgent(model=model),
        "data_redteam": lambda model: DataRedTeamAgent(model=model),
        # 학습팀
        "review_scheduler": lambda model: ReviewSchedulerAgent(model=model),
        "quiz_master": lambda model: QuizMasterAgent(model=model),
        "explainer": lambda model: ExplainerAgent(model=model),
        "commute_scheduler": lambda model: CommuteSchedulerAgent(model=model),
        "learning_redteam": lambda model: LearningRedTeamAgent(model=model),
        # 분석팀
        "tracker": lambda model: TrackerAgent(model=model),
        "diagnostician": lambda model: DiagnosticianAgent(model=model),
        "validator": lambda model: ValidatorAgent(model=model),
        "predictor": lambda model: PredictorAgent(model=model),
        "analytics_redteam": lambda model: AnalyticsRedTeamAgent(model=model),
        # 피드백팀
        "burnout_watcher": lambda model: BurnoutWatcherAgent(model=model),
        "habit_designer": lambda model: HabitDesignerAgent(model=model),
        "system_improver": lambda model: SystemImproverAgent(model=model),
        "debate_moderator": lambda model: DebateModeratorAgent(model=model),
        "feedback_redteam": lambda model: FeedbackRedTeamAgent(model=model),
        # 연구팀
        "strategist": lambda model: StrategistAgent(model=model),
        "passer_profiler": lambda model: PasserProfilerAgent(model=model),
        "trend_analyst": lambda model: TrendAnalystAgent(model=model),
        "ai_researcher": lambda model: AIResearcherAgent(model=model),
        "research_redteam": lambda model: ResearchRedTeamAgent(model=model),
        # 업데이트팀
        "strategy_updater": lambda model: StrategyUpdaterAgent(model=model),
        "system_patcher": lambda model: SystemPatcherAgent(model=model),
        "content_updater": lambda model: ContentUpdaterAgent(model=model),
        "update_redteam": lambda model: UpdateRedTeamAgent(model=model),
        # 외교팀
        "gemini_diplomat": lambda model: GeminiDiplomatAgent(model=model),
        "notion_diplomat": lambda model: NotionDiplomatAgent(model=model),
        "response_integrator": lambda model: ResponseIntegratorAgent(model=model),
        "cross_checker": lambda model: CrossCheckerAgent(model=model),
        # 채용팀
        "recruiter": lambda model: RecruiterAgent(model=model),
        "capability_evaluator": lambda model: CapabilityEvaluatorAgent(model=model),
        "recruitment_redteam": lambda model: RecruitmentRedTeamAgent(model=model),
    }
