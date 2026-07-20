from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderDefinition:
    name: str
    display_name: str
    protocol: str
    base_url: str | None
    api_key_environment_variable: str | None
    default_model: str


FAKE_PROVIDER_DEFINITION = ProviderDefinition(
    name="fake",
    display_name="Fake Provider",
    protocol="fake",
    base_url=None,
    api_key_environment_variable=None,
    default_model="fake-model",
)
