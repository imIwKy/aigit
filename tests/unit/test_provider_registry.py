import json

import pytest

from aigit.providers.loader import (
    ProviderDefinitionError,
    load_provider_registry,
)
from aigit.providers.registry import ProviderRegistryError


def write_providers_file(tmp_path, content: dict) -> None:
    config_directory = tmp_path / ".aigit"
    config_directory.mkdir()

    (config_directory / "providers.json").write_text(
        json.dumps(content),
        encoding="utf-8",
    )


def test_missing_file_contains_only_fake_provider(tmp_path) -> None:
    registry = load_provider_registry(tmp_path)

    assert registry.get("fake").protocol == "fake"

    with pytest.raises(
        ProviderRegistryError,
        match="No usable AI provider",
    ):
        registry.select(None)


def test_loads_provider_definitions(tmp_path) -> None:
    write_providers_file(
        tmp_path,
        {
            "default": "openai",
            "providers": {
                "openai": {
                    "display_name": "OpenAI",
                    "protocol": "openai-compatible",
                    "base_url": "https://api.openai.com/v1",
                    "api_key_environment_variable": "OPENAI_API_KEY",
                    "default_model": "gpt-4o-mini",
                }
            },
        },
    )

    registry = load_provider_registry(tmp_path)
    definition = registry.get("openai")

    assert definition.name == "openai"
    assert definition.protocol == "openai-compatible"
    assert definition.base_url == "https://api.openai.com/v1"
    assert definition.default_model == "gpt-4o-mini"


def test_uses_configured_default_provider(tmp_path) -> None:
    write_providers_file(
        tmp_path,
        {
            "default": "openai",
            "providers": {
                "openai": {
                    "display_name": "OpenAI",
                    "protocol": "openai-compatible",
                    "base_url": "https://api.openai.com/v1",
                    "api_key_environment_variable": "OPENAI_API_KEY",
                    "default_model": "gpt-4o-mini",
                }
            },
        },
    )

    registry = load_provider_registry(tmp_path)

    assert registry.select(None).name == "openai"


def test_selects_single_real_provider_without_default(tmp_path) -> None:
    write_providers_file(
        tmp_path,
        {
            "providers": {
                "openai": {
                    "display_name": "OpenAI",
                    "protocol": "openai-compatible",
                    "base_url": "https://api.openai.com/v1",
                    "api_key_environment_variable": "OPENAI_API_KEY",
                    "default_model": "gpt-4o-mini",
                }
            },
        },
    )

    registry = load_provider_registry(tmp_path)

    assert registry.select(None).name == "openai"


def test_multiple_providers_require_default(tmp_path) -> None:
    provider = {
        "display_name": "Provider",
        "protocol": "openai-compatible",
        "base_url": "https://example.com/v1",
        "api_key_environment_variable": "EXAMPLE_API_KEY",
        "default_model": "example-model",
    }

    write_providers_file(
        tmp_path,
        {
            "providers": {
                "first": provider,
                "second": {
                    **provider,
                    "base_url": "https://second.example.com/v1",
                },
            },
        },
    )

    registry = load_provider_registry(tmp_path)

    with pytest.raises(
        ProviderRegistryError,
        match="Multiple providers",
    ):
        registry.select(None)


def test_explicit_provider_selection_overrides_default(tmp_path) -> None:
    provider = {
        "display_name": "Provider",
        "protocol": "openai-compatible",
        "base_url": "https://example.com/v1",
        "api_key_environment_variable": "EXAMPLE_API_KEY",
        "default_model": "example-model",
    }

    write_providers_file(
        tmp_path,
        {
            "default": "first",
            "providers": {
                "first": provider,
                "second": {
                    **provider,
                    "base_url": "https://second.example.com/v1",
                },
            },
        },
    )

    registry = load_provider_registry(tmp_path)

    assert registry.select("second").name == "second"


def test_unknown_provider_fails(tmp_path) -> None:
    registry = load_provider_registry(tmp_path)

    with pytest.raises(
        ProviderRegistryError,
        match="Provider 'missing' was not found",
    ):
        registry.select("missing")


def test_anthropic_protocol_is_supported(tmp_path) -> None:
    write_providers_file(
        tmp_path,
        {
            "providers": {
                "anthropic": {
                    "display_name": "Anthropic",
                    "protocol": "anthropic",
                    "base_url": None,
                    "api_key_environment_variable": "ANTHROPIC_API_KEY",
                    "default_model": "claude-test-model",
                }
            }
        },
    )

    registry = load_provider_registry(tmp_path)

    definition = registry.get("anthropic")

    assert definition.name == "anthropic"
    assert definition.display_name == "Anthropic"
    assert definition.protocol == "anthropic"
    assert definition.base_url is None
    assert definition.api_key_environment_variable == "ANTHROPIC_API_KEY"
    assert definition.default_model == "claude-test-model"


def test_unsupported_protocol_fails(tmp_path) -> None:
    write_providers_file(
        tmp_path,
        {
            "providers": {
                "unknown": {
                    "display_name": "Unknown",
                    "protocol": "unsupported",
                    "base_url": None,
                    "api_key_environment_variable": None,
                    "default_model": "unknown-model",
                }
            }
        },
    )

    with pytest.raises(
        ProviderDefinitionError,
        match="Unsupported provider protocol",
    ):
        load_provider_registry(tmp_path)


def test_missing_required_field_fails(tmp_path) -> None:
    write_providers_file(
        tmp_path,
        {
            "providers": {
                "openai": {
                    "display_name": "OpenAI",
                    "protocol": "openai-compatible",
                }
            },
        },
    )

    with pytest.raises(
        ProviderDefinitionError,
        match="missing",
    ):
        load_provider_registry(tmp_path)
