import argparse
import logging
from collections.abc import Sequence

from aigit.config.environment import load_environment
from aigit.config.loader import ConfigError, load_config
from aigit.git import GitError, GitRepository
from aigit.logging_config import configure_logging
from aigit.providers.factory import ProviderFactory
from aigit.providers.loader import ProviderDefinitionError
from aigit.workflows.commit import run_commit_workflow

logger = logging.getLogger(__name__)


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

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable detailed diagnostic logging.",
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
    configure_logging(args.debug)
    logger.debug("Starting command: %s", args.command)

    load_environment()

    try:
        config = load_config()
    except ConfigError as error:
        logger.debug("Configuration loading failed", exc_info=True)
        print(f"Configuration error: {error}")
        return 1

    if args.command == "commit":
        try:
            logger.debug(
                "Creating provider with configured name: %s",
                config.provider.name or "<automatic selection>",
            )
            provider = ProviderFactory().create(config.provider)
        except ProviderDefinitionError as error:
            logger.debug("Provider definition lookup failed", exc_info=True)
            print(f"Provider configuration error: {error}")
            return 1
        except Exception as error:
            logger.debug("Provider creation failed", exc_info=True)
            print(f"Provider error: {error}")
            return 1

        try:
            repository = GitRepository()
        except GitError as error:
            logger.debug("Git initialization failed", exc_info=True)
            print(f"Git error: {error}")
            return 1

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
