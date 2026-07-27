import logging
from typing import Any

from anthropic import Anthropic

from aigit.config.environment import get_required_environment_variable
from aigit.config.models import ProviderConfig
from aigit.providers.definitions import ProviderDefinition

logger = logging.getLogger(__name__)


class AnthropicProviderError(RuntimeError):
    pass


class AnthropicProvider:
    def __init__(
        self,
        config: ProviderConfig,
        definition: ProviderDefinition,
        client: Any | None = None,
    ) -> None:
        self.config = config
        self.definition = definition

        api_key_name = definition.api_key_environment_variable

        if not api_key_name:
            raise AnthropicProviderError(
                "Anthropic provider does not define an API key environment variable."
            )

        api_key = get_required_environment_variable(api_key_name)

        self.model = config.model or definition.default_model
        self.client = client or Anthropic(api_key=api_key)

    def generate_commit_message(self, diff: str) -> str:
        logger.debug(
            "Sending staged diff to Anthropic using model '%s' "
            "(diff length: %d characters)",
            self.model,
            len(diff),
        )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=self.config.temperature,
                system=self.config.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Staged Git diff:\n{diff}",
                    }
                ],
            )
        except Exception as error:
            logger.debug("Anthropic request failed", exc_info=True)
            raise AnthropicProviderError(
                f"Anthropic request failed: {error}"
            ) from error

        try:
            text_parts: list[str] = []

            for block in response.content:
                if getattr(block, "type", None) != "text":
                    continue

                text = getattr(block, "text", None)

                if isinstance(text, str):
                    text_parts.append(text)

            message = "".join(text_parts)
        except (AttributeError, TypeError) as error:
            raise AnthropicProviderError(
                "Anthropic returned an invalid response."
            ) from error

        if not message.strip():
            raise AnthropicProviderError("Anthropic returned an empty commit message.")

        return message.strip()
