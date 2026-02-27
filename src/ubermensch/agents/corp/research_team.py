"""연구팀 (CEO 직속) - 외부 정보 수집 및 전략 연구."""

from __future__ import annotations

import logging

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class StrategistAgent(BaseAgent):
    """전략 스카우터 (팀장) - NCS/경제학 고득점 전략, 시간 배분법 연구.

    Input: 시험 커뮤니티, 합격 수기
    Output: 정답률 향상 전략 보고서
    """

    def __init__(
        self, name: str = "strategist", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 연구팀 팀장 '전략 스카우터'입니다.\n"
                "역할:\n"
                "- NCS/경제학 고득점 전략 연구\n"
                "- 시험 시간 배분법, 찍기 전략 연구\n"
                "- 시험 커뮤니티 정보 분석\n"
                "- 팀원(합격자 프로파일러, 트렌드 분석관, AI 연구원) 조율\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"전략 연구 요청: {message.task}\n\n"
            f"시험 유형: {context.get('exam_type', 'NCS')}\n"
            f"현재 점수 수준: {context.get('current_level', '')}\n"
            f"목표: {context.get('target', '')}\n\n"
            "고득점을 위한 전략을 연구하고 보고서를 작성해주세요.\n"
            "시간 배분법, 문제 풀이 순서, 찍기 전략 등을 포함해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class PasserProfilerAgent(BaseAgent):
    """합격자 프로파일러 - 단기 합격자 공부법, 일정표 분석.

    Input: 합격 후기, 인터뷰
    Output: 합격자 패턴 분석 보고서
    """

    def __init__(
        self, name: str = "passer_profiler", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 연구팀 '합격자 프로파일러'입니다.\n"
                "역할:\n"
                "- 단기 합격자들의 공부법 패턴 분석\n"
                "- 합격자 일정표, 교재 선택 분석\n"
                "- 공통된 성공 요인 추출\n"
                "- 우리 상황에 적용 가능한 요소 필터링\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"합격자 분석 요청: {message.task}\n\n"
            f"합격 후기 데이터: {context.get('testimonials', '')}\n"
            f"대상 시험: {context.get('exam_type', 'NCS')}\n\n"
            "합격자 패턴을 분석하고 보고서를 작성해주세요.\n"
            "공통 성공 요인과 우리에게 적용 가능한 요소를 구분해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class TrendAnalystAgent(BaseAgent):
    """출제 트렌드 분석관 - 최근 시험 출제 경향, 기출 패턴 변화 감지.

    Input: 기출문제, 시험 리뷰
    Output: 출제 트렌드 리포트
    """

    def __init__(
        self, name: str = "trend_analyst", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 연구팀 '출제 트렌드 분석관'입니다.\n"
                "역할:\n"
                "- 최근 NCS/경제학 시험의 출제 경향 분석\n"
                "- 기출 패턴 변화 감지 (신유형, 비중 변화 등)\n"
                "- 다음 시험 출제 예상 영역 도출\n"
                "- 학습 우선순위 조정 권고\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"출제 트렌드 분석 요청: {message.task}\n\n"
            f"기출 데이터: {context.get('past_exams', '')}\n"
            f"시험 리뷰: {context.get('exam_reviews', '')}\n\n"
            "출제 트렌드를 분석하고 리포트를 작성해주세요.\n"
            "다음 시험 출제 예상과 학습 우선순위 조정 권고를 포함해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class AIResearcherAgent(BaseAgent):
    """AI 기술 연구원 - 학습 자동화 최신 기술, 새 AI 도구 추적.

    Input: GitHub, 기술 블로그
    Output: 기술 업데이트 제안서
    """

    def __init__(
        self, name: str = "ai_researcher", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 연구팀 'AI 기술 연구원'입니다.\n"
                "역할:\n"
                "- 학습 자동화에 활용 가능한 최신 AI 기술 추적\n"
                "- 새로운 AI 도구 (MCP 서버, 에이전트 프레임워크 등) 평가\n"
                "- 기존 시스템에 통합 가능한 기술 제안\n"
                "- 기술 발전 추세 분석\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"기술 연구 요청: {message.task}\n\n"
            f"관심 영역: {context.get('focus_area', '학습 자동화')}\n"
            f"현재 기술 스택: {context.get('current_stack', '')}\n\n"
            "최신 기술 동향을 분석하고 업데이트 제안서를 작성해주세요.\n"
            "기존 시스템과의 호환성도 고려해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class ResearchRedTeamAgent(BaseAgent):
    """정보 신뢰도 검증관 (레드팀) - 후기/전략 신뢰성 검증, 생존자 편향 필터링.

    Input: 모든 연구 결과
    Output: 신뢰도 판정 + 적용 권고
    """

    def __init__(
        self, name: str = "research_redteam", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 연구팀 레드팀 '정보 신뢰도 검증관'입니다.\n"
                "역할:\n"
                "- 모든 연구 결과의 신뢰도 검증 (품질 게이트)\n"
                "- 합격 후기/전략의 생존자 편향 필터링\n"
                "- '우리 상황에 적용 가능한가?' 판단\n"
                "- 출처 신뢰도 평가\n\n"
                "판정: TRUSTWORTHY(신뢰) / BIASED(편향 의심) / UNRELIABLE(불신뢰)\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"연구 결과 신뢰도 검증 요청:\n"
            f"연구 내용: {message.task}\n\n"
            f"출처: {context.get('source', '')}\n"
            f"연구 결과: {context.get('findings', '')}\n\n"
            "신뢰도를 검증해주세요:\n"
            "1. 생존자 편향이 존재하는가?\n"
            "2. 출처가 신뢰할 수 있는가?\n"
            "3. 우리 상황에 적용 가능한가?\n"
            "4. 표본이 충분히 대표성이 있는가?\n\n"
            "판정: TRUSTWORTHY / BIASED / UNRELIABLE 중 하나와 근거를 제시해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )
