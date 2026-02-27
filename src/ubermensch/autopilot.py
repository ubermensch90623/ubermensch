"""자율 운영 엔진 — Learning Agent Corp.을 자동으로 굴려주는 오토파일럿.

CEO가 미션을 분석하고 팀에 분배하고 결과를 취합하는 자동 루프입니다.
ANTHROPIC_API_KEY가 있으면 실제 Claude API를 호출하고,
없으면 데모 모드로 시뮬레이션합니다.

사용법:
    python -m ubermensch.autopilot              # 자동 실행
    python -m ubermensch.autopilot --demo       # 데모 모드 (API 키 불필요)
    python -m ubermensch.autopilot --cycles 3   # 3사이클 실행
"""

from __future__ import annotations

import asyncio
import argparse
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from ubermensch.agents.corp.organization import (
    LearningAgentCorp,
    TEAM_CONFIGS,
    HIRING_PRIORITY,
)
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus
from ubermensch.core.persistence import save_corp_state, restore_corp

logger = logging.getLogger(__name__)

# ─── 데모용 시뮬레이션 응답 ────────────────────────────────────────

DEMO_RESPONSES: dict[str, dict[str, str]] = {
    "ceo": {
        "mission_analysis": (
            "## CEO 미션 분석 보고\n\n"
            "현재 상황: NCS+경제학 시험 준비 조직 가동 개시\n\n"
            "### 이번 사이클 우선순위\n"
            "1. **데이터팀**: Keep 노트 400개 파이프라인 점검 → 가장 시급\n"
            "2. **분석팀**: 학습 진도 측정 체계 구축\n"
            "3. **학습팀**: 오늘의 복습 스케줄 생성\n\n"
            "### 의사결정\n"
            "- TF 편성: 불필요 (기존 팀 구조로 처리 가능)\n"
            "- 리스크: 데이터 파이프라인 미구축 시 전사 마비\n"
        ),
        "synthesis": (
            "## CEO 종합 보고\n\n"
            "### 이번 사이클 결과\n"
            "✓ 데이터팀: 파이프라인 설계 완료, 노트 분류 기준 수립\n"
            "✓ 분석팀: 성과 측정 KPI 3개 정의 (정답률, 학습시간, 복습률)\n"
            "✓ 학습팀: 에빙하우스 기반 복습 스케줄 v1 생성\n"
            "△ 피드백팀: 번아웃 지수 측정 기준 초안 작성 중\n\n"
            "### 다음 사이클 지시사항\n"
            "1. 데이터팀: 실제 Keep 노트 10개로 파일럿 이관 실행\n"
            "2. 연구팀: 합격자 학습 패턴 3개 이상 수집\n"
            "3. 외교팀: Gemini에게 경제학 기출 트렌드 분석 요청\n"
        ),
    },
    "cto": {
        "default": (
            "## CTO 기술 보고\n\n"
            "### 파이프라인 상태\n"
            "- Keep API: 접근 가능 (OAuth 설정 필요)\n"
            "- Notion API: 토큰 설정 완료 대기\n"
            "- 데이터 흐름: Keep → 파싱 → 분류 → 검수 → Notion\n\n"
            "### 기술 권고\n"
            "1. Keep Takeout으로 일괄 내보내기 후 배치 처리 권장\n"
            "2. Notion DB 스키마를 먼저 확정해야 함\n"
            "3. MCP 프로토콜로 Gemini 연동 준비 중\n"
        ),
    },
    "coo": {
        "default": (
            "## COO 운영 보고\n\n"
            "### 오늘의 학습 스케줄\n"
            "- 09:00-10:30 NCS 수리영역 복습 (에빙하우스 D+3)\n"
            "- 10:30-12:00 경제학 미시 Chapter 4-5\n"
            "- 14:00-15:30 NCS 언어영역 신규\n"
            "- 15:30-17:00 경제학 기출 3회분\n\n"
            "### 병목 감지\n"
            "- 없음 (조직 가동 첫날)\n"
            "### 실행률: 대기중\n"
        ),
    },
    "cfo": {
        "default": (
            "## CFO 성과 보고\n\n"
            "### KPI 현황\n"
            "- 정답률: 측정 전 (데이터 부족)\n"
            "- 학습시간 ROI: 측정 전\n"
            "- 주간 목표 달성률: N/A\n\n"
            "### 분석 권고\n"
            "1. 최소 1주일간 데이터 축적 후 ROI 분석 가능\n"
            "2. 초기 3일은 베이스라인 측정에 집중 권고\n"
            "3. 과목별 시간 대비 점수 상승률 추적 시작\n"
        ),
    },
    "cmo": {
        "default": (
            "## CMO 동기부여 보고\n\n"
            "### 번아웃 지수\n"
            "- 현재: SAFE (조직 가동 첫날)\n"
            "- 연속 학습일수: 0일 → 목표 7일\n\n"
            "### 동기부여 전략\n"
            "1. 첫날 성공 경험 설계: 쉬운 문제 5개로 시작\n"
            "2. 일일 리포트로 작은 성취감 제공\n"
            "3. 3일 연속 달성 시 난이도 단계 상향\n"
        ),
    },
    "plumber": {
        "default": (
            "## 배관공 파이프라인 보고\n\n"
            "### Keep 노트 현황\n"
            "- 총 400개 노트 중 분류 대상: 400개\n"
            "- NCS 관련 추정: ~250개\n"
            "- 경제학 관련 추정: ~120개\n"
            "- 기타/메모: ~30개\n\n"
            "### 파이프라인 설계\n"
            "1단계: Keep Takeout 내보내기\n"
            "2단계: JSON 파싱 → 분류사에게 전달\n"
            "3단계: 분류 결과 → 검수관 검증\n"
            "4단계: 검증 완료 → Notion DB 적재\n"
        ),
    },
    "data_redteam": {
        "default": (
            "## 데이터 레드팀 검증 보고\n\n"
            "### 판정: WARN (경고 후 진행)\n\n"
            "### 리스크 분석\n"
            "1. Keep 노트 형식 불일치 가능성: 중\n"
            "   - 핸드폰 메모 → 줄바꿈/서식 불규칙\n"
            "2. 중복 노트 존재 가능성: 높음\n"
            "   - 같은 문제를 다른 날에 반복 작성\n"
            "3. 데이터 유실 리스크: 낮음\n"
            "   - 원본 Keep은 보존\n\n"
            "### 권고: 10개 샘플로 파일럿 실행 후 전체 이관\n"
        ),
    },
    "tracker": {
        "default": (
            "## 추적관 분석 보고\n\n"
            "### 측정 체계 구축\n"
            "- 정답률 추적: 과목/유형별 분리 준비\n"
            "- 시간 추적: 세션별 학습시간 기록 시작\n"
            "- 복습 주기 추적: 에빙하우스 곡선 기반\n\n"
            "### 초기 베이스라인\n"
            "- 아직 데이터 없음. 최초 학습 세션 후 측정 시작.\n"
        ),
    },
    "review_scheduler": {
        "default": (
            "## 복습 설계사 보고\n\n"
            "### 에빙하우스 스케줄 v1\n"
            "- D+1: 24시간 후 1차 복습 (기억률 40% → 80% 회복)\n"
            "- D+3: 3일 후 2차 복습\n"
            "- D+7: 1주 후 3차 복습\n"
            "- D+14: 2주 후 4차 복습\n"
            "- D+30: 1개월 후 최종 확인\n\n"
            "### 오늘의 복습 대상\n"
            "- 아직 학습 이력 없음. 첫 학습 후 스케줄 생성.\n"
        ),
    },
    "strategist": {
        "default": (
            "## 전략가 연구 보고\n\n"
            "### NCS 시험 트렌드\n"
            "1. 수리영역: 자료해석 비중 증가 추세\n"
            "2. 언어영역: 문맥 파악 문제 강화\n"
            "3. 추론영역: 복합 추론 문제 신규 출제\n\n"
            "### 전략 제안\n"
            "- 자료해석 유형에 시간 투자 비중 30% 할당\n"
            "- 합격자 대비 취약 영역 식별 필요\n"
        ),
    },
    "burnout_watcher": {
        "default": (
            "## 번아웃 감시관 보고\n\n"
            "### 현재 상태: SAFE\n"
            "- 컨디션: 정상 (조직 가동 첫날)\n"
            "- 무력감 지수: 0 (기준치)\n"
            "- 과부하 징후: 없음\n\n"
            "### 모니터링 계획\n"
            "- 일일 학습시간 > 6시간 시 CAUTION 발령\n"
            "- 3일 연속 목표 미달 시 WARNING 발령\n"
            "- 7일 연속 미달 시 CRITICAL → 스케줄 강제 조정\n"
        ),
    },
    "gemini_diplomat": {
        "default": (
            "## 외교관 보고 (Gemini 채널)\n\n"
            "### 연동 상태\n"
            "- Gemini API: 설정 대기\n"
            "- MCP 프로토콜: 구현 예정\n\n"
            "### 계획\n"
            "1. 경제학 기출 분석을 Gemini에 교차 검증 요청\n"
            "2. Claude와 Gemini 답변 비교 → 불일치 시 cross_checker 투입\n"
            "3. 각 AI의 강점 영역 매핑\n"
        ),
    },
}

