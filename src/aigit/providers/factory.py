from aigit.config.models import ProviderConfig
from aigit.providers.definitions import PROVIDER_DEFINITIONS
from aigit.providers.fake import FakeProvider
from aigit.providers.openai import OpenAIProvider


class ProviderFactory:
    def create(self, config: ProviderConfig):
        definition = PROVIDER_DEFINITIONS.get(config.name)

        if definition is None:
            raise ValueError(f"Unknown provider: {config.name}")

        if definition.protocol == "fake":
            return FakeProvider(config)

        if definition.protocol == "openai":
            return OpenAIProvider(config, definition)

        raise ValueError(f"Unsupported provider protocol: {definition.protocol}")
