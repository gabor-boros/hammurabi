from unittest.mock import Mock

from hammurabi.preconditions.directories import IsDirectoryExists, IsDirectoryNotExists


def test_directory_exists():
    input_dir = Mock()
    input_dir.is_dir.return_value = True

    rule = IsDirectoryExists(path=input_dir)
    result = rule.task()

    assert input_dir.is_dir.called is True
    assert result is True


def test_directory_not_exists():
    input_dir = Mock()
    input_dir.is_dir.return_value = False

    rule = IsDirectoryNotExists(path=input_dir)
    result = rule.task()

    assert input_dir.is_dir.called is True
    assert result is True
