"""LLM Provider 유닛 테스트."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from ubermensch.core.provider import (
    AnthropicProvider,
    LLMProvider,
    MockProvider,
    configure,
    get_provider,
)


class TestMockProvider:
    async def test_default_response(self):
        provider = MockProvider(default_response="hello")
        result = await provider.complete(
            messages=[{"role": "user", "content": "anything"}],
        )
        assert result == "hello"

    async def test_pattern_matching(self):
        provider = MockProvider(
            default_response="default",
            responses={
                "보안": "보안 분석 결과",
                "성능": "성능 분석 결과",
            },
        )

        result = await provider.complete(
            messages=[{"role": "user", "content": "보안 취약점을 분석하세요"}],
        )
        assert result == "보안 분석 결과"

        result = await provider.complete(
            messages=[{"role": "user", "content": "성능 이슈를 분석하세요"}],
        )
        assert result == "성능 분석 결과"

        result = await provider.complete(
            messages=[{"role": "user", "content": "기타 요청"}],
        )
        assert result == "default"

    async def test_system_prompt_matching(self):
        """시스템 프롬프트도 패턴 매칭에 포함."""
        provider = MockProvider(
            default_response="default",
            responses={"team lead": "I am the lead"},
        )

        result = await provider.complete(
            messages=[{"role": "user", "content": "hello"}],
            system="You are a team lead.",
        )
        assert result == "I am the lead"

    async def test_add_response(self):
        provider = MockProvider()
        provider.add_response("TASK:", "TASK: Analyze | DESCRIPTION: Do it | PRIORITY: 8")

        result = await provider.complete(
            messages=[{"role": "user", "content": "Create TASK: plans"}],
        )
        assert "TASK: Analyze" in result

    async def test_call_count(self):
        provider = MockProvider()
        assert provider._call_count == 0

        await provider.complete(messages=[{"role": "user", "content": "1"}])
        await provider.complete(messages=[{"role": "user", "content": "2"}])

        assert provider._call_count == 2

    async def test_call_log(self):
        provider = MockProvider()
        await provider.complete(
            messages=[{"role": "user", "content": "test"}],
            model="test-model",
            system="test system",
        )

        assert len(provider._call_log) == 1
        log = provider._call_log[0]
        assert log["model"] == "test-model"
        assert "test system" in log["system"]

    async def test_first_pattern_wins(self):
        """여러 패턴이 매칭되면 첫 번째가 선택됨."""
        provider = MockProvider(
            responses={
                "코드": "first match",
                "코드 리뷰": "second match",
            },
        )

        result = await provider.complete(
            messages=[{"role": "user", "content": "코드 리뷰해주세요"}],
        )
        assert result == "first match"

    async def test_regex_pattern(self):
        """정규식 패턴 지원."""
        provider = MockProvider()
        provider.add_response(r"TASK:.*PRIORITY:\s*\d+", "parsed task response")

        result = await provider.complete(
            messages=[{"role": "user", "content": "TASK: hello | PRIORITY: 5"}],
        )
        assert result == "parsed task response"

    async def test_ignore_non_string_content(self):
        """content가 문자열이 아닌 경우 안전하게 무시."""
        provider = MockProvider(default_response="ok")
        result = await provider.complete(
            messages=[{"role": "user", "content": ["image", "data"]}],
        )
        assert result == "ok"


class TestGetProvider:
    def test_explicit_provider(self):
        """명시적 provider는 항상 우선."""
        mock = MockProvider()
        assert get_provider(mock) is mock

    def test_auto_detect_mock_without_key(self):
        """API 키 없으면 MockProvider."""
        with patch.dict(os.environ, {}, clear=True):
            # 글로벌 provider 리셋
            configure()
            provider = get_provider()
            assert isinstance(provider, MockProvider)

    def test_auto_detect_anthropic_with_key(self):
        """API 키 있으면 AnthropicProvider."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            configure()
            provider = get_provider()
            assert isinstance(provider, AnthropicProvider)


class TestConfigure:
    def test_configure_with_provider(self):
        """provider 인스턴스로 설정."""
        mock = MockProvider(default_response="configured")
        configure(provider=mock)

        provider = get_provider()
        assert provider is mock

        # 정리
        configure()

    def test_configure_with_api_key(self):
        """API 키로 AnthropicProvider 생성."""
        configure(api_key="sk-test-key")

        provider = get_provider()
        assert isinstance(provider, AnthropicProvider)

        # 정리
        configure()

    def test_configure_reset(self):
        """인자 없이 호출하면 자동 감지로 복원."""
        mock = MockProvider()
        configure(provider=mock)
        assert get_provider() is mock

        configure()  # 리셋
        with patch.dict(os.environ, {}, clear=True):
            provider = get_provider()
            assert isinstance(provider, MockProvider)
            assert provider is not mock  # 새 인스턴스


class TestLLMProviderInterface:
    def test_is_abstract(self):
        """LLMProvider는 직접 인스턴스화할 수 없음."""
        with pytest.raises(TypeError):
            LLMProvider()  # type: ignore[abstract]

    async def test_custom_provider(self):
        """커스텀 프로바이더 구현 테스트."""

        class EchoProvider(LLMProvider):
            async def complete(self, messages, **kwargs):
                return f"Echo: {messages[-1]['content']}"

        provider = EchoProvider()
        result = await provider.complete(
            messages=[{"role": "user", "content": "hello"}],
        )
        assert result == "Echo: hello"
