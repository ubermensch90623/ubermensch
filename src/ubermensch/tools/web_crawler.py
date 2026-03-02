"""Web crawling tool for agents."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    """크롤링 결과."""

    url: str
    title: str
    text: str
    links: list[str]
    status_code: int


class WebCrawler:
    """비동기 웹 크롤러.

    에이전트가 웹 페이지를 가져오고 내용을 추출할 수 있게 합니다.
    """

    def __init__(
        self,
        timeout: int = 30,
        max_content_length: int = 50_000,
        user_agent: str = "Ubermensch-Agent/0.1",
    ):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_content_length = max_content_length
        self.headers = {"User-Agent": user_agent}

    async def fetch(self, url: str) -> CrawlResult:
        """URL에서 페이지를 가져와 텍스트와 링크를 추출합니다."""
        async with (
            aiohttp.ClientSession(timeout=self.timeout, headers=self.headers) as session,
            session.get(url) as response,
        ):
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            # 불필요한 태그 제거
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            text = soup.get_text(separator="\n", strip=True)

            # 텍스트 길이 제한
            if len(text) > self.max_content_length:
                text = text[: self.max_content_length] + "\n... (truncated)"

            # 링크 추출
            links = []
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                full_url = urljoin(url, href)
                if urlparse(full_url).scheme in ("http", "https"):
                    links.append(full_url)

            return CrawlResult(
                url=url,
                title=title,
                text=text,
                links=list(dict.fromkeys(links)),  # 중복 제거, 순서 유지
                status_code=response.status,
            )

    async def fetch_multiple(self, urls: list[str]) -> list[CrawlResult]:
        """여러 URL을 동시에 크롤링합니다."""
        tasks = [self.fetch(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        crawl_results: list[CrawlResult] = []
        for i, r in enumerate(results):
            if isinstance(r, BaseException):
                logger.error(f"Failed to crawl {urls[i]}: {r}")
                crawl_results.append(
                    CrawlResult(
                        url=urls[i],
                        title="",
                        text=f"Error: {r}",
                        links=[],
                        status_code=0,
                    )
                )
            else:
                crawl_results.append(r)
        return crawl_results

    async def search_and_fetch(
        self,
        query: str,
        search_url: str = "https://html.duckduckgo.com/html/",
        max_results: int = 5,
    ) -> list[CrawlResult]:
        """DuckDuckGo로 검색한 뒤 결과 페이지들을 크롤링합니다."""
        async with (
            aiohttp.ClientSession(timeout=self.timeout, headers=self.headers) as session,
            session.post(search_url, data={"q": query}) as response,
        ):
            html = await response.text()

        soup = BeautifulSoup(html, "html.parser")
        result_links: list[str] = []

        for a_tag in soup.select("a.result__a"):
            href = a_tag.get("href", "")
            if href and urlparse(href).scheme in ("http", "https"):
                result_links.append(href)
            if len(result_links) >= max_results:
                break

        if not result_links:
            logger.warning(f"No search results found for: {query}")
            return []

        logger.info(f"Found {len(result_links)} results for '{query}', fetching...")
        return await self.fetch_multiple(result_links)
