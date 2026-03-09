"""
자기정교화 루프 - 토론 결과를 반복적으로 개선한다.

흐름:
1. 초기 결과물에 대해 토론 실행
2. 토론 결과의 품질 평가
3. 품질 기준 미달 시 피드백 반영하여 재토론
4. 품질 기준 충족 또는 최대 반복 도달 시 종료
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from agents.base import Agent
from config.settings import AgentConfig, SystemConfig
from core.debate import DebateArena, DebateResult

logger = logging.getLogger(__name__)


@dataclass
class RefinementResult:
    """정교화 결과"""
    original_task: str
    iterations: list[DebateResult]
    final_output: str
    final_quality: float
    total_iterations: int
    converged: bool  # 품질 기준 도달 여부


class RefinementLoop:
    """
    자기정교화 루프.
    토론 → 평가 → 개선을 반복하여 결과물의 품질을 높인다.
    """

    def __init__(self, config: SystemConfig, agent_configs: list[AgentConfig]):
        self.config = config
        self.refinement_config = config.refinement
        self.agent_configs = agent_configs
        self.evaluator = Agent(
            AgentConfig(
                name="평가자",
                role="품질 평가자",
                perspective="결과물의 전반적 품질을 객관적으로 평가한다.",
                temperature=0.3,
            ),
            api_key=config.api_key,
        )

    def run(self, task: str) -> RefinementResult:
        """정교화 루프 실행"""
        logger.info(f"=== 정교화 루프 시작: {task[:80]}... ===")

        iterations: list[DebateResult] = []
        current_task = task

        for i in range(1, self.refinement_config.max_iterations + 1):
            logger.info(f"=== 정교화 반복 {i}/{self.refinement_config.max_iterations} ===")

            # 토론 실행
            arena = DebateArena(self.config, self.agent_configs)
            debate_result = arena.run(current_task)
            iterations.append(debate_result)

            # 품질 평가
            quality = self._evaluate_quality(task, debate_result)
            logger.info(f"품질 점수: {quality:.2f}")

            if quality >= self.refinement_config.quality_threshold:
                logger.info(f"품질 기준 도달! (점수: {quality:.2f})")
                return RefinementResult(
                    original_task=task,
                    iterations=iterations,
                    final_output=debate_result.final_proposal,
                    final_quality=quality,
                    total_iterations=i,
                    converged=True,
                )

            # 개선을 위한 태스크 재구성
            current_task = self._build_improvement_task(
                task, debate_result, quality
            )

        # 최대 반복 도달
        best = max(iterations, key=lambda d: d.consensus_score)
        return RefinementResult(
            original_task=task,
            iterations=iterations,
            final_output=best.final_proposal,
            final_quality=self._evaluate_quality(task, best),
            total_iterations=len(iterations),
            converged=False,
        )

    def _evaluate_quality(self, original_task: str, result: DebateResult) -> float:
        """결과물의 품질을 0~1 점수로 평가"""
        prompt = (
            f"다음 태스크에 대한 해결 결과물의 품질을 평가하라.\n"
            f"반드시 0.0에서 1.0 사이의 숫자 하나만 응답하라.\n"
            f"0.0 = 완전 부적절, 1.0 = 완벽\n\n"
            f"태스크: {original_task}\n\n"
            f"결과물:\n{result.final_proposal[:2000]}\n\n"
            f"토론 합의 점수: {result.consensus_score:.2f}\n"
            f"승인 여부: {result.approved}\n\n"
            f"품질 점수(숫자만):"
        )
        response = self.evaluator.respond(prompt, [])

        try:
            # 응답에서 숫자 추출
            import re
            numbers = re.findall(r"0?\.\d+|1\.0|0|1", response)
            if numbers:
                score = float(numbers[0])
                return max(0.0, min(1.0, score))
        except (ValueError, IndexError):
            pass

        # 파싱 실패 시 합의 점수를 품질 지표로 사용
        return result.consensus_score

    def _build_improvement_task(
        self, original_task: str, result: DebateResult, quality: float
    ) -> str:
        """개선을 위해 태스크를 재구성"""
        # 반대 의견들 수집
        dissents = [
            v.reason for v in result.votes if not v.approve
        ]
        dissent_text = "\n".join(f"- {d}" for d in dissents) if dissents else "없음"

        return (
            f"이전 시도의 품질이 부족하다 (점수: {quality:.2f}). "
            f"아래 원본 태스크를 다시 해결하되, 이전의 문제점을 개선하라.\n\n"
            f"원본 태스크: {original_task}\n\n"
            f"이전 시도의 결과:\n{result.final_proposal[:1000]}\n\n"
            f"이전 시도에서 지적된 문제점:\n{dissent_text}\n\n"
            f"토론 요약:\n{result.summary[:500]}\n\n"
            f"위 문제점을 해결한 개선된 버전을 제시하라."
        )
