"""피드백팀 (CMO 산하) - 시스템과 사용자 경험을 지속 개선."""

from __future__ import annotations

import logging

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class BurnoutWatcherAgent(BaseAgent):
    """번아웃 감시관 (팀장) - 무력감/스트레스 신호 감지, 학습량 자동 조절.

    Input: 활동 패턴 + 컨디션
    Output: 개입 알림 + 조절 명령
    """

    def __init__(
        self, name: str = "burnout_watcher", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 피드백팀 팀장 '번아웃 감시관'입니다.\n"
                "역할:\n"
                "- 무력감, 스트레스, 번아웃 신호 조기 감지\n"
                "- 학습량 자동 조절 권고\n"
                "- 위험 수준 판단 및 개입 알림 발동\n"
                "- 팀원(습관설계사, 시스템개선관, 회의진행관) 조율\n\n"
                "번아웃 신호:\n"
                "- 3일 이상 공부 중단\n"
                "- 정답률 급격 하락\n"
                "- 학습 시간 급감\n"
                "- 반복적 같은 유형 오답\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"번아웃 감시 요청: {message.task}\n\n"
            f"연속 학습일수: {context.get('streak_days', 0)}일\n"
            f"최근 7일 학습 시간: {context.get('weekly_hours', [])}시간\n"
            f"정답률 추이: {context.get('accuracy_trend', [])}\n"
            f"컨디션 자가 평가: {context.get('self_condition', '미입력')}\n\n"
            "번아웃 위험도를 평가하고, 필요시 개입 방안을 제시해주세요.\n"
            "위험 수준: SAFE / CAUTION / WARNING / CRITICAL"
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class HabitDesignerAgent(BaseAgent):
    """습관설계사 - 게이미피케이션, 작은 성공 경험 설계.

    Input: 행동 데이터
    Output: 보상/알림 트리거
    """

    def __init__(
        self, name: str = "habit_designer", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 피드백팀 '습관설계사'입니다.\n"
                "역할:\n"
                "- 게이미피케이션 요소 설계 (경험치, 레벨, 뱃지 등)\n"
                "- 작은 성공 경험을 통한 동기부여 루프 설계\n"
                "- 습관 형성을 위한 트리거-루틴-보상 사이클 구성\n"
                "- 진행 상황 시각화 방안 제안\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"습관 설계 요청: {message.task}\n\n"
            f"현재 학습 패턴: {context.get('study_pattern', '')}\n"
            f"목표 행동: {context.get('target_behavior', '')}\n"
            f"기존 보상 체계: {context.get('current_rewards', '없음')}\n\n"
            "효과적인 습관 형성 방안을 설계해주세요.\n"
            "트리거-루틴-보상 구조로 제시해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class SystemImproverAgent(BaseAgent):
    """시스템개선관 - 사용 안 되는 기능 제거, 워크플로우 단순화.

    Input: 사용 로그 + 피드백
    Output: 시스템 업데이트
    """

    def __init__(
        self, name: str = "system_improver", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 피드백팀 '시스템개선관'입니다.\n"
                "역할:\n"
                "- 사용되지 않는 기능 식별 및 제거 권고\n"
                "- 워크플로우 단순화 방안 제안\n"
                "- 사용자 피드백 기반 UX 개선\n"
                "- 복잡도 감소를 위한 리팩토링 제안\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"시스템 개선 요청: {message.task}\n\n"
            f"사용 로그: {context.get('usage_log', [])}\n"
            f"사용자 피드백: {context.get('feedback', '')}\n"
            f"현재 기능 목록: {context.get('features', [])}\n\n"
            "시스템 개선 방안을 제시해주세요.\n"
            "제거할 기능, 단순화할 워크플로우, 개선할 UX를 구분하여 제안해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class DebateModeratorAgent(BaseAgent):
    """회의 진행관 - 에이전트 간 토론 주재, 갈등 조율, 합의 도출.

    Input: 각 부서 보고서
    Output: 의사결정 기록
    """

    def __init__(
        self, name: str = "debate_moderator", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 피드백팀 '회의 진행관'입니다.\n"
                "역할:\n"
                "- 에이전트 간 의견 충돌 시 토론 주재\n"
                "- 각 입장의 근거를 정리하고 비교\n"
                "- 합의점 도출 또는 상위 결정권자에게 에스컬레이션\n"
                "- 의사결정 과정 기록 및 문서화\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"토론/조율 요청: {message.task}\n\n"
            f"입장 A: {context.get('position_a', '')}\n"
            f"입장 B: {context.get('position_b', '')}\n"
            f"배경 정보: {context.get('background', '')}\n\n"
            "각 입장의 근거를 정리하고, 합의점을 도출해주세요.\n"
            "합의가 어려우면 에스컬레이션 권고와 함께 쟁점을 정리해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class FeedbackRedTeamAgent(BaseAgent):
    """부작용 검증관 (레드팀) - 개선이 오히려 악화시키는지, 복잡도 증가 방지.

    Input: 모든 변경 사항
    Output: 부작용 리포트 + 롤백 권고
    """

    def __init__(
        self, name: str = "feedback_redteam", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 피드백팀 레드팀 '부작용 검증관'입니다.\n"
                "역할:\n"
                "- 모든 시스템 변경/개선의 부작용 사전 검증 (품질 게이트)\n"
                "- '이 변경이 오히려 상황을 악화시키지 않는가?' 관점\n"
                "- 불필요한 복잡도 증가 방지\n"
                "- 문제 발견 시 롤백 권고\n\n"
                "판정: SAFE(안전) / RISKY(위험) / ROLLBACK(롤백 권고)\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"변경 사항 부작용 검증 요청:\n"
            f"변경 내용: {message.task}\n\n"
            f"변경 목적: {context.get('purpose', '')}\n"
            f"영향 범위: {context.get('scope', '')}\n"
            f"기존 상태: {context.get('current_state', '')}\n\n"
            "부작용을 검증해주세요:\n"
            "1. 이 변경이 기존 워크플로우를 방해하지 않는가?\n"
            "2. 불필요한 복잡도를 추가하지 않는가?\n"
            "3. 의도하지 않은 부작용은 없는가?\n\n"
            "판정: SAFE / RISKY / ROLLBACK 중 하나와 근거를 제시해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )
