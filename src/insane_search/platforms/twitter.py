"""Twitter / X 우회 페처.

공식 twitter.com 는 비로그인/프로그램 접근에 대해 402/로그인 페이지를 반환한다.
여기서는 두 가지 공개 우회 경로를 사용한다:

1. syndication.twimg.com — 트위터가 임베드 위젯용으로 공개한 JSON 엔드포인트.
   토큰을 클라이언트 측에서 계산할 수 있고 인증이 필요 없다.
2. nitter — 오픈소스 트위터 프론트엔드. syndication 이 실패할 때만 시도.

두 경로 모두 API 키가 필요 없다.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from ..http import make_client

_TWEET_PATH = re.compile(r"^/([^/]+)/status(?:es)?/(\d+)")

# 백업용 nitter 인스턴스들. 첫 성공 응답만 사용한다.
_NITTER_INSTANCES = (
    "https://nitter.net",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
)

_BASE36 = "0123456789abcdefghijklmnopqrstuvwxyz"


@dataclass
class Tweet:
    id: str
    author: str
    author_handle: str
    text: str
    created_at: str | None
    url: str
    source: str  # "syndication" | "nitter"


def parse_tweet_url(url: str) -> tuple[str, str] | None:
    """twitter.com/x.com URL 에서 (handle, tweet_id) 추출."""
    p = urlparse(url)
    if p.hostname not in {
        "twitter.com",
        "www.twitter.com",
        "mobile.twitter.com",
        "x.com",
        "www.x.com",
    }:
        return None
    m = _TWEET_PATH.match(p.path)
    if not m:
        return None
    return m.group(1), m.group(2)


def _float_to_base36(n: float) -> str:
    """JS Number.prototype.toString(36) 의 파이썬 포트."""
    if n < 0:
        return "-" + _float_to_base36(-n)
    int_part = int(n)
    frac = n - int_part
    if int_part == 0:
        int_str = "0"
    else:
        int_str = ""
        while int_part > 0:
            int_str = _BASE36[int_part % 36] + int_str
            int_part //= 36
    if frac == 0:
        return int_str
    out = int_str + "."
    # JS 는 안정화될 때까지 찍지만 실용상 16자리면 충분하다.
    for _ in range(16):
        frac *= 36
        digit = int(frac)
        out += _BASE36[digit]
        frac -= digit
        if frac == 0:
            break
    return out


def syndication_token(tweet_id: str) -> str:
    r"""syndication.twimg.com 이 요구하는 토큰을 계산한다.

    JS 원본:
        ((Number(id) / 1e15) * Math.PI).toString(36).replace(/(0+|\.)/g, '')
    """
    n = (int(tweet_id) / 1e15) * math.pi
    return re.sub(r"(0+|\.)", "", _float_to_base36(n))


async def _from_syndication(client: httpx.AsyncClient, tweet_id: str) -> Tweet | None:
    token = syndication_token(tweet_id)
    url = (
        "https://cdn.syndication.twimg.com/tweet-result"
        f"?id={tweet_id}&token={token}&lang=en"
    )
    r = await client.get(url)
    if r.status_code != 200:
        return None
    try:
        data = r.json()
    except ValueError:
        return None
    if not isinstance(data, dict) or "text" not in data:
        return None
    user = data.get("user", {}) or {}
    return Tweet(
        id=str(data.get("id_str", tweet_id)),
        author=user.get("name", ""),
        author_handle=user.get("screen_name", ""),
        text=data.get("text", ""),
        created_at=data.get("created_at"),
        url=f"https://x.com/{user.get('screen_name','i')}/status/{tweet_id}",
        source="syndication",
    )


async def _from_nitter(
    client: httpx.AsyncClient, handle: str, tweet_id: str
) -> Tweet | None:
    from selectolax.parser import HTMLParser

    for base in _NITTER_INSTANCES:
        try:
            r = await client.get(f"{base}/{handle}/status/{tweet_id}")
        except httpx.HTTPError:
            continue
        if r.status_code != 200 or "tweet-content" not in r.text:
            continue
        tree = HTMLParser(r.text)
        content = tree.css_first(".main-tweet .tweet-content")
        if not content:
            continue
        name = tree.css_first(".main-tweet .fullname")
        date = tree.css_first(".main-tweet .tweet-date a")
        return Tweet(
            id=tweet_id,
            author=name.text(strip=True) if name else "",
            author_handle=handle,
            text=content.text(strip=True),
            created_at=date.attributes.get("title") if date else None,
            url=f"https://x.com/{handle}/status/{tweet_id}",
            source="nitter",
        )
    return None


async def fetch_tweet(url: str) -> Tweet:
    parsed = parse_tweet_url(url)
    if not parsed:
        raise ValueError(f"Twitter/X 트윗 URL 이 아닙니다: {url}")
    handle, tweet_id = parsed

    async with make_client() as client:
        tweet = await _from_syndication(client, tweet_id)
        if tweet:
            return tweet
        tweet = await _from_nitter(client, handle, tweet_id)
        if tweet:
            return tweet

    raise RuntimeError(
        f"syndication 과 nitter 양쪽 모두 트윗 {tweet_id} 을 가져오지 못했습니다."
    )


def format_tweet(t: Tweet) -> str:
    header = f"# @{t.author_handle}" + (f" ({t.author})" if t.author else "")
    meta = [t.url]
    if t.created_at:
        meta.append(t.created_at)
    meta.append(f"via {t.source}")
    return f"{header}\n\n{t.text}\n\n---\n" + " · ".join(meta) + "\n"
