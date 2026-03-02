"""Übermensch 사용 예제: 멀티에이전트 리서치

사용법:
    export ANTHROPIC_API_KEY="your-api-key"
    python examples/research_example.py
"""

import asyncio
import logging

from ubermensch.core.orchestrator import SubagentOrchestrator
from ubermensch.agents.researcher import ResearcherAgent, SummarizerAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)


async def main():
    # 1. 오케스트레이터 생성
    orchestrator = SubagentOrchestrator()

    # 2. 서브에이전트 등록
    orchestrator.register_agent(ResearcherAgent(name="researcher"))
    orchestrator.register_agent(SummarizerAgent(name="summarizer"))

    # 3. 사용자 요청 실행
    result = await orchestrator.run(
        "AI 에이전트 프레임워크의 최신 트렌드를 조사하고 핵심 내용을 요약해줘"
    )

    print("\n" + "=" * 60)
    print("최종 결과:")
    print("=" * 60)
    print(result)


async def manual_example():
    """수동으로 서브에이전트를 제어하는 예제."""

    orchestrator = SubagentOrchestrator()
    orchestrator.register_agent(ResearcherAgent(name="researcher"))
    orchestrator.register_agent(SummarizerAgent(name="summarizer"))

    # 여러 에이전트에게 동시에 작업 위임
    results = await orchestrator.delegate_parallel([
        {
            "agent": "researcher",
            "task": "Python asyncio best practices 2025",
        },
        {
            "agent": "researcher",
            "task": "Multi-agent AI systems architecture",
        },
    ])

    for r in results:
        print(f"\n[{r.agent_name}] Status: {r.status.value}")
        if r.success:
            print(f"  Data: {r.data}")
        else:
            print(f"  Error: {r.error}")


if __name__ == "__main__":
    asyncio.run(main())
