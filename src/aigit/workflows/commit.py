import logging

from aigit.git import GitError, GitRepositoryPort
from aigit.providers import LlmProvider

logger = logging.getLogger(__name__)


def run_commit_workflow(
    repository: GitRepositoryPort,
    provider: LlmProvider,
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

    logger.debug("Read staged diff containing %d characters", len(diff))

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

    print("\nSuggested commit message:")
    print("--------------------------------")
    print(message)
    print("--------------------------------")

    answer = input("Create this commit? [y/N]: ").strip().lower()

    if answer not in {"y", "yes"}:
        logger.debug("User declined commit")
        print("Commit cancelled.")
        return 0

    try:
        repository.commit(message)
    except GitError as error:
        logger.debug("Git commit failed", exc_info=True)
        print(f"Error creating commit: {error}")
        return 1

    print("Commit created.")
    return 0
