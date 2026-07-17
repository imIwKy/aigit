import pytest

from aigit.config.environment import (
    get_required_environment_variable,
    load_environment,
)


def test_load_environment_reads_project_env_file(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("TEST_AIGIT_SECRET", raising=False)

    env_file = tmp_path / ".env"
    env_file.write_text(
        "TEST_AIGIT_SECRET=from-dotenv\n",
        encoding="utf-8",
    )

    load_environment(tmp_path)

    assert get_required_environment_variable("TEST_AIGIT_SECRET") == ("from-dotenv")


def test_existing_environment_variable_takes_precedence(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("TEST_AIGIT_SECRET", "from-shell")

    env_file = tmp_path / ".env"
    env_file.write_text(
        "TEST_AIGIT_SECRET=from-dotenv\n",
        encoding="utf-8",
    )

    load_environment(tmp_path)

    assert get_required_environment_variable("TEST_AIGIT_SECRET") == ("from-shell")


def test_missing_required_environment_variable_raises(monkeypatch) -> None:
    monkeypatch.delenv("MISSING_AIGIT_SECRET", raising=False)

    with pytest.raises(
        RuntimeError,
        match="Required environment variable is not set",
    ):
        get_required_environment_variable("MISSING_AIGIT_SECRET")


def test_missing_env_file_is_allowed(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("TEST_AIGIT_SECRET", raising=False)

    load_environment(tmp_path)

    with pytest.raises(RuntimeError):
        get_required_environment_variable("TEST_AIGIT_SECRET")
