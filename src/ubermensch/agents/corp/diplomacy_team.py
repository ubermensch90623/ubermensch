"""외교팀 (CTO 산하) - AI간 협업 및 크로스체크."""

from __future__ import annotations

import logging

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class GeminiDiplomatAgent(BaseAgent):
    """Gemini 외교관 (팀장) - Gemini에게 문제 풀이 검증, 대안 해설 요청.

    Input: 검증 필요한 문제/풀이
    Output: Gemini 검증 결과 + 대안 풀이
    MCP 서버 경유로 Gemini와 통신
    """

    def __init__(
        self, name: str = "gemini_diplomat", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 외교팀 팀장 'Gemini 외교관'입니다.\n"
                "역할:\n"
                "- Gemini AI에게 문제 풀이 검증 요청\n"
                "- 대안 해설, 개념 설명 요청\n"
                "- MCP 프로토콜을 통한 실시간 협업 관리\n"
                "- 팀원(Notion 외교관, 응답 통합관) 조율\n\n"
                "요청 형식:\n"
                "- 명확한 질문/과제 정의\n"
                "- 필요한 컨텍스트 제공\n"
                "- 기대하는 응답 형식 명시\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"Gemini 협업 요청 준비: {message.task}\n\n"
            f"검증할 문제: {context.get('question', '')}\n"
            f"현재 풀이: {context.get('current_solution', '')}\n"
            f"요청 유형: {context.get('request_type', '검증')}\n\n"
            "Gemini에게 보낼 요청 메시지를 작성해주세요.\n"
            "명확한 질문, 충분한 컨텍스트, 기대 응답 형식을 포함해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class NotionDiplomatAgent(BaseAgent):
    """Notion AI 외교관 - Notion AI에게 DB 분석, 복습 스케줄 최적화 요청.

    Input: 분석 요청 + DB 쿼리
    Output: Notion AI 분석 결과
    """

    def __init__(
        self, name: str = "notion_diplomat", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 외교팀 'Notion AI 외교관'입니다.\n"
                "역할:\n"
                "- Notion AI에게 데이터베이스 분석 요청\n"
                "- 복습 스케줄 최적화 요청\n"
                "- 데이터 요약 및 인사이트 추출 요청\n"
                "- Notion API/DB 쿼리 작성\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"Notion AI 협업 요청 준비: {message.task}\n\n"
            f"분석 대상 DB: {context.get('database', '')}\n"
            f"요청 유형: {context.get('request_type', '분석')}\n"
            f"쿼리 조건: {context.get('query', '')}\n\n"
            "Notion AI에게 보낼 요청을 작성해주세요.\n"
            "DB 쿼리와 기대하는 분석 결과를 포함해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class ResponseIntegratorAgent(BaseAgent):
    """응답 통합관 - 여러 AI의 응답을 비교/종합하여 최적의 답 도출.

    Input: 복수 AI 응답
    Output: 통합 결론 + 신뢰도 판정
    """

    def __init__(
        self,
        name: str = "response_integrator",
        model: str = "claude-sonnet-4-20250514",
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 외교팀 '응답 통합관'입니다.\n"
                "역할:\n"
                "- 여러 AI(Claude, Gemini, Notion AI)의 응답을 비교/종합\n"
                "- 불일치 시 근거 비교하여 최적의 답 도출\n"
                "- 각 AI 응답의 신뢰도 평가\n"
                "- 통합 결론 문서화\n\n"
                "비교 기준:\n"
                "- 논리적 일관성\n"
                "- 근거의 충분성\n"
                "- 답변의 구체성\n"
                "- AI 간 합의 정도\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"AI 응답 통합 요청: {message.task}\n\n"
            f"Claude 응답: {context.get('claude_response', '')}\n"
            f"Gemini 응답: {context.get('gemini_response', '')}\n"
            f"Notion AI 응답: {context.get('notion_response', '')}\n\n"
            "각 AI의 응답을 비교하고 통합 결론을 도출해주세요.\n"
            "불일치 지점, 합의 지점, 최종 신뢰도를 포함해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class CrossCheckerAgent(BaseAgent):
    """크로스체크관 (레드팀) - AI가 AI를 검증한 게 맞는지 최종 검증.

    Input: 통합 결론
    Output: 최종 신뢰도 판정 + 수동 검증 필요 플래그
    """

    def __init__(
        self, name: str = "cross_checker", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 외교팀 레드팀 '크로스체크관'입니다.\n"
                "역할:\n"
                "- AI가 AI를 검증한 결과의 최종 검증 (품질 게이트)\n"
                "- 양쪽 AI가 다 틀릴 가능성 체크\n"
                "- AI 할루시네이션(환각) 탐지\n"
                "- 수동 검증이 필요한 항목 플래그\n\n"
                "판정:\n"
                "- VERIFIED: AI 검증 결과 신뢰 가능\n"
                "- SUSPICIOUS: 추가 검토 필요\n"
                "- MANUAL_CHECK: 반드시 사람이 직접 확인해야 함\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        prompt = (
            f"크로스체크 요청:\n"
            f"검증 대상: {message.task}\n\n"
            f"통합 결론: {context.get('integrated_conclusion', '')}\n"
            f"원본 질문: {context.get('original_question', '')}\n"
            f"참여 AI: {context.get('participating_ais', [])}\n\n"
            "최종 검증을 수행해주세요:\n"
            "1. AI들이 서로의 오류를 제대로 감지했는가?\n"
            "2. 공통적으로 틀릴 수 있는 지점이 있는가?\n"
            "3. 할루시네이션 징후가 있는가?\n"
            "4. 사람의 직접 확인이 필요한 부분이 있는가?\n\n"
            "판정: VERIFIED / SUSPICIOUS / MANUAL_CHECK 중 하나와 근거를 제시해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )
