from aigit.git import GitError, GitRepositoryPort
from aigit.providers import LlmProvider


def run_commit_workflow(
    repository: GitRepositoryPort,
    provider: LlmProvider,
) -> int:
    if not repository.is_repository():
        print("Error: not inside a Git repository.")
        return 1

    try:
        diff = repository.staged_diff()
    except GitError as error:
        print(f"Error: {error}")
        return 1

    if not diff.strip():
        print("No staged changes found.")
        print("Stage changes with: git add <files>")
        return 1

    try:
        message = provider.generate_commit_message(diff).strip()
    except Exception as error:
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
        print("Commit cancelled.")
        return 0

    try:
        repository.commit(message)
    except GitError as error:
        print(f"Error creating commit: {error}")
        return 1

    print("Commit created.")
    return 0
