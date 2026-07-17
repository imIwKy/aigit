from aigit.config.models import ProviderConfig


class FakeProvider:
    def __init__(self, config: ProviderConfig) -> None:
        self.config = config

    def generate_commit_message(self, diff: str) -> str:
        return self.config.fake_message