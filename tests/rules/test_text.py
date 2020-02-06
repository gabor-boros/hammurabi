from unittest.mock import Mock, call, patch

import pytest

from hammurabi.rules.text import LineExists, LineNotExists, LineReplaced


def get_line_exists_rule(
    path=None,
    text="Example text",
    criteria="Example criteria",
    target="Example target",
    position=1,
    respect_indentation=True,
    lines=[],
):
    mock_file = Mock()
    mock_file.read.return_value.splitlines.return_value = lines

    rule = LineExists(
        name="Line exists rule",
        path=path,
        text=text,
        criteria=criteria,
        target=target,
        position=position,
        respect_indentation=respect_indentation,
    )

    rule.param.open.return_value.__enter__ = Mock(return_value=mock_file)
    rule.param.open.return_value.__exit__ = Mock()

    return rule, mock_file


def test_line_exists():
    expected_path = Mock()
    target = "target"

    rule, mock_file = get_line_exists_rule(
        path=expected_path, target=target, lines=[target, "other line"]
    )

    rule.task()

    write_args = list(mock_file.writelines.call_args[0][0])
    assert write_args == [f"{target}\n", f"{rule.text}\n", "other line\n"]


def test_line_exists_insert_before():
    expected_path = Mock()
    target = "target"

    rule, mock_file = get_line_exists_rule(
        path=expected_path, target=target, lines=[target, "other line"], position=0
    )

    rule.task()

    write_args = list(mock_file.writelines.call_args[0][0])
    assert write_args == [f"{rule.text}\n", f"{target}\n", "other line\n"]


def test_line_exists_with_indentation():
    expected_path = Mock()
    target = "\ttarget"

    rule, mock_file = get_line_exists_rule(
        path=expected_path, target=target, lines=[target, "other line"]
    )

    rule.task()

    write_args = list(mock_file.writelines.call_args[0][0])
    assert write_args == [f"{target}\n", f"{rule.text}\n", "other line\n"]


@patch("hammurabi.rules.text.re")
def test_line_exists_re_compiled(mocked_re):
    expected_path = Mock()
    criteria = "criteria"
    target = "target"

    get_line_exists_rule(path=expected_path, criteria=criteria, target=target)

    mocked_re.compile.assert_has_calls([call(criteria), call(target), call(r"^\s+")])


def test_line_exists_empty_file():
    expected_path = Mock()
    target = "target"

    rule, mock_file = get_line_exists_rule(path=expected_path, target=target)

    rule.task()

    write_args = list(mock_file.writelines.call_args[0][0])
    assert write_args == [f"{rule.text}\n"]


def test_line_exists_no_match():
    expected_path = Mock()
    target = "target"

    rule, mock_file = get_line_exists_rule(
        path=expected_path, target=target, lines=["no", "match"]
    )

    with pytest.raises(LookupError) as exc:
        rule.task()

    assert str(exc.value).startswith("No matching line for")
    assert mock_file.writelines.called is False


def test_line_exists_multiple_matches():
    expected_path = Mock()
    target = "target"

    rule, mock_file = get_line_exists_rule(
        path=expected_path, target=target, lines=["target", "target_match"]
    )

    with pytest.raises(LookupError) as exc:
        rule.task()

    assert str(exc.value).startswith("Multiple matching lines for")
    assert mock_file.writelines.called is False


def test_line_exists_failed_criteria():
    expected_path = Mock()
    criteria = "criteria"

    rule, mock_file = get_line_exists_rule(
        path=expected_path, criteria=criteria, lines=[criteria, "other line"]
    )

    rule.task()

    assert mock_file.writelines.called is False


def test_line_not_exists():
    pass


def test_line_not_exists_no_match():
    pass


def test_line_replaced():
    pass


def test_line_replaced_no_match():
    pass


def test_line_replaced_failed_criteria():
    pass
