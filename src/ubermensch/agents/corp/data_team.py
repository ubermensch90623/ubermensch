"""데이터팀 (CTO 산하) - Keep 400개 노트를 Notion으로 흘려보내는 파이프라인."""

from __future__ import annotations

import logging

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class PlumberAgent(BaseAgent):
    """배관공 (팀장) - Keep->Notion 데이터 파이프라인 구축/유지.

    Input: Keep 400개 노트
    Output: Notion DB 레코드
    """

    def __init__(self, name: str = "plumber", model: str = "claude-sonnet-4-20250514"):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 데이터팀 팀장 '배관공'입니다.\n"
                "역할:\n"
                "- Google Keep 노트를 Notion 데이터베이스로 이관하는 파이프라인 구축\n"
                "- 데이터 흐름 설계 및 동기화 관리\n"
                "- 파이프라인 장애 감지 및 복구\n"
                "- 팀원(분류사, 검수관) 작업 조율\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        context = message.context
        raw_notes = context.get("notes", [])
        prompt = (
            f"파이프라인 작업 요청: {message.task}\n\n"
            f"처리 대상 노트 수: {len(raw_notes) if isinstance(raw_notes, list) else raw_notes}\n"
            f"현재 파이프라인 상태: {context.get('pipeline_status', '정상')}\n\n"
            "데이터 이관 계획을 수립하고 처리 절차를 제시해주세요.\n"
            "각 노트에 대해: 파싱 -> 분류 -> 검수 -> Notion DB 적재 순서로 진행합니다."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class ClassifierAgent(BaseAgent):
    """분류사 - 문제/풀이/오답분석 자동 파싱 및 태깅.

    Input: 원본 텍스트
    Output: 구조화된 데이터
    """

    def __init__(
        self, name: str = "classifier", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 데이터팀 '분류사'입니다.\n"
                "역할:\n"
                "- 원본 텍스트에서 문제/풀이/오답분석을 자동으로 파싱\n"
                "- 과목, 유형, 난이도 등의 태그 부여\n"
                "- 구조화된 데이터 형식으로 변환\n\n"
                "출력 형식:\n"
                "- 과목: [NCS/경제학/...]\n"
                "- 유형: [수리/언어/추론/...]\n"
                "- 난이도: [상/중/하]\n"
                "- 문제: [문제 내용]\n"
                "- 풀이: [풀이 과정]\n"
                "- 오답분석: [오답 이유]\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        text = message.context.get("text", message.task)
        prompt = (
            f"다음 텍스트를 구조화된 데이터로 파싱해주세요:\n\n{text}\n\n"
            "문제, 풀이, 오답분석을 분리하고 적절한 태그를 부여해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class InspectorAgent(BaseAgent):
    """검수관 (QA) - 파싱 오류 검출, 중복 제거, 데이터 품질 관리.

    Input: 파싱된 데이터
    Output: 검증된 데이터
    """

    def __init__(
        self, name: str = "inspector", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 데이터팀 '검수관'입니다.\n"
                "역할:\n"
                "- 파싱된 데이터의 오류 검출\n"
                "- 중복 데이터 제거\n"
                "- 데이터 품질 기준 충족 여부 확인\n"
                "- 검수 결과 리포트 작성\n\n"
                "검수 기준:\n"
                "- 필수 필드 누락 여부\n"
                "- 태그 정확성\n"
                "- 내용 무결성\n"
                "- 중복 여부\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        parsed_data = message.context.get("parsed_data", message.task)
        prompt = (
            f"다음 파싱된 데이터를 검수해주세요:\n\n{parsed_data}\n\n"
            "오류, 누락, 중복, 품질 문제를 식별하고 검수 결과를 보고해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )


class DataRedTeamAgent(BaseAgent):
    """데이터 검증관 (레드팀) - 파싱/동기화 오류 사전 체크, 데이터 깨짐 방지.

    Input: 모든 데이터 작업
    Output: 오류 리포트 + 차단
    """

    def __init__(
        self, name: str = "data_redteam", model: str = "claude-sonnet-4-20250514"
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "당신은 데이터팀 레드팀 '데이터 검증관'입니다.\n"
                "역할:\n"
                "- 모든 데이터 작업에 대한 사전 검증 (품질 게이트)\n"
                "- 파싱/동기화 오류 사전 탐지\n"
                "- 데이터 깨짐 방지를 위한 무결성 검사\n"
                "- 문제 발견 시 작업 차단 및 오류 리포트 작성\n\n"
                "판정: PASS(통과) / BLOCK(차단) / WARN(경고 후 진행)\n\n"
                "한국어로 응답하세요."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        work_item = message.context.get("work_item", message.task)
        work_type = message.context.get("work_type", "general")
        prompt = (
            f"데이터 작업 검증 요청:\n"
            f"작업 유형: {work_type}\n"
            f"작업 내용:\n{work_item}\n\n"
            "다음을 검증해주세요:\n"
            "1. 데이터 무결성 위험이 있는가?\n"
            "2. 파싱/동기화 오류 가능성이 있는가?\n"
            "3. 기존 데이터와 충돌할 수 있는가?\n\n"
            "판정: PASS / BLOCK / WARN 중 하나와 근거를 제시해주세요."
        )
        analysis = await self.ask_llm(prompt)
        return TaskResult(
            agent_name=self.name, status=TaskStatus.COMPLETED, data=analysis
        )
