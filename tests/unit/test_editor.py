import subprocess
from pathlib import Path

import pytest

from aigit.workflows.commit import edit_commit_message


def fake_executable_finder(name: str) -> str:
    return f"/fake/bin/{name}"


def test_editor_returns_edited_message(monkeypatch) -> None:
    monkeypatch.setenv("VISUAL", "fake-editor --wait")
    commands: list[list[str]] = []

    def fake_editor_runner(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        commands.append(command)

        temporary_path = Path(command[-1])
        temporary_path.write_text(
            "fix: edited commit message\n\n- Correct behavior",
            encoding="utf-8",
        )

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )

    result = edit_commit_message(
        "feat: generated commit message",
        editor_runner=fake_editor_runner,
        executable_finder=fake_executable_finder,
    )

    assert result == "fix: edited commit message\n\n- Correct behavior"
    assert commands[0][0] == "/fake/bin/fake-editor"
    assert commands[0][1] == "--wait"
    assert "aigit-commit-" in commands[0][2]


def test_editor_preserves_paths_with_spaces(monkeypatch) -> None:
    monkeypatch.setenv("EDITOR", "fake-editor --wait")
    captured_command: list[str] = []

    def fake_editor_runner(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        captured_command.extend(command)

        Path(command[-1]).write_text(
            "chore: update message",
            encoding="utf-8",
        )

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )

    result = edit_commit_message(
        "chore: generated message",
        editor_runner=fake_editor_runner,
        executable_finder=lambda _: "C:/Program Files/Fake Editor/fake-editor.exe",
    )

    assert result == "chore: update message"
    assert captured_command[0] == ("C:/Program Files/Fake Editor/fake-editor.exe")
    assert captured_command[1] == "--wait"
    assert "aigit-commit-" in captured_command[2]


def test_editor_uses_default_editor_when_not_configured(
    monkeypatch,
) -> None:
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.delenv("EDITOR", raising=False)

    captured_command: list[str] = []

    def fake_editor_runner(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        captured_command.extend(command)

        Path(command[-1]).write_text(
            "docs: update commit message",
            encoding="utf-8",
        )

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )

    def fake_finder(name: str) -> str | None:
        if name == "notepad.exe":
            return "C:/Windows/System32/notepad.exe"

        if ":" in name:
            return name

        return f"C:/fake/{name}.exe"

    result = edit_commit_message(
        "docs: generated message",
        editor_runner=fake_editor_runner,
        executable_finder=fake_finder,
    )

    assert result == "docs: update commit message"
    assert captured_command[0] == "C:/Windows/System32/notepad.exe"


def test_editor_raises_when_executable_is_missing(
    monkeypatch,
) -> None:
    monkeypatch.setenv("EDITOR", "missing-editor")

    with pytest.raises(
        RuntimeError,
        match="was not found on PATH",
    ):
        edit_commit_message(
            "chore: generated message",
            executable_finder=lambda _: None,
        )


def test_editor_raises_when_process_fails(monkeypatch) -> None:
    monkeypatch.setenv("EDITOR", "fake-editor")

    def fake_editor_runner(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=command,
            returncode=1,
            stdout="",
            stderr="editor failed",
        )

    with pytest.raises(
        RuntimeError,
        match="Editor exited with status 1: editor failed",
    ):
        edit_commit_message(
            "chore: generated message",
            editor_runner=fake_editor_runner,
            executable_finder=fake_executable_finder,
        )


def test_editor_raises_when_edited_message_is_empty(
    monkeypatch,
) -> None:
    monkeypatch.setenv("EDITOR", "fake-editor")

    def fake_editor_runner(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        Path(command[-1]).write_text("", encoding="utf-8")

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )

    with pytest.raises(
        RuntimeError,
        match="Edited commit message cannot be empty",
    ):
        edit_commit_message(
            "chore: generated message",
            editor_runner=fake_editor_runner,
            executable_finder=fake_executable_finder,
        )
