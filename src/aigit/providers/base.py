from typing import Protocol


class LlmProvider(Protocol):
    def generate_commit_message(self, diff: str) -> str:
        ...