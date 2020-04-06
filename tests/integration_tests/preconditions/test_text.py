from pathlib import Path

import pytest

from hammurabi.preconditions.text import IsLineExists, IsLineNotExists
from tests.fixtures import temporary_file

assert temporary_file


@pytest.mark.integration
def test_line_exists(temporary_file):
    expected_line = "my-line"

    expected_file = Path(temporary_file.name)
    expected_file.write_text(expected_line)

    rule = IsLineExists(path=expected_file, criteria=fr"{expected_line}")
    result = rule.task()

    assert result is True


@pytest.mark.integration
def test_line_not_exists(temporary_file):
    expected_line = "my-line"

    expected_file = Path(temporary_file.name)
    expected_file.write_text("other-line")

    rule = IsLineNotExists(path=expected_file, criteria=fr"{expected_line}")
    result = rule.task()

    assert result is True
