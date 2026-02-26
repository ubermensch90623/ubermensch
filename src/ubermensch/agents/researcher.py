"""Research-focused agents for information gathering and summarization."""

from __future__ import annotations

import logging

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus
from ubermensch.tools.web_crawler import WebCrawler

logger = logging.getLogger(__name__)


class ResearcherAgent(BaseAgent):
    """웹 검색과 크롤링을 통해 정보를 수집하는 에이전트."""

    def __init__(
        self,
        name: str = "researcher",
        model: str = "claude-sonnet-4-20250514",
        max_search_results: int = 5,
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "You are a research agent. Your job is to gather, analyze, and "
                "organize information from web sources. Always provide factual, "
                "well-sourced information. Respond in Korean."
            ),
        )
        self.crawler = WebCrawler()
        self.max_search_results = max_search_results

    async def execute(self, message: AgentMessage) -> TaskResult:
        """검색 쿼리를 받아 웹에서 정보를 수집하고 분석합니다."""
        query = message.task
        urls = message.context.get("urls", [])

        # URL이 직접 제공된 경우 해당 URL 크롤링
        if urls:
            crawl_results = await self.crawler.fetch_multiple(urls)
        else:
            # 검색어로 검색 후 크롤링
            crawl_results = await self.crawler.search_and_fetch(
                query, max_results=self.max_search_results
            )

        if not crawl_results:
            return TaskResult(
                agent_name=self.name,
                status=TaskStatus.FAILED,
                error=f"No results found for: {query}",
            )

        # 크롤링 결과를 LLM에게 분석 요청
        source_text = "\n\n---\n\n".join(
            f"Source: {r.url}\nTitle: {r.title}\n\n{r.text[:5000]}"
            for r in crawl_results
            if r.status_code == 200 or r.status_code == 0
        )

        analysis_prompt = (
            f"Research query: {query}\n\n"
            f"Collected sources:\n{source_text}\n\n"
            "Based on these sources, provide a comprehensive analysis. "
            "Include key findings, important details, and source references."
        )

        analysis = await self.ask_llm(analysis_prompt)

        return TaskResult(
            agent_name=self.name,
            status=TaskStatus.COMPLETED,
            data={
                "query": query,
                "sources": [r.url for r in crawl_results],
                "analysis": analysis,
            },
        )


class SummarizerAgent(BaseAgent):
    """텍스트 요약 전문 에이전트."""

    def __init__(
        self,
        name: str = "summarizer",
        model: str = "claude-sonnet-4-20250514",
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "You are a summarization agent. Your job is to create clear, "
                "concise summaries of provided content. Preserve key information "
                "while reducing length. Respond in Korean."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        """텍스트를 받아 요약합니다."""
        text = message.context.get("text", message.task)
        max_length = message.context.get("max_length", "500 words")

        summary_prompt = (
            f"Summarize the following content in {max_length} or less:\n\n{text}"
        )

        summary = await self.ask_llm(summary_prompt)

        return TaskResult(
            agent_name=self.name,
            status=TaskStatus.COMPLETED,
            data={"summary": summary},
        )
