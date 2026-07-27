import json
from pathlib import Path
from typing import Any

from aigit.providers.definitions import (
    FAKE_PROVIDER_DEFINITION,
    ProviderDefinition,
)
from aigit.providers.registry import ProviderRegistry


class ProviderDefinitionError(RuntimeError):
    pass


def load_provider_registry(
    project_root: Path | None = None,
) -> ProviderRegistry:
    root = project_root or Path.cwd()
    path = root / ".aigit" / "providers.json"

    definitions = {
        "fake": FAKE_PROVIDER_DEFINITION,
    }

    if not path.exists():
        return ProviderRegistry(definitions=definitions)

    try:
        raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ProviderDefinitionError(f"Invalid JSON in {path}: {error}") from error

    providers = raw.get("providers", {})

    if not isinstance(providers, dict):
        raise ProviderDefinitionError("'providers' must be an object.")

    for name, values in providers.items():
        if not isinstance(values, dict):
            raise ProviderDefinitionError(f"Provider '{name}' must be an object.")

        definitions[name] = _build_definition(name, values)

    default = raw.get("default")

    if default is not None and default not in definitions:
        raise ProviderDefinitionError(f"Default provider '{default}' was not found.")

    return ProviderRegistry(
        definitions=definitions,
        default=default,
    )


def _build_definition(
    name: str,
    values: dict[str, Any],
) -> ProviderDefinition:
    required_fields = (
        "display_name",
        "protocol",
        "base_url",
        "default_model",
    )

    missing_fields = [field for field in required_fields if field not in values]

    if missing_fields:
        raise ProviderDefinitionError(
            f"Provider '{name}' is missing: {', '.join(missing_fields)}"
        )

    protocol = values["protocol"]

    if protocol not in {"openai-compatible", "anthropic", "fake"}:
        raise ProviderDefinitionError(
            f"Unsupported provider protocol '{protocol}'. "
            "Supported protocols: openai-compatible, anthropic, fake."
        )

    return ProviderDefinition(
        name=name,
        display_name=values["display_name"],
        protocol=protocol,
        base_url=values["base_url"],
        api_key_environment_variable=values.get("api_key_environment_variable"),
        default_model=values["default_model"],
    )
