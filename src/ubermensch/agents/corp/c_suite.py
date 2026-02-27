"""C-Suite (경영진) - CEO, CTO, COO, CFO, CMO."""

from __future__ import annotations

import logging

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class CEOAgent(BaseAgent):
    """CEO 아키텍트 - 전체 전략 수립, 부서간 우선순위 조율, 의사결정.

    KPI: 주간 목표 달성률
    직속: 연구팀, 채용팀, TF팀
    """

    def __init__(self, name: str = "ceo", model: str = "claude-sonnet-4-20250514"):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 Learning Agent Corp.의 CEO입니다.\n"
                "역할:\n"
                "- 전체 학습 전략 수립 및 부서간 우선순위 조율\n"
                "- TF팀 편성 판단 (기존 팀으로 해결 가능한지 먼저 검토)\n"
                "- 주간 목표 설정 및 달성률 추적\n"
                "- 부서간 갈등 조율 및 최종 의사결정\n\n"
                "원칙:\n"
                "- 린스타트업 방식: 1명씩 채용하며 검증\n"
                "- 레드팀은 첫 작업부터 함께 투입\n"
                "- 동시 TF 최대 2개\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        report_type = context.get("type", "decision")

        if report_type == "tf_request":
            prompt = (
                f"TF팀 편성 요청입니다.\n\n"
                f"문제 상황: {message.task}\n"
                f"현재 활성 TF: {context.get('active_tfs', 0)}개\n"
                f"가용 에이전트: {context.get('available_agents', [])}\n\n"
                "1. 기존 팀으로 해결 가능한가?\n"
                "2. TF 편성이 필요하다면 누구를 차출할 것인가?\n"
                "3. TF 리더는 누구로 지정할 것인가?\n"
                "4. 목표와 기한은?"
            )
        elif report_type == "priority":
            prompt = (
                f"우선순위 조율 요청입니다.\n\n"
                f"상황: {message.task}\n"
                f"부서별 현황: {context.get('department_status', {})}\n\n"
                "부서간 우선순위를 조율하고 최종 결정을 내려주세요."
            )
        else:
            prompt = (
                f"의사결정 요청입니다.\n\n"
                f"안건: {message.task}\n"
                f"배경: {context.get('background', '')}\n"
                f"선택지: {context.get('options', [])}\n\n"
                "각 선택지의 장단점을 분석하고 최종 결정을 내려주세요."
            )

        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class CTOAgent(BaseAgent):
    """CTO 시스템 엔지니어 - Keep<>Notion 파이프라인, 자동화 인프라 구축.

    KPI: 데이터 동기화율
    산하: 데이터팀, 업데이트팀, 외교팀
    """

    def __init__(self, name: str = "cto", model: str = "claude-sonnet-4-20250514"):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 Learning Agent Corp.의 CTO입니다.\n"
                "역할:\n"
                "- Keep<>Notion 데이터 파이프라인 설계 및 관리\n"
                "- 자동화 인프라 구축 (MCP 프로토콜, API 연동)\n"
                "- 데이터팀, 업데이트팀, 외교팀 기술 방향 설정\n"
                "- 시스템 장애 대응 및 기술 부채 관리\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"기술 검토 요청: {message.task}\n\n"
            f"현재 시스템 상태: {context.get('system_status', '정상')}\n"
            f"관련 파이프라인: {context.get('pipeline', '')}\n\n"
            "기술적 분석과 권고사항을 제시해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class COOAgent(BaseAgent):
    """COO 운영총괄 - 일일 학습 스케줄 실행, 병목 제거.

    KPI: 일일 실행률
    산하: 학습팀
    """

    def __init__(self, name: str = "coo", model: str = "claude-sonnet-4-20250514"):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 Learning Agent Corp.의 COO입니다.\n"
                "역할:\n"
                "- 일일 학습 스케줄의 원활한 실행 관리\n"
                "- 학습팀 병목 제거 및 실행률 극대화\n"
                "- 실행 가능한 일정인지 현실성 점검\n"
                "- 학습팀 성과 모니터링 및 피드백\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"운영 점검 요청: {message.task}\n\n"
            f"오늘의 학습 계획: {context.get('daily_plan', '')}\n"
            f"현재 진행률: {context.get('progress', '미측정')}\n"
            f"병목 사항: {context.get('bottlenecks', '없음')}\n\n"
            "실행 상태를 점검하고 병목 해결 방안을 제시해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class CFOAgent(BaseAgent):
    """CFO 성과분석관 - 점수 추적, ROI 분석.

    KPI: 주간 점수 변화량
    산하: 분석팀
    """

    def __init__(self, name: str = "cfo", model: str = "claude-sonnet-4-20250514"):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 Learning Agent Corp.의 CFO입니다.\n"
                "역할:\n"
                "- 점수 추적 및 시간 대비 점수 상승 ROI 분석\n"
                "- 분석팀 방향 설정 및 성과 지표 정의\n"
                "- 학습 투자 효율성 극대화 전략\n"
                "- 주간 성과 보고서 작성\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"성과 분석 요청: {message.task}\n\n"
            f"점수 데이터: {context.get('scores', {})}\n"
            f"투자 시간: {context.get('time_invested', '')}\n"
            f"목표: {context.get('target', '')}\n\n"
            "ROI 분석과 개선 방향을 제시해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class CMOAgent(BaseAgent):
    """CMO 동기부여관 - 번아웃 방지, 무력감 감지, 성공 경험 설계.

    KPI: 연속 학습일수
    산하: 피드백팀
    """

    def __init__(self, name: str = "cmo", model: str = "claude-sonnet-4-20250514"):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 Learning Agent Corp.의 CMO입니다.\n"
                "역할:\n"
                "- 번아웃 방지 및 무력감 조기 감지\n"
                "- 작은 성공 경험 설계로 동기부여 유지\n"
                "- 피드백팀 방향 설정 및 사용자 경험 최적화\n"
                "- 연속 학습일수 유지 전략\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"동기부여 점검 요청: {message.task}\n\n"
            f"연속 학습일수: {context.get('streak_days', 0)}일\n"
            f"최근 컨디션: {context.get('condition', '보통')}\n"
            f"학습 패턴: {context.get('study_pattern', '')}\n\n"
            "동기부여 상태를 진단하고 유지/개선 방안을 제시해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )
