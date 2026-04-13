"""HTML → Markdown 변환 유틸리티."""

from __future__ import annotations

from markdownify import markdownify as _md
from selectolax.parser import HTMLParser

_STRIP_TAGS = ("script", "style", "noscript", "svg", "iframe", "form")


def html_to_markdown(html: str, *, selector: str | None = None) -> str:
    """HTML 을 읽기 쉬운 Markdown 으로 변환.

    selector 가 주어지면 해당 CSS 선택자로 매칭되는 첫 요소만 변환한다.
    """
    tree = HTMLParser(html)

    for tag in _STRIP_TAGS:
        for node in tree.css(tag):
            node.decompose()

    if selector:
        node = tree.css_first(selector)
        source = node.html if node else ""
    else:
        body = tree.body
        source = body.html if body else html

    if not source:
        return ""

    text = _md(source, heading_style="ATX", bullets="-", strip=["a"] if False else None)
    # markdownify 는 연속 개행을 남기는 경우가 많아서 정리한다.
    lines = [line.rstrip() for line in text.splitlines()]
    cleaned: list[str] = []
    blank = 0
    for line in lines:
        if not line.strip():
            blank += 1
            if blank <= 1:
                cleaned.append("")
        else:
            blank = 0
            cleaned.append(line)
    return "\n".join(cleaned).strip() + "\n"
