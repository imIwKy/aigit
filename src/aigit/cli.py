import argparse
from collections.abc import Sequence

from aigit.git import GitRepository
from aigit.providers import FakeProvider
from aigit.workflows.commit import run_commit_workflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aigit",
        description="AI-assisted Git workflow tools.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="aigit 0.1.0",
    )

    commands = parser.add_subparsers(
        dest="command",
        required=True,
        title="commands",
    )

    commands.add_parser(
        "commit",
        help="Generate a commit message from staged changes.",
    )

    commands.add_parser(
        "docs",
        help="Synchronize documentation with recent changes.",
    )

    commands.add_parser(
        "pr",
        help="Generate and create a pull request.",
    )

    return parser


def run_command(args: argparse.Namespace) -> int:
    if args.command == "commit":
        repository = GitRepository()
        provider = FakeProvider()

        return run_commit_workflow(repository, provider)

    if args.command == "docs":
        print("docs workflow not implemented")
        return 0

    if args.command == "pr":
        print("pr workflow not implemented")
        return 0

    return 1


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    raise SystemExit(run_command(args))