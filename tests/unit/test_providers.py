import pytest

from aigit.config.models import ProviderConfig
from aigit.providers import FakeProvider, LlmProvider
from aigit.providers.definitions import PROVIDER_DEFINITIONS
from aigit.providers.factory import ProviderFactory
from aigit.providers.openai import OpenAIProvider


def test_fake_provider_uses_configured_message() -> None:
    config = ProviderConfig(
        fake_message="feat: configured provider message",
    )
    provider = FakeProvider(config)

    result = provider.generate_commit_message("some diff")

    assert result == "feat: configured provider message"


def test_fake_provider_matches_provider_interface() -> None:
    config = ProviderConfig()
    provider: LlmProvider = FakeProvider(config)

    assert provider.generate_commit_message("some diff")


def test_fake_provider_definition_exists() -> None:
    definition = PROVIDER_DEFINITIONS["fake"]

    assert definition.name == "fake"
    assert definition.protocol == "fake"
    assert definition.base_url is None
    assert definition.api_key_environment_variable is None


def test_factory_creates_fake_provider() -> None:
    config = ProviderConfig(
        name="fake",
        fake_message="feat: created by factory",
    )

    provider = ProviderFactory().create(config)

    assert isinstance(provider, FakeProvider)
    assert provider.generate_commit_message("some diff") == (
        "feat: created by factory"
    )


def test_factory_rejects_unknown_provider() -> None:
    config = ProviderConfig(name="does-not-exist")

    with pytest.raises(ValueError, match="Unknown provider"):
        ProviderFactory().create(config)


def test_factory_creates_openai_provider(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    config = ProviderConfig(
        name="openai",
        model="gpt-4o-mini",
    )

    provider = ProviderFactory().create(config)

    assert isinstance(provider, OpenAIProvider)