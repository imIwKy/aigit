from typing import Any

from openai import OpenAI

from aigit.config.environment import get_required_environment_variable
from aigit.config.models import ProviderConfig
from aigit.providers.definitions import ProviderDefinition


class OpenAIProviderError(RuntimeError):
    pass


class OpenAIProvider:
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
            raise OpenAIProviderError(
                "OpenAI provider has no API key environment variable configured."
            )

        api_key = get_required_environment_variable(api_key_name)

        self.model = config.model or definition.default_model
        self.client = client or OpenAI(
            api_key=api_key,
            base_url=definition.base_url,
        )

    def generate_commit_message(self, diff: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.config.temperature,
                messages=[
                    {
                        "role": "system",
                        "content": self.config.system_prompt,
                    },
                    {
                        "role": "user",
                        "content": (
                            "Generate a Conventional Commit message based on "
                            "this staged Git diff.\n\n"
                            "Rules:\n"
                            "- Keep the title under 72 characters.\n"
                            "- Do not invent changes.\n"
                            "- Include body bullets only if useful.\n\n"
                            f"Git diff:\n{diff}"
                        ),
                    },
                ],
            )
        except Exception as error:
            raise OpenAIProviderError(
                f"OpenAI request failed: {error}"
            ) from error

        try:
            message = response.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as error:
            raise OpenAIProviderError(
                "OpenAI returned an invalid response."
            ) from error

        if not message or not message.strip():
            raise OpenAIProviderError(
                "OpenAI returned an empty commit message."
            )

        return message.strip()