"""URL → 플랫폼 디스패치 로직 검증."""

from __future__ import annotations

import pytest

from insane_search.router import detect_platform


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://twitter.com/jack/status/20", "twitter"),
        ("https://x.com/sama/status/1800000000000000000", "twitter"),
        ("https://mobile.twitter.com/foo/status/123", "twitter"),
        # 프로필 URL 은 트윗이 아니므로 twitter 전략 대상이 아님
        ("https://x.com/sama", "generic"),
        ("https://www.reddit.com/r/python/comments/abc123/some_title/", "reddit"),
        ("https://old.reddit.com/r/LocalLLaMA/comments/xyz/", "reddit"),
        ("https://reddit.com/r/python", "reddit"),
        ("https://stackoverflow.com/questions/12345/how-do-i", "stackoverflow"),
        ("https://serverfault.com/questions/999/why", "stackoverflow"),
        ("https://math.stackexchange.com/questions/1/foo", "stackoverflow"),
        ("https://blog.naver.com/someblog/223000000000", "naver"),
        ("https://m.blog.naver.com/someblog/223000000000", "naver"),
        (
            "https://blog.naver.com/PostView.naver?blogId=x&logNo=123",
            "naver",
        ),
        ("https://example.com/some/page", "generic"),
    ],
)
def test_detect_platform(url: str, expected: str) -> None:
    assert detect_platform(url) == expected
