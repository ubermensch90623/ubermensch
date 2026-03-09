"""
토론 엔진 - 다수의 에이전트가 주제에 대해 토론하고 합의에 도달한다.

흐름:
1. 태스크가 주어지면 각 에이전트가 순서대로 의견 제시
2. 각 에이전트가 다른 에이전트의 의견을 비평
3. 합의에 도달할 때까지 라운드 반복
4. 최종 투표로 결과 확정
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from dataclasses import dataclass, field

from agents.base import Agent, Message, Vote
from config.settings import AgentConfig, DebateConfig, SystemConfig

logger = logging.getLogger(__name__)


@dataclass
class DebateResult:
    """토론 결과"""
    task: str
    final_proposal: str
    rounds: int
    votes: list[Vote]
    consensus_score: float
    approved: bool
    discussion_log: list[Message]
    summary: str = ""


class DebateArena:
    """
    토론 장(場).
    여러 에이전트가 모여 주제를 토론하고 합의에 도달한다.
    """

    def __init__(self, config: SystemConfig, agent_configs: list[AgentConfig]):
        self.config = config
        self.debate_config = config.debate
        self.agents = [
            Agent(ac, api_key=config.api_key) for ac in agent_configs
        ]
        self.discussion_log: list[Message] = []
        self.current_round = 0

    def run(self, task: str) -> DebateResult:
        """
        주어진 태스크에 대해 전체 토론을 실행한다.

        1단계: 초기 제안 수집
        2단계: 비평 및 토론 라운드
        3단계: 합의 확인 및 최종 투표
        """
        logger.info(f"=== 토론 시작: {task[:80]}... ===")
        logger.info(f"참여 에이전트: {[a.name for a in self.agents]}")

        # 1단계: 각 에이전트가 초기 제안
        proposals = self._collect_initial_proposals(task)

        # 2단계: 토론 라운드 반복
        current_proposal = proposals[0]  # 첫 번째 에이전트(설계자)의 제안으로 시작
        for round_num in range(1, self.debate_config.max_rounds + 1):
            self.current_round = round_num
            logger.info(f"--- 라운드 {round_num} ---")

            # 비평 수집
            critiques = self._collect_critiques(current_proposal, round_num)

            # 개선안 생성 (구현자 에이전트가 피드백 반영)
            implementer = self._find_agent_by_role("실행 전문가") or self.agents[0]
            current_proposal = implementer.refine(
                current_proposal, critiques
            )
            self.discussion_log.append(Message(
                sender=implementer.name,
                role=implementer.role,
                content=current_proposal,
                round_num=round_num,
                message_type="proposal",
            ))

            # 합의 확인
            if self.debate_config.enable_voting:
                votes = self._vote(current_proposal, round_num)
                consensus = self._calculate_consensus(votes)
                logger.info(f"합의 점수: {consensus:.2f}")

                if consensus >= self.debate_config.consensus_threshold:
                    logger.info(f"합의 도달! (점수: {consensus:.2f})")
                    return self._build_result(
                        task, current_proposal, round_num,
                        votes, consensus, approved=True,
                    )

        # 최대 라운드 도달 - 최종 투표
        logger.info("최대 라운드 도달. 최종 투표 진행.")
        final_votes = self._vote(current_proposal, self.current_round)
        final_consensus = self._calculate_consensus(final_votes)
        approved = final_consensus >= (self.debate_config.consensus_threshold * 0.8)

        return self._build_result(
            task, current_proposal, self.current_round,
            final_votes, final_consensus, approved=approved,
        )

    def _collect_initial_proposals(self, task: str) -> list[str]:
        """각 에이전트로부터 초기 제안 수집"""
        proposals = []
        context = (
            f"다음 태스크에 대해 너의 관점에서 해결 방안을 제시하라.\n"
            f"구체적이고 실행 가능한 제안을 하라.\n\n"
            f"태스크: {task}"
        )
        for agent in self.agents:
            response = agent.respond(context, [])
            proposals.append(response)
            self.discussion_log.append(Message(
                sender=agent.name,
                role=agent.role,
                content=response,
                round_num=0,
                message_type="proposal",
            ))
            logger.info(f"[{agent.name}] 초기 제안 완료")

        return proposals

    def _collect_critiques(self, proposal: str, round_num: int) -> list[str]:
        """각 에이전트로부터 비평 수집"""
        critiques = []
        for agent in self.agents:
            critique = agent.critique(proposal, self.discussion_log)
            critiques.append(critique)
            self.discussion_log.append(Message(
                sender=agent.name,
                role=agent.role,
                content=critique,
                round_num=round_num,
                message_type="critique",
            ))
            logger.info(f"[{agent.name}] 비평 완료")

        return critiques

    def _vote(self, proposal: str, round_num: int) -> list[Vote]:
        """전체 에이전트 투표"""
        votes = []
        for agent in self.agents:
            vote = agent.vote(proposal, self.discussion_log)
            votes.append(vote)
            self.discussion_log.append(Message(
                sender=agent.name,
                role=agent.role,
                content=f"투표: {'승인' if vote.approve else '반대'} "
                        f"(점수: {vote.score:.2f}) - {vote.reason}",
                round_num=round_num,
                message_type="vote",
            ))
        return votes

    def _calculate_consensus(self, votes: list[Vote]) -> float:
        """합의 점수 계산 (0~1)"""
        if not votes:
            return 0.0
        return sum(v.score for v in votes) / len(votes)

    def _find_agent_by_role(self, role: str) -> Agent | None:
        """역할로 에이전트 검색"""
        for agent in self.agents:
            if agent.role == role:
                return agent
        return None

    def _build_result(
        self, task: str, proposal: str, rounds: int,
        votes: list[Vote], consensus: float, approved: bool,
    ) -> DebateResult:
        """토론 결과 객체 생성"""
        # 검토자가 요약 생성
        reviewer = self._find_agent_by_role("최종 검토자") or self.agents[-1]
        summary = reviewer.respond(
            f"전체 토론을 요약하라. 최종 제안의 핵심 내용, 주요 논점, "
            f"합의 사항을 간결하게 정리하라.\n\n최종 제안:\n{proposal}",
            self.discussion_log,
        )

        result = DebateResult(
            task=task,
            final_proposal=proposal,
            rounds=rounds,
            votes=votes,
            consensus_score=consensus,
            approved=approved,
            discussion_log=self.discussion_log,
            summary=summary,
        )

        if self.config.log_debates:
            self._save_log(result)

        return result

    def _save_log(self, result: DebateResult):
        """토론 로그를 파일로 저장"""
        os.makedirs(self.config.log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.config.log_dir, f"debate_{timestamp}.json")

        log_data = {
            "task": result.task,
            "final_proposal": result.final_proposal,
            "rounds": result.rounds,
            "consensus_score": result.consensus_score,
            "approved": result.approved,
            "summary": result.summary,
            "votes": [
                {
                    "agent": v.agent_name,
                    "approve": v.approve,
                    "score": v.score,
                    "reason": v.reason,
                }
                for v in result.votes
            ],
            "discussion": [
                {
                    "sender": m.sender,
                    "role": m.role,
                    "type": m.message_type,
                    "round": m.round_num,
                    "content": m.content[:500],  # 로그 크기 제한
                }
                for m in result.discussion_log
            ],
            "timestamp": timestamp,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)

        logger.info(f"토론 로그 저장: {filepath}")
