"""Debugger agent - investigates issues with competing hypothesis methodology."""

from __future__ import annotations

import logging

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class DebuggerAgent(BaseAgent):
    """경쟁 가설 방법론으로 버그를 조사하는 에이전트.

    여러 가설을 동시에 세우고, 각각을 검증/반증하여
    가장 가능성 높은 근본 원인을 찾아냅니다.
    단일 에이전트가 하나의 가설에 편향되는 앵커링 효과를 방지합니다.
    """

    def __init__(
        self,
        name: str = "debugger",
        model: str = "claude-sonnet-4-20250514",
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "You are a debugging agent using the competing hypothesis "
                "methodology. Your approach:\n"
                "1. Generate multiple plausible hypotheses for the root cause\n"
                "2. For each hypothesis, identify evidence that would confirm or deny it\n"
                "3. Evaluate available evidence against all hypotheses simultaneously\n"
                "4. Eliminate hypotheses that conflict with evidence\n"
                "5. Rank remaining hypotheses by likelihood\n\n"
                "Key principles:\n"
                "- Don't anchor on the first plausible explanation\n"
                "- Consider both direct and indirect causes\n"
                "- Distinguish between correlation and causation\n"
                "- Track confidence levels for each hypothesis\n"
                "- Recommend specific diagnostic steps to resolve ambiguity\n\n"
                "Respond in Korean."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        """버그/이슈를 경쟁 가설 방법론으로 조사합니다."""
        symptoms = message.context.get("symptoms", "")
        error_logs = message.context.get("error_logs", "")
        code = message.context.get("code", "")
        environment = message.context.get("environment", "")
        other_hypotheses = message.context.get("other_hypotheses", [])

        debug_prompt = f"Debugging task: {message.task}\n\n"

        if symptoms:
            debug_prompt += f"Symptoms:\n{symptoms}\n\n"

        if error_logs:
            debug_prompt += f"Error logs:\n{error_logs}\n\n"

        if code:
            debug_prompt += f"Relevant code:\n```\n{code}\n```\n\n"

        if environment:
            debug_prompt += f"Environment info:\n{environment}\n\n"

        if other_hypotheses:
            debug_prompt += (
                "Other agents' hypotheses to challenge:\n"
                + "\n".join(f"- {h}" for h in other_hypotheses)
                + "\n\n"
            )

        debug_prompt += (
            "Investigate using the competing hypothesis methodology:\n\n"
            "1. HYPOTHESES: List 3-5 plausible root causes. For each:\n"
            "   - Description of the hypothesis\n"
            "   - Initial confidence (0-100%)\n"
            "   - Evidence that would confirm it\n"
            "   - Evidence that would deny it\n\n"
            "2. EVIDENCE ANALYSIS: Evaluate available evidence against "
            "ALL hypotheses simultaneously.\n\n"
            "3. ELIMINATION: Which hypotheses can be eliminated and why?\n\n"
            "4. RANKING: Rank remaining hypotheses by likelihood with reasoning.\n\n"
            "5. NEXT STEPS: What specific diagnostic steps would help "
            "resolve remaining ambiguity?\n\n"
            "6. RECOMMENDED FIX: Based on the most likely hypothesis, "
            "what is the recommended fix?"
        )

        analysis = await self.ask_llm(debug_prompt)

        return TaskResult(
            agent_name=self.name,
            status=TaskStatus.COMPLETED,
            data={
                "investigation_type": "competing_hypothesis",
                "analysis": analysis,
            },
        )
