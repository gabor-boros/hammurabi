import stat
from unittest.mock import Mock

from hammurabi.preconditions.attributes import (
    HasMode,
    HasNoMode,
    IsNotOwnedBy,
    IsOwnedBy,
)


def test_has_mode():
    input_file = Mock()
    input_file.stat.return_value.st_mode = stat.S_IRUSR

    rule = HasMode(path=input_file, mode=stat.S_IRUSR)
    result = rule.task()

    assert input_file.stat.called is True
    assert result is True


def test_has_no_mode():
    input_file = Mock()
    input_file.stat.return_value.st_mode = stat.S_IXUSR

    rule = HasNoMode(path=input_file, mode=stat.S_IRUSR)
    result = rule.task()

    assert input_file.stat.called is True
    assert result is True


def test_is_owned_by():
    expected_user = "user"
    expected_group = "group"

    input_file = Mock()
    input_file.owner.return_value = expected_user
    input_file.group.return_value = expected_group

    rule = IsOwnedBy(path=input_file, owner=f"{expected_user}:{expected_group}")
    result = rule.task()

    assert input_file.owner.called is True
    assert input_file.group.called is True
    assert result is True


def test_is_owned_by_user():
    expected_user = "user"
    expected_group = "group"

    input_file = Mock()
    input_file.owner.return_value = expected_user
    input_file.group.return_value = expected_group

    rule = IsOwnedBy(path=input_file, owner=f"{expected_user}")
    result = rule.task()

    assert input_file.owner.called is True
    assert input_file.group.called is True
    assert result is True


def test_is_owned_by_group():
    expected_user = "user"
    expected_group = "group"

    input_file = Mock()
    input_file.owner.return_value = expected_user
    input_file.group.return_value = expected_group

    rule = IsOwnedBy(path=input_file, owner=f":{expected_group}")
    result = rule.task()

    assert input_file.owner.called is True
    assert input_file.group.called is True
    assert result is True


def test_is_not_owned_by():
    expected_user = "user"
    expected_group = "group"

    input_file = Mock()
    input_file.owner.return_value = "other-user"
    input_file.group.return_value = "other-group"

    rule = IsNotOwnedBy(path=input_file, owner=f"{expected_user}:{expected_group}")
    result = rule.task()

    assert input_file.owner.called is True
    assert input_file.group.called is True
    assert result is True
