from pathlib import Path
from unittest.mock import Mock, call, patch

import click
import pytest
import typer
from typer.colors import GREEN, RED

from hammurabi import __version__
from hammurabi.main import (
    DEFAULT_GITHUB_TOKEN,
    DEFAULT_LOG_LEVEL,
    DEFAULT_PROJECT_CONFIG,
    DEFAULT_REPOSITORY,
    NON_ACTIONABLE_SUBCOMMANDS,
    LoggingChoices,
    enforce,
    error_message,
    main,
    print_message,
    success_message,
    version,
)


@patch("hammurabi.main.typer")
def test_print_message(mock_typer):
    mocked_styled_message = Mock()
    mock_typer.style.return_value = mocked_styled_message

    expected_message = "test"
    expected_color = GREEN
    expected_is_bold = True
    expected_should_exit = False
    exit_code = 0

    print_message(
        expected_message,
        expected_color,
        expected_is_bold,
        expected_should_exit,
        exit_code,
    )

    mock_typer.style.assert_called_once_with(
        expected_message, fg=expected_color, bold=expected_is_bold
    )
    mock_typer.echo.assert_called_once_with(mocked_styled_message)


@patch("hammurabi.main.sys")
@patch("hammurabi.main.typer")
def test_print_message_with_exit(mock_typer, mock_sys):
    mocked_styled_message = Mock()
    mock_typer.style.return_value = mocked_styled_message

    expected_message = "test"
    expected_color = GREEN
    expected_is_bold = True
    expected_should_exit = True
    expected_exit_code = 0

    print_message(
        expected_message,
        expected_color,
        expected_is_bold,
        expected_should_exit,
        expected_exit_code,
    )

    mock_typer.style.assert_called_once_with(
        expected_message, fg=expected_color, bold=expected_is_bold
    )
    mock_typer.echo.assert_called_once_with(mocked_styled_message)
    mock_sys.exit.assert_called_once_with(expected_exit_code)


@patch("hammurabi.main.print_message")
def test_success_message_printed(mock_print):
    expected_message = "test"
    expected_color = GREEN
    expected_is_bold = True
    expected_should_exit = False
    expected_exit_code = 0

    success_message(expected_message)

    mock_print.assert_called_once_with(
        expected_message,
        expected_color,
        expected_is_bold,
        expected_should_exit,
        expected_exit_code,
    )


@patch("hammurabi.main.print_message")
def test_error_message_printed(mock_print):
    expected_message = "test"
    expected_color = RED
    expected_is_bold = True
    expected_should_exit = True
    expected_exit_code = 1

    error_message(expected_message)

    mock_print.assert_called_once_with(
        expected_message,
        expected_color,
        expected_is_bold,
        expected_should_exit,
        expected_exit_code,
    )


@patch("hammurabi.main.logging")
@patch("hammurabi.main.github3")
@patch("hammurabi.main.success_message")
@patch("hammurabi.main.config")
@patch("hammurabi.main.os")
def test_main_intermediate_actions(
    mock_os, mock_config, mock_success_message, mock_github, mock_logging
):
    ctx = Mock()
    ctx.invoked_subcommand = "fakecommand"
    ctx.obj = dict()

    # Passing default params, because typer not resolves the
    # typer.Option parameter assignments (since it is not an
    # integration test)
    main(
        ctx,
        Path(DEFAULT_PROJECT_CONFIG),
        DEFAULT_REPOSITORY,
        DEFAULT_GITHUB_TOKEN,
        LoggingChoices.DEBUG,
    )

    mock_os.environ.setdefault.assert_called_once_with(
        "HAMMURABI_SETTINGS_PATH", DEFAULT_PROJECT_CONFIG
    )
    mock_config.load.assert_called_once_with()
    mock_success_message.assert_called_once_with("Configuration loaded")
    assert mock_github.login.called is False
    mock_logging.root.setLevel.assert_called_once_with("DEBUG")
    ctx.ensure_object.assert_called_once_with(dict)
    assert ctx.obj["config"] == mock_config


@patch("hammurabi.main.logging")
@patch("hammurabi.main.github3")
@patch("hammurabi.main.error_message")
@patch("hammurabi.main.success_message")
@patch("hammurabi.main.config")
@patch("hammurabi.main.os")
def test_main_skips_config_load(
    mock_os,
    mock_config,
    mock_success_message,
    mock_error_message,
    mock_github,
    mock_logging,
):
    ctx = Mock()
    ctx.invoked_subcommand = NON_ACTIONABLE_SUBCOMMANDS[0]

    main(ctx)

    assert mock_os.environ.setdefault.called is False
    assert mock_config.load.called is False
    assert mock_success_message.called is False
    assert mock_error_message.called is False
    assert mock_github.login.called is False
    assert mock_logging.root.setLevel.called is False
    assert ctx.ensure_object.called is False


