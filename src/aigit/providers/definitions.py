from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderDefinition:
    name: str
    display_name: str
    protocol: str
    base_url: str | None
    api_key_environment_variable: str | None
    default_model: str


PROVIDER_DEFINITIONS: dict[str, ProviderDefinition] = {
    "fake": ProviderDefinition(
        name="fake",
        display_name="Fake Provider",
        protocol="fake",
        base_url=None,
        api_key_environment_variable=None,
        default_model="fake-model",
    ),
    "openai": ProviderDefinition(
        name="openai",
        display_name="OpenAI",
        protocol="openai",
        base_url="https://api.openai.com/v1",
        api_key_environment_variable="OPENAI_API_KEY",
        default_model="gpt-4o-mini",
    ),
}
