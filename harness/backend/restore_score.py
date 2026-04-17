"""restore_score — 복원률 매트릭스 (기관 × NCS영역/과목).

입력: data/restored/c0_passed.jsonl (C-0 통과 claim 만)
출력: {agency: {area: {"restored": N, "target": M, "rate": ratio}}}

북극성: 복원률 90%+. 히트맵 색상 색인은 UI 측에서:
  rate >= 0.90 → green / 0.70-0.89 → yellow / < 0.70 → red
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List


# 목표 분포 (기관별 영역·문항수) — 격리 해제된 팩트로만 채워져야 함.
# CLAUDE.md 캠코 수치는 현재 격리 중이므로 placeholder 로 수협 + NCS 일반 만.
# 사용자 B2 해소 후 공식 PDF 기반 재설정.
TARGET_DISTRIBUTION: Dict[str, Dict[str, int]] = {
    "캠코": {
        # 격리 중 — 공식 PDF 재확인 후 설정
        "_quarantine_note": 1,
    },
    "수협": {
        "NCS": 0,           # 선택과목 + NCS 구성, 세부 배점 미확인 (격리)
        "선택과목": 0,
        "_quarantine_note": 1,
    },
}


@dataclass
class CellScore:
    restored: int = 0
    target: int = 0

    @property
    def rate(self) -> float:
        return (self.restored / self.target) if self.target else 0.0

    def to_dict(self) -> dict:
        return {"restored": self.restored, "target": self.target, "rate": self.rate}


@dataclass
class AgencyMatrix:
    agency: str
    cells: Dict[str, CellScore] = field(default_factory=dict)

    @property
    def total_restored(self) -> int:
        return sum(c.restored for c in self.cells.values())

    @property
    def total_target(self) -> int:
        return sum(c.target for c in self.cells.values())

    @property
    def overall_rate(self) -> float:
        return (
            self.total_restored / self.total_target if self.total_target else 0.0
        )

    def to_dict(self) -> dict:
        return {
            "agency": self.agency,
            "cells": {k: v.to_dict() for k, v in self.cells.items()},
            "total_restored": self.total_restored,
            "total_target": self.total_target,
            "overall_rate": self.overall_rate,
        }


def load_restored(path: Path) -> List[dict]:
    if not path.exists():
        return []
    records: List[dict] = []
    with path.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def _detect_agency(rec: dict) -> str:
    for key in ("agency", "기관", "target_agency"):
        v = rec.get(key)
        if v:
            return str(v)
    return "미분류"


def _detect_area(rec: dict) -> str:
    for key in ("area", "영역", "subject", "subtype"):
        v = rec.get(key)
        if v:
            return str(v)
    return "일반"


def build_matrix(
    records: Iterable[dict],
    target: Dict[str, Dict[str, int]] = TARGET_DISTRIBUTION,
) -> Dict[str, AgencyMatrix]:
    matrices: Dict[str, AgencyMatrix] = {}
    for agency, areas in target.items():
        m = AgencyMatrix(agency=agency)
        for area, cnt in areas.items():
            if area.startswith("_"):
                continue
            m.cells[area] = CellScore(target=cnt)
        matrices[agency] = m
    for rec in records:
        agency = _detect_agency(rec)
        area = _detect_area(rec)
        if agency not in matrices:
            matrices[agency] = AgencyMatrix(agency=agency)
        cells = matrices[agency].cells
        if area not in cells:
            cells[area] = CellScore()
        cells[area].restored += 1
    return matrices


def summary_for_ui(matrices: Dict[str, AgencyMatrix]) -> dict:
    # SC2 지적(2026-04-18): CLAUDE.md 북극성 95% 와 정렬.
    return {
        "north_star_goal": 0.95,
        "agencies": [m.to_dict() for m in matrices.values()],
        "alerts": [
            {
                "agency": m.agency,
                "overall_rate": m.overall_rate,
                "level": (
                    "green" if m.overall_rate >= 0.90
                    else "yellow" if m.overall_rate >= 0.70
                    else "red"
                ),
            }
            for m in matrices.values()
        ],
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    records = load_restored(root / "data" / "restored" / "c0_passed.jsonl")
    matrices = build_matrix(records)
    print(json.dumps(summary_for_ui(matrices), ensure_ascii=False, indent=2))
