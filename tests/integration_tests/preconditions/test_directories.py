from pathlib import Path

import pytest

from hammurabi.preconditions.directories import IsDirectoryExists, IsDirectoryNotExists
from tests.fixtures import temporary_dir, temporary_file

assert temporary_dir
assert temporary_file


@pytest.mark.integration
def test_directory_exists(temporary_dir):
    rule = IsDirectoryExists(path=Path(temporary_dir))
    result = rule.task()

    assert result is True


@pytest.mark.integration
def test_directory_not_exists(temporary_dir):
    rule = IsDirectoryNotExists(path=Path("random/dir/ec/to/ry"))
    result = rule.task()

    assert result is True


@pytest.mark.integration
def test_directory_not_exists_is_file(temporary_file):
    rule = IsDirectoryNotExists(path=Path(temporary_file.name))
    result = rule.task()

    assert result is True
