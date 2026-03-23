from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class NCSProblem:
    number: str
    page: int
    category: str
    question: str
    choices: list[str] = field(default_factory=list)
    answer: str | None = None
    explanation: str | None = None
    source_file: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class NCSDocument:
    source_file: str
    problems: list[NCSProblem]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_file": self.source_file,
            "problem_count": len(self.problems),
            "problems": [problem.to_dict() for problem in self.problems],
        }
