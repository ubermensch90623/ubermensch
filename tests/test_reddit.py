"""Reddit URL 파서 및 댓글 파싱 검증."""

from __future__ import annotations

import pytest

from insane_search.platforms.reddit import _parse_comment, parse_reddit_url


def test_parse_reddit_url() -> None:
    assert parse_reddit_url(
        "https://www.reddit.com/r/python/comments/abc123/some_title/"
    ) == ("post", "abc123")
    assert parse_reddit_url("https://old.reddit.com/r/python/comments/xyz/") == (
        "post",
        "xyz",
    )
    assert parse_reddit_url("https://www.reddit.com/comments/abc123/") == (
        "post",
        "abc123",
    )
    assert parse_reddit_url("https://www.reddit.com/r/python/") == ("sub", "python")
    assert parse_reddit_url("https://www.reddit.com/") == ("other", None)

    with pytest.raises(ValueError):
        parse_reddit_url("https://twitter.com/x")


def test_parse_comment_recursive() -> None:
    tree = {
        "kind": "t1",
        "data": {
            "author": "alice",
            "body": "hello",
            "score": 5,
            "replies": {
                "data": {
                    "children": [
                        {
                            "kind": "t1",
                            "data": {
                                "author": "bob",
                                "body": "hi",
                                "score": 2,
                                "replies": "",
                            },
                        },
                        # more 객체는 걸러져야 한다.
                        {"kind": "more", "data": {}},
                    ]
                }
            },
        },
    }
    c = _parse_comment(tree)
    assert c is not None
    assert c.author == "alice"
    assert c.score == 5
    assert len(c.replies) == 1
    assert c.replies[0].author == "bob"
