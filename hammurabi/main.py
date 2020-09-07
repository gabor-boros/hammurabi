from enum import Enum
import logging
import os
from pathlib import Path
import sys

import github3
import typer

from hammurabi import Pillar, __version__
from hammurabi.config import (
    DEFAULT_ALLOW_PUSH,
    DEFAULT_DRY_RUN,
    DEFAULT_GENERATE_REPORT,
    DEFAULT_GITHUB_TOKEN,
    DEFAULT_LOG_LEVEL,
    DEFAULT_PROJECT_CONFIG,
    DEFAULT_REPOSITORY,
    config,
)

NON_ACTIONABLE_SUBCOMMANDS = ["version"]


class LoggingChoices(str, Enum):
    """
    Logging choices for CLI settings.
    """

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


app = typer.Typer()


def print_message(message: str, color: str, bold: bool, should_exit: bool, code: int):
    """
    Print formatted message and exit if requested.
    """

    typer.echo(typer.style(message, fg=color, bold=bold))

    if should_exit:
        sys.exit(code)


def error_message(message: str, should_exit: bool = True, code: int = 1):
    """
    Print error message and exit the CLI application
    """

    print_message(message, typer.colors.RED, True, should_exit, code)


def success_message(message: str):
    """
    Print error message and exit the CLI application
    """

    print_message(message, typer.colors.GREEN, True, False, 0)


@app.callback()
def main(
    ctx: typer.Context,
    cfg: Path = typer.Option(
        DEFAULT_PROJECT_CONFIG, "--config", "-c", help="Set the configuration file."
    ),
    repository: str = typer.Option(
        DEFAULT_REPOSITORY,
        help="Set the remote repository. Required format: owner/repository.",
    ),
    token: str = typer.Option(DEFAULT_GITHUB_TOKEN, help="Set github access token."),
    log_level: LoggingChoices = typer.Option(
        DEFAULT_LOG_LEVEL, help="Set logging level."
    ),
):
    """
    Hammurabi is an extensible CLI tool responsible for enforcing user-defined rules on a git
    repository.

    Find more information at: https://hammurabi.readthedocs.io/latest/
    """

    if ctx.invoked_subcommand in NON_ACTIONABLE_SUBCOMMANDS:
        return

    os.environ.setdefault("HAMMURABI_SETTINGS_PATH", str(cfg.expanduser()))

    try:
        # Reload the configuration
        config.load()
        success_message("Configuration loaded")
    except Exception as exc:  # pylint: disable=broad-except
        error_message(f"Failed to load configuration: {str(exc)}")
        return

    if token != DEFAULT_GITHUB_TOKEN:
        config.github = github3.login(token=token)

    if repository != DEFAULT_REPOSITORY:
        config.settings.repository = repository

    if log_level != DEFAULT_LOG_LEVEL:
        logging.root.setLevel(log_level.value)

    ctx.ensure_object(dict)
    ctx.obj["config"] = config


@app.command(short_help="Print hammurabi version.")
def version():
    """
    Print hammurabi version.
    """

    typer.echo(__version__)


@app.command(short_help="Execute registered laws.")
def enforce(
    ctx: typer.Context,
    dry_run: bool = typer.Option(DEFAULT_DRY_RUN, help="Execute laws in dry run mode."),
    allow_push: bool = typer.Option(DEFAULT_ALLOW_PUSH, help="Push changes to remote."),
    report: bool = typer.Option(
        DEFAULT_GENERATE_REPORT, help="Generate execution report."
    ),
):
    """
    The `enforce` command executes the laws registered on the pillar. But the command
    has other responsibilities too. It will make sure the execution report is generated
    and controls if the changes are pushed to remote or not.
    """

    if allow_push != DEFAULT_ALLOW_PUSH:
        ctx.obj["config"].settings.allow_push = allow_push

    if dry_run != DEFAULT_DRY_RUN:
        ctx.obj["config"].settings.dry_run = dry_run

    pillar: Pillar = ctx.obj["config"].settings.pillar
    pillar.enforce()
    success_message("Finished successfully")

    if report:
        pillar.reporter.report()
        success_message("Report generated")


if __name__ == "__main__":
    app()
