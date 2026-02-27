"""팀 설정 영속화 - JSON 파일로 조직 상태 저장/복원.

LearningAgentCorp의 채용 상태, 팀 구성, TF 이력을
JSON 파일로 저장하고 복원합니다.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_STATE_FILE = "corp_state.json"


def save_corp_state(
    corp: Any,
    path: str | Path = DEFAULT_STATE_FILE,
) -> Path:
    """조직 상태를 JSON 파일로 저장합니다.

    저장 내용:
        - 채용된 에이전트 목록 (이름 + 모델)
        - 팀 빌드 상태
        - TF 이력

    Args:
        corp: LearningAgentCorp 인스턴스
        path: 저장 경로

    Returns:
        저장된 파일 경로
    """
    file_path = Path(path)

    # 채용된 에이전트 정보
    agents_data: list[dict[str, str]] = []
    for name, agent in corp._agents.items():
        agents_data.append({
            "name": agent.name,
            "model": agent.model,
            "class": type(agent).__name__,
        })

    # TF 이력
    tf_records: list[dict[str, Any]] = []
    for name, record in corp.tf_manager._task_forces.items():
        tf_records.append({
            "name": record.name,
            "problem": record.problem,
            "leader": record.leader,
            "members": record.members,
            "goal": record.goal,
            "created_at": record.created_at,
            "resolved_at": record.resolved_at,
            "result": record.result,
            "lessons": record.lessons,
        })

    state = {
        "version": 1,
        "model": corp.model,
        "deployed_agents": agents_data,
        "task_force_history": tf_records,
    }

    file_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    logger.info(f"Corp state saved to {file_path} ({len(agents_data)} agents)")
    return file_path


def load_corp_state(
    path: str | Path = DEFAULT_STATE_FILE,
) -> dict[str, Any]:
    """JSON 파일에서 조직 상태를 로드합니다.

    Args:
        path: 파일 경로

    Returns:
        파싱된 상태 딕셔너리

    Raises:
        FileNotFoundError: 파일이 없을 때
        json.JSONDecodeError: JSON 파싱 실패 시
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"State file not found: {file_path}")

    state = json.loads(file_path.read_text())
    logger.info(
        f"Corp state loaded from {file_path} "
        f"({len(state.get('deployed_agents', []))} agents)"
    )
    return state


def restore_corp(
    path: str | Path = DEFAULT_STATE_FILE,
) -> Any:
    """JSON 파일에서 LearningAgentCorp를 복원합니다.

    Args:
        path: 상태 파일 경로

    Returns:
        복원된 LearningAgentCorp 인스턴스
    """
    # 순환 import 방지
    from ubermensch.agents.corp.organization import (
        LearningAgentCorp,
        _get_agent_factory,
    )
    from ubermensch.agents.corp.task_force import TaskForceRecord

    state = load_corp_state(path)
    model = state.get("model", "claude-sonnet-4-20250514")
    corp = LearningAgentCorp(model=model)

    # 에이전트 복원
    factory = _get_agent_factory()
    for agent_data in state.get("deployed_agents", []):
        name = agent_data["name"]
        agent_model = agent_data.get("model", model)
        create = factory.get(name)
        if create:
            agent = create(agent_model)
            corp.hire(agent)
        else:
            logger.warning(f"Agent '{name}' not found in factory, skipping")

    # TF 이력 복원
    for tf_data in state.get("task_force_history", []):
        record = TaskForceRecord(
            name=tf_data["name"],
            problem=tf_data["problem"],
            leader=tf_data["leader"],
            members=tf_data["members"],
            goal=tf_data["goal"],
            created_at=tf_data["created_at"],
            resolved_at=tf_data.get("resolved_at"),
            result=tf_data.get("result"),
            lessons=tf_data.get("lessons"),
        )
        corp.tf_manager._task_forces[record.name] = record

    logger.info(f"Corp restored: {corp.headcount} agents")
    return corp
