"""Devil's Advocate agent - challenges and stress-tests other agents' findings."""

from __future__ import annotations

import logging

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class DevilsAdvocateAgent(BaseAgent):
    """다른 에이전트의 결과에 반론을 제기하는 에이전트.

    과학적 토론 방식으로 다른 에이전트의 분석, 결론, 제안에 대해
    비판적 검토를 수행합니다. 확증 편향을 방지하고 더 견고한
    결론을 도출하는 데 도움을 줍니다.
    """

    def __init__(
        self,
        name: str = "devils_advocate",
        model: str = "claude-sonnet-4-20250514",
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "You are a devil's advocate agent. Your role is to:\n"
                "1. Challenge assumptions in other agents' analyses\n"
                "2. Identify logical fallacies and weak arguments\n"
                "3. Propose alternative explanations and counter-examples\n"
                "4. Stress-test conclusions with edge cases\n"
                "5. Point out overlooked risks and blind spots\n\n"
                "Rules:\n"
                "- Be constructive, not destructive. The goal is stronger conclusions.\n"
                "- Back every challenge with reasoning or evidence.\n"
                "- Acknowledge when findings are well-supported.\n"
                "- Rate your confidence in each challenge: HIGH, MEDIUM, LOW.\n"
                "- Suggest what additional investigation would resolve disagreements.\n\n"
                "Respond in Korean."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        """다른 에이전트의 결과를 비판적으로 검토합니다."""
        findings = message.context.get("findings", "")
        agent_source = message.context.get("source_agent", "unknown")
        hypothesis = message.context.get("hypothesis", "")

        challenge_prompt = f"Devil's advocate review task: {message.task}\n\n"

        if findings:
            challenge_prompt += (
                f"Findings from agent '{agent_source}':\n{findings}\n\n"
            )

        if hypothesis:
            challenge_prompt += f"Hypothesis being tested:\n{hypothesis}\n\n"

        challenge_prompt += (
            "Perform a critical review:\n"
            "1. ASSUMPTIONS: What assumptions are being made? Are they valid?\n"
            "2. CHALLENGES: What are the weaknesses in the analysis?\n"
            "   For each, rate confidence (HIGH/MEDIUM/LOW) and provide reasoning.\n"
            "3. ALTERNATIVES: What other explanations or approaches exist?\n"
            "4. EDGE CASES: What scenarios would break the proposed solution?\n"
            "5. STRENGTHS: What aspects are well-reasoned and should be kept?\n"
            "6. VERDICT: Overall assessment - does the analysis hold up, "
            "need revision, or should be reconsidered entirely?"
        )

        analysis = await self.ask_llm(challenge_prompt)

        return TaskResult(
            agent_name=self.name,
            status=TaskStatus.COMPLETED,
            data={
                "review_type": "devils_advocate",
                "source_agent": agent_source,
                "analysis": analysis,
            },
        )
