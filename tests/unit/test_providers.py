import pytest

from aigit.config.models import ProviderConfig
from aigit.providers import FakeProvider, LlmProvider
from aigit.providers.definitions import (
    FAKE_PROVIDER_DEFINITION,
    ProviderDefinition,
)
from aigit.providers.factory import ProviderFactory
from aigit.providers.openai_compatible import (
    OpenAICompatibleProvider,
)
from aigit.providers.registry import ProviderRegistry, ProviderRegistryError

OPENAI_DEFINITION = ProviderDefinition(
    name="openai",
    display_name="OpenAI",
    protocol="openai-compatible",
    base_url="https://api.openai.com/v1",
    api_key_environment_variable="OPENAI_API_KEY",
    default_model="gpt-4o-mini",
)


def make_registry() -> ProviderRegistry:
    return ProviderRegistry(
        definitions={
            "fake": FAKE_PROVIDER_DEFINITION,
            "openai": OPENAI_DEFINITION,
        },
        default="openai",
    )


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
    definition = FAKE_PROVIDER_DEFINITION

    assert definition.name == "fake"
    assert definition.protocol == "fake"
    assert definition.base_url is None
    assert definition.api_key_environment_variable is None


def test_factory_creates_fake_provider() -> None:
    config = ProviderConfig(
        name="fake",
        fake_message="feat: created by factory",
    )

    provider = ProviderFactory(
        registry=make_registry(),
    ).create(config)

    assert isinstance(provider, FakeProvider)
    assert provider.generate_commit_message("some diff") == ("feat: created by factory")


def test_factory_rejects_unknown_provider() -> None:
    config = ProviderConfig(name="does-not-exist")

    with pytest.raises(
        ProviderRegistryError,
        match="not found",
    ):
        ProviderFactory(
            registry=make_registry(),
        ).create(config)


def test_factory_creates_openai_compatible_provider(
    monkeypatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    config = ProviderConfig(
        name="openai",
        model="gpt-4o-mini",
    )

    provider = ProviderFactory(
        registry=make_registry(),
    ).create(config)

    assert isinstance(provider, OpenAICompatibleProvider)
