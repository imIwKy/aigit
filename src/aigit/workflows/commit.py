import logging
import os
import shlex
import shutil
import subprocess  # nosec B404 - required to launch the configured editor
import tempfile
from pathlib import Path
from typing import Callable

from aigit.git import GitError, GitRepositoryPort
from aigit.providers import LlmProvider

logger = logging.getLogger(__name__)
editor_logger = logging.getLogger("aigit.editor")


EditorRunner = Callable[..., subprocess.CompletedProcess[str]]
ExecutableFinder = Callable[[str], str | None]


def validate_commit_title(
    message: str,
    max_title_length: int,
) -> str | None:
    if max_title_length <= 0:
        raise ValueError("Maximum commit title length must be greater than zero.")

    title = message.splitlines()[0] if message.splitlines() else ""

    if len(title) > max_title_length:
        return (
            f"Commit title is {len(title)} characters long; "
            f"the maximum is {max_title_length}."
        )

    return None


def edit_commit_message(
    message: str,
    *,
    editor_runner: EditorRunner | None = None,
    executable_finder: ExecutableFinder | None = None,
) -> str:
    run_editor = editor_runner or subprocess.run
    find_executable = executable_finder or shutil.which

    configured_editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")

    if configured_editor:
        command = shlex.split(
            configured_editor,
            posix=os.name != "nt",
        )

        if os.name == "nt":
            command = [argument.strip('"') for argument in command]

        executable = find_executable(command[0])

        if executable is None:
            raise RuntimeError(
                f"Configured editor '{command[0]}' was not found on PATH. "
                "Set VISUAL or EDITOR to an installed editor."
            )

        command[0] = executable
    else:
        executable = find_executable("notepad.exe")

        if executable is None:
            raise RuntimeError(
                "No editor configured. Set the VISUAL or EDITOR environment variable."
            )

        command = [executable]

    if executable is None:
        raise RuntimeError(
            f"Configured editor '{command[0]}' was not found on PATH. "
            "Set VISUAL or EDITOR to an installed editor."
        )

    command[0] = executable

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".txt",
        prefix="aigit-commit-",
        delete=False,
    ) as temporary_file:
        temporary_file.write(message)
        temporary_file.write("\n")
        temporary_path = Path(temporary_file.name)

    try:
        command.append(str(temporary_path))

        editor_logger.debug("Temporary commit file: %s", temporary_path)
        editor_logger.debug("Launching editor command: %r", command)

        result = run_editor(
            command,
            check=False,
            shell=False,
            capture_output=True,
            text=True,
        )

        for line in result.stdout.splitlines():
            editor_logger.debug("stdout: %s", line)

        for line in result.stderr.splitlines():
            editor_logger.debug("stderr: %s", line)

        if result.returncode != 0:
            error_detail = result.stderr.strip()

            if error_detail:
                raise RuntimeError(
                    f"Editor exited with status {result.returncode}: {error_detail}"
                )

            raise RuntimeError(f"Editor exited with status {result.returncode}.")

        edited_message = temporary_path.read_text(
            encoding="utf-8",
        ).strip()

        if not edited_message:
            raise RuntimeError("Edited commit message cannot be empty.")

        return edited_message
    finally:
        temporary_path.unlink(missing_ok=True)


def run_commit_workflow(
    repository: GitRepositoryPort, provider: LlmProvider, max_title_length: int = 72
) -> int:
    logger.debug("Starting commit workflow")

    if not repository.is_repository():
        logger.debug("Current directory is not a Git repository")
        print("Error: not inside a Git repository.")
        return 1

    try:
        diff = repository.staged_diff()
    except GitError as error:
        logger.debug("Unable to read staged diff", exc_info=True)
        print(f"Error: {error}")
        return 1

    if not diff.strip():
        logger.debug("No staged changes found")
        print("No staged changes found.")
        print("Stage changes with: git add <files>")
        return 1

    try:
        message = provider.generate_commit_message(diff).strip()
    except Exception as error:
        logger.debug("Provider failed to generate a commit message", exc_info=True)
        print(f"Error generating commit message: {error}")
        return 1

    if not message:
        print("Error: provider returned an empty commit message.")
        return 1

    while True:
        print("\nSuggested commit message:")
        print("--------------------------------")
        print(message)
        print("--------------------------------")

        answer = (
            input("Choose an action: [y]es, [e]dit, [r]egenerate, [N]o: ")
            .strip()
            .lower()
        )

        if answer in {"", "n", "no", "c", "cancel"}:
            logger.debug("User cancelled commit")
            print("Commit cancelled.")
            return 0

        if answer in {"y", "yes"}:
            validation_error = validate_commit_title(
                message,
                max_title_length,
            )

            if validation_error:
                print(f"Cannot create commit: {validation_error}")
                print("Edit or regenerate the message.")
                continue

            break

        if answer in {"e", "edit"}:
            try:
                message = edit_commit_message(message)
            except (OSError, RuntimeError) as error:
                logger.debug("Commit message editing failed", exc_info=True)
                print(f"Error editing commit message: {error}")
                return 1

            continue

        if answer in {"r", "retry", "regenerate"}:
            logger.debug("Regenerating commit message")

            try:
                message = provider.generate_commit_message(diff).strip()
            except Exception as error:
                logger.debug(
                    "Provider failed during message regeneration",
                    exc_info=True,
                )
                print(f"Error generating commit message: {error}")
                return 1

            if not message:
                print("Error: provider returned an empty commit message.")
                return 1

            continue

        print("Invalid choice. Select y, e, r, or n.")

    try:
        repository.commit(message)
    except GitError as error:
        logger.debug("Git commit failed", exc_info=True)
        print(f"Error creating commit: {error}")
        return 1

    print("Commit created.")
    return 0
