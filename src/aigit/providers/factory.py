from aigit.config.models import ProviderConfig
from aigit.providers.fake import FakeProvider
from aigit.providers.loader import load_provider_registry
from aigit.providers.openai_compatible import (
    OpenAICompatibleProvider,
)
from aigit.providers.registry import ProviderRegistry


class ProviderFactory:
    def __init__(
        self,
        registry: ProviderRegistry | None = None,
    ) -> None:
        self.registry = registry or load_provider_registry()

    def create(self, config: ProviderConfig):
        definition = self.registry.select(config.name)

        if definition.protocol == "fake":
            return FakeProvider(config)

        if definition.protocol == "openai-compatible":
            return OpenAICompatibleProvider(
                config,
                definition,
            )

        raise ValueError(f"Unsupported provider protocol: {definition.protocol}")
