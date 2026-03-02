"""LLM Provider abstraction - API 키 없이도 사용 가능한 프레임워크.

프로바이더 우선순위:
    1. 명시적으로 전달된 provider 인스턴스
    2. configure()로 설정된 글로벌 프로바이더
    3. 자동 감지: ANTHROPIC_API_KEY가 있으면 AnthropicProvider, 없으면 MockProvider

사용 예:
    # API 키가 환경변수에 있으면 자동으로 Anthropic 사용
    team = AgentTeam(name="my-team")

    # API 키를 코드에서 설정
    from ubermensch import configure
    configure(api_key="sk-...")

    # Mock 모드 (API 키 불필요)
    from ubermensch import MockProvider
    team = AgentTeam(name="my-team", provider=MockProvider())

    # 커스텀 프로바이더
    team = AgentTeam(name="my-team", provider=MyOpenAIProvider())
"""

from __future__ import annotations

import logging
import os
import re
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """LLM 프로바이더 추상 클래스.

    모든 LLM 호출은 이 인터페이스를 통해 이루어집니다.
    커스텀 프로바이더를 만들려면 이 클래스를 상속하고 complete()를 구현하세요.
    """

    @abstractmethod
    async def complete(
        self,
        messages: list[dict[str, Any]],
        model: str = "claude-sonnet-4-20250514",
        system: str = "",
        max_tokens: int = 4096,
        tools: list[dict[str, Any]] | None = None,
    ) -> str:
        """LLM에 완성 요청을 보내고 텍스트 응답을 반환합니다.

        Args:
            messages: [{"role": "user"|"assistant", "content": "..."}]
            model: 사용할 모델 이름
            system: 시스템 프롬프트
            max_tokens: 최대 응답 토큰 수
            tools: 도구 정의 리스트 (선택)

        Returns:
            LLM 텍스트 응답
        """
        ...


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API 프로바이더."""

    def __init__(self, api_key: str | None = None) -> None:
        import anthropic

        self._client = (
            anthropic.AsyncAnthropic(api_key=api_key)
            if api_key
            else anthropic.AsyncAnthropic()
        )

    async def complete(
        self,
        messages: list[dict[str, Any]],
        model: str = "claude-sonnet-4-20250514",
        system: str = "",
        max_tokens: int = 4096,
        tools: list[dict[str, Any]] | None = None,
    ) -> str:
        kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        response = await self._client.messages.create(**kwargs)
        text_parts = [block.text for block in response.content if block.type == "text"]
        return "\n".join(text_parts)


class MockProvider(LLMProvider):
    """API 키 없이 사용 가능한 Mock 프로바이더.

    테스트, 데모, 프로토타이핑에 유용합니다.
    패턴 매칭으로 입력에 따라 다른 응답을 반환할 수 있습니다.

    사용 예:
        # 기본 응답
        provider = MockProvider(default_response="OK")

        # 패턴 매칭
        provider = MockProvider(responses={
            "보안": "보안 분석 결과입니다.",
            "성능": "성능 분석 결과입니다.",
        })

        # TASK: 파싱이 필요한 경우
        provider = MockProvider(default_response=(
            "TASK: 분석 | DESCRIPTION: 코드 분석 | PRIORITY: 8"
        ))
    """

    def __init__(
        self,
        default_response: str = "[Mock] 분석이 완료되었습니다.",
        responses: dict[str, str] | None = None,
    ) -> None:
        self.default_response = default_response
        self._responses: list[tuple[re.Pattern[str], str]] = []
        self._call_count = 0
        self._call_log: list[dict[str, Any]] = []

        if responses:
            for pattern, response in responses.items():
                self.add_response(pattern, response)

    def add_response(self, pattern: str, response: str) -> None:
        """특정 패턴에 매칭되는 응답을 추가합니다.

        Args:
            pattern: 정규식 패턴 (대소문자 무시)
            response: 매칭 시 반환할 응답
        """
        self._responses.append((re.compile(pattern, re.IGNORECASE), response))

    async def complete(
        self,
        messages: list[dict[str, Any]],
        model: str = "claude-sonnet-4-20250514",
        system: str = "",
        max_tokens: int = 4096,
        tools: list[dict[str, Any]] | None = None,
    ) -> str:
        self._call_count += 1

        # 메시지에서 텍스트 추출
        parts = [system]
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                parts.append(content)
        full_text = " ".join(parts)

        # 호출 로그 기록
        self._call_log.append({
            "call_number": self._call_count,
            "model": model,
            "system": system[:100],
            "text_preview": full_text[:200],
        })

        # 패턴 매칭
        for pattern, response in self._responses:
            if pattern.search(full_text):
                return response

        return self.default_response


# --- 글로벌 설정 ---

_default_provider: LLMProvider | None = None


def get_provider(provider: LLMProvider | None = None) -> LLMProvider:
    """프로바이더를 반환합니다.

    우선순위:
        1. 인자로 전달된 provider
        2. configure()로 설정된 글로벌 프로바이더
        3. 자동 감지 (API 키 유무)

    Returns:
        사용할 LLMProvider 인스턴스
    """
    if provider is not None:
        return provider

    global _default_provider
    if _default_provider is not None:
        return _default_provider

    # 자동 감지
    if os.environ.get("ANTHROPIC_API_KEY"):
        return AnthropicProvider()

    logger.info(
        "ANTHROPIC_API_KEY 미설정 → MockProvider 사용. "
        "실제 LLM: configure(api_key='sk-...') 또는 환경변수 설정."
    )
    return MockProvider()


def configure(
    provider: LLMProvider | None = None,
    api_key: str | None = None,
) -> None:
    """글로벌 LLM 프로바이더를 설정합니다.

    Args:
        provider: 사용할 프로바이더 인스턴스
        api_key: Anthropic API 키 (provider 미지정 시 AnthropicProvider 생성)

    사용 예:
        # Anthropic API 키 설정
        configure(api_key="sk-ant-...")

        # 커스텀 프로바이더
        configure(provider=MyProvider())

        # 초기화 (자동 감지로 복원)
        configure()
    """
    global _default_provider

    if provider is not None:
        _default_provider = provider
    elif api_key is not None:
        _default_provider = AnthropicProvider(api_key=api_key)
    else:
        _default_provider = None
