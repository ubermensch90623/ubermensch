"""Übermensch 셀프 리뷰 - 이 프로젝트 코드를 에이전트들이 직접 리뷰합니다.

사용법:
    # 1. Mock 모드 (API 키 불필요, 흐름 확인용)
    python examples/self_review.py --mock

    # 2. 실제 모드 (API 키 필요)
    export ANTHROPIC_API_KEY="sk-..."
    python examples/self_review.py

    # 3. 특정 파일만
    python examples/self_review.py src/ubermensch/core/team.py
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from ubermensch import (
    AgentTeam,
    CodeReviewerAgent,
    DevilsAdvocateAgent,
    Discussion,
    HookContext,
    HookEvent,
    HookResult,
    PerformanceReviewerAgent,
    SecurityReviewerAgent,
)


def read_source_files(paths: list[str] | None = None) -> dict[str, str]:
    """소스 파일들을 읽어옵니다."""
    root = Path(__file__).parent.parent / "src" / "ubermensch"

    if paths:
        files = {}
        for p in paths:
            path = Path(p)
            if path.exists():
                files[str(path)] = path.read_text()
        return files

    # 기본: 핵심 모듈들
    targets = [
        root / "core" / "team.py",
        root / "core" / "shared_task_list.py",
        root / "core" / "mailbox.py",
        root / "core" / "hooks.py",
        root / "core" / "discussion.py",
        root / "core" / "base_agent.py",
    ]
    return {str(f.relative_to(root.parent.parent)): f.read_text() for f in targets if f.exists()}


_original_ask_llm = None


def apply_mock(team: AgentTeam) -> None:
    """LLM 호출을 mock으로 대체합니다."""
    global _original_ask_llm
    from ubermensch.core.base_agent import BaseAgent

    # 팀 리드의 synthesize용 mock client
    mock_response = MagicMock()
    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = (
        "## 종합 리뷰 (Mock)\n\n"
        "보안: asyncio.Lock 기반 동시성 제어 양호. 외부 입력 검증 강화 필요.\n"
        "성능: asyncio.gather 병렬 처리 양호. 대규모 태스크 시 O(n) 순회 주의.\n"
        "품질: 추상 클래스 패턴 일관성 양호. 타입 힌트 잘 적용됨.\n\n"
        "→ export ANTHROPIC_API_KEY='sk-...' 로 실제 분석을 실행하세요."
    )
    mock_response.content = [mock_block]
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    team._client = mock_client

    # 에이전트 개별 ask_llm mock (에이전트 이름별 다른 응답)
    mock_responses = {
        "security_reviewer": (
            "## 보안 분석\n"
            "1. asyncio.Lock 사용으로 SharedTaskList 동시성 제어 양호\n"
            "2. AgentMessage.context에 사용자 입력이 그대로 전달됨 → sanitization 고려\n"
            "3. LLM 응답 파싱(TASK:/APPROVED: 등) 시 prompt injection 방어 필요\n"
            "4. WebCrawler에서 SSRF 방지를 위한 URL 화이트리스트 권장"
        ),
        "performance_reviewer": (
            "## 성능 분석\n"
            "1. asyncio.gather로 병렬 실행 - 양호\n"
            "2. SharedTaskList.get_available_tasks()가 매번 전체 리스트 정렬 → 힙 구조 고려\n"
            "3. _agent_worker의 0.5초 sleep 폴링 → asyncio.Event 기반으로 개선 가능\n"
            "4. Mailbox의 asyncio.Queue는 메모리 제한 없음 → maxsize 설정 권장"
        ),
        "code_reviewer": (
            "## 코드 품질 분석\n"
            "1. BaseAgent 추상 클래스 패턴 일관성 양호\n"
            "2. HookRegistry 데코레이터 API가 직관적\n"
            "3. Discussion._extract_text에서 dict key fallback 체인이 brittle\n"
            "4. TeamPersistence.save_team이 Any 타입에 의존 → Protocol 정의 권장"
        ),
        "security_expert": (
            "## 보안 심층 분석\n"
            "1. 에이전트 간 메시지가 메모리에만 존재 → 현재로서는 안전\n"
            "2. _plan_tasks의 LLM 응답 파싱이 정규식 없이 문자열 split → 주입 벡터\n"
            "3. respawn_teammate에서 팩토리 kwargs를 그대로 전달 → 검증 필요"
        ),
        "challenger": (
            "## 반론\n"
            "1. SSRF 위험은 과장됨: WebCrawler는 선택적 도구이고 기본 사용 안 함\n"
            "2. prompt injection은 LLM 자체 문제이지 프레임워크 책임이 아님\n"
            "3. 다만 _plan_tasks 파싱의 robustness는 동의 → JSON 구조화 응답 권장"
        ),
    }

    _original_ask_llm = BaseAgent.ask_llm

    async def patched_ask_llm(self, prompt, context=None, max_tokens=4096):
        return mock_responses.get(self.name, f"[{self.name}] Mock 분석 완료.")

    BaseAgent.ask_llm = patched_ask_llm  # type: ignore[assignment]


def restore_mock() -> None:
    """ask_llm을 원래대로 복원합니다."""
    global _original_ask_llm
    if _original_ask_llm is not None:
        from ubermensch.core.base_agent import BaseAgent

        BaseAgent.ask_llm = _original_ask_llm  # type: ignore[assignment]


async def main():
    parser = argparse.ArgumentParser(description="Übermensch 셀프 리뷰")
    parser.add_argument("files", nargs="*", help="리뷰할 파일 경로")
    parser.add_argument("--mock", action="store_true", help="Mock 모드 (API 키 불필요)")
    args = parser.parse_args()

    # 소스 코드 읽기
    sources = read_source_files(args.files or None)
    if not sources:
        print("리뷰할 파일이 없습니다.")
        sys.exit(1)

    code_block = "\n\n".join(f"# --- {name} ---\n{code[:3000]}" for name, code in sources.items())

    print(f"리뷰 대상: {len(sources)}개 파일")
    for name in sources:
        print(f"  - {name}")

    # 팀 구성
    team = AgentTeam(name="self-review")

    if args.mock:
        apply_mock(team)

    # 훅: 진행 상황 출력
    @team.hooks.on(HookEvent.TEAMMATE_SPAWNED)
    async def on_spawn(ctx: HookContext) -> HookResult:
        print(f"  + {ctx.agent_name} 합류")
        return HookResult()

    @team.hooks.on(HookEvent.TASK_COMPLETED)
    async def on_complete(ctx: HookContext) -> HookResult:
        print(f"  ✓ {ctx.agent_name}: {ctx.task_title}")
        return HookResult()

    @team.hooks.on(HookEvent.TASK_FAILED)
    async def on_fail(ctx: HookContext) -> HookResult:
        print(f"  ✗ {ctx.agent_name}: {ctx.task_title} - {ctx.data.get('error', '?')}")
        return HookResult()

    # 에이전트 스폰
    print("\n팀 구성 중...")
    await team.spawn_teammate(SecurityReviewerAgent())
    await team.spawn_teammate(PerformanceReviewerAgent())
    await team.spawn_teammate(CodeReviewerAgent())

    # 태스크 생성
    await team.create_tasks(
        [
            {
                "title": "보안 리뷰",
                "description": f"이 코드의 보안 취약점을 분석하세요:\n\n{code_block}",
                "priority": 10,
            },
            {
                "title": "성능 리뷰",
                "description": f"이 코드의 성능 이슈를 분석하세요:\n\n{code_block}",
                "priority": 8,
            },
            {
                "title": "코드 품질 리뷰",
                "description": f"이 코드의 품질, 패턴, 테스트 커버리지를 분석하세요:\n\n{code_block}",
                "priority": 6,
            },
        ]
    )

    # 팀 실행
    print("\n리뷰 시작...\n")
    result = await team.run_team(
        f"다음 코드를 보안, 성능, 품질 관점에서 종합 리뷰:\n\n{code_block[:1000]}",
        auto_plan=False,
    )

    # 결과 출력
    print("\n" + "=" * 60)
    print("에이전트별 결과")
    print("=" * 60)

    for r in result["results"]:
        status = "PASS" if r.success else "FAIL"
        print(f"\n[{r.agent_name}] {status}")
        print("-" * 40)
        data = r.data if r.success else r.error
        if isinstance(data, dict):
            print(data.get("analysis", str(data))[:500])
        else:
            print(str(data)[:500])

    print("\n" + "=" * 60)
    print("종합 의견")
    print("=" * 60)
    print(result["synthesis"][:1000])

    # 토론 (보안 리뷰에 DevilsAdvocate 반론)
    security_result = next(
        (r for r in result["results"] if r.agent_name == "security_reviewer"),
        None,
    )
    if security_result and security_result.success:
        print("\n" + "=" * 60)
        print("보안 리뷰 토론 (SecurityReviewer vs DevilsAdvocate)")
        print("=" * 60)

        disc = Discussion(
            presenter=SecurityReviewerAgent(name="security_expert"),
            critic=DevilsAdvocateAgent(name="challenger"),
            rounds=1,
        )
        if args.mock:
            disc._client = team._client

        debate = await disc.run(
            topic="Übermensch 프레임워크 보안 리뷰 검증",
            context={
                "code": code_block[:2000],
                "findings": str(security_result.data)[:1000],
            },
        )

        for turn in debate.turns:
            print(f"\n[R{turn.round}] {turn.speaker} ({turn.role}):")
            print(turn.content[:300])

        print(f"\n합의:\n{debate.consensus[:500]}")

    await team.cleanup()
    if args.mock:
        restore_mock()
    print("\n완료!")


if __name__ == "__main__":
    asyncio.run(main())
