from typing import Any

from openai import OpenAI

from aigit.config.environment import get_required_environment_variable
from aigit.config.models import ProviderConfig
from aigit.providers.definitions import ProviderDefinition


class OpenAIProviderError(RuntimeError):
    pass


class OpenAICompatibleProvider:
    def __init__(
        self,
        config: ProviderConfig,
        definition: ProviderDefinition,
        client: Any | None = None,
    ) -> None:
        self.config = config
        self.definition = definition

        api_key_name = definition.api_key_environment_variable
        api_key = "local"

        if api_key_name:
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
                        "content": f"Staged Git diff:\n{diff}",
                    },
                ],
            )
        except Exception as error:
            raise OpenAIProviderError(f"OpenAI request failed: {error}") from error

        try:
            message = response.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as error:
            raise OpenAIProviderError("OpenAI returned an invalid response.") from error

        if not message or not message.strip():
            raise OpenAIProviderError("OpenAI returned an empty commit message.")

        return clean_commit_message(message)


def clean_commit_message(message: str) -> str:
    cleaned = message.strip()

    # Remove Markdown code fences:
    # ```text
    # feat: example
    # ```
    if cleaned.startswith("```") and cleaned.endswith("```"):
        lines = cleaned.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    # Remove triple quote wrappers.
    for quote in ("'''", '"""'):
        if cleaned.startswith(quote) and cleaned.endswith(quote):
            cleaned = cleaned[len(quote) : -len(quote)].strip()
            break

    # Remove single quote wrappers around the entire message.
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {"'", '"'}:
        cleaned = cleaned[1:-1].strip()

    return cleaned


OpenAIProvider = OpenAICompatibleProvider
