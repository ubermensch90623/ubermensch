"""Review-focused agents for security, performance, and code quality analysis."""

from __future__ import annotations

import logging

from ubermensch.core.base_agent import BaseAgent
from ubermensch.core.message import AgentMessage, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class SecurityReviewerAgent(BaseAgent):
    """보안 취약점을 분석하는 리뷰 에이전트.

    OWASP Top 10, 인증/인가, 입력 검증, 민감 데이터 처리 등을 검토합니다.
    """

    def __init__(
        self,
        name: str = "security_reviewer",
        model: str = "claude-sonnet-4-20250514",
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "You are a security review agent. Your job is to analyze code and "
                "systems for security vulnerabilities. Focus on:\n"
                "- OWASP Top 10 vulnerabilities (injection, XSS, CSRF, etc.)\n"
                "- Authentication and authorization flaws\n"
                "- Input validation and sanitization\n"
                "- Sensitive data exposure\n"
                "- Security misconfiguration\n"
                "- Cryptographic weaknesses\n\n"
                "Rate each finding with severity: CRITICAL, HIGH, MEDIUM, LOW.\n"
                "Provide specific remediation recommendations.\n"
                "Respond in Korean."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        """코드나 시스템을 보안 관점에서 분석합니다."""
        code = message.context.get("code", "")
        file_paths = message.context.get("file_paths", [])

        review_prompt = (
            f"Security review task: {message.task}\n\n"
        )

        if code:
            review_prompt += f"Code to review:\n```\n{code}\n```\n\n"

        if file_paths:
            review_prompt += f"Related files: {', '.join(file_paths)}\n\n"

        review_prompt += (
            "Perform a thorough security review. For each finding:\n"
            "1. Severity (CRITICAL/HIGH/MEDIUM/LOW)\n"
            "2. Vulnerability type\n"
            "3. Location/affected code\n"
            "4. Impact description\n"
            "5. Remediation recommendation\n\n"
            "Also note what security aspects are well-implemented."
        )

        analysis = await self.ask_llm(review_prompt)

        return TaskResult(
            agent_name=self.name,
            status=TaskStatus.COMPLETED,
            data={
                "review_type": "security",
                "analysis": analysis,
            },
        )


class PerformanceReviewerAgent(BaseAgent):
    """성능 병목 및 최적화 기회를 분석하는 에이전트.

    시간 복잡도, 메모리 사용, I/O 패턴, 캐싱 전략 등을 검토합니다.
    """

    def __init__(
        self,
        name: str = "performance_reviewer",
        model: str = "claude-sonnet-4-20250514",
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "You are a performance review agent. Your job is to analyze code "
                "and systems for performance issues. Focus on:\n"
                "- Algorithm complexity (time and space)\n"
                "- Memory allocation patterns and leaks\n"
                "- I/O bottlenecks (network, disk, database)\n"
                "- Caching opportunities\n"
                "- Concurrency and parallelism issues\n"
                "- Resource pooling and connection management\n"
                "- N+1 query patterns\n\n"
                "Rate each finding with impact: HIGH, MEDIUM, LOW.\n"
                "Provide specific optimization suggestions with expected improvement.\n"
                "Respond in Korean."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        """코드나 시스템을 성능 관점에서 분석합니다."""
        code = message.context.get("code", "")
        metrics = message.context.get("metrics", {})

        review_prompt = (
            f"Performance review task: {message.task}\n\n"
        )

        if code:
            review_prompt += f"Code to review:\n```\n{code}\n```\n\n"

        if metrics:
            review_prompt += f"Performance metrics: {metrics}\n\n"

        review_prompt += (
            "Perform a thorough performance review. For each finding:\n"
            "1. Impact level (HIGH/MEDIUM/LOW)\n"
            "2. Issue type (algorithm, I/O, memory, etc.)\n"
            "3. Current behavior and bottleneck\n"
            "4. Recommended optimization\n"
            "5. Expected improvement estimate"
        )

        analysis = await self.ask_llm(review_prompt)

        return TaskResult(
            agent_name=self.name,
            status=TaskStatus.COMPLETED,
            data={
                "review_type": "performance",
                "analysis": analysis,
            },
        )


class CodeReviewerAgent(BaseAgent):
    """코드 품질, 테스트 커버리지, 베스트 프랙티스를 검토하는 에이전트.

    코드 스타일, 설계 패턴, 테스트 충분성, 유지보수성을 분석합니다.
    """

    def __init__(
        self,
        name: str = "code_reviewer",
        model: str = "claude-sonnet-4-20250514",
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=(
                "You are a code quality review agent. Your job is to analyze code "
                "for quality, maintainability, and test coverage. Focus on:\n"
                "- Code clarity and readability\n"
                "- Design patterns and SOLID principles\n"
                "- Error handling completeness\n"
                "- Test coverage and test quality\n"
                "- API design and contracts\n"
                "- Documentation adequacy\n"
                "- Code duplication and DRY violations\n"
                "- Naming conventions\n\n"
                "For test coverage, identify untested paths and edge cases.\n"
                "Provide actionable improvement suggestions.\n"
                "Respond in Korean."
            ),
        )

    async def execute(self, message: AgentMessage) -> TaskResult:
        """코드를 품질/테스트 관점에서 분석합니다."""
        code = message.context.get("code", "")
        tests = message.context.get("tests", "")
        pr_diff = message.context.get("pr_diff", "")

        review_prompt = f"Code review task: {message.task}\n\n"

        if code:
            review_prompt += f"Source code:\n```\n{code}\n```\n\n"

        if tests:
            review_prompt += f"Test code:\n```\n{tests}\n```\n\n"

        if pr_diff:
            review_prompt += f"PR diff:\n```\n{pr_diff}\n```\n\n"

        review_prompt += (
            "Perform a thorough code quality review:\n"
            "1. Code quality issues (clarity, design, naming)\n"
            "2. Error handling gaps\n"
            "3. Test coverage analysis (untested paths, missing edge cases)\n"
            "4. Improvement suggestions with priority\n"
            "5. Positive aspects worth maintaining"
        )

        analysis = await self.ask_llm(review_prompt)

        return TaskResult(
            agent_name=self.name,
            status=TaskStatus.COMPLETED,
            data={
                "review_type": "code_quality",
                "analysis": analysis,
            },
        )
