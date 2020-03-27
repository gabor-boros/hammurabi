from unittest.mock import Mock, call, patch

import pytest

from hammurabi.rules.text import LineExists, LineNotExists, LineReplaced


def get_line_exists_rule(
    text="Example text",
    criteria="Example criteria",
    target="Example target",
    position=1,
    lines=[],
    **kwargs,
):
    mock_file = Mock()
    mock_file.read.return_value.splitlines.return_value = lines

    rule = LineExists(
        name="Line exists rule",
        text=text,
        criteria=criteria,
        target=target,
        position=position,
        **kwargs,
    )

    rule.param.open.return_value.__enter__ = Mock(return_value=mock_file)
    rule.param.open.return_value.__exit__ = Mock()

    return rule, mock_file


def get_line_replaced_rule(
    text="Example text", target="Example target", lines=None, **kwargs
):
    mock_file = Mock()

    if lines is None:
        lines = [target]

    mock_file.read.return_value.splitlines.return_value = lines

    rule = LineReplaced(name="Line replaced rule", text=text, target=target, **kwargs)

    rule.param.open.return_value.__enter__ = Mock(return_value=mock_file)
    rule.param.open.return_value.__exit__ = Mock()

    return rule, mock_file


def test_line_exists():
    expected_path = Mock()
    target = "target"

    rule, mock_file = get_line_exists_rule(
        path=expected_path, target=target, lines=[target, "other line"]
    )

    result = rule.task()

    write_args = list(mock_file.writelines.call_args[0][0])
    assert write_args == [f"{target}\n", f"{rule.text}\n", "other line\n"]
    assert result == expected_path


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
    expected_path = Mock()
    text = "remove me"
    lines = ["one", text, "three"]
    mock_file = Mock()
    mock_file.read.return_value.splitlines.return_value = lines

    rule = LineNotExists(name="Line not exists rule", path=expected_path, text=text)
    rule.param.open.return_value.__enter__ = Mock(return_value=mock_file)
    rule.param.open.return_value.__exit__ = Mock()

    result = rule.task()

    write_args = list(mock_file.writelines.call_args[0][0])
    assert write_args == ["one\n", "three\n"]
    assert result == expected_path


@patch("hammurabi.rules.text.re")
def test_line_not_exists_re_compiled(mocked_re):
    expected_path = Mock()
    text = "text"

    LineNotExists(name="Line not exists rule", path=expected_path, text=text)

    mocked_re.compile.assert_has_calls([call(text)])


def test_line_not_exists_no_match():
    expected_path = Mock()
    text = "remove me"
    lines = ["one", "two"]
    mock_file = Mock()
    mock_file.read.return_value.splitlines.return_value = lines

    rule = LineNotExists(name="Line not exists rule", path=expected_path, text=text)
    rule.param.open.return_value.__enter__ = Mock(return_value=mock_file)
    rule.param.open.return_value.__exit__ = Mock()

    rule.task()

    assert mock_file.writelines.called is False


def test_line_replaced():
    expected_path = Mock()
    replacement = "replacement"

    rule, mock_file = get_line_replaced_rule(path=expected_path, text=replacement)

    result = rule.task()

    write_args = list(mock_file.writelines.call_args[0][0])
    assert write_args == [f"{replacement}\n"]
    assert result == expected_path


def test_line_replaced_with_indentation():
    expected_path = Mock()
    replacement = "replacement"

    rule, mock_file = get_line_replaced_rule(
        path=expected_path,
        text=replacement,
        target="\treplace me",
        lines=["\treplace me", "other line"],
    )

    rule.task()

    write_args = list(mock_file.writelines.call_args[0][0])
    assert write_args == [f"\t{replacement}\n", "other line\n"]


@patch("hammurabi.rules.text.re")
def test_line_replaced_re_compiled(mocked_re):
    expected_path = Mock()
    target = "target"

    get_line_replaced_rule(path=expected_path, target=target)

    mocked_re.compile.assert_has_calls([call(target), call(r"^\s+")])


def test_line_replaced_empty_file():
    expected_path = Mock()
    replacement = "replacement"

    rule, mock_file = get_line_replaced_rule(
        path=expected_path, text=replacement, lines=[]
    )

    rule.task()

    assert mock_file.writelines.called is False


def test_line_replaced_no_match():
    expected_path = Mock()

    rule, mock_file = get_line_replaced_rule(path=expected_path, lines=["no", "match"])

    with pytest.raises(LookupError) as exc:
        rule.task()

    assert str(exc.value).startswith("No matching line for")
    assert mock_file.writelines.called is False


def test_line_replaced_no_match_but_text():
    expected_path = Mock()
    replacement = "apple tree"

    rule, mock_file = get_line_replaced_rule(
        path=expected_path, lines=["no", "match", replacement], text=replacement
    )

    result = rule.task()

    write_args = list(mock_file.writelines.call_args[0][0])
    assert write_args == ["no\n", "match\n", f"{replacement}\n"]
    assert result == expected_path


def test_line_replaced_no_match_no_text():
    expected_path = Mock()

    rule, mock_file = get_line_replaced_rule(
        path=expected_path, lines=["no", "match"], text="apple tree"
    )

    with pytest.raises(LookupError) as exc:
        rule.task()

    assert str(exc.value).startswith("No matching line for")
    assert mock_file.writelines.called is False


def test_line_replaced_both_target_and_text():
    expected_path = Mock()
    target = "target"
    text = "apple tree"

    rule, mock_file = get_line_replaced_rule(
        path=expected_path, lines=["no", target, text], target=target, text=text
    )

    with pytest.raises(LookupError) as exc:
        rule.task()

    # Use rule.target because of transformations on it
    assert str(exc.value) == f'Both "{rule.target}" and "{rule.text}" exists'
    assert mock_file.writelines.called is False
