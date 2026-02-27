"""자율 운영 엔진 — Learning Agent Corp.을 자동으로 굴려주는 오토파일럿.

CEO가 미션을 분석하고 팀에 분배하고 결과를 취합하는 자동 루프입니다.
LocalBrain이 각 에이전트의 두뇌 역할을 하므로 API 키가 필요 없습니다.

사용법:
    python -m ubermensch auto                # 1사이클 실행
    python -m ubermensch auto --cycles 5     # 5사이클 실행
    python -m ubermensch.autopilot           # 직접 실행
"""

from __future__ import annotations

import asyncio
import argparse
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from ubermensch.agents.corp.organization import LearningAgentCorp, TEAM_CONFIGS
from ubermensch.core.local_brain import LocalBrain
from ubermensch.core.message import AgentMessage
from ubermensch.core.persistence import save_corp_state, restore_corp

logger = logging.getLogger(__name__)


class Autopilot:
    """Learning Agent Corp. 자율 운영 엔진.

    CEO를 중심으로 전체 조직을 자동으로 굴립니다.
    LocalBrain이 각 에이전트의 ask_llm을 대체하여
    API 키 없이 완전 자율 동작합니다.
    """

    def __init__(
        self,
        state_path: str | Path = "corp_state.json",
        study_state_path: str | Path = "study_state.json",
        verbose: bool = False,
    ) -> None:
        self.state_path = Path(state_path)
        self.study_state_path = Path(study_state_path)
        self.verbose = verbose
        self.corp: LearningAgentCorp | None = None
        self.brain: LocalBrain | None = None
        self.cycle_count = 0
        self._log: list[str] = []

    def _print(self, msg: str) -> None:
        print(msg)
        self._log.append(msg)

    def _header(self, title: str) -> None:
        self._print("")
        self._print(f"{'─' * 56}")
        self._print(f"  {title}")
        self._print(f"{'─' * 56}")

    def _agent_report(self, name: str, response: str, max_lines: int = 8) -> None:
        """에이전트 보고서 출력."""
        self._print(f"\n▸ {name.upper()}")
        lines = response.strip().split("\n")
        for line in lines[:max_lines]:
            self._print(f"  {line}")
        if len(lines) > max_lines:
            self._print(f"  ... (+{len(lines) - max_lines}줄)")

    def boot(self) -> None:
        """조직 부팅 + LocalBrain 주입."""
        self._header("BOOT: Learning Agent Corp. 기동")

        # 조직 복원 또는 생성
        if self.state_path.exists():
            self.corp = restore_corp(self.state_path)
            self._print(f"  저장된 조직 복원: {self.corp.headcount}명")
        else:
            self.corp = LearningAgentCorp()
            self._print("  새 조직 생성")

        if self.corp.headcount == 0:
            self._print("  전체 채용 실행 중...")
            self.corp.hire_all()
            self.corp.build_all_teams()
            self._print(f"  채용 완료: {self.corp.headcount}명, {len(TEAM_CONFIGS)}개 팀")

        # LocalBrain 생성 + 주입
        self.brain = LocalBrain(state_path=self.study_state_path)
        self.brain.inject(self.corp)
        self._print(f"  LocalBrain 주입 완료 (Day {self.brain.state.day}, Cycle {self.brain.state.cycle})")

        save_corp_state(self.corp, self.state_path)

    async def _ask(self, agent_name: str, task: str, context: dict | None = None) -> str:
        """에이전트 실행 — LocalBrain이 주입되어 있으므로 API 불필요."""
        agent = self.corp.get_agent(agent_name)
        if agent is None:
            return f"[{agent_name}] 미배치"

        result = await agent.run(AgentMessage(task=task, context=context or {}))
        return result.data if result.success else f"[실패] {result.error}"

    async def phase_1_ceo_analysis(self) -> str:
        """Phase 1: CEO 미션 분석."""
        self._header(f"CYCLE {self.cycle_count} — Phase 1: CEO 미션 분석")

        response = await self._ask("ceo", "현재 조직 상태를 분석하고 이번 사이클 지시를 내려줘.", {
            "type": "mission_analysis",
            "headcount": self.corp.headcount,
            "cycle": self.cycle_count,
        })
        self._print(response)
        return response

    async def phase_2_csuite_parallel(self) -> dict[str, str]:
        """Phase 2: C-Suite 병렬 보고."""
        self._header(f"CYCLE {self.cycle_count} — Phase 2: C-Suite 보고")

        csuite_tasks = {
            "cto": "시스템 및 파이프라인 상태를 점검하고 보고해줘.",
            "coo": "오늘의 학습 스케줄을 점검하고 실행 계획을 보고해줘.",
            "cfo": "현재 성과 데이터를 분석하고 KPI 현황을 보고해줘.",
            "cmo": "사용자의 동기부여 상태를 점검하고 보고해줘.",
        }

        results: dict[str, str] = {}

        async def _run(name: str, task: str) -> tuple[str, str]:
            return name, await self._ask(name, task)

        done = await asyncio.gather(
            *[_run(n, t) for n, t in csuite_tasks.items()],
            return_exceptions=True,
        )

        for item in done:
            if isinstance(item, Exception):
                self._print(f"  [에러] {item}")
            else:
                name, response = item
                results[name] = response
                self._agent_report(name, response)

        return results

    async def phase_3_team_execution(self) -> dict[str, str]:
        """Phase 3: 팀장급 병렬 실행."""
        self._header(f"CYCLE {self.cycle_count} — Phase 3: 팀 실행")

        team_tasks = {
            "plumber": "데이터 파이프라인 현황을 보고해줘.",
            "tracker": "학습 성과 추적 현황을 보고해줘.",
            "review_scheduler": "복습 스케줄 현황을 보고해줘.",
            "strategist": "시험 전략 연구 현황을 보고해줘.",
            "burnout_watcher": "번아웃 모니터링 현황을 보고해줘.",
            "gemini_diplomat": "외부 AI 연동 현황을 보고해줘.",
        }

        results: dict[str, str] = {}

        async def _run(name: str, task: str) -> tuple[str, str]:
            return name, await self._ask(name, task)

        done = await asyncio.gather(
            *[_run(n, t) for n, t in team_tasks.items()],
            return_exceptions=True,
        )

        for item in done:
            if isinstance(item, Exception):
                self._print(f"  [에러] {item}")
            else:
                name, response = item
                results[name] = response
                self._agent_report(name, response, max_lines=6)

        return results

    async def phase_4_redteam(self) -> dict[str, str]:
        """Phase 4: 레드팀 검증."""
        self._header(f"CYCLE {self.cycle_count} — Phase 4: 레드팀 검증")

        results: dict[str, str] = {}
        response = await self._ask("data_redteam", "이번 사이클 데이터 작업을 검증해줘.")
        results["data_redteam"] = response
        self._agent_report("data_redteam", response, max_lines=6)

        return results

    async def phase_5_ceo_synthesis(
        self, csuite: dict, teams: dict, redteam: dict
    ) -> str:
        """Phase 5: CEO 종합."""
        self._header(f"CYCLE {self.cycle_count} — Phase 5: CEO 종합")

        response = await self._ask("ceo", "종합 보고를 작성해줘.", {
            "type": "synthesis",
            "csuite": {k: v[:200] for k, v in csuite.items()},
            "teams": {k: v[:200] for k, v in teams.items()},
            "redteam": {k: v[:200] for k, v in redteam.items()},
        })
        self._print(response)
        return response

    async def run_cycle(self) -> dict[str, Any]:
        """1사이클 = 분석 → C-Suite → 팀 → 레드팀 → 종합."""
        self.cycle_count += 1

        # 사이클 진행 — 학습 상태 시뮬레이션
        self.brain.advance()
        s = self.brain.state

        self._header(
            f"Day {s.day} | Cycle {s.cycle} | "
            f"연속 {s.streak}일 | "
            f"정답률 {sum(s.accuracy_by_type.values())/max(len(s.accuracy_by_type),1):.0%}"
        )

        started = time.time()

        ceo_plan = await self.phase_1_ceo_analysis()
        csuite = await self.phase_2_csuite_parallel()
        teams = await self.phase_3_team_execution()
        redteam = await self.phase_4_redteam()
        synthesis = await self.phase_5_ceo_synthesis(csuite, teams, redteam)

        elapsed = time.time() - started

        # 저장
        save_corp_state(self.corp, self.state_path)
        self.brain.state.save(self.study_state_path)

        self._header(f"CYCLE {self.cycle_count} 완료 ({elapsed:.1f}s)")

        return {
            "cycle": self.cycle_count,
            "day": s.day,
            "elapsed": elapsed,
            "accuracy": sum(s.accuracy_by_type.values()) / max(len(s.accuracy_by_type), 1),
            "burnout": s.burnout_level,
            "notes_migrated": s.migrated_notes,
        }

    async def run(self, cycles: int = 1) -> list[dict[str, Any]]:
        """지정된 사이클 수만큼 자율 실행."""
        self.boot()

        self._header("AUTOPILOT START")
        self._print(f"  모드: LocalBrain (API 키 불필요)")
        self._print(f"  사이클: {cycles}회")
        self._print(f"  인원: {self.corp.headcount}명")
        self._print(f"  시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        all_results = []
        for _ in range(cycles):
            result = await self.run_cycle()
            all_results.append(result)

        # 최종 요약
        self._header("AUTOPILOT COMPLETE")
        self._print(f"  총 {len(all_results)} 사이클 완료")
        self._print("")
        self._print("  사이클 | Day | 정답률 | 번아웃  | 노트 이관")
        self._print("  " + "─" * 48)
        for r in all_results:
            self._print(
                f"  {r['cycle']:>5d}  | "
                f"D{r['day']:<2d} | "
                f"{r['accuracy']:>5.0%}  | "
                f"{r['burnout']:<8s}| "
                f"{r['notes_migrated']}/400"
            )

        s = self.brain.state
        self._print("")
        self._print(f"  최종 상태: Day {s.day}, 연속 {s.streak}일, 토픽 {len(s.studied_topics)}개")
        self._print(f"  상태 저장: {self.state_path}, {self.study_state_path}")

        return all_results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Learning Agent Corp. 자율 운영 엔진 (API 키 불필요)",
    )
    parser.add_argument(
        "--cycles", type=int, default=1, help="실행 사이클 수 (기본값: 1)",
    )
    parser.add_argument(
        "--state", default="corp_state.json", help="조직 상태 파일",
    )
    parser.add_argument(
        "--study-state", default="study_state.json", help="학습 상태 파일",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="상세 로그",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    pilot = Autopilot(
        state_path=args.state,
        study_state_path=args.study_state,
        verbose=args.verbose,
    )
    asyncio.run(pilot.run(cycles=args.cycles))


if __name__ == "__main__":
    main()
