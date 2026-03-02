"""Discussion pipeline - structured multi-agent debate system.

에이전트 간 구조화된 토론을 통해 더 견고한 결론을 도출합니다.

흐름:
    1. 발표자(presenter)가 초기 분석을 수행
    2. 비평자(critic)가 반론을 제기
    3. 발표자가 반론에 대응
    4. N 라운드 반복 후 합의 도출

사용 예:
    discussion = Discussion(
        presenter=SecurityReviewerAgent(),
        critic=DevilsAdvocateAgent(),
        rounds=2,
    )
    result = await discussion.run("Review this code for security issues")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult
from ubermensch.core.provider import LLMProvider, get_provider

logger = logging.getLogger(__name__)


@dataclass
class DiscussionTurn:
    """토론의 한 턴."""

    round: int
    speaker: str
    role: str  # "analysis", "challenge", "response", "consensus"
    content: str


@dataclass
class DiscussionResult:
    """토론 전체 결과."""

    topic: str
    turns: list[DiscussionTurn] = field(default_factory=list)
    consensus: str = ""
    presenter_name: str = ""
    critic_name: str = ""


class Discussion:
    """2자 간 구조화된 토론.

    Args:
        presenter: 초기 분석을 수행하는 에이전트
        critic: 반론을 제기하는 에이전트 (보통 DevilsAdvocateAgent)
        rounds: 토론 라운드 수 (기본 2)
        model: 합의 도출에 사용할 모델
        provider: LLM 프로바이더 (미지정 시 글로벌/자동 감지)
    """

    def __init__(
        self,
        presenter: BaseAgent,
        critic: BaseAgent,
        rounds: int = 2,
        model: str = "claude-sonnet-4-20250514",
        provider: LLMProvider | None = None,
    ) -> None:
        self.presenter = presenter
        self.critic = critic
        self.rounds = max(1, rounds)
        self.model = model
        self._provider: LLMProvider | None = provider

    @property
    def provider(self) -> LLMProvider:
        if self._provider is None:
            self._provider = get_provider()
        return self._provider

    async def run(
        self,
        topic: str,
        context: dict[str, Any] | None = None,
    ) -> DiscussionResult:
        """토론을 실행합니다.

        Args:
            topic: 토론 주제/태스크
            context: 추가 컨텍스트 (코드, 로그 등)

        Returns:
            DiscussionResult with all turns and consensus
        """
        ctx = context or {}
        result = DiscussionResult(
            topic=topic,
            presenter_name=self.presenter.name,
            critic_name=self.critic.name,
        )

        # Round 1: 초기 분석
        logger.info(f"[Discussion] Round 1: {self.presenter.name} analyzes")
        analysis = await self.presenter.run(AgentMessage(task=topic, context=ctx))
        analysis_text = self._extract_text(analysis)

        result.turns.append(
            DiscussionTurn(
                round=1,
                speaker=self.presenter.name,
                role="analysis",
                content=analysis_text,
            )
        )

        previous_analysis = analysis_text

        for round_num in range(1, self.rounds + 1):
            # 비평자 반론
            logger.info(f"[Discussion] Round {round_num}: {self.critic.name} challenges")
            challenge = await self.critic.run(
                AgentMessage(
                    task=f"Challenge this analysis on: {topic}",
                    context={
                        **ctx,
                        "findings": previous_analysis,
                        "source_agent": self.presenter.name,
                        "round": round_num,
                    },
                )
            )
            challenge_text = self._extract_text(challenge)

            result.turns.append(
                DiscussionTurn(
                    round=round_num,
                    speaker=self.critic.name,
                    role="challenge",
                    content=challenge_text,
                )
            )

            # 발표자 대응
            logger.info(f"[Discussion] Round {round_num}: {self.presenter.name} responds")
            response = await self.presenter.run(
                AgentMessage(
                    task=(
                        f"Respond to the challenge on your analysis of: {topic}\n\n"
                        f"Your original analysis:\n{previous_analysis}\n\n"
                        f"Challenge from {self.critic.name}:\n{challenge_text}\n\n"
                        "Address each point. Acknowledge valid criticisms and "
                        "defend well-supported conclusions."
                    ),
                    context=ctx,
                )
            )
            response_text = self._extract_text(response)

            result.turns.append(
                DiscussionTurn(
                    round=round_num,
                    speaker=self.presenter.name,
                    role="response",
                    content=response_text,
                )
            )

            previous_analysis = response_text

        # 합의 도출
        result.consensus = await self._build_consensus(result)

        return result

    async def _build_consensus(self, discussion: DiscussionResult) -> str:
        """토론 결과를 종합하여 합의를 도출합니다."""
        turns_text = "\n\n".join(
            f"[Round {t.round}] {t.speaker} ({t.role}):\n{t.content}" for t in discussion.turns
        )

        prompt = (
            f"Topic: {discussion.topic}\n\n"
            f"Discussion transcript:\n{turns_text}\n\n"
            "Based on this discussion, synthesize a final consensus:\n"
            "1. Points both sides agree on\n"
            "2. Resolved disagreements (and how they were resolved)\n"
            "3. Remaining open questions\n"
            "4. Final recommendation\n\n"
            "In Korean."
        )

        return await self.provider.complete(
            model=self.model,
            max_tokens=4096,
            system=(
                "You are a neutral moderator synthesizing a debate between two agents. "
                "Provide a balanced, actionable consensus."
            ),
            messages=[{"role": "user", "content": prompt}],
        )

    @staticmethod
    def _extract_text(result: TaskResult) -> str:
        """TaskResult에서 텍스트를 추출합니다."""
        if not result.success:
            return f"[FAILED] {result.error}"
        data = result.data
        if isinstance(data, str):
            return data
        if isinstance(data, dict):
            # 에이전트별 다양한 data 구조 지원
            return (
                data.get("analysis")
                or data.get("plan")
                or data.get("guide")
                or data.get("summary")
                or str(data)
            )
        return str(data)


class MultiDiscussion:
    """여러 에이전트 간 다자 토론.

    모든 에이전트가 순서대로 발표하고, 다른 에이전트가 교차 비평합니다.
    """

    def __init__(
        self,
        agents: list[BaseAgent],
        rounds: int = 1,
        model: str = "claude-sonnet-4-20250514",
        provider: LLMProvider | None = None,
    ) -> None:
        self.agents = agents
        self.rounds = max(1, rounds)
        self.model = model
        self._provider: LLMProvider | None = provider

    @property
    def provider(self) -> LLMProvider:
        if self._provider is None:
            self._provider = get_provider()
        return self._provider

    async def run(
        self,
        topic: str,
        context: dict[str, Any] | None = None,
    ) -> DiscussionResult:
        """다자 토론을 실행합니다."""
        ctx = context or {}
        result = DiscussionResult(
            topic=topic,
            presenter_name=", ".join(a.name for a in self.agents),
            critic_name="(cross-review)",
        )

        # 각 에이전트가 동시에 초기 분석
        import asyncio

        initial_tasks = [agent.run(AgentMessage(task=topic, context=ctx)) for agent in self.agents]
        initial_results = await asyncio.gather(*initial_tasks)

        analyses: dict[str, str] = {}
        for agent, res in zip(self.agents, initial_results, strict=True):
            text = Discussion._extract_text(res)
            analyses[agent.name] = text
            result.turns.append(
                DiscussionTurn(round=1, speaker=agent.name, role="analysis", content=text)
            )

        # 교차 비평 라운드
        for round_num in range(1, self.rounds + 1):
            for _i, agent in enumerate(self.agents):
                # 다른 에이전트들의 분석을 비평
                others = {name: text for name, text in analyses.items() if name != agent.name}
                others_text = "\n\n".join(f"{name}:\n{text}" for name, text in others.items())

                challenge = await agent.run(
                    AgentMessage(
                        task=(
                            f"Review and challenge these analyses on: {topic}\n\n"
                            f"Other agents' findings:\n{others_text}"
                        ),
                        context={**ctx, "round": round_num},
                    )
                )
                challenge_text = Discussion._extract_text(challenge)
                analyses[agent.name] = challenge_text

                result.turns.append(
                    DiscussionTurn(
                        round=round_num + 1,
                        speaker=agent.name,
                        role="challenge",
                        content=challenge_text,
                    )
                )

        # 합의 도출
        disc = Discussion(
            self.agents[0], self.agents[-1], model=self.model, provider=self._provider
        )
        result.consensus = await disc._build_consensus(result)

        return result
