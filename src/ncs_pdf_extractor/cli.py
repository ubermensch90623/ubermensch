from __future__ import annotations

import argparse
from pathlib import Path

from .exporters import export_json, export_markdown
from .parser import extract_problems_from_pages
from .pdf_reader import extract_pages_from_pdf


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="PDF에서 NCS 문제를 추출해 JSON/Markdown으로 정리합니다."
    )
    parser.add_argument("input", nargs="+", help="PDF 파일 또는 PDF가 있는 디렉터리")
    parser.add_argument(
        "--output-dir",
        default="output",
        help="결과물을 저장할 디렉터리 (기본값: output)",
    )
    return parser


def resolve_pdf_files(inputs: list[str]) -> list[Path]:
    pdfs: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if path.is_dir():
            pdfs.extend(sorted(path.glob("*.pdf")))
        elif path.suffix.lower() == ".pdf":
            pdfs.append(path)
    return sorted(set(pdfs))


def main() -> None:
    args = build_parser().parse_args()
    pdf_files = resolve_pdf_files(args.input)

    if not pdf_files:
        raise SystemExit("처리할 PDF 파일을 찾지 못했습니다.")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for pdf_path in pdf_files:
        pages = extract_pages_from_pdf(pdf_path)
        document = extract_problems_from_pages(pages, source_file=str(pdf_path))
        stem = pdf_path.stem
        json_path = export_json(document, output_dir / f"{stem}.json")
        md_path = export_markdown(document, output_dir / f"{stem}.md")
        print(f"[완료] {pdf_path} -> {json_path}, {md_path}")


if __name__ == "__main__":
    main()
