"""Learning Agent Corp. -- 40명 에이전트 조직."""

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
from ubermensch.agents.corp.organization import LearningAgentCorp

__all__ = [
    # C-Suite
    "CEOAgent",
    "CTOAgent",
    "COOAgent",
    "CFOAgent",
    "CMOAgent",
    # 데이터팀
    "PlumberAgent",
    "ClassifierAgent",
    "InspectorAgent",
    "DataRedTeamAgent",
    # 학습팀
    "ReviewSchedulerAgent",
    "QuizMasterAgent",
    "ExplainerAgent",
    "CommuteSchedulerAgent",
    "LearningRedTeamAgent",
    # 분석팀
    "TrackerAgent",
    "DiagnosticianAgent",
    "ValidatorAgent",
    "PredictorAgent",
    "AnalyticsRedTeamAgent",
    # 피드백팀
    "BurnoutWatcherAgent",
    "HabitDesignerAgent",
    "SystemImproverAgent",
    "DebateModeratorAgent",
    "FeedbackRedTeamAgent",
    # 연구팀
    "StrategistAgent",
    "PasserProfilerAgent",
    "TrendAnalystAgent",
    "AIResearcherAgent",
    "ResearchRedTeamAgent",
    # 업데이트팀
    "StrategyUpdaterAgent",
    "SystemPatcherAgent",
    "ContentUpdaterAgent",
    "UpdateRedTeamAgent",
    # 외교팀
    "GeminiDiplomatAgent",
    "NotionDiplomatAgent",
    "ResponseIntegratorAgent",
    "CrossCheckerAgent",
    # 채용팀
    "RecruiterAgent",
    "CapabilityEvaluatorAgent",
    "RecruitmentRedTeamAgent",
    # TF & 조직
    "TaskForceManager",
    "LearningAgentCorp",
]
