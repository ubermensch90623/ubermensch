"""시스템 설정 - 에이전트 자기정교화 시스템 구성"""

import os
from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    """개별 에이전트 설정"""
    name: str
    role: str
    perspective: str
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 4096
    temperature: float = 0.7


@dataclass
class DebateConfig:
    """토론 엔진 설정"""
    max_rounds: int = 5
    consensus_threshold: float = 0.8  # 합의 도달 기준 (0~1)
    min_agents: int = 2
    max_agents: int = 6
    enable_voting: bool = True


@dataclass
class RefinementConfig:
    """정교화 루프 설정"""
    max_iterations: int = 3
    quality_threshold: float = 0.85  # 품질 기준 도달 시 중단
    auto_apply: bool = False  # 자동 적용 여부 (사람 승인 필요 시 False)


@dataclass
class TaskWatcherConfig:
    """태스크 감시 설정"""
    watch_paths: list[str] = field(default_factory=lambda: ["./tasks/queue"])
    poll_interval_seconds: int = 10
    enabled: bool = True


@dataclass
class SystemConfig:
    """전체 시스템 설정"""
    api_key: str = field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", ""))
    debate: DebateConfig = field(default_factory=DebateConfig)
    refinement: RefinementConfig = field(default_factory=RefinementConfig)
    task_watcher: TaskWatcherConfig = field(default_factory=TaskWatcherConfig)
    log_debates: bool = True
    log_dir: str = "./logs"
