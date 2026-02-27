"""학습팀 (COO 산하) - 가공된 데이터를 실제 학습 활동으로 전환."""

from __future__ import annotations

import logging

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class ReviewSchedulerAgent(BaseAgent):
    """복습관 (팀장) - 에빙하우스 망각곡선 기반 복습 스케줄 생성.

    Input: 검증된 데이터 + 복습 이력
    Output: 오늘의 복습 리스트
    """

    def __init__(
        self, name: str = "review_scheduler", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 학습팀 팀장 '복습관'입니다.\n"
                "역할:\n"
                "- 에빙하우스 망각곡선에 기반한 복습 스케줄 생성\n"
                "- 학습 이력과 정답률을 반영한 우선순위 결정\n"
                "- 하루 가용 시간에 맞춘 현실적인 복습량 설정\n"
                "- 팀원(출제관, 해설관, 출퇴근관) 작업 조율\n\n"
                "망각곡선 기준:\n"
                "- 1일 후: 70% 망각\n"
                "- 3일 후: 80% 망각\n"
                "- 7일 후: 90% 망각\n"
                "- 복습 시 간격이 점점 넓어짐 (1일→3일→7일→14일→30일)\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"복습 스케줄 생성 요청: {message.task}\n\n"
            f"학습 이력: {context.get('study_history', [])}\n"
            f"오늘 가용 시간: {context.get('available_hours', 2)}시간\n"
            f"취약 영역: {context.get('weak_areas', [])}\n\n"
            "에빙하우스 망각곡선에 기반하여 오늘의 복습 리스트를 생성해주세요.\n"
            "각 항목에 예상 소요 시간도 포함해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class QuizMasterAgent(BaseAgent):
    """출제관 - 취약점 기반 맞춤형 문제 출제 및 난이도 조절.

    Input: 취약점 분석 + 복습 리스트
    Output: 맞춤형 퀴즈
    """

    def __init__(
        self, name: str = "quiz_master", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 학습팀 '출제관'입니다.\n"
                "역할:\n"
                "- 취약점 기반 맞춤형 문제 출제\n"
                "- 난이도 단계적 조절 (쉬운 것부터 시작하여 점진적 상승)\n"
                "- NCS/경제학 시험 형식에 맞춘 문제 설계\n"
                "- 함정 선지 및 실전 감각 향상을 위한 변형 문제 포함\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"문제 출제 요청: {message.task}\n\n"
            f"취약 영역: {context.get('weak_areas', [])}\n"
            f"현재 난이도: {context.get('difficulty', '중')}\n"
            f"출제 수: {context.get('count', 5)}문제\n"
            f"과목: {context.get('subject', 'NCS')}\n\n"
            "취약점을 집중 공략하는 맞춤형 문제를 출제해주세요.\n"
            "각 문제에 보기(5지선다), 정답, 해설을 포함해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class ExplainerAgent(BaseAgent):
    """해설관 - 오답에 대한 소크라테스식 해설, 개념 연결.

    Input: 오답 데이터
    Output: 이해도 향상 피드백
    """

    def __init__(
        self, name: str = "explainer", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 학습팀 '해설관'입니다.\n"
                "역할:\n"
                "- 오답에 대한 소크라테스식 해설 (질문을 통해 스스로 깨닫게 유도)\n"
                "- 관련 개념 간 연결고리 설명\n"
                "- 왜 틀렸는지, 왜 정답이 맞는지 근본 원리 설명\n"
                "- 유사 문제에서 같은 실수를 반복하지 않도록 패턴 인식 도움\n\n"
                "해설 방식:\n"
                "1. 먼저 질문으로 학습자의 사고 과정을 탐색\n"
                "2. 오류가 발생한 지점을 짚어줌\n"
                "3. 올바른 추론 과정을 단계별로 안내\n"
                "4. 핵심 개념을 정리하고 관련 개념과 연결\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"오답 해설 요청: {message.task}\n\n"
            f"문제: {context.get('question', '')}\n"
            f"선택한 답: {context.get('chosen_answer', '')}\n"
            f"정답: {context.get('correct_answer', '')}\n"
            f"과목/유형: {context.get('subject', '')}\n\n"
            "소크라테스식으로 해설해주세요. "
            "왜 틀렸는지, 올바른 사고 과정은 무엇인지 단계별로 안내해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class CommuteSchedulerAgent(BaseAgent):
    """출퇴근관 - 출퇴근 2시간에 최적화된 마이크로 학습 세션 설계.

    Input: 일일 스케줄 + 컨디션
    Output: 모바일 학습 큐
    """

    def __init__(
        self, name: str = "commute_scheduler", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 학습팀 '출퇴근관'입니다.\n"
                "역할:\n"
                "- 출퇴근 시간(약 2시간)에 최적화된 마이크로 학습 세션 설계\n"
                "- 모바일 환경에서 효율적인 학습 콘텐츠 큐 구성\n"
                "- 지하철/버스 환경 특성 반영 (소음, 집중력 저하 등)\n"
                "- 5-10분 단위의 짧은 학습 모듈로 구성\n\n"
                "설계 원칙:\n"
                "- 출근길(아침): 가벼운 복습, 암기 위주\n"
                "- 퇴근길(저녁): 문제 풀이, 분석 위주\n"
                "- 환승 시간: 플래시카드 형태의 빠른 복습\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"출퇴근 학습 세션 설계 요청: {message.task}\n\n"
            f"출퇴근 시간: {context.get('commute_time', '편도 1시간')}\n"
            f"교통수단: {context.get('transport', '지하철')}\n"
            f"오늘의 컨디션: {context.get('condition', '보통')}\n"
            f"복습 대상: {context.get('review_items', [])}\n\n"
            "출퇴근 시간에 최적화된 마이크로 학습 큐를 설계해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class LearningRedTeamAgent(BaseAgent):
    """현실성 검증관 (레드팀) - 학습량/난이도 실행 가능성 체크.

    Input: 모든 학습 계획
    Output: 현실성 판정 + 조정 권고
    """

    def __init__(
        self, name: str = "learning_redteam", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 학습팀 레드팀 '현실성 검증관'입니다.\n"
                "역할:\n"
                "- 모든 학습 계획의 현실성 검증 (품질 게이트)\n"
                "- '이 양 실제로 가능해?' 관점에서 검토\n"
                "- 난이도가 적절한지, 과부하는 아닌지 체크\n"
                "- 비현실적인 계획은 차단하고 조정안 제시\n\n"
                "판정: PASS(현실적) / ADJUST(조정 필요) / BLOCK(비현실적)\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"학습 계획 현실성 검증 요청:\n"
            f"계획 내용: {message.task}\n\n"
            f"가용 시간: {context.get('available_hours', '')}시간\n"
            f"현재 컨디션: {context.get('condition', '보통')}\n"
            f"최근 학습량: {context.get('recent_workload', '')}\n\n"
            "현실성을 검증해주세요:\n"
            "1. 이 학습량이 주어진 시간 내에 가능한가?\n"
            "2. 난이도 설정이 적절한가?\n"
            "3. 번아웃 위험은 없는가?\n\n"
            "판정: PASS / ADJUST / BLOCK 중 하나와 근거를 제시해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )
