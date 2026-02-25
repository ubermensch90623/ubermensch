"""Übermensch 사용 예제: Agent Teams - Plan Approval 아키텍처 설계

ArchitectAgent가 설계 계획을 수립하고 Lead의 승인을 받은 후
구현 가이드를 생성합니다.

사용법:
    export ANTHROPIC_API_KEY="your-api-key"
    python examples/team_architecture.py
"""

import asyncio
import logging

from ubermensch.agents.architect import ArchitectAgent
from ubermensch.agents.devils_advocate import DevilsAdvocateAgent
from ubermensch.agents.reviewers import SecurityReviewerAgent
from ubermensch.core.message import AgentMessage
from ubermensch.core.team import AgentTeam

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)


async def main():
    team = AgentTeam(name="architecture-team")

    architect = ArchitectAgent()
    team.spawn_teammate(architect)
    team.spawn_teammate(SecurityReviewerAgent())
    team.spawn_teammate(DevilsAdvocateAgent())

    # Step 1: Architect가 먼저 계획 수립
    plan_result = await architect.run(
        AgentMessage(
            task="Design a real-time notification system with WebSocket support",
            context={
                "plan_only": True,
                "constraints": (
                    "- Must support 10K concurrent connections\n"
                    "- Message delivery latency < 100ms\n"
                    "- Must handle reconnection gracefully\n"
                    "- Event sourcing for message history"
                ),
            },
        )
    )

    print("=" * 60)
    print("Architect's Plan:")
    print("=" * 60)
    print(plan_result.data["plan"])

    # Step 2: Lead가 계획 승인 검토
    approval = await team.request_plan_approval(
        agent_name="architect",
        plan=plan_result.data["plan"],
        approval_criteria=(
            "Approve only if the plan includes:\n"
            "- Scalability strategy\n"
            "- Security considerations\n"
            "- Failure handling\n"
            "- Clear implementation phases"
        ),
    )

    print(f"\nApproval: {'APPROVED' if approval.approved else 'REJECTED'}")
    print(f"Feedback: {approval.feedback}")

    if approval.approved:
        # Step 3: 승인 후 상세 구현 가이드 생성
        guide_result = await architect.run(
            AgentMessage(
                task="Create implementation guide for the notification system",
                context={
                    "approved_plan": plan_result.data["plan"],
                },
            )
        )

        print("\n" + "=" * 60)
        print("Implementation Guide:")
        print("=" * 60)
        print(guide_result.data["guide"])

    # Step 4: 나머지 팀원들이 병렬로 리뷰
    await team.create_tasks([
        {
            "title": "Security review of architecture",
            "description": (
                f"Review this architecture plan for security concerns:\n"
                f"{plan_result.data['plan']}"
            ),
            "priority": 8,
        },
        {
            "title": "Challenge architecture assumptions",
            "description": (
                f"Challenge the assumptions in this architecture:\n"
                f"{plan_result.data['plan']}"
            ),
            "priority": 7,
        },
    ])

    result = await team.run_team(
        user_request="Review and validate the notification system architecture.",
        auto_plan=False,
    )

    print("\n" + "=" * 60)
    print("Team Review:")
    print("=" * 60)
    print(result["synthesis"])

    await team.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
