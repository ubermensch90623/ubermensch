"""HTML → Markdown 유틸 검증."""

from __future__ import annotations

from insane_search.markdown import html_to_markdown


def test_strips_scripts_and_styles() -> None:
    html = """
    <html><body>
      <script>alert('x')</script>
      <style>.a{color:red}</style>
      <h1>Title</h1>
      <p>hello <b>world</b></p>
    </body></html>
    """
    md = html_to_markdown(html)
    assert "alert" not in md
    assert "color:red" not in md
    assert "# Title" in md
    assert "hello" in md


def test_selector_scope() -> None:
    html = """
    <html><body>
      <div class="sidebar"><p>noise</p></div>
      <article class="post"><h2>Real</h2><p>content</p></article>
    </body></html>
    """
    md = html_to_markdown(html, selector="article.post")
    assert "noise" not in md
    assert "Real" in md
    assert "content" in md


def test_collapses_blank_lines() -> None:
    html = "<p>a</p><p>b</p><p>c</p>"
    md = html_to_markdown(html)
    # 연속 빈 줄이 2개 이상 나오면 안 된다.
    assert "\n\n\n" not in md
