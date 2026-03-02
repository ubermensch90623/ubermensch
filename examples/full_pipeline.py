"""Übermensch 풀 파이프라인 예제: 리서치 → 리뷰 → 토론 → 합의

1단계: ResearcherAgent가 웹에서 정보를 수집
2단계: SecurityReviewer + PerformanceReviewer가 병렬 리뷰
3단계: DevilsAdvocateAgent가 리뷰 결과에 반론
4단계: Discussion 파이프라인으로 토론 → 합의 도출
5단계: ArchitectAgent가 최종 설계 계획 수립

사용법:
    # Mock 모드 (API 키 불필요, 기본)
    python examples/full_pipeline.py

    # 실제 모드
    export ANTHROPIC_API_KEY="your-api-key"
    python examples/full_pipeline.py
"""

import asyncio
import logging

from ubermensch.agents.architect import ArchitectAgent
from ubermensch.agents.devils_advocate import DevilsAdvocateAgent
from ubermensch.agents.researcher import ResearcherAgent
from ubermensch.agents.reviewers import (
    PerformanceReviewerAgent,
    SecurityReviewerAgent,
)
from ubermensch.core.discussion import Discussion
from ubermensch.core.hooks import HookContext, HookEvent, HookResult
from ubermensch.core.message import AgentMessage
from ubermensch.core.persistence import TeamPersistence
from ubermensch.core.team import AgentTeam

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)


async def main():
    print("=" * 60)
    print("Übermensch Full Pipeline: Research → Review → Debate → Plan")
    print("=" * 60)

    # --- Stage 1: 리서치 ---
    print("\n--- Stage 1: Research ---")
    researcher = ResearcherAgent()
    research_result = await researcher.run(
        AgentMessage(
            task="Python WebSocket 보안 베스트 프랙티스 2025",
            context={"urls": ["https://owasp.org/www-project-web-security-testing-guide/"]},
        )
    )

    if research_result.success:
        research_data = research_result.data.get("analysis", "No analysis")
        print(f"Research completed. Sources: {len(research_result.data.get('sources', []))}")
    else:
        research_data = "Research failed, proceeding with general knowledge."
        print(f"Research failed: {research_result.error}")

    # --- Stage 2: 팀 병렬 리뷰 ---
    print("\n--- Stage 2: Parallel Team Review ---")
    team = AgentTeam(name="review-pipeline")

    # 훅 설정: 태스크 완료 시 로그
    @team.hooks.on(HookEvent.TASK_COMPLETED)
    async def log_completion(ctx: HookContext) -> HookResult:
        print(f"  [Hook] Task completed by {ctx.agent_name}: {ctx.task_title}")
        return HookResult()

    await team.spawn_teammate(SecurityReviewerAgent())
    await team.spawn_teammate(PerformanceReviewerAgent())

    sample_code = """
import asyncio
import websockets

connected = set()

async def handler(websocket):
    connected.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            # Broadcast to all
            for ws in connected:
                await ws.send(json.dumps(data))
    finally:
        connected.discard(websocket)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()
"""

    await team.create_tasks([
        {
            "title": "Security review of WebSocket server",
            "description": (
                f"Review this WebSocket code for security issues. "
                f"Research context:\n{research_data[:2000]}\n\n"
                f"Code:\n```python\n{sample_code}\n```"
            ),
            "priority": 10,
        },
        {
            "title": "Performance review of WebSocket server",
            "description": (
                f"Review this WebSocket code for performance issues.\n\n"
                f"Code:\n```python\n{sample_code}\n```"
            ),
            "priority": 8,
        },
    ])

    # 팀 실행 (auto_plan=False)
    team_result = await team.run_team(
        "WebSocket 서버 코드를 보안/성능 관점에서 리뷰",
        auto_plan=False,
    )

    print(f"\nTeam review completed. Results: {len(team_result['results'])}")

    # --- Stage 3: 토론 (SecurityReviewer vs DevilsAdvocate) ---
    print("\n--- Stage 3: Debate ---")
    security_findings = ""
    for r in team_result["results"]:
        if r.agent_name == "security_reviewer" and r.success:
            data = r.data
            security_findings = data.get("analysis", str(data)) if isinstance(data, dict) else str(data)

    discussion = Discussion(
        presenter=SecurityReviewerAgent(name="security_expert"),
        critic=DevilsAdvocateAgent(name="challenger"),
        rounds=1,
    )

    debate_result = await discussion.run(
        topic="WebSocket 서버 보안 리뷰 검증",
        context={"findings": security_findings, "code": sample_code},
    )

    print(f"Debate completed. Turns: {len(debate_result.turns)}")
    print(f"\nConsensus:\n{debate_result.consensus[:500]}...")

    # --- Stage 4: 아키텍처 설계 ---
    print("\n--- Stage 4: Architecture Planning ---")
    architect = ArchitectAgent()

    plan_result = await architect.run(
        AgentMessage(
            task="Secure WebSocket server architecture design",
            context={
                "plan_only": True,
                "constraints": (
                    f"Security findings:\n{security_findings[:1000]}\n\n"
                    f"Debate consensus:\n{debate_result.consensus[:1000]}"
                ),
            },
        )
    )

    if plan_result.success:
        plan = plan_result.data.get("plan", "")
        print(f"Architecture plan created ({len(plan)} chars)")

        # Plan Approval
        approval = await team.request_plan_approval(
            agent_name="architect",
            plan=plan,
            approval_criteria="Must address all security findings from the review.",
        )
        print(f"Plan {'APPROVED' if approval.approved else 'REJECTED'}: {approval.feedback[:200]}")

    # --- 팀 상태 저장 ---
    persistence = TeamPersistence()
    persistence.save_team(team)
    print(f"\nTeam state saved to {persistence.base_dir / team.name}")

    # --- 정리 ---
    await team.cleanup()

    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
