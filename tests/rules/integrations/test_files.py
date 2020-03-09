import os
from pathlib import Path
import tempfile

import pytest

# Fixture usage is not recognized by PyCharm - do not remove
# this import
from hammurabi.rules.files import (
    FileEmptied,
    FileExists,
    FileNotExists,
    FilesExist,
    FilesNotExist,
)
from tests.rules.fixtures import temporary_file


@pytest.mark.integration
def test_file_exists():
    expected_file = Path(tempfile.gettempdir()).joinpath("test_file_exists")

    # Remove expected file for sure
    try:
        os.unlink(expected_file)
    except FileNotFoundError:
        pass

    rule = FileExists(name="File exists rule", path=expected_file)
    rule.task()

    assert expected_file.exists() is True


@pytest.mark.integration
def test_files_exist():
    expected_files = [
        Path(tempfile.gettempdir()).joinpath("test_files_exist_1"),
        Path(tempfile.gettempdir()).joinpath("test_files_exist_2"),
        Path(tempfile.gettempdir()).joinpath("test_files_exist_3"),
    ]

    # Remove expected file for sure
    map(os.remove, expected_files)

    rule = FilesExist(name="Files exist rule", paths=expected_files)
    rule.task()

    assert all([f.exists() for f in expected_files]) is True


@pytest.mark.integration
def test_file_not_exists(temporary_file):
    temporary_file = Path(temporary_file.name)

    rule = FileNotExists(name="File not exists rule", path=temporary_file)
    rule.task()

    assert temporary_file.exists() is False


@pytest.mark.integration
def test_files_not_exist(temporary_file):
    expected_files = [
        Path(temporary_file.name),
    ]

    rule = FilesNotExist(name="Files not exist rule", paths=expected_files)
    rule.task()

    for f in expected_files:
        assert f.exists() is False


@pytest.mark.integration
def test_file_emptied(temporary_file):
    with temporary_file as f:
        f.write(b"Hello world!")

    rule = FileEmptied(name="File exists rule", path=Path(temporary_file.name))
    rule.task()

    # At this point the file is closed, and we need to reopen it
    with open(temporary_file.name) as f:
        assert f.read() == ""

    os.unlink(temporary_file.name)  # Make sure to remove the file
