"""URL → 플랫폼별 페처 디스패처."""

from __future__ import annotations

from urllib.parse import urlparse

from .http import make_client
from .markdown import html_to_markdown
from .platforms import naver, reddit, stackoverflow, twitter


def detect_platform(url: str) -> str:
    """URL 을 보고 어떤 우회 전략을 쓸지 이름을 반환한다."""
    p = urlparse(url)
    host = p.hostname or ""
    if twitter.parse_tweet_url(url):
        return "twitter"
    if host.endswith(".reddit.com") or host == "reddit.com":
        return "reddit"
    if stackoverflow.parse_question_url(url):
        return "stackoverflow"
    if naver.is_naver_blog(url):
        return "naver"
    return "generic"


async def fetch(url: str) -> str:
    """URL 을 받아 platform-aware 하게 가져온 마크다운을 돌려준다."""
    platform = detect_platform(url)

    if platform == "twitter":
        tweet = await twitter.fetch_tweet(url)
        return twitter.format_tweet(tweet)

    if platform == "reddit":
        post = await reddit.fetch_post(url)
        return reddit.format_post(post)

    if platform == "stackoverflow":
        q = await stackoverflow.fetch_question(url)
        return stackoverflow.format_question(q)

    if platform == "naver":
        p = await naver.fetch_post(url)
        return naver.format_post(p)

    # 기본 HTML → markdown. 그냥 WebFetch 가 아니라 "사람" 헤더를 씌워서 받아온다.
    async with make_client() as client:
        r = await client.get(url)
        r.raise_for_status()
        return html_to_markdown(r.text)