@patch("hammurabi.main.logging")
@patch("hammurabi.main.github3")
@patch("hammurabi.main.error_message")
@patch("hammurabi.main.config")
@patch("hammurabi.main.os")
def test_main_bad_config(
    mock_os, mock_config, mock_error_message, mock_github, mock_logging
):
    ctx = Mock()
    ctx.invoked_subcommand = "fakecommand"
    ctx.obj = dict()

    load_error_message = "Whoops"
    mock_config.load.side_effect = Exception(load_error_message)

    # Passing default params, because typer not resolves the
    # typer.Option parameter assignments (since it is not an
    # integration test)
    main(
        ctx,
        Path(DEFAULT_PROJECT_CONFIG),
        DEFAULT_REPOSITORY,
        DEFAULT_GITHUB_TOKEN,
        LoggingChoices.DEBUG,
    )

    mock_os.environ.setdefault.assert_called_once_with(
        "HAMMURABI_SETTINGS_PATH", DEFAULT_PROJECT_CONFIG
    )
    mock_config.load.assert_called_once_with()
    mock_error_message.assert_called_once_with(
        f"Failed to load configuration: {load_error_message}"
    )
    assert mock_github.login.called is False
    assert mock_logging.root.setLevel.called is False
    assert ctx.ensure_object.called is False


@patch("hammurabi.main.logging")
@patch("hammurabi.main.github3")
@patch("hammurabi.main.success_message")
@patch("hammurabi.main.config")
@patch("hammurabi.main.os")
def test_main_new_github_token_set(
    mock_os, mock_config, mock_success_message, mock_github, mock_logging
):
    ctx = Mock()
    ctx.invoked_subcommand = "fakecommand"
    ctx.obj = dict()

    expected_token = "Some other token"

    # Passing default params, because typer not resolves the
    # typer.Option parameter assignments (since it is not an
    # integration test)
    main(
        ctx,
        Path(DEFAULT_PROJECT_CONFIG),
        DEFAULT_REPOSITORY,
        expected_token,
        LoggingChoices.DEBUG,
    )

    mock_os.environ.setdefault.assert_called_once_with(
        "HAMMURABI_SETTINGS_PATH", DEFAULT_PROJECT_CONFIG
    )
    mock_config.load.assert_called_once_with()
    mock_success_message.assert_called_once_with("Configuration loaded")
    mock_github.login.assert_called_once_with(token=expected_token)
    mock_logging.root.setLevel.assert_called_once_with("DEBUG")
    ctx.ensure_object.assert_called_once_with(dict)
    assert ctx.obj["config"] == mock_config


@patch("hammurabi.main.typer")
def test_version(mock_typer):
    version()
    mock_typer.echo.assert_called_once_with(__version__)


@patch("hammurabi.main.success_message")
def test_enforce(mock_success_message):
    expected_config = Mock()

    ctx = Mock()
    ctx.invoked_subcommand = "fakecommand"
    ctx.obj = {"config": expected_config}

    settings = ctx.obj["config"].settings
    settings.pillar = Mock()

    expected_dry_run = True
    expected_allow_push = False
    expected_report = False

    enforce(ctx, expected_dry_run, expected_allow_push, expected_report)

    settings.pillar.enforce.assert_called_once_with()
    mock_success_message.assert_called_once_with("Finished successfully")
    assert settings.dry_run == expected_dry_run
    assert settings.allow_push == expected_allow_push


@patch("hammurabi.main.success_message")
def test_enforce_with_report(mock_success_message):
    expected_config = Mock()

    ctx = Mock()
    ctx.invoked_subcommand = "fakecommand"
    ctx.obj = {"config": expected_config}

    settings = ctx.obj["config"].settings
    settings.pillar = Mock()

    expected_dry_run = True
    expected_allow_push = False
    expected_report = True

    enforce(ctx, expected_dry_run, expected_allow_push, expected_report)

    settings.pillar.enforce.assert_called_once_with()
    assert settings.dry_run == expected_dry_run
    assert settings.allow_push == expected_allow_push
    settings.pillar.reporter.report.assert_called_once_with()
    mock_success_message.has_calls(
        [call("Finished successfully"), call("Report generated")]
    )
