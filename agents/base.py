"""기본 에이전트 - 모든 에이전트의 베이스 클래스"""

from __future__ import annotations

import anthropic
from dataclasses import dataclass, field
from config.settings import AgentConfig


@dataclass
class Message:
    """에이전트 간 주고받는 메시지"""
    sender: str
    role: str
    content: str
    round_num: int
    message_type: str = "discussion"  # discussion, critique, proposal, vote


@dataclass
class Vote:
    """에이전트의 투표"""
    agent_name: str
    approve: bool
    score: float  # 0~1
    reason: str


class Agent:
    """
    기본 에이전트.
    각 에이전트는 고유한 역할과 관점을 가지고 토론에 참여한다.
    """

    def __init__(self, config: AgentConfig, api_key: str):
        self.config = config
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation_history: list[Message] = []

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def role(self) -> str:
        return self.config.role

    def _build_system_prompt(self) -> str:
        return (
            f"너는 '{self.config.name}'이라는 이름의 AI 에이전트이다.\n"
            f"역할: {self.config.role}\n"
            f"관점: {self.config.perspective}\n\n"
            "너는 다른 에이전트들과 토론하며 작업의 품질을 높이는 것이 목표이다.\n"
            "항상 너의 역할과 관점에 맞게 의견을 제시하라.\n"
            "다른 에이전트의 의견에 동의하거나 반박할 때는 구체적인 근거를 제시하라.\n"
            "최종 목표는 최고 품질의 결과물을 만드는 것이다."
        )

    def respond(self, context: str, discussion_history: list[Message]) -> str:
        """토론 컨텍스트와 히스토리를 바탕으로 응답 생성"""
        messages = self._format_history(discussion_history)
        messages.append({"role": "user", "content": context})

        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system=self._build_system_prompt(),
            messages=messages,
        )
        return response.content[0].text

    def critique(self, proposal: str, discussion_history: list[Message]) -> str:
        """제안에 대한 비평 생성"""
        context = (
            f"다음 제안을 너의 관점({self.config.perspective})에서 비평하라.\n"
            f"장점, 단점, 개선점을 구체적으로 제시하라.\n\n"
            f"제안:\n{proposal}"
        )
        return self.respond(context, discussion_history)

    def vote(self, proposal: str, discussion_history: list[Message]) -> Vote:
        """제안에 대해 투표"""
        context = (
            f"다음 제안에 대해 평가하라.\n"
            f"반드시 아래 형식으로 응답하라:\n"
            f"승인: [예/아니오]\n"
            f"점수: [0.0~1.0]\n"
            f"이유: [한 줄 설명]\n\n"
            f"제안:\n{proposal}"
        )
        response_text = self.respond(context, discussion_history)
        return self._parse_vote(response_text)

    def refine(self, original: str, feedbacks: list[str]) -> str:
        """피드백을 반영하여 제안 개선"""
        feedback_text = "\n---\n".join(
            f"피드백 {i+1}:\n{fb}" for i, fb in enumerate(feedbacks)
        )
        context = (
            f"아래 원본을 주어진 피드백들을 반영하여 개선하라.\n"
            f"모든 피드백을 고려하되, 너의 관점에서 타당한 것만 반영하라.\n\n"
            f"원본:\n{original}\n\n"
            f"피드백들:\n{feedback_text}"
        )
        return self.respond(context, [])

    def _format_history(self, history: list[Message]) -> list[dict]:
        """토론 히스토리를 API 메시지 형식으로 변환"""
        messages = []
        for msg in history:
            role = "assistant" if msg.sender == self.name else "user"
            content = f"[{msg.sender} ({msg.role})] {msg.content}"
            messages.append({"role": role, "content": content})

        # API 요구사항: 연속된 같은 role 메시지 병합
        merged = []
        for msg in messages:
            if merged and merged[-1]["role"] == msg["role"]:
                merged[-1]["content"] += "\n\n" + msg["content"]
            else:
                merged.append(msg)

        # 첫 메시지가 assistant이면 빈 user 메시지 추가
        if merged and merged[0]["role"] == "assistant":
            merged.insert(0, {"role": "user", "content": "(토론 시작)"})

        return merged

    def _parse_vote(self, text: str) -> Vote:
        """투표 응답 파싱"""
        lines = text.strip().split("\n")
        approve = False
        score = 0.5
        reason = text

        for line in lines:
            line_lower = line.strip().lower()
            if line_lower.startswith("승인"):
                approve = "예" in line_lower or "yes" in line_lower
            elif line_lower.startswith("점수"):
                try:
                    score = float("".join(c for c in line if c.isdigit() or c == "."))
                    score = max(0.0, min(1.0, score))
                except ValueError:
                    score = 0.5
            elif line_lower.startswith("이유"):
                reason = line.split(":", 1)[-1].strip() if ":" in line else line

        return Vote(
            agent_name=self.name,
            approve=approve,
            score=score,
            reason=reason,
        )
