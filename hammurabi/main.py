import logging
from pathlib import Path

import click
from github3 import login

from hammurabi import Pillar, __version__
from hammurabi.config import config


@click.group()
@click.pass_context
@click.option(
    "-c",
    "--config",
    "cfg",
    type=click.Path(exists=True),
    default="pyproject.toml",
    show_default=True,
    help="Set the configuration file.",
)
@click.option(
    "--target",
    type=click.Path(exists=True),
    default=None,
    help="Set target path. If target is a git repo, commits will be created.",
)
@click.option(
    "--repository",
    type=click.STRING,
    default=None,
    help="Set the remote repository. Required format: owner/repository",
)
@click.option(
    "--github-token", type=click.STRING, default=None, help="Set github access token"
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default=None,
    help="Set logging level.",
)
def cli(
    ctx: click.Context,
    cfg: click.Path,
    target: click.Path,
    repository: str,
    github_token: str,
    log_level: str,
):
    """
    Hammurabi is an extensible CLI tool responsible for enforcing user-defined rules on a git
    repository.

    Find more information at: https://hammurabi.readthedocs.io/latest/
    """

    try:
        config.load(str(cfg))
    except KeyError as exc:
        raise click.ClickException(str(exc))

    if target:
        config.repo = Path(str(target))

    if repository:
        config.repo = repository

    if github_token:
        config.github = login(github_token)

    if log_level:
        config.log_level = log_level
        logging.root.setLevel(config.log_level)

    ctx.ensure_object(dict)
    ctx.obj["config"] = config


@cli.command()
def version():
    """
    Print Hammurabi version.
    """

    click.echo(__version__)


@cli.command()
@click.option(
    "-a",
    "--rule-can-abort",
    is_flag=True,
    default=False,
    type=click.BOOL,
    help="Abort the law when a rule raise an exception.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    type=click.BOOL,
    help="Execute in dry run mode.",
)
@click.pass_context
def enforce(ctx: click.Context, rule_can_abort: bool, dry_run: bool):
    """
    Execute all registered Law.
    """

    if dry_run:
        ctx.obj["config"].dry_run = dry_run

    if rule_can_abort:
        ctx.obj["config"].rule_can_abort = rule_can_abort

    pillar: Pillar = ctx.obj["config"].pillar
    pillar.enforce()


@cli.group()
def get():
    """
    Show a specific resource or group of resources.
    """


@get.command(name="order")
@click.pass_context
def get_order(ctx: click.Context):
    """
    Show the Pillar's execution order.
    """

    pillar: Pillar = ctx.obj["config"].pillar

    for law in pillar.laws:
        click.echo(f"- {law.name}")

        for rule in law.get_execution_order():
            click.echo(f"  --> {rule.name}")


@get.command(name="laws")
@click.pass_context
def get_laws(ctx: click.Context):
    """
    Show the registered Laws and rules on the Pillar.
    """

    pillar: Pillar = ctx.obj["config"].pillar

    for law in pillar.laws:
        click.echo(f"- {law.name}")


@get.command(name="law", help="Specific law to get")
@click.argument("law", type=click.STRING)
@click.pass_context
def get_law(ctx: click.Context, law: str):
    """
    Show specific registered Law.
    """

    pillar: Pillar = ctx.obj["config"].pillar

    try:
        registered_law = pillar.get_law(law)
    except StopIteration:
        raise click.ClickException(click.style(f'No such law "{law}"', fg="red"))

    click.echo(f"{registered_law.documentation}")


@get.command(name="rules")
@click.pass_context
def get_rules(ctx: click.Context):
    """
    TODO
    """

    pillar: Pillar = ctx.obj["config"].pillar

    for rule in pillar.rules:
        click.echo(f"- {rule.name}")


@get.command(name="rule")
@click.argument("rule", type=click.STRING)
@click.pass_context
def get_rule(ctx: click.Context, rule: str):
    """
    Specific rule to get.
    """

    pillar: Pillar = ctx.obj["config"].pillar

    try:
        registered_rule = pillar.get_rule(rule)
    except StopIteration:
        raise click.ClickException(click.style(f'No such rule "{rule}"', fg="red"))

    click.echo(f"{registered_rule.documentation}")


@cli.group()
def describe():
    """
    Show details of a specific resource or group of resources.
    """


@describe.command(name="law", help="Specific law to describe")
@click.argument("law", type=click.STRING)
@click.pass_context
def describe_law(ctx: click.Context, law: str):
    """
    Show details of the given Law.
    """

    pillar: Pillar = ctx.obj["config"].pillar
    registered_law = pillar.get_law(law)

    if not registered_law:
        raise click.ClickException(click.style(f'No such law "{law}"', fg="red"))

    click.echo(f"{registered_law.documentation}")
    click.echo(f"Rules:")
    for rule in registered_law.get_execution_order():
        click.echo(f"  --> {rule.name}")


@describe.command(name="rule")
@click.argument("rule", type=click.STRING)
@click.pass_context
def describe_rule(ctx: click.Context, rule: str):
    """
    Specific rule to describe.
    """

    pillar: Pillar = ctx.obj["config"].pillar
    registered_rule = pillar.get_rule(rule)

    if not registered_rule:
        raise click.ClickException(click.style(f'No such rule "{rule}"', fg="red"))

    click.echo(f"{registered_rule.documentation}")

    click.echo(f"Chain:")
    for chain in registered_rule.get_execution_order():
        click.echo(f"  --> {chain.name}")
