#!/usr/bin/env python3
"""
에이전트 자기정교화 시스템 (Agent Self-Refinement System)

에이전트들이 서로 토론하고, 비평하고, 개선하여
스스로 작업을 정교화하고 발전시키는 시스템.

사용법:
    # 단일 태스크 실행 (토론 + 정교화)
    python main.py run "API 서버의 인증 시스템을 설계하라"

    # 태스크 큐에 추가
    python main.py add "로깅 시스템 개선" --priority high

    # 감시 모드 (할 일이 생기면 자동 실행)
    python main.py watch

    # 대화형 모드
    python main.py interactive
"""

import argparse
import logging
import signal
import sys
import uuid

from agents.roles import get_default_team, get_full_team, ROLE_PRESETS
from config.settings import SystemConfig, DebateConfig, RefinementConfig, TaskWatcherConfig
from core.debate import DebateArena
from core.refinement import RefinementLoop
from tasks.watcher import TaskWatcher, TaskQueue, Task, TaskPriority

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ubermensch")


def create_config() -> SystemConfig:
    """시스템 설정 생성"""
    return SystemConfig(
        debate=DebateConfig(
            max_rounds=5,
            consensus_threshold=0.8,
            enable_voting=True,
        ),
        refinement=RefinementConfig(
            max_iterations=3,
            quality_threshold=0.85,
            auto_apply=False,
        ),
        task_watcher=TaskWatcherConfig(
            watch_paths=["./tasks/queue"],
            poll_interval_seconds=10,
            enabled=True,
        ),
    )


def run_single_task(task: str, use_full_team: bool = False, refine: bool = True):
    """단일 태스크 실행"""
    config = create_config()

    if not config.api_key:
        logger.error("ANTHROPIC_API_KEY 환경변수를 설정하세요.")
        sys.exit(1)

    team = get_full_team() if use_full_team else get_default_team()
    logger.info(f"팀 구성: {[a.name for a in team]}")

    if refine:
        loop = RefinementLoop(config, team)
        result = loop.run(task)
        print("\n" + "=" * 60)
        print("최종 결과")
        print("=" * 60)
        print(f"반복 횟수: {result.total_iterations}")
        print(f"품질 점수: {result.final_quality:.2f}")
        print(f"수렴 여부: {'예' if result.converged else '아니오'}")
        print("-" * 60)
        print(result.final_output)
    else:
        arena = DebateArena(config, team)
        result = arena.run(task)
        print("\n" + "=" * 60)
        print("토론 결과")
        print("=" * 60)
        print(f"라운드: {result.rounds}")
        print(f"합의 점수: {result.consensus_score:.2f}")
        print(f"승인 여부: {'예' if result.approved else '아니오'}")
        print("-" * 60)
        print(result.final_proposal)
        print("-" * 60)
        print("요약:", result.summary)


def add_task(title: str, description: str = "", priority: str = "medium"):
    """태스크 큐에 추가"""
    queue = TaskQueue()
    task = Task(
        id=str(uuid.uuid4())[:8],
        title=title,
        description=description or title,
        priority=TaskPriority(priority),
    )
    filepath = queue.add_task(task)
    print(f"태스크 추가됨: {task.id} -> {filepath}")


def watch_mode():
    """감시 모드 - 할 일이 생기면 자동 실행"""
    config = create_config()

    if not config.api_key:
        logger.error("ANTHROPIC_API_KEY 환경변수를 설정하세요.")
        sys.exit(1)

    def on_task(task: Task):
        """태스크 처리 콜백"""
        team_configs = get_default_team()

        # 태스크에 팀 지정이 있으면 해당 역할만 사용
        if task.team:
            team_configs = [
                ROLE_PRESETS[role]
                for role in task.team
                if role in ROLE_PRESETS
            ] or get_default_team()

        loop = RefinementLoop(config, team_configs)
        result = loop.run(task.description)

        logger.info(
            f"태스크 '{task.title}' 완료 - "
            f"품질: {result.final_quality:.2f}, "
            f"수렴: {result.converged}"
        )
        return result.final_output

    watcher = TaskWatcher(config.task_watcher, on_task)

    # Ctrl+C로 종료
    def signal_handler(sig, frame):
        print("\n감시 모드 종료...")
        watcher.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    print("감시 모드 시작. 태스크를 ./tasks/queue/ 에 추가하세요.")
    print("종료: Ctrl+C")
    watcher.start()


def interactive_mode():
    """대화형 모드"""
    config = create_config()

    if not config.api_key:
        logger.error("ANTHROPIC_API_KEY 환경변수를 설정하세요.")
        sys.exit(1)

    print("=" * 60)
    print("에이전트 자기정교화 시스템 - 대화형 모드")
    print("=" * 60)
    print("명령어:")
    print("  토론할 내용을 입력하세요")
    print("  'team full' - 전체 팀(6명) 사용")
    print("  'team default' - 기본 팀(4명) 사용")
    print("  'quit' - 종료")
    print("-" * 60)

    use_full_team = False

    while True:
        try:
            user_input = input("\n주제> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료합니다.")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            break
        if user_input.lower() == "team full":
            use_full_team = True
            print("전체 팀(6명)으로 변경됨")
            continue
        if user_input.lower() == "team default":
            use_full_team = False
            print("기본 팀(4명)으로 변경됨")
            continue

        run_single_task(user_input, use_full_team=use_full_team)


def main():
    parser = argparse.ArgumentParser(
        description="에이전트 자기정교화 시스템 (Agent Self-Refinement System)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", help="실행할 명령")

    # run 명령
    run_parser = subparsers.add_parser("run", help="단일 태스크 실행")
    run_parser.add_argument("task", help="처리할 태스크 설명")
    run_parser.add_argument(
        "--full-team", action="store_true", help="전체 팀(6명) 사용"
    )
    run_parser.add_argument(
        "--no-refine", action="store_true", help="정교화 루프 없이 토론만 실행"
    )

    # add 명령
    add_parser = subparsers.add_parser("add", help="태스크 큐에 추가")
    add_parser.add_argument("title", help="태스크 제목")
    add_parser.add_argument("--description", "-d", default="", help="상세 설명")
    add_parser.add_argument(
        "--priority", "-p",
        choices=["low", "medium", "high", "critical"],
        default="medium",
        help="우선순위",
    )

    # watch 명령
    subparsers.add_parser("watch", help="감시 모드 (자동 실행)")

    # interactive 명령
    subparsers.add_parser("interactive", help="대화형 모드")

    args = parser.parse_args()

    if args.command == "run":
        run_single_task(
            args.task,
            use_full_team=args.full_team,
            refine=not args.no_refine,
        )
    elif args.command == "add":
        add_task(args.title, args.description, args.priority)
    elif args.command == "watch":
        watch_mode()
    elif args.command == "interactive":
        interactive_mode()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
