"""
실행 방법: python run.py

끝. 그게 다임.
"""

import asyncio

from ubermensch import (
    AgentTeam,
    CodeReviewerAgent,
    DevilsAdvocateAgent,
    Discussion,
    MockProvider,
    PerformanceReviewerAgent,
    SecurityReviewerAgent,
    configure,
)


async def main():
    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║   Übermensch - AI 에이전트 팀 데모       ║")
    print("  ╚══════════════════════════════════════════╝")
    print()

    # API 키 없어도 됨. 자동으로 데모 모드.
    configure(provider=MockProvider(responses={
        "security": (
            "보안 분석 결과:\n"
            "  1. 동시성 제어 (asyncio.Lock) → 양호\n"
            "  2. 사용자 입력 검증 → 개선 필요\n"
            "  3. LLM 응답 파싱 시 injection 방어 → 권장"
        ),
        "performance": (
            "성능 분석 결과:\n"
            "  1. asyncio.gather 병렬 처리 → 양호\n"
            "  2. 태스크 폴링 0.5초 간격 → Event 기반 개선 가능\n"
            "  3. 메모리 제한 없는 큐 → maxsize 설정 권장"
        ),
        "code quality|code review": (
            "코드 품질 분석 결과:\n"
            "  1. 추상 클래스 패턴 일관성 → 양호\n"
            "  2. Hook 데코레이터 API → 직관적\n"
            "  3. 타입 힌트 → 잘 적용됨"
        ),
        "synthesiz|종합|team lead": (
            "종합 의견:\n"
            "  보안, 성능, 코드 품질 모두 기본 수준 양호.\n"
            "  입력 검증과 메모리 제한 설정을 추가하면 더 좋겠음."
        ),
        "challenge|반론|devil": (
            "반론:\n"
            "  1. 입력 검증은 프레임워크가 아니라 사용자 책임 아닌가?\n"
            "  2. 메모리 제한은 실제 부하 테스트 후 결정해도 늦지 않음"
        ),
        "consensus|합의": (
            "합의:\n"
            "  기본 구조는 견고함. 입력 검증은 가이드 문서로,\n"
            "  메모리 제한은 설정 옵션으로 제공하는 것이 합리적."
        ),
    }))

    # ── 1단계: 팀 만들기 ──
    print("1단계: AI 에이전트 팀 구성 중...")
    print()

    team = AgentTeam(name="demo-team")

    await team.spawn_teammate(SecurityReviewerAgent())
    print("  보안 전문가 합류")

    await team.spawn_teammate(PerformanceReviewerAgent())
    print("  성능 전문가 합류")

    await team.spawn_teammate(CodeReviewerAgent())
    print("  코드 품질 전문가 합류")

    # ── 2단계: 할 일 주기 ──
    print()
    print("2단계: 팀에 리뷰 태스크 배정 중...")

    await team.create_tasks([
        {"title": "보안 리뷰", "description": "코드 보안 취약점 분석", "priority": 10},
        {"title": "성능 리뷰", "description": "성능 병목 분석", "priority": 8},
        {"title": "품질 리뷰", "description": "코드 품질 및 패턴 분석", "priority": 6},
    ])

    # ── 3단계: 실행 ──
    print()
    print("3단계: 팀이 병렬로 작업 중...")
    print()

    result = await team.run_team("코드 종합 리뷰", auto_plan=False)

    # ── 결과 출력 ──
    print("=" * 50)
    print("  결과")
    print("=" * 50)

    for r in result["results"]:
        icon = "O" if r.success else "X"
        print(f"\n  [{icon}] {r.agent_name}")
        print(f"  {'-' * 40}")
        data = r.data if r.success else r.error
        for line in str(data).split("\n"):
            print(f"    {line}")

    print()
    print("=" * 50)
    print("  종합 의견")
    print("=" * 50)
    for line in result["synthesis"].split("\n"):
        print(f"    {line}")

    # ── 4단계: 토론 ──
    print()
    print("=" * 50)
    print("  보너스: 보안 전문가 vs 반론 전문가 토론")
    print("=" * 50)

    disc = Discussion(
        presenter=SecurityReviewerAgent(name="보안전문가"),
        critic=DevilsAdvocateAgent(name="반론전문가"),
        rounds=1,
    )

    debate = await disc.run("프레임워크 보안 검증")

    for turn in debate.turns:
        role_name = {
            "analysis": "분석",
            "challenge": "반론",
            "response": "대응",
        }.get(turn.role, turn.role)

        print(f"\n  [{role_name}] {turn.speaker}:")
        for line in turn.content.split("\n"):
            print(f"    {line}")

    print(f"\n  [합의]:")
    for line in debate.consensus.split("\n"):
        print(f"    {line}")

    # 정리
    await team.cleanup()
    configure()

    print()
    print("=" * 50)
    print("  데모 완료!")
    print()
    print("  이게 Übermensch 프레임워크입니다.")
    print("  AI 에이전트들이 팀으로 협업하는 구조.")
    print()
    print("  실제 LLM을 쓰려면:")
    print("    export ANTHROPIC_API_KEY='sk-ant-...'")
    print("    그 후 같은 코드 실행하면 진짜 AI가 답변합니다.")
    print("=" * 50)
    print()


if __name__ == "__main__":
    asyncio.run(main())
