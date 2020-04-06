from pathlib import Path
import stat

import pytest

from hammurabi.preconditions.attributes import (
    HasMode,
    HasNoMode,
    IsNotOwnedBy,
    IsOwnedBy,
)
from tests.fixtures import temporary_file

assert temporary_file


@pytest.mark.integration
def test_has_mode(temporary_file):
    rule = HasMode(path=Path(temporary_file.name), mode=stat.S_IRUSR)
    result = rule.task()

    assert result is True


@pytest.mark.integration
def test_has_no_mode(temporary_file):
    rule = HasNoMode(path=Path(temporary_file.name), mode=stat.S_IWOTH)
    result = rule.task()

    assert result is True


@pytest.mark.integration
def test_is_owned_by(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_user = expected_file.owner()
    expected_group = expected_file.group()

    rule = IsOwnedBy(path=expected_file, owner=f"{expected_user}:{expected_group}")
    result = rule.task()

    assert result is True


@pytest.mark.integration
def test_is_not_owned_by(temporary_file):
    expected_user = "fake-user"
    expected_group = "fake-group"

    rule = IsNotOwnedBy(
        path=Path(temporary_file.name), owner=f"{expected_user}:{expected_group}"
    )
    result = rule.task()

    assert result is True
