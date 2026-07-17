from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderConfig:
    name: str = "fake"
    model: str | None = None
    system_prompt: str = (
        "Generate a Conventional Commit message from the provided Git diff. "
        "Return only the commit message. "
        "Do not wrap it in quotes or Markdown code fences."
    )
    temperature: float = 0.2
    fake_message: str = "chore: update files"


@dataclass(frozen=True)
class CommitConfig:
    max_title_length: int = 72


@dataclass(frozen=True)
class AppConfig:
    provider: ProviderConfig
    commit: CommitConfig