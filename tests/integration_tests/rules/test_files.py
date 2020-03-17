import os
from pathlib import Path
import tempfile

import pytest

from hammurabi.rules.files import (
    FileEmptied,
    FileExists,
    FileNotExists,
    FilesExist,
    FilesNotExist,
)
from tests.fixtures import temporary_file

assert temporary_file


@pytest.mark.integration
def test_file_exists():
    expected_file = Path(tempfile.gettempdir()).joinpath("test_file_exists")

    rule = FileExists(name="File exists rule", path=expected_file)
    rule.task()

    assert expected_file.exists() is True
    expected_file.unlink()


@pytest.mark.integration
def test_files_exist():
    expected_files = [
        Path(tempfile.gettempdir()).joinpath("test_files_exist_1"),
        Path(tempfile.gettempdir()).joinpath("test_files_exist_2"),
        Path(tempfile.gettempdir()).joinpath("test_files_exist_3"),
    ]

    rule = FilesExist(name="Files exist rule", paths=expected_files)
    rule.task()

    assert all([f.exists() for f in expected_files]) is True

    # Cleanup
    for expected_file in expected_files:
        expected_file.unlink()


@pytest.mark.integration
def test_file_not_exists(temporary_file):
    temporary_file = Path(temporary_file.name)

    rule = FileNotExists(name="File not exists rule", path=temporary_file)
    rule.task()

    assert temporary_file.exists() is False


@pytest.mark.integration
def test_files_not_exist(temporary_file):
    expected_files = [Path(temporary_file.name)]

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
