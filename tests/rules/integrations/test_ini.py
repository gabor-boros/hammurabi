import os
from pathlib import Path
import tempfile

import pytest

from hammurabi.rules.ini import (
    SectionExists,
    SectionNotExists, SectionRenamed)
from tests.rules.fixtures import temporary_file

@pytest.mark.integration
def test_section_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("[main]")

    rule = SectionExists(
        name="Ensure section exists",
        path=expected_file,
        section="test_section",
        target="main",
        options=(
            ("option_1", "some value"),
            ("option_2", True),
        ),
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "[main]\n[test_section]\noption_1 = some value\noption_2 = True\n"
    expected_file.unlink()


@pytest.mark.integration
def test_section_exists_empty_file(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("")

    rule = SectionExists(
        name="Ensure section exists",
        path=expected_file,
        section="test_section",
        target=r"^$",
        options=(
            ("option_1", "some value"),
            ("option_2", True),
        ),
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "[test_section]\noption_1 = some value\noption_2 = True\n"
    expected_file.unlink()


@pytest.mark.integration
def test_section_exists_add_before(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("[main]")

    rule = SectionExists(
        name="Ensure section exists",
        path=expected_file,
        section="test_section",
        target="main",
        add_after=False,
        options=(
            ("option_1", "some value"),
            ("option_2", True),
        ),
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "[test_section]\noption_1 = some value\noption_2 = True\n[main]"
    expected_file.unlink()


@pytest.mark.integration
def test_section_not_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("[main]\n[remains]")

    rule = SectionNotExists(
        name="Ensure section not exists",
        path=expected_file,
        section="main"
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "[remains]"
    expected_file.unlink()


@pytest.mark.integration
def test_section_not_exists_no_section_match(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("[main]")

    rule = SectionNotExists(
        name="Ensure section not exists",
        path=expected_file,
        section="remove_me_if_you_can"
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "[main]"
    expected_file.unlink()


@pytest.mark.integration
def test_section_renamed(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("[main]")

    rule = SectionRenamed(
        name="Ensure section renamed",
        path=expected_file,
        section="main",
        new_name="new_name"
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "[new_name]\n"
    expected_file.unlink()
