"""Twitter syndication token 및 URL 파서 검증."""

from __future__ import annotations

from insane_search.platforms.twitter import (
    parse_tweet_url,
    syndication_token,
)


def test_parse_tweet_url_variants() -> None:
    assert parse_tweet_url("https://twitter.com/jack/status/20") == ("jack", "20")
    assert parse_tweet_url("https://x.com/sama/status/1800000000000000000") == (
        "sama",
        "1800000000000000000",
    )
    assert parse_tweet_url("https://mobile.twitter.com/foo/statuses/7") == (
        "foo",
        "7",
    )
    assert parse_tweet_url("https://x.com/sama") is None
    assert parse_tweet_url("https://example.com/jack/status/20") is None


def test_syndication_token_is_deterministic_and_non_empty() -> None:
    # 토큰은 트윗 ID 별로 결정적이고 비어있지 않아야 한다.
    a = syndication_token("20")
    b = syndication_token("20")
    c = syndication_token("1800000000000000000")
    assert a == b
    assert a
    assert c
    # 토큰은 소문자 영숫자로만 구성되며 '.' 이나 선행/후행 '0' 런이 없어야 한다.
    # (JS 정규식 /(0+|\.)/g 를 그대로 포팅했으므로)
    assert "." not in a
    # 0 문자열이 자체적으로 남을 수는 있지만 "00" 같은 연속 0 은 없다 (모두 지워짐).
    assert "00" not in a
    assert "00" not in c
