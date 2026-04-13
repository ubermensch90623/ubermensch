"""Insane Search MCP 서버.

Claude Code 에 두 개의 도구를 노출한다:

    insane_fetch(url)        — 플랫폼 우회 전략으로 URL 을 가져와 markdown 반환
    insane_search(query, …)  — 인증 없는 웹 검색

stdio 전송으로 동작하므로, Claude Code 의 `.mcp.json` 또는 `claude mcp add`
로 등록하면 된다.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import search as _search
from .router import detect_platform, fetch

mcp = FastMCP("insane-search")


@mcp.tool()
async def insane_fetch(url: str) -> str:
    """기본 WebFetch 가 실패/빈약한 사이트를 플랫폼별 우회 전략으로 가져온다.

    지원 플랫폼:
      * Twitter/X      — cdn.syndication.twimg.com (토큰 계산) + nitter 폴백
      * Reddit         — www.reddit.com/comments/<id>.json (UA 위장)
      * StackOverflow  — api.stackexchange.com (공식 무인증 API)
      * Naver Blog     — m.blog.naver.com / PostView.naver (iframe 풀기)

    그 외 URL 은 데스크톱 크롬처럼 보이는 헤더로 일반 GET 후 HTML→Markdown 변환.

    Args:
        url: 가져올 URL.

    Returns:
        Markdown 문자열.
    """
    return await fetch(url)


@mcp.tool()
async def insane_search(query: str, platform: str = "", limit: int = 10) -> str:
    """DuckDuckGo HTML 을 사용한 무인증 웹 검색.

    Args:
        query: 검색어.
        platform: 특정 플랫폼으로 한정 (twitter | reddit | stackoverflow | naver).
                  빈 문자열이면 전체 웹 검색.
        limit: 반환할 결과 개수 (최대 20).

    Returns:
        번호가 매겨진 검색 결과의 Markdown 목록.
    """
    p = platform.strip().lower() or None
    hits = await _search.search(query, platform=p, limit=min(limit, 20))
    return _search.format_hits(hits)


@mcp.tool()
async def insane_detect(url: str) -> str:
    """URL 이 어떤 우회 전략을 타게 될지 미리 확인 (디버그 용)."""
    return detect_platform(url)


def main() -> None:
    """`insane-search` 콘솔 스크립트의 진입점."""
    mcp.run()


if __name__ == "__main__":
    main()
