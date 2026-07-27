from aigit.workflows.commit import run_commit_workflow


class FakeRepository:
    def __init__(
        self,
        *,
        is_repo: bool = True,
        diff: str = "diff --git a/example.txt b/example.txt",
    ) -> None:
        self.repo_exists = is_repo
        self.diff = diff
        self.committed_messages: list[str] = []

    def is_repository(self) -> bool:
        return self.repo_exists

    def staged_diff(self) -> str:
        return self.diff

    def commit(self, message: str) -> None:
        self.committed_messages.append(message)


class FakeProvider:
    def __init__(self, message: str = "feat: add example file") -> None:
        self.message = message
        self.received_diff: str | None = None

    def generate_commit_message(self, diff: str) -> str:
        self.received_diff = diff
        return self.message


def test_commit_is_created_when_user_accepts(monkeypatch) -> None:
    repository = FakeRepository()
    provider = FakeProvider()

    monkeypatch.setattr("builtins.input", lambda _: "y")

    result = run_commit_workflow(repository, provider)

    assert result == 0
    assert repository.committed_messages == ["feat: add example file"]
    assert provider.received_diff == repository.diff


def test_commit_is_not_created_when_user_rejects(monkeypatch) -> None:
    repository = FakeRepository()
    provider = FakeProvider()

    monkeypatch.setattr("builtins.input", lambda _: "n")

    result = run_commit_workflow(repository, provider)

    assert result == 0
    assert repository.committed_messages == []


def test_commit_fails_without_staged_changes(capsys) -> None:
    repository = FakeRepository(diff="")
    provider = FakeProvider()

    result = run_commit_workflow(repository, provider)

    assert result == 1
    assert repository.committed_messages == []
    assert provider.received_diff is None
    assert "No staged changes found." in capsys.readouterr().out


def test_commit_fails_outside_git_repository(capsys) -> None:
    repository = FakeRepository(is_repo=False)
    provider = FakeProvider()

    result = run_commit_workflow(repository, provider)

    assert result == 1
    assert repository.committed_messages == []
    assert "not inside a Git repository" in capsys.readouterr().out


def test_commit_fails_when_provider_returns_empty_message(capsys) -> None:
    repository = FakeRepository()
    provider = FakeProvider(message="")

    result = run_commit_workflow(repository, provider)

    assert result == 1
    assert repository.committed_messages == []
    assert "empty commit message" in capsys.readouterr().out


def test_commit_uses_manually_edited_message(monkeypatch) -> None:
    repository = FakeRepository()
    provider = FakeProvider()

    monkeypatch.setattr(
        "aigit.workflows.commit.edit_commit_message",
        lambda message: "fix: edited commit message",
    )
    monkeypatch.setattr("builtins.input", lambda _: "e")

    # The implementation should then prompt again for final approval.
    answers = iter(["e", "y"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    result = run_commit_workflow(repository, provider)

    assert result == 0
    assert repository.committed_messages == [
        "fix: edited commit message",
    ]


def test_commit_can_regenerate_message(monkeypatch) -> None:
    repository = FakeRepository()
    provider = FakeProvider(message="feat: regenerated message")

    answers = iter(["r", "y"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    result = run_commit_workflow(repository, provider)

    assert result == 0
    assert repository.committed_messages == [
        "feat: regenerated message",
    ]
    assert provider.received_diff == repository.diff
