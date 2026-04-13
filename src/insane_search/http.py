"""공용 HTTP 클라이언트.

Claude Code의 기본 WebFetch가 막히는 이유는 대부분:
  1. 빈약한 User-Agent → 봇으로 간주됨
  2. Accept-Language 누락 → 일부 사이트가 차단
  3. 리다이렉트 미추적 → iframe 기반 사이트 실패

여기서는 "평범한 데스크톱 크롬" 처럼 보이는 기본 헤더를 씌운 httpx 클라이언트를
제공한다. 인증/API 키는 사용하지 않는다.
"""

from __future__ import annotations

import httpx

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "User-Agent": DEFAULT_UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
}

DEFAULT_TIMEOUT = httpx.Timeout(15.0, connect=5.0)


def make_client(
    *,
    headers: dict[str, str] | None = None,
    follow_redirects: bool = True,
    timeout: httpx.Timeout | float | None = None,
) -> httpx.AsyncClient:
    """일관된 기본값을 가진 httpx.AsyncClient 를 만든다."""
    merged = dict(DEFAULT_HEADERS)
    if headers:
        merged.update(headers)
    return httpx.AsyncClient(
        headers=merged,
        follow_redirects=follow_redirects,
        timeout=timeout or DEFAULT_TIMEOUT,
        http2=True,
    )
