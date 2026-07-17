import json

import pytest

from aigit.config.loader import ConfigError, load_config
from aigit.config.models import ProviderConfig
from aigit.providers import FakeProvider


def test_load_config_returns_defaults_when_file_is_missing(tmp_path) -> None:
    config = load_config(tmp_path)

    assert config.provider.name == "fake"
    assert config.provider.model is None
    assert config.provider.temperature == 0.2
    assert config.commit.max_title_length == 72


def test_load_config_reads_project_config(tmp_path) -> None:
    config_directory = tmp_path / ".aigit"
    config_directory.mkdir()

    config_file = config_directory / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "provider": {
                    "name": "fake",
                    "model": "test-model",
                    "system_prompt": "Use project-specific rules.",
                    "temperature": 0.7,
                    "fake_message": "feat: configured message",
                },
                "commit": {
                    "max_title_length": 60,
                },
            }
        ),
        encoding="utf-8",
    )

    config = load_config(tmp_path)

    assert config.provider.name == "fake"
    assert config.provider.model == "test-model"
    assert config.provider.system_prompt == "Use project-specific rules."
    assert config.provider.temperature == 0.7
    assert config.provider.fake_message == "feat: configured message"
    assert config.commit.max_title_length == 60


def test_load_config_uses_defaults_for_missing_values(tmp_path) -> None:
    config_directory = tmp_path / ".aigit"
    config_directory.mkdir()

    config_file = config_directory / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "provider": {
                    "model": "partial-model",
                },
            }
        ),
        encoding="utf-8",
    )

    config = load_config(tmp_path)

    assert config.provider.model == "partial-model"
    assert config.provider.name == "fake"
    assert config.provider.temperature == 0.2
    assert config.commit.max_title_length == 72


def test_load_config_rejects_invalid_json(tmp_path) -> None:
    config_directory = tmp_path / ".aigit"
    config_directory.mkdir()

    config_file = config_directory / "config.json"
    config_file.write_text("{ invalid json", encoding="utf-8")

    with pytest.raises(ConfigError, match="Invalid JSON"):
        load_config(tmp_path)


def test_fake_provider_uses_configured_message() -> None:
    provider_config = ProviderConfig(
        fake_message="feat: message from configuration",
    )
    provider = FakeProvider(provider_config)

    result = provider.generate_commit_message("some diff")

    assert result == "feat: message from configuration"