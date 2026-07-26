from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderConfig:
    name: str | None = None
    model: str | None = None
    system_prompt: str = (
        "Generate a concise Conventional Commit message from the staged Git diff."
    )
    temperature: float = 0.2
    fake_message: str = "chore: update files"


@dataclass(frozen=True)
class CommitConfig:
    provider: str | None = None
    max_title_length: int = 72


@dataclass(frozen=True)
class AppConfig:
    provider: ProviderConfig
    commit: CommitConfig
