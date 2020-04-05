from pathlib import Path

import pytest

from hammurabi.preconditions.files import IsFileExists, IsFileNotExists
from tests.fixtures import temporary_dir, temporary_file

assert temporary_dir
assert temporary_file


@pytest.mark.integration
def test_file_exists(temporary_file):
    rule = IsFileExists(path=Path(temporary_file.name))
    result = rule.task()

    assert result is True


@pytest.mark.integration
def test_file_not_exists():
    rule = IsFileNotExists(path=Path("ran/dom/file/name"))
    result = rule.task()

    assert result is True


@pytest.mark.integration
def test_file_not_exists_is_dir(temporary_dir):
    rule = IsFileNotExists(path=Path(temporary_dir))
    result = rule.task()

    assert result is True
