"""python -m ubermensch 또는 ubermensch 명령어로 실행."""

import asyncio
import sys
from pathlib import Path


def main():
    # run.py가 프로젝트 루트에 있으면 그걸 실행
    run_py = Path(__file__).parent.parent.parent / "run.py"
    if run_py.exists():
        exec(compile(run_py.read_text(), str(run_py), "exec"), {"__name__": "__main__"})
        return

    # run.py가 없으면 내장 데모
    from ubermensch import AgentTeam, MockProvider, SecurityReviewerAgent, configure

    async def _demo():
        configure(provider=MockProvider(responses={
            "security": "보안 분석: 동시성 제어 양호, 입력 검증 강화 권장",
        }))

        print("\n  Übermensch Demo\n")
        team = AgentTeam(name="quick-demo")
        await team.spawn_teammate(SecurityReviewerAgent())
        await team.create_tasks([{"title": "보안 리뷰", "description": "코드 보안 분석"}])

        result = await team.run_team("보안 리뷰", auto_plan=False)

        for r in result["results"]:
            print(f"  [{r.agent_name}] {r.data}")

        print(f"\n  종합: {result['synthesis']}")
        await team.cleanup()
        configure()

    asyncio.run(_demo())


if __name__ == "__main__":
    main()