# 나머지 에이전트는 기본 응답
DEFAULT_AGENT_RESPONSE = "작업 수행 완료. 상세 결과는 팀장에게 보고됨."


def _get_demo_response(agent_name: str, task_type: str = "default") -> str:
    """데모 모드에서 에이전트의 시뮬레이션 응답을 반환."""
    agent_responses = DEMO_RESPONSES.get(agent_name, {})
    return agent_responses.get(task_type, agent_responses.get("default", DEFAULT_AGENT_RESPONSE))


# ─── 자율 운영 엔진 ─────────────────────────────────────────────

class Autopilot:
    """Learning Agent Corp. 자율 운영 엔진.

    CEO를 중심으로 전체 조직을 자동으로 굴립니다.
    """

    def __init__(
        self,
        state_path: str | Path = "corp_state.json",
        demo: bool = False,
        verbose: bool = False,
    ) -> None:
        self.state_path = Path(state_path)
        self.demo = demo
        self.verbose = verbose
        self.corp: LearningAgentCorp | None = None
        self.cycle_count = 0
        self._log: list[str] = []

    def _print(self, msg: str, prefix: str = "") -> None:
        """출력 + 로그 저장."""
        line = f"{prefix}{msg}" if prefix else msg
        print(line)
        self._log.append(line)

    def _header(self, title: str) -> None:
        self._print("")
        self._print(f"{'─' * 50}")
        self._print(f"  {title}")
        self._print(f"{'─' * 50}")

    def boot(self) -> LearningAgentCorp:
        """조직 부팅 — 저장된 상태 복원 또는 새로 생성."""
        self._header("BOOT: Learning Agent Corp. 기동")

        if self.state_path.exists():
            self.corp = restore_corp(self.state_path)
            self._print(f"  저장된 상태 복원: {self.corp.headcount}명")
        else:
            self.corp = LearningAgentCorp()
            self._print("  새 조직 생성")

        if self.corp.headcount == 0:
            self._print("  전체 채용 실행 중...")
            self.corp.hire_all()
            self.corp.build_all_teams()
            self._print(f"  채용 완료: {self.corp.headcount}명")

        save_corp_state(self.corp, self.state_path)
        self._print(f"  상태 저장: {self.state_path}")
        return self.corp

    async def _ask_agent(self, agent_name: str, task: str, context: dict | None = None) -> str:
        """에이전트에게 질문 — 데모 모드면 시뮬레이션."""
        agent = self.corp.get_agent(agent_name)
        if agent is None:
            return f"[{agent_name}] 미배치"

        if self.demo:
            await asyncio.sleep(0.1)  # 시뮬레이션 딜레이
            return _get_demo_response(agent_name, (context or {}).get("type", "default"))

        result = await agent.run(AgentMessage(task=task, context=context or {}))
        return result.data if result.success else f"[실패] {result.error}"

    async def phase_ceo_analysis(self) -> str:
        """Phase 1: CEO 미션 분석 및 지시."""
        self._header(f"CYCLE {self.cycle_count} — Phase 1: CEO 미션 분석")

        response = await self._ask_agent(
            "ceo",
            "현재 조직 상태를 분석하고, 이번 사이클에서 각 팀이 해야 할 일을 결정해줘.",
            {
                "type": "mission_analysis",
                "headcount": self.corp.headcount,
                "agents": self.corp.agent_names,
                "cycle": self.cycle_count,
            },
        )
        self._print(response)
        return response

    async def phase_team_execution(self) -> dict[str, str]:
        """Phase 2: 팀별 병렬 실행."""
        self._header(f"CYCLE {self.cycle_count} — Phase 2: 팀 실행")

        # 핵심 에이전트들에게 동시에 지시
        tasks = {
            "cto": ("시스템 및 파이프라인 상태를 점검하고 보고해줘.", {}),
            "coo": ("오늘의 학습 스케줄을 점검하고 실행 계획을 보고해줘.", {}),
            "cfo": ("현재 성과 데이터를 분석하고 KPI 현황을 보고해줘.", {}),
            "cmo": ("사용자의 동기부여 상태를 점검하고 보고해줘.", {}),
            "plumber": ("데이터 파이프라인 현황을 보고해줘.", {}),
            "tracker": ("학습 성과 추적 현황을 보고해줘.", {}),
            "review_scheduler": ("복습 스케줄 현황을 보고해줘.", {}),
            "strategist": ("시험 전략 연구 현황을 보고해줘.", {}),
            "burnout_watcher": ("번아웃 모니터링 현황을 보고해줘.", {}),
            "gemini_diplomat": ("외부 AI 연동 현황을 보고해줘.", {}),
        }

        results: dict[str, str] = {}

        # 병렬 실행
        async def _run_agent(name: str, task: str, ctx: dict) -> tuple[str, str]:
            res = await self._ask_agent(name, task, ctx)
            return name, res

        coros = [_run_agent(name, task, ctx) for name, (task, ctx) in tasks.items()]
        done = await asyncio.gather(*coros, return_exceptions=True)

        for item in done:
            if isinstance(item, Exception):
                self._print(f"  [에러] {item}")
            else:
                name, response = item
                results[name] = response
                self._print(f"\n{'▸ ' + name.upper()}")
                # 간결 모드: 첫 3줄만 표시
                lines = response.strip().split("\n")
                for line in lines[:6]:
                    self._print(f"  {line}")
                if len(lines) > 6:
                    self._print(f"  ... (+{len(lines) - 6}줄)")

        return results

    async def phase_redteam_review(self) -> dict[str, str]:
        """Phase 3: 레드팀 검증."""
        self._header(f"CYCLE {self.cycle_count} — Phase 3: 레드팀 검증")

        redteam_agents = [
            ("data_redteam", "데이터팀 작업 결과를 검증해줘."),
        ]

        results: dict[str, str] = {}
        for name, task in redteam_agents:
            response = await self._ask_agent(name, task, {"type": "review"})
            results[name] = response
            self._print(f"\n{'▸ ' + name.upper()}")
            for line in response.strip().split("\n")[:5]:
                self._print(f"  {line}")

        return results

    async def phase_ceo_synthesis(self, team_results: dict, redteam_results: dict) -> str:
        """Phase 4: CEO 종합 및 다음 사이클 지시."""
        self._header(f"CYCLE {self.cycle_count} — Phase 4: CEO 종합")

        response = await self._ask_agent(
            "ceo",
            "각 팀의 보고와 레드팀 검증 결과를 종합하고, 다음 사이클 지시를 내려줘.",
            {
                "type": "synthesis",
                "team_results": {k: v[:200] for k, v in team_results.items()},
                "redteam_results": {k: v[:200] for k, v in redteam_results.items()},
            },
        )
        self._print(response)
        return response

    async def run_cycle(self) -> dict[str, Any]:
        """한 사이클 실행: 분석 → 실행 → 검증 → 종합."""
        self.cycle_count += 1
        started = time.time()

        # Phase 1: CEO 분석
        ceo_plan = await self.phase_ceo_analysis()

        # Phase 2: 팀 병렬 실행
        team_results = await self.phase_team_execution()

        # Phase 3: 레드팀 검증
        redteam_results = await self.phase_redteam_review()

        # Phase 4: CEO 종합
        synthesis = await self.phase_ceo_synthesis(team_results, redteam_results)

        elapsed = time.time() - started

        self._header(f"CYCLE {self.cycle_count} 완료 ({elapsed:.1f}s)")

        # 상태 저장
        save_corp_state(self.corp, self.state_path)
        self._print(f"  상태 자동 저장: {self.state_path}")

        return {
            "cycle": self.cycle_count,
            "elapsed": elapsed,
            "ceo_plan": ceo_plan,
            "team_results": team_results,
            "redteam_results": redteam_results,
            "synthesis": synthesis,
        }

    async def run(self, cycles: int = 1) -> list[dict[str, Any]]:
        """지정된 사이클 수만큼 자율 실행."""
        self.boot()

        self._header("AUTOPILOT START")
        self._print(f"  모드: {'데모' if self.demo else '실제 API'}")
        self._print(f"  사이클: {cycles}회")
        self._print(f"  인원: {self.corp.headcount}명")
        self._print(f"  시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        all_results = []
        for i in range(cycles):
            result = await self.run_cycle()
            all_results.append(result)

        self._header("AUTOPILOT COMPLETE")
        self._print(f"  총 {len(all_results)} 사이클 실행 완료")
        self._print(f"  상태: {self.state_path}")

        return all_results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Learning Agent Corp. 자율 운영 엔진",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="데모 모드 (API 키 없이 시뮬레이션)",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="실행 사이클 수 (기본값: 1)",
    )
    parser.add_argument(
        "--state",
        default="corp_state.json",
        help="상태 파일 경로",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="상세 로그 출력",
    )
    args = parser.parse_args()

    # API 키 확인
    has_api_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    if not has_api_key and not args.demo:
        print("⚠ ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        print("  데모 모드로 전환합니다. (--demo 옵션과 동일)")
        print("  실제 API를 사용하려면: export ANTHROPIC_API_KEY=sk-...")
        print()
        args.demo = True

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    pilot = Autopilot(
        state_path=args.state,
        demo=args.demo,
        verbose=args.verbose,
    )
    asyncio.run(pilot.run(cycles=args.cycles))


if __name__ == "__main__":
    main()
