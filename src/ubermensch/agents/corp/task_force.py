"""TF팀 시스템 (CEO 산하) - 문제 발생 시 기존 에이전트 차출하여 임시 팀 편성."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.team import AgentTeam

logger = logging.getLogger(__name__)

MAX_CONCURRENT_TFS = 2
MAX_TF_LIFESPAN_DAYS = 7


@dataclass
class TaskForceRecord:
    """TF팀 편성 기록."""

    name: str
    problem: str
    leader: str
    members: list[str]
    goal: str
    created_at: float = field(default_factory=time.time)
    resolved_at: float | None = None
    result: str | None = None
    lessons: str | None = None

    @property
    def active(self) -> bool:
        return self.resolved_at is None

    @property
    def age_days(self) -> float:
        return (time.time() - self.created_at) / 86400


class TaskForceManager:
    """TF팀 관리자 - CEO가 사용하는 TF 편성/관리 도구.

    운영 규칙:
    - 동시 TF 최대 2개
    - TF 수명 최대 1주일 (초과 시 상설팀 전환 검토)
    - 원래 팀 업무 우선 (차출로 원래 팀 마비 방지)
    - TF 결과 문서화 필수
    """

    def __init__(self) -> None:
        self._task_forces: dict[str, TaskForceRecord] = {}
        self._teams: dict[str, AgentTeam] = {}
        self._agent_pool: dict[str, BaseAgent] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """에이전트 풀에 등록 (차출 대상)."""
        self._agent_pool[agent.name] = agent

    def register_agents(self, agents: list[BaseAgent]) -> None:
        """여러 에이전트를 풀에 등록."""
        for agent in agents:
            self.register_agent(agent)

    @property
    def active_tfs(self) -> list[TaskForceRecord]:
        return [tf for tf in self._task_forces.values() if tf.active]

    @property
    def active_count(self) -> int:
        return len(self.active_tfs)

    def can_create_tf(self) -> bool:
        """새 TF 편성 가능 여부."""
        return self.active_count < MAX_CONCURRENT_TFS

    def create_tf(
        self,
        name: str,
        problem: str,
        leader_name: str,
        member_names: list[str],
        goal: str,
        model: str = "claude-sonnet-4-20250514",
    ) -> AgentTeam | None:
        """TF팀을 편성합니다.

        Args:
            name: TF팀 이름
            problem: 해결할 문제
            leader_name: TF 리더 에이전트 이름
            member_names: TF 멤버 에이전트 이름 목록
            goal: TF 목표
            model: 사용할 모델

        Returns:
            편성된 AgentTeam, 또는 제한 초과 시 None
        """
        if not self.can_create_tf():
            logger.warning(
                f"TF 편성 불가: 동시 TF 최대 {MAX_CONCURRENT_TFS}개 "
                f"(현재 {self.active_count}개)"
            )
            return None

        # 리더 확인
        leader = self._agent_pool.get(leader_name)
        if leader is None:
            logger.error(f"TF 리더 '{leader_name}' not found in agent pool")
            return None

        # 멤버 확인
        members: list[BaseAgent] = []
        for member_name in member_names:
            agent = self._agent_pool.get(member_name)
            if agent is None:
                logger.warning(f"TF 멤버 '{member_name}' not found, skipping")
                continue
            members.append(agent)

        # AgentTeam 생성
        team = AgentTeam(name=f"TF-{name}", model=model)
        team.spawn_teammate(leader)
        for member in members:
            team.spawn_teammate(member)

        # 기록
        all_members = [leader_name] + [m.name for m in members]
        record = TaskForceRecord(
            name=name,
            problem=problem,
            leader=leader_name,
            members=all_members,
            goal=goal,
        )
        self._task_forces[name] = record
        self._teams[name] = team

        logger.info(
            f"TF '{name}' 편성 완료: 리더={leader_name}, "
            f"멤버={len(all_members)}명, 목표={goal}"
        )
        return team

    async def dissolve_tf(
        self,
        name: str,
        result: str,
        lessons: str,
    ) -> TaskForceRecord | None:
        """TF팀을 해산합니다.

        Args:
            name: TF팀 이름
            result: 해결 결과
            lessons: 교훈 (다음에 어떻게 예방할지)

        Returns:
            해산된 TF 기록
        """
        record = self._task_forces.get(name)
        if record is None:
            logger.warning(f"TF '{name}' not found")
            return None

        record.resolved_at = time.time()
        record.result = result
        record.lessons = lessons

        # AgentTeam 정리
        team = self._teams.pop(name, None)
        if team:
            await team.cleanup()

        logger.info(f"TF '{name}' 해산 완료 (수명: {record.age_days:.1f}일)")
        return record

    def get_expired_tfs(self) -> list[TaskForceRecord]:
        """수명 초과 TF 목록."""
        return [
            tf
            for tf in self.active_tfs
            if tf.age_days > MAX_TF_LIFESPAN_DAYS
        ]

    def status(self) -> str:
        """TF 시스템 현황."""
        lines = [
            f"=== TF 시스템 현황 ===",
            f"활성 TF: {self.active_count}/{MAX_CONCURRENT_TFS}",
            f"에이전트 풀: {len(self._agent_pool)}명",
        ]

        for tf in self.active_tfs:
            lines.append(
                f"\n[TF-{tf.name}] 리더: {tf.leader} | "
                f"멤버: {len(tf.members)}명 | "
                f"수명: {tf.age_days:.1f}일 | "
                f"목표: {tf.goal}"
            )

        expired = self.get_expired_tfs()
        if expired:
            lines.append(f"\n⚠️  수명 초과 TF: {[tf.name for tf in expired]}")

        history = [tf for tf in self._task_forces.values() if not tf.active]
        if history:
            lines.append(f"\n해산 완료: {len(history)}건")

        return "\n".join(lines)
