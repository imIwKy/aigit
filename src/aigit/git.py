from subprocess import CompletedProcess, run
from typing import Protocol


class GitError(RuntimeError):
    pass


class GitRepositoryPort(Protocol):
    def is_repository(self) -> bool: ...

    def staged_diff(self) -> str: ...

    def commit(self, message: str) -> None: ...


class GitRepository:
    def _run(self, *args: str) -> CompletedProcess[str]:
        result = run(
            ["git", *args],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise GitError(result.stderr.strip() or "Git command failed")

        return result

    def is_repository(self) -> bool:
        result = run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
        )

        return result.returncode == 0 and result.stdout.strip() == "true"

    def staged_diff(self) -> str:
        return self._run("diff", "--cached").stdout

    def commit(self, message: str) -> None:
        self._run("commit", "-m", message)
