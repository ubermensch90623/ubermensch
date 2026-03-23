from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


def extract_pages_from_pdf(pdf_path: str | Path) -> list[dict[str, str | int]]:
    """Return extracted plain text for each PDF page."""
    path = Path(pdf_path)
    reader = PdfReader(str(path))
    pages: list[dict[str, str | int]] = []

    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append(
            {
                "page": index,
                "text": text.replace("\x00", "").strip(),
            }
        )

    return pages
