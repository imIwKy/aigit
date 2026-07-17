from types import SimpleNamespace

import pytest

from aigit.config.models import ProviderConfig
from aigit.providers.definitions import PROVIDER_DEFINITIONS
from aigit.providers.openai import (
    OpenAIProvider,
    OpenAIProviderError,
)


class FakeCompletions:
    def __init__(self, response=None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.create_arguments: dict[str, object] | None = None

    def create(self, **kwargs):
        self.create_arguments = kwargs

        if self.error:
            raise self.error

        return self.response


class FakeOpenAIClient:
    def __init__(self, completions: FakeCompletions) -> None:
        self.chat = SimpleNamespace(completions=completions)


def make_response(message: str | None):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=message),
            )
        ]
    )


def make_provider(
    monkeypatch,
    completions: FakeCompletions,
    *,
    config: ProviderConfig | None = None,
) -> OpenAIProvider:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    provider_config = config or ProviderConfig(
        name="openai",
        model="gpt-4o-mini",
        system_prompt="Write concise commit messages.",
        temperature=0.2,
    )

    client = FakeOpenAIClient(completions)

    return OpenAIProvider(
        config=provider_config,
        definition=PROVIDER_DEFINITIONS["openai"],
        client=client,
    )


def test_generates_commit_message(monkeypatch) -> None:
    completions = FakeCompletions(
        response=make_response("feat: add provider support")
    )
    provider = make_provider(monkeypatch, completions)

    result = provider.generate_commit_message("diff --git ...")

    assert result == "feat: add provider support"


def test_sends_expected_request(monkeypatch) -> None:
    completions = FakeCompletions(
        response=make_response("feat: add provider support")
    )
    provider = make_provider(monkeypatch, completions)

    diff = "diff --git a/example.txt b/example.txt"
    provider.generate_commit_message(diff)

    assert completions.create_arguments == {
        "model": "gpt-4o-mini",
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": "Write concise commit messages.",
            },
            {
                "role": "user",
                "content": (
                    "Generate a Conventional Commit message based on "
                    "this staged Git diff.\n\n"
                    "Rules:\n"
                    "- Keep the title under 72 characters.\n"
                    "- Do not invent changes.\n"
                    "- Include body bullets only if useful.\n\n"
                    f"Git diff:\n{diff}"
                ),
            },
        ],
    }


def test_uses_definition_default_model(monkeypatch) -> None:
    completions = FakeCompletions(
        response=make_response("chore: update files")
    )
    provider = make_provider(
        monkeypatch,
        completions,
        config=ProviderConfig(name="openai", model=None),
    )

    provider.generate_commit_message("some diff")

    assert completions.create_arguments is not None
    assert completions.create_arguments["model"] == "gpt-4o-mini"


def test_rejects_empty_response(monkeypatch) -> None:
    completions = FakeCompletions(response=make_response(""))
    provider = make_provider(monkeypatch, completions)

    with pytest.raises(
        OpenAIProviderError,
        match="empty commit message",
    ):
        provider.generate_commit_message("some diff")


def test_rejects_invalid_response(monkeypatch) -> None:
    completions = FakeCompletions(response=SimpleNamespace(choices=[]))
    provider = make_provider(monkeypatch, completions)

    with pytest.raises(
        OpenAIProviderError,
        match="invalid response",
    ):
        provider.generate_commit_message("some diff")


def test_wraps_api_errors(monkeypatch) -> None:
    completions = FakeCompletions(
        error=RuntimeError("connection failed"),
    )
    provider = make_provider(monkeypatch, completions)

    with pytest.raises(
        OpenAIProviderError,
        match="OpenAI request failed",
    ):
        provider.generate_commit_message("some diff")


def test_requires_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    config = ProviderConfig(
        name="openai",
        model="gpt-4o-mini",
    )

    completions = FakeCompletions(
        response=make_response("feat: add provider support")
    )
    client = FakeOpenAIClient(completions)

    with pytest.raises(
        RuntimeError,
        match="Required environment variable is not set",
    ):
        OpenAIProvider(
            config=config,
            definition=PROVIDER_DEFINITIONS["openai"],
            client=client,
        )