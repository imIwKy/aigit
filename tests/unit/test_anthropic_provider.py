from types import SimpleNamespace
from typing import Any

import pytest
from tests.unit.test_commit_workflow import FakeProvider, FakeRepository

from aigit.config.models import ProviderConfig
from aigit.providers.anthropic import (
    AnthropicProvider,
    AnthropicProviderError,
)
from aigit.providers.definitions import ProviderDefinition
from aigit.workflows.commit import run_commit_workflow


def anthropic_definition() -> ProviderDefinition:
    return ProviderDefinition(
        name="anthropic",
        display_name="Anthropic",
        protocol="anthropic",
        base_url=None,
        api_key_environment_variable="ANTHROPIC_API_KEY",
        default_model="claude-test-model",
    )


class FakeMessages:
    def __init__(
        self,
        response: Any | None = None,
        error: Exception | None = None,
    ) -> None:
        self.response = response
        self.error = error
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)

        if self.error is not None:
            raise self.error

        return self.response


class FakeAnthropicClient:
    def __init__(
        self,
        response: Any | None = None,
        error: Exception | None = None,
    ) -> None:
        self.messages = FakeMessages(
            response=response,
            error=error,
        )


def test_commit_rejects_title_over_configured_limit(
    monkeypatch,
    capsys,
) -> None:
    repository = FakeRepository()
    provider = FakeProvider(
        message="feat: this commit title is too long",
    )

    answers = iter(["y", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    result = run_commit_workflow(
        repository,
        provider,
        max_title_length=10,
    )

    assert result == 0
    assert repository.committed_messages == []
    assert "maximum is 10" in capsys.readouterr().out


def test_anthropic_provider_sends_expected_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-api-key")

    response = SimpleNamespace(
        content=[
            SimpleNamespace(
                type="text",
                text="feat: add Anthropic provider",
            ),
        ],
    )
    client = FakeAnthropicClient(response=response)

    provider = AnthropicProvider(
        ProviderConfig(
            model="claude-test-model",
            temperature=0.1,
            system_prompt="Generate a commit message.",
        ),
        anthropic_definition(),
        client=client,
    )

    diff = "diff --git a/example.txt b/example.txt"
    result = provider.generate_commit_message(diff)

    assert result == "feat: add Anthropic provider"

    assert client.messages.calls == [
        {
            "model": "claude-test-model",
            "max_tokens": 1024,
            "temperature": 0.1,
            "system": "Generate a commit message.",
            "messages": [
                {
                    "role": "user",
                    "content": f"Staged Git diff:\n{diff}",
                }
            ],
        }
    ]


def test_anthropic_provider_uses_default_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-api-key")

    response = SimpleNamespace(
        content=[
            SimpleNamespace(
                type="text",
                text="fix: correct provider response handling",
            ),
        ],
    )
    client = FakeAnthropicClient(response=response)

    provider = AnthropicProvider(
        ProviderConfig(),
        anthropic_definition(),
        client=client,
    )

    result = provider.generate_commit_message("staged diff")

    assert result == "fix: correct provider response handling"
    assert client.messages.calls[0]["model"] == "claude-test-model"


def test_anthropic_provider_joins_text_blocks_and_ignores_other_blocks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-api-key")

    response = SimpleNamespace(
        content=[
            SimpleNamespace(
                type="thinking",
                thinking="Internal reasoning.",
            ),
            SimpleNamespace(
                type="text",
                text="feat: add provider",
            ),
            SimpleNamespace(
                type="tool_use",
                id="tool-1",
            ),
            SimpleNamespace(
                type="text",
                text="\n\n- Add Anthropic support",
            ),
        ],
    )
    client = FakeAnthropicClient(response=response)

    provider = AnthropicProvider(
        ProviderConfig(),
        anthropic_definition(),
        client=client,
    )

    result = provider.generate_commit_message("staged diff")

    assert result == "feat: add provider\n\n- Add Anthropic support"


def test_anthropic_provider_wraps_api_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-api-key")

    client = FakeAnthropicClient(
        error=RuntimeError("service unavailable"),
    )

    provider = AnthropicProvider(
        ProviderConfig(),
        anthropic_definition(),
        client=client,
    )

    with pytest.raises(
        AnthropicProviderError,
        match="Anthropic request failed: service unavailable",
    ):
        provider.generate_commit_message("staged diff")


def test_anthropic_provider_rejects_empty_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-api-key")

    response = SimpleNamespace(
        content=[
            SimpleNamespace(
                type="text",
                text="   ",
            ),
        ],
    )
    client = FakeAnthropicClient(response=response)

    provider = AnthropicProvider(
        ProviderConfig(),
        anthropic_definition(),
        client=client,
    )

    with pytest.raises(
        AnthropicProviderError,
        match="Anthropic returned an empty commit message",
    ):
        provider.generate_commit_message("staged diff")


def test_anthropic_provider_requires_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(
        RuntimeError,
        match="Required environment variable is not set",
    ):
        AnthropicProvider(
            ProviderConfig(),
            anthropic_definition(),
            client=FakeAnthropicClient(),
        )
