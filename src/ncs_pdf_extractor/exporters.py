from __future__ import annotations

import json
from pathlib import Path

from .models import NCSDocument
from .parser import regroup_by_category


def export_json(document: NCSDocument, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "document": document.to_dict(),
        "by_category": regroup_by_category(document),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_markdown(document: NCSDocument, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# NCS 문제 정리 - {document.source_file}",
        "",
        f"- 총 문항 수: **{len(document.problems)}**",
        "",
    ]

    grouped = regroup_by_category(document)
    for category, problems in grouped.items():
        lines.extend([f"## {category}", ""])
        for problem in problems:
            lines.append(f"### {problem['number']} (p.{problem['page']})")
            lines.append(problem["question"])
            lines.append("")
            if problem["choices"]:
                lines.append("선택지:")
                for choice in problem["choices"]:
                    lines.append(f"- {choice}")
                lines.append("")
            if problem["answer"]:
                lines.append(f"정답: {problem['answer']}")
            if problem["explanation"]:
                lines.append(f"해설: {problem['explanation']}")
            lines.append("")

    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return path
