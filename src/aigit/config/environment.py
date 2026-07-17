import os
from pathlib import Path

from dotenv import load_dotenv


def load_environment(project_root: Path | None = None) -> None:
    root = project_root or Path.cwd()

    global_env_path = Path.home() / ".config" / "aigit" / ".env"
    project_env_path = root / ".env"

    # Load global secrets first.
    load_dotenv(global_env_path)

    # Load project values only when they are not already defined globally.
    load_dotenv(project_env_path)


def get_required_environment_variable(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Required environment variable is not set: {name}"
        )

    return value