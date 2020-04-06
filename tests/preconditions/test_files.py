from unittest.mock import Mock

from hammurabi.preconditions.files import IsFileExists, IsFileNotExists


def test_file_exists():
    input_file = Mock()
    input_file.is_file.return_value = True

    rule = IsFileExists(path=input_file)
    result = rule.task()

    assert input_file.is_file.called is True
    assert result is True


def test_file_not_exists():
    input_file = Mock()
    input_file.is_file.return_value = False

    rule = IsFileNotExists(path=input_file)
    result = rule.task()

    assert input_file.is_file.called is True
    assert result is True
