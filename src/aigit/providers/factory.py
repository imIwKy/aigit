import logging

from aigit.config.models import ProviderConfig
from aigit.providers.fake import FakeProvider
from aigit.providers.loader import load_provider_registry
from aigit.providers.openai_compatible import (
    OpenAICompatibleProvider,
)
from aigit.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)


class ProviderFactory:
    def __init__(
        self,
        registry: ProviderRegistry | None = None,
    ) -> None:
        self.registry = registry or load_provider_registry()

    def create(self, config: ProviderConfig):
        definition = self.registry.select(config.name)

        logger.debug(
            "Selected provider '%s' using protocol '%s'",
            definition.name,
            definition.protocol,
        )

        if definition.protocol == "fake":
            logger.debug("Creating fake provider")
            return FakeProvider(config)

        if definition.protocol == "openai-compatible":
            logger.debug(
                "Creating OpenAI-compatible provider: base_url=%s, model=%s",
                definition.base_url,
                config.model or definition.default_model,
            )
            return OpenAICompatibleProvider(config, definition)

        raise ValueError(f"Unsupported provider protocol: {definition.protocol}")
