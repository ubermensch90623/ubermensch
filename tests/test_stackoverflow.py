"""Stack Exchange URL 파서 검증."""

from __future__ import annotations

from insane_search.platforms.stackoverflow import parse_question_url


def test_parse_question_url() -> None:
    assert parse_question_url(
        "https://stackoverflow.com/questions/12345/how-do-i-x"
    ) == ("stackoverflow", 12345)
    assert parse_question_url(
        "https://math.stackexchange.com/questions/1/foo"
    ) == ("math", 1)
    assert parse_question_url(
        "https://serverfault.com/questions/999/why"
    ) == ("serverfault", 999)
    assert parse_question_url("https://stackoverflow.com/users/1/jon") is None
    assert parse_question_url("https://example.com/questions/1") is None
