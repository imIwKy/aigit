import json
from pathlib import Path
from typing import Any

from aigit.config.models import AppConfig, CommitConfig, ProviderConfig


class ConfigError(RuntimeError):
    pass


def load_config(project_root: Path | None = None) -> AppConfig:
    root = project_root or Path.cwd()
    config_path = root / ".aigit" / "config.json"

    if not config_path.exists():
        return AppConfig(
            provider=ProviderConfig(),
            commit=CommitConfig(),
        )

    try:
        raw_config: dict[str, Any] = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ConfigError(f"Invalid JSON in {config_path}: {error}") from error
    except OSError as error:
        raise ConfigError(f"Unable to read {config_path}: {error}") from error

    provider_values = raw_config.get("provider", {})
    commit_values = raw_config.get("commit", {})

    return AppConfig(
        provider=ProviderConfig(
            name=provider_values.get("name", "fake"),
            model=provider_values.get("model"),
            system_prompt=provider_values.get(
                "system_prompt",
                ProviderConfig().system_prompt,
            ),
            temperature=provider_values.get("temperature", 0.2),
            fake_message=provider_values.get(
                "fake_message",
                "chore: update files",
            ),
        ),
        commit=CommitConfig(
            max_title_length=commit_values.get("max_title_length", 72),
        ),
    )
