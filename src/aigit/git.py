import shutil
import subprocess  # nosec B404 - required to invoke Git safely
from subprocess import CompletedProcess  # nosec B404 - required to invoke Git safely
from typing import Protocol


class GitError(RuntimeError):
    """Raised when a Git command cannot be executed successfully."""


class GitRepositoryPort(Protocol):
    def is_repository(self) -> bool: ...

    def staged_diff(self) -> str: ...

    def commit(self, message: str) -> None: ...


class GitRepository:
    def __init__(self) -> None:
        git_executable = shutil.which("git")

        if git_executable is None:
            raise GitError("Git executable was not found on PATH.")

        self.git_executable: str = git_executable

    def _run(self, *args: str) -> CompletedProcess[str]:
        result = subprocess.run(  # nosec B603
            [self.git_executable, *args],
            capture_output=True,
            text=True,
            shell=False,
        )

        if result.returncode != 0:
            raise GitError(result.stderr.strip() or "Git command failed")

        return result

    def is_repository(self) -> bool:
        result = subprocess.run(  # nosec B603
            [
                self.git_executable,
                "rev-parse",
                "--is-inside-work-tree",
            ],
            capture_output=True,
            text=True,
            shell=False,
        )

        return result.returncode == 0 and result.stdout.strip() == "true"

    def staged_diff(self) -> str:
        return self._run("diff", "--cached").stdout

    def commit(self, message: str) -> None:
        self._run("commit", "-m", message)
