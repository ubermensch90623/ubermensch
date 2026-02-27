"""Learning Agent Corp. 1차 채용 실행 예제

배관공(PlumberAgent)과 데이터 검증관(DataRedTeamAgent)을 채용하고
데이터팀을 구성하여 Keep 노트 파싱 파이프라인을 시연합니다.

CEO 메모: "데이터 없으면 전사 마비" - 1차 채용 최우선순위

사용법:
    export ANTHROPIC_API_KEY="your-api-key"
    python examples/corp_first_hire.py
"""

import asyncio
import logging

from ubermensch.agents.corp.organization import LearningAgentCorp
from ubermensch.core.message import AgentMessage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


# 샘플 Keep 노트 데이터
SAMPLE_KEEP_NOTES = [
    {
        "id": 1,
        "text": (
            "NCS 수리 - 비율 문제\n"
            "문제: A회사와 B회사의 매출 비율이 3:5이고, "
            "B회사와 C회사의 매출 비율이 2:3일 때, "
            "A회사와 C회사의 매출 비율은?\n"
            "내 답: 2:5 (틀림)\n"
            "정답: 2:5... 맞았는데? 아 3:5 * 2:3 = 6:15 = 2:5 맞네\n"
            "근데 실전에서 비율 연결 실수함"
        ),
    },
    {
        "id": 2,
        "text": (
            "경제학 - 수요탄력성\n"
            "가격이 10% 올랐는데 수요가 5% 줄면 탄력성 = 0.5 (비탄력적)\n"
            "헷갈리는 점: 탄력성이 1보다 작으면 비탄력적\n"
            "실수: 공식에 절댓값 안 씌워서 음수로 계산함"
        ),
    },
    {
        "id": 3,
        "text": (
            "NCS 언어 - 빈칸 추론\n"
            "지문에서 접속사 찾기가 핵심\n"
            "'그러나' 뒤에 필자 주장 옴\n"
            "오답 이유: 선지 3번이 지문 내용 그대로인데 "
            "필자 주장이 아니라 배경 설명이었음"
        ),
    },
]


async def main():
    print("=" * 60)
    print("Learning Agent Corp. — 1차 채용 실행")
    print("=" * 60)

    # 1. 조직 생성
    corp = LearningAgentCorp()
    print(f"\n조직 생성 완료")

    # 2. 1차 채용: 배관공 + 데이터 검증관
    wave1 = corp.hire_wave(1)
    print(f"\n1차 채용 완료: {[a.name for a in wave1]}")

    # 3. 현재 조직 현황
    print(f"\n{corp.status()}")

    # 4. 데이터팀 빌드 (리더 + 레드팀만으로 최소 팀 구성)
    from ubermensch.agents.corp.organization import TEAM_CONFIGS

    data_team_config = TEAM_CONFIGS[0]  # 데이터팀
    data_team = corp.build_team(data_team_config)

    if data_team is None:
        print("데이터팀 빌드 실패")
        return

    print(f"\n데이터팀 빌드 완료: {data_team.teammate_names}")

    # 5. 배관공에게 노트 파싱 파이프라인 작업 지시
    plumber = corp.get_agent("plumber")
    if plumber is None:
        print("배관공 없음")
        return

    print("\n" + "=" * 60)
    print("배관공: Keep 노트 파이프라인 설계")
    print("=" * 60)

    pipeline_result = await plumber.run(
        AgentMessage(
            task="Keep 노트 3개를 Notion DB로 이관하기 위한 파이프라인을 설계해주세요.",
            context={
                "notes": SAMPLE_KEEP_NOTES,
                "pipeline_status": "초기 구축 단계",
            },
        )
    )

    if pipeline_result.success:
        print(pipeline_result.data)
    else:
        print(f"실패: {pipeline_result.error}")

    # 6. 레드팀이 파이프라인 설계 검증
    redteam = corp.get_agent("data_redteam")
    if redteam is None:
        print("데이터 검증관 없음")
        return

    print("\n" + "=" * 60)
    print("데이터 검증관: 파이프라인 설계 검증")
    print("=" * 60)

    verification_result = await redteam.run(
        AgentMessage(
            task="배관공의 파이프라인 설계를 검증해주세요.",
            context={
                "work_item": pipeline_result.data,
                "work_type": "pipeline_design",
            },
        )
    )

    if verification_result.success:
        print(verification_result.data)
    else:
        print(f"실패: {verification_result.error}")

    # 7. 팀 실행 (자동 태스크 분배)
    print("\n" + "=" * 60)
    print("데이터팀 협업: 샘플 노트 처리")
    print("=" * 60)

    team_result = await data_team.run_team(
        user_request=(
            "다음 3개의 Keep 노트를 파싱하고 검증해주세요:\n"
            + "\n---\n".join(note["text"] for note in SAMPLE_KEEP_NOTES)
        ),
    )

    print("\n[팀 종합 결과]")
    print(team_result["synthesis"])

    # 정리
    await data_team.cleanup()
    print("\n데이터팀 정리 완료")
    print(f"\n최종 조직 현황:\n{corp.status()}")


if __name__ == "__main__":
    asyncio.run(main())
