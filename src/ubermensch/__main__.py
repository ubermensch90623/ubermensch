"""Learning Agent Corp. CLI 진입점.

사용법:
    python -m ubermensch              # 대화형 모드 (기본)
    python -m ubermensch status       # 조직 현황
    python -m ubermensch hire 1       # 1차 채용
    python -m ubermensch hire-all     # 전체 채용
    python -m ubermensch save         # 상태 저장
    python -m ubermensch restore      # 상태 복원
    python -m ubermensch run <요청>   # 단일 요청 실행
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from ubermensch.agents.corp.organization import LearningAgentCorp, TEAM_CONFIGS
from ubermensch.core.message import AgentMessage
from ubermensch.core.persistence import save_corp_state, restore_corp

DEFAULT_STATE_PATH = Path("corp_state.json")

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)


def _print_banner() -> None:
    print("=" * 50)
    print("  Learning Agent Corp.  —  Übermensch v0.2")
    print("  NCS + 경제학 시험 준비 AI 에이전트 조직")
    print("=" * 50)


def _load_or_create(state_path: Path) -> tuple[LearningAgentCorp, bool]:
    """저장된 상태가 있으면 복원, 없으면 새로 생성."""
    if state_path.exists():
        corp = restore_corp(state_path)
        return corp, True
    return LearningAgentCorp(), False


def cmd_status(args: argparse.Namespace) -> None:
    """조직 현황 출력."""
    corp, restored = _load_or_create(Path(args.state))
    if restored:
        print(f"[저장된 상태에서 복원: {args.state}]\n")
    else:
        print("[새 조직 (저장된 상태 없음)]\n")
    print(corp.status())


def cmd_hire(args: argparse.Namespace) -> None:
    """특정 차수 채용."""
    state_path = Path(args.state)
    corp, restored = _load_or_create(state_path)
    if restored:
        print(f"[저장된 상태에서 복원: {args.state}]")

    wave = args.wave
    print(f"\n{wave}차 채용 실행 중...")
    hired = corp.hire_wave(wave)
    if hired:
        print(f"채용 완료: {[a.name for a in hired]}")
    else:
        print("채용할 에이전트가 없습니다 (이미 채용됨 또는 유효하지 않은 차수)")

    save_corp_state(corp, state_path)
    print(f"\n상태 저장 완료: {state_path}")
    print(f"\n{corp.status()}")


def cmd_hire_all(args: argparse.Namespace) -> None:
    """전체 채용."""
    state_path = Path(args.state)
    corp, restored = _load_or_create(state_path)

    print("전체 채용 실행 중...")
    hired = corp.hire_all()
    print(f"채용 완료: {len(hired)}명")

    corp.build_all_teams()
    print(f"팀 빌드 완료: {len(TEAM_CONFIGS)}개 팀")

    save_corp_state(corp, state_path)
    print(f"\n상태 저장 완료: {state_path}")
    print(f"\n{corp.status()}")


def cmd_save(args: argparse.Namespace) -> None:
    """현재 상태 저장."""
    state_path = Path(args.state)
    corp, restored = _load_or_create(state_path)
    if not restored:
        print("저장할 상태가 없습니다. 먼저 hire 또는 hire-all을 실행하세요.")
        return
    save_corp_state(corp, state_path)
    print(f"상태 저장 완료: {state_path} ({corp.headcount}명)")


def cmd_restore(args: argparse.Namespace) -> None:
    """저장된 상태 복원."""
    state_path = Path(args.state)
    if not state_path.exists():
        print(f"상태 파일을 찾을 수 없습니다: {state_path}")
        sys.exit(1)
    corp = restore_corp(state_path)
    print(f"조직 복원 완료: {corp.headcount}명")
    print(f"\n{corp.status()}")


def cmd_run(args: argparse.Namespace) -> None:
    """단일 요청 실행."""
    state_path = Path(args.state)
    corp, restored = _load_or_create(state_path)

    if corp.headcount == 0:
        print("에이전트가 없습니다. 먼저 채용하세요:")
        print("  python -m ubermensch hire-all")
        sys.exit(1)

    request = " ".join(args.request)
    if not request:
        print("요청을 입력하세요:")
        print("  python -m ubermensch run '오늘 공부할 내용을 정해줘'")
        sys.exit(1)

    ceo = corp.get_agent("ceo")
    if ceo is None:
        # CEO가 없으면 첫 번째 에이전트에게 전달
        agent_name = corp.agent_names[0]
        agent = corp.get_agent(agent_name)
        print(f"[CEO 미배치 — '{agent_name}'에게 전달]\n")
    else:
        agent = ceo
        print(f"[CEO에게 전달]\n")

    async def _run() -> None:
        result = await agent.run(
            AgentMessage(task=request, context={"mode": "cli"})
        )
        if result.success:
            print(result.data)
        else:
            print(f"실패: {result.error}")

    asyncio.run(_run())


def cmd_interactive(args: argparse.Namespace) -> None:
    """대화형 모드."""
    _print_banner()
    state_path = Path(args.state)
    corp, restored = _load_or_create(state_path)

    if restored:
        print(f"\n저장된 조직 복원 완료 ({corp.headcount}명)")
    else:
        print("\n새 조직을 시작합니다.")
        print("전체 에이전트를 채용합니다...")
        corp.hire_all()
        corp.build_all_teams()
        save_corp_state(corp, state_path)
        print(f"채용 완료: {corp.headcount}명, 상태 저장: {state_path}")

    print(f"\n{corp.status()}")
    print("\n" + "-" * 50)
    print("명령어:")
    print("  <요청>       CEO에게 요청 전달")
    print("  /status      조직 현황")
    print("  /save        상태 저장")
    print("  /quit        종료")
    print("-" * 50)

    ceo = corp.get_agent("ceo")
    if ceo is None:
        print("경고: CEO가 배치되지 않았습니다.")
        return

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료합니다.")
            save_corp_state(corp, state_path)
            break

        if not user_input:
            continue

        if user_input == "/quit":
            print("상태 저장 중...")
            save_corp_state(corp, state_path)
            print("종료합니다.")
            break

        if user_input == "/status":
            print(f"\n{corp.status()}")
            continue

        if user_input == "/save":
            save_corp_state(corp, state_path)
            print(f"저장 완료: {state_path}")
            continue

        # CEO에게 요청 전달
        async def _ask(request: str) -> None:
            result = await ceo.run(
                AgentMessage(task=request, context={"mode": "interactive"})
            )
            if result.success:
                print(f"\n{result.data}")
            else:
                print(f"\n실패: {result.error}")

        asyncio.run(_ask(user_input))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ubermensch",
        description="Learning Agent Corp. — NCS+경제학 AI 에이전트 조직",
    )
    parser.add_argument(
        "--state",
        default=str(DEFAULT_STATE_PATH),
        help=f"상태 파일 경로 (기본값: {DEFAULT_STATE_PATH})",
    )

    subparsers = parser.add_subparsers(dest="command")

    # today
    subparsers.add_parser("today", help="오늘의 학습 플랜")

    # status
    subparsers.add_parser("status", help="조직 현황 출력")

    # hire
    hire_parser = subparsers.add_parser("hire", help="특정 차수 채용 (1~7)")
    hire_parser.add_argument("wave", type=int, help="채용 차수 (1~7)")

    # hire-all
    subparsers.add_parser("hire-all", help="전체 에이전트 채용")

    # save
    subparsers.add_parser("save", help="상태 저장")

    # restore
    subparsers.add_parser("restore", help="저장된 상태 복원 + 현황 출력")

    # run
    run_parser = subparsers.add_parser("run", help="단일 요청 실행")
    run_parser.add_argument("request", nargs="+", help="CEO에게 전달할 요청")

    # autopilot
    auto_parser = subparsers.add_parser("auto", help="자율 운영 모드 (오토파일럿)")
    auto_parser.add_argument("--cycles", type=int, default=1, help="실행 사이클 수")

    # pipeline
    pipe_parser = subparsers.add_parser("pipeline", help="Keep 노트 데이터 파이프라인")
    pipe_sub = pipe_parser.add_subparsers(dest="pipe_command")

    pipe_dir = pipe_sub.add_parser("from-keep", help="Keep Takeout 디렉토리에서 파싱")
    pipe_dir.add_argument("path", help="Keep Takeout 디렉토리 경로")
    pipe_dir.add_argument("-o", "--output", default="notes.json", help="출력 파일")

    pipe_text = pipe_sub.add_parser("from-text", help="텍스트 파일에서 파싱")
    pipe_text.add_argument("path", help="텍스트 파일 경로")
    pipe_text.add_argument("-o", "--output", default="notes.json", help="출력 파일")

    pipe_sub.add_parser("stats", help="저장된 노트 통계")

    # quiz
    quiz_parser = subparsers.add_parser("quiz", help="퀴즈 생성")
    quiz_parser.add_argument("-n", "--count", type=int, default=5, help="문항 수")
    quiz_parser.add_argument("--focus", default="", help="집중 영역 (수리, 미시 등)")
    quiz_parser.add_argument("--answers", action="store_true", help="정답 표시")
    quiz_parser.add_argument("--notes", default="notes.json", help="노트 파일")

    args = parser.parse_args()

    commands = {
        "status": cmd_status,
        "hire": cmd_hire,
        "hire-all": cmd_hire_all,
        "save": cmd_save,
        "restore": cmd_restore,
        "run": cmd_run,
    }

    if args.command is None:
        # 기본: 대화형 모드
        cmd_interactive(args)
    elif args.command == "today":
        from ubermensch.daily_plan import generate_daily_plan
        print(generate_daily_plan())
    elif args.command == "auto":
        from ubermensch.autopilot import Autopilot
        pilot = Autopilot(state_path=args.state)
        asyncio.run(pilot.run(cycles=args.cycles))
    elif args.command == "quiz":
        from ubermensch.data.quiz import QuizGenerator
        gen = QuizGenerator()
        count = gen.load_notes(args.notes)
        if count == 0:
            print("퀴즈 소스 노트가 없습니다.")
            print("먼저 파이프라인을 실행하세요: python -m ubermensch pipeline from-keep <경로>")
            sys.exit(1)
        quiz = gen.generate(count=args.count, focus_area=args.focus)
        print(quiz.render(show_answers=args.answers))
    elif args.command == "pipeline":
        from ubermensch.data.pipeline import DataPipeline
        from ubermensch.data.note import load_notes
        pipeline = DataPipeline()
        if args.pipe_command == "from-keep":
            results = pipeline.run_from_directory(args.path)
            pipeline.save_results(args.output)
            print(pipeline.stats.summary())
            print(f"\n저장 완료: {args.output} ({len(results)}개 노트)")
        elif args.pipe_command == "from-text":
            text = Path(args.path).read_text(encoding="utf-8")
            results = pipeline.run_from_text(text)
            pipeline.save_results(args.output)
            print(pipeline.stats.summary())
            print(f"\n저장 완료: {args.output} ({len(results)}개 노트)")
        elif args.pipe_command == "stats":
            if not Path("notes.json").exists():
                print("notes.json 파일이 없습니다. 먼저 pipeline from-keep 을 실행하세요.")
            else:
                notes = load_notes("notes.json")
                from collections import Counter
                cats = Counter(n.category.value for n in notes)
                types = Counter(n.note_type.value for n in notes)
                print(f"총 노트: {len(notes)}개")
                print(f"\n카테고리: {dict(cats)}")
                print(f"유형: {dict(types)}")
                verified = sum(1 for n in notes if n.verified)
                print(f"검수 완료: {verified}/{len(notes)}")
        else:
            pipe_parser.print_help()
    elif args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
