from unittest.mock import Mock, patch

from hammurabi.preconditions.text import IsLineExist, IsLineNotExist


@patch("hammurabi.preconditions.text.re")
def test_line_exists(mock_re):
    expected_line = "my-line"

    input_file = Mock()
    input_file.is_file.return_value = True
    input_file.read_text.return_value.splitlines.return_value = [expected_line]

    mock_criteria = Mock()
    mock_criteria.match.side_effect = [True]
    mock_re.compile.return_value = mock_criteria

    rule = IsLineExist(path=input_file, criteria=fr"{expected_line}")
    result = rule.task()

    mock_re.compile.assert_called_once_with(expected_line)
    mock_criteria.match.assert_called_once_with(expected_line)
    assert input_file.read_text.called is True
    assert input_file.read_text.return_value.splitlines.called is True
    assert result is True


@patch("hammurabi.preconditions.text.re")
def test_line_not_exists(mock_re):
    expected_line = "my-line"
    other_line = "other-line"

    input_file = Mock()
    input_file.is_file.return_value = True
    input_file.read_text.return_value.splitlines.return_value = [other_line]

    mock_criteria = Mock()
    mock_criteria.match.side_effect = [False]
    mock_re.compile.return_value = mock_criteria

    rule = IsLineNotExist(path=input_file, criteria=fr"{expected_line}")
    result = rule.task()

    mock_re.compile.assert_called_once_with(expected_line)
    mock_criteria.match.assert_called_once_with(other_line)
    assert input_file.read_text.called is True
    assert input_file.read_text.return_value.splitlines.called is True
    assert result is True
