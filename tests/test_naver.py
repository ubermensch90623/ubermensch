"""Naver 블로그 URL 파서 검증."""

from __future__ import annotations

from insane_search.platforms.naver import _extract_ids, is_naver_blog


def test_extract_ids() -> None:
    assert _extract_ids("https://blog.naver.com/someblog/223000000000") == (
        "someblog",
        "223000000000",
    )
    assert _extract_ids("https://m.blog.naver.com/someblog/223000000000") == (
        "someblog",
        "223000000000",
    )
    assert _extract_ids(
        "https://blog.naver.com/PostView.naver?blogId=x&logNo=42"
    ) == ("x", "42")
    assert _extract_ids("https://blog.naver.com/someblog") is None
    assert _extract_ids("https://example.com/someblog/123") is None


def test_is_naver_blog() -> None:
    assert is_naver_blog("https://blog.naver.com/a/1")
    assert not is_naver_blog("https://twitter.com/a/status/1")
