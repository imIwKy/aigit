from typing import Protocol


class LlmProvider(Protocol):
    def generate_commit_message(self, diff: str) -> str:
        ...


class FakeProvider:
    def generate_commit_message(self, diff: str) -> str:
        if "new file mode" in diff:
            return "feat: add example file"

        return "chore: update files"