"""인증 없는 웹 검색.

DuckDuckGo 의 HTML 엔드포인트(html.duckduckgo.com/html/) 는 API 키 없이도
검색 결과를 HTML 로 돌려준다. 결과 수가 많지는 않지만 Claude Code 가 "한번
더 살펴볼 힌트" 로 쓰기에는 충분하다.

플랫폼 힌트(site: 연산자) 를 자동으로 붙여 주는 얇은 래퍼도 제공한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

from selectolax.parser import HTMLParser

from .http import make_client


@dataclass
class SearchHit:
    title: str
    url: str
    snippet: str


_PLATFORM_SITES = {
    "twitter": "site:twitter.com OR site:x.com",
    "reddit": "site:reddit.com",
    "stackoverflow": "site:stackoverflow.com OR site:stackexchange.com",
    "naver": "site:blog.naver.com",
}


def _unwrap_ddg(href: str) -> str:
    """DuckDuckGo HTML 결과의 /l/?uddg=... 래퍼를 실제 URL 로 푼다."""
    if href.startswith("//"):
        href = "https:" + href
    p = urlparse(href)
    if p.path.startswith("/l/"):
        q = parse_qs(p.query)
        if "uddg" in q:
            from urllib.parse import unquote

            return unquote(q["uddg"][0])
    return href


async def search(query: str, *, platform: str | None = None, limit: int = 10) -> list[SearchHit]:
    if platform and platform in _PLATFORM_SITES:
        query = f"{_PLATFORM_SITES[platform]} {query}"

    async with make_client() as client:
        r = await client.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://html.duckduckgo.com/",
            },
        )
        r.raise_for_status()

    tree = HTMLParser(r.text)
    hits: list[SearchHit] = []
    for result in tree.css(".result"):
        a = result.css_first("a.result__a")
        if not a:
            continue
        href = a.attributes.get("href") or ""
        url = _unwrap_ddg(href)
        snippet = result.css_first(".result__snippet")
        hits.append(
            SearchHit(
                title=a.text(strip=True),
                url=url,
                snippet=snippet.text(strip=True) if snippet else "",
            )
        )
        if len(hits) >= limit:
            break
    return hits


def format_hits(hits: list[SearchHit]) -> str:
    if not hits:
        return "_결과 없음_\n"
    lines: list[str] = []
    for i, h in enumerate(hits, 1):
        lines.append(f"{i}. [{h.title}]({h.url})")
        if h.snippet:
            lines.append(f"   {h.snippet}")
    return "\n".join(lines) + "\n"
