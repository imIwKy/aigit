import logging
from dataclasses import dataclass

from aigit.providers.definitions import ProviderDefinition


class ProviderRegistryError(RuntimeError):
    pass


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProviderRegistry:
    definitions: dict[str, ProviderDefinition]
    default: str | None = None

    def get(self, name: str) -> ProviderDefinition:
        definition = self.definitions.get(name)

        if definition is None:
            raise ProviderRegistryError(f"Provider '{name}' was not found.")

        return definition

    def select(self, requested_name: str | None) -> ProviderDefinition:
        if requested_name:
            logger.debug("Selecting explicitly requested provider: %s", requested_name)
            return self.get(requested_name)

        if self.default:
            logger.debug("Selecting registry default provider: %s", self.default)
            return self.get(self.default)

        non_fake = [
            definition
            for definition in self.definitions.values()
            if definition.protocol != "fake"
        ]

        if len(non_fake) == 1:
            return non_fake[0]

        if len(non_fake) > 1:
            raise ProviderRegistryError(
                "Multiple providers are configured, but no default "
                "provider is selected. Set provider.name or providers.default."
            )

        raise ProviderRegistryError(
            "No usable AI provider is configured. Add a provider to "
            ".aigit/providers.json or explicitly select the fake provider."
        )
