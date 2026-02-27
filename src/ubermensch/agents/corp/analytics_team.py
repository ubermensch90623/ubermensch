"""분석팀 (CFO 산하) - 학습 효과를 수치로 증명하고 방향을 검증."""

from __future__ import annotations

import logging

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class TrackerAgent(BaseAgent):
    """추적관 (팀장) - 공부량/정답률/시간 투자 일일 추적.

    Input: 학습 활동 로그
    Output: 일일/주간 리포트
    """

    def __init__(
        self, name: str = "tracker", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 분석팀 팀장 '추적관'입니다.\n"
                "역할:\n"
                "- 공부량, 정답률, 시간 투자량을 일일/주간 단위로 추적\n"
                "- 성과 지표 대시보드 생성\n"
                "- 추세 변화 감지 및 알림\n"
                "- 팀원(진단관, 검증관, 예측관) 작업 조율\n\n"
                "추적 지표:\n"
                "- 일일 학습 시간 (분 단위)\n"
                "- 문제 풀이 수\n"
                "- 정답률 (과목별, 유형별)\n"
                "- 복습 완료율\n"
                "- 연속 학습일수\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"성과 추적 요청: {message.task}\n\n"
            f"활동 로그: {context.get('activity_log', [])}\n"
            f"기간: {context.get('period', '오늘')}\n"
            f"이전 데이터: {context.get('previous_data', {})}\n\n"
            "성과 추적 리포트를 생성해주세요. 추세 변화가 있다면 강조해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class DiagnosticianAgent(BaseAgent):
    """진단관 - 오답 패턴 분석, 취약 유형 식별.

    Input: 오답 이력 데이터
    Output: 취약점 맵
    """

    def __init__(
        self, name: str = "diagnostician", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 분석팀 '진단관'입니다.\n"
                "역할:\n"
                "- 오답 데이터를 분석하여 반복되는 실수 패턴 식별\n"
                "- 과목별/유형별 취약 영역 매핑\n"
                "- 실수 원인 분류 (개념 부족, 계산 실수, 시간 부족, 함정 등)\n"
                "- 취약점 맵 기반 학습 처방 권고\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"오답 진단 요청: {message.task}\n\n"
            f"오답 이력: {context.get('wrong_answers', [])}\n"
            f"과목: {context.get('subject', '전체')}\n\n"
            "오답 패턴을 분석하고 취약점 맵을 작성해주세요.\n"
            "각 취약점에 대해 원인과 처방을 제시해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class ValidatorAgent(BaseAgent):
    """검증관 - 학습 방법 효과 A/B 테스트, ROI 분석.

    Input: 성과 데이터 + 방법론
    Output: 방법 효과성 보고서
    """

    def __init__(
        self, name: str = "validator", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 분석팀 '검증관'입니다.\n"
                "역할:\n"
                "- 학습 방법의 효과성을 데이터 기반으로 검증\n"
                "- A/B 테스트 설계 및 결과 분석\n"
                "- 시간 투자 대비 점수 향상 ROI 계산\n"
                "- 비효율적인 학습 방법 식별 및 대안 제시\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"학습 방법 검증 요청: {message.task}\n\n"
            f"방법 A: {context.get('method_a', '')}\n"
            f"방법 B: {context.get('method_b', '')}\n"
            f"성과 데이터: {context.get('performance_data', {})}\n\n"
            "학습 방법의 효과성을 비교 분석해주세요.\n"
            "ROI(시간 투자 대비 점수 향상)도 계산해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class PredictorAgent(BaseAgent):
    """예측관 - 현재 추세 기반 합격 가능성 예측, 갭 분석.

    Input: 성과 추이 데이터
    Output: 합격 확률 + 필요 액션
    """

    def __init__(
        self, name: str = "predictor", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 분석팀 '예측관'입니다.\n"
                "역할:\n"
                "- 현재 학습 추세를 기반으로 합격 가능성 예측\n"
                "- 목표 점수와 현재 점수 간 갭 분석\n"
                "- 갭을 메우기 위해 필요한 구체적 액션 도출\n"
                "- 시나리오별 합격 확률 제시 (최선/보통/최악)\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"합격 예측 요청: {message.task}\n\n"
            f"현재 점수: {context.get('current_score', '')}\n"
            f"목표 점수: {context.get('target_score', '')}\n"
            f"시험까지 남은 기간: {context.get('days_left', '')}일\n"
            f"점수 추이: {context.get('score_trend', [])}\n\n"
            "합격 가능성을 예측하고 갭 분석을 수행해주세요.\n"
            "갭을 메우기 위한 구체적 액션 플랜도 제시해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class AnalyticsRedTeamAgent(BaseAgent):
    """통계 검증관 (레드팀) - 분석 결과 신뢰도 체크, 착각/편향 방지.

    Input: 모든 분석 결과
    Output: 신뢰도 판정 + 재분석 요청
    """

    def __init__(
        self, name: str = "analytics_redteam", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 분석팀 레드팀 '통계 검증관'입니다.\n"
                "역할:\n"
                "- 모든 분석 결과의 신뢰도 검증 (품질 게이트)\n"
                "- 통계적 오류, 샘플 편향, 과적합 탐지\n"
                "- 착각 방지 (작은 표본에서의 성급한 일반화 등)\n"
                "- 확증 편향 필터링\n\n"
                "판정: RELIABLE(신뢰) / QUESTIONABLE(의심) / UNRELIABLE(불신뢰)\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"분석 결과 검증 요청:\n"
            f"분석 내용: {message.task}\n\n"
            f"데이터 출처: {context.get('source_agent', '')}\n"
            f"표본 크기: {context.get('sample_size', '미상')}\n"
            f"분석 결과: {context.get('analysis_result', '')}\n\n"
            "신뢰도를 검증해주세요:\n"
            "1. 통계적 오류는 없는가?\n"
            "2. 편향이 존재하는가?\n"
            "3. 결론이 데이터로 뒷받침되는가?\n\n"
            "판정: RELIABLE / QUESTIONABLE / UNRELIABLE 중 하나와 근거를 제시해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )
