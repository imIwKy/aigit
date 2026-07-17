import argparse
from collections.abc import Sequence

from aigit.config.environment import load_environment
from aigit.config.loader import ConfigError, load_config
from aigit.git import GitRepository
from aigit.providers.factory import ProviderFactory
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
    load_environment()

    try:
        config = load_config()
    except ConfigError as error:
        print(f"Configuration error: {error}")
        return 1

    if args.command == "commit":
        try:
            provider = ProviderFactory().create(config.provider)
        except Exception as error:
            print(f"Provider error: {error}")
            return 1

        return run_commit_workflow(
            GitRepository(),
            provider,
        )

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
