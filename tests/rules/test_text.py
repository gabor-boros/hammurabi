from unittest.mock import Mock, call, patch

import pytest

from hammurabi.rules.text import LineExists, LineNotExists, LineReplaced


def get_line_exists_rule(
    text="Example text", match="Example match", position=1, lines=[], **kwargs
):
    mock_file = Mock()
    mock_file.read.return_value.splitlines.return_value = lines

    rule = LineExists(
        name="Line exists rule", text=text, match=match, position=position, **kwargs
    )

    rule.param.open.return_value.__enter__ = Mock(return_value=mock_file)
    rule.param.open.return_value.__exit__ = Mock()

    return rule, mock_file


def get_line_replaced_rule(
    text="Example text", match="Example match", lines=None, **kwargs
):
    mock_file = Mock()

    if lines is None:
        lines = [match]

    mock_file.read.return_value.splitlines.return_value = lines

    rule = LineReplaced(name="Line replaced rule", text=text, match=match, **kwargs)

    rule.param.open.return_value.__enter__ = Mock(return_value=mock_file)
    rule.param.open.return_value.__exit__ = Mock()

    return rule, mock_file


def test_line_exists():
    expected_path = Mock()
    match = "match"

    rule, mock_file = get_line_exists_rule(
        path=expected_path, match=match, lines=[match, "other line"]
    )

    result = rule.task()

    write_args = list(mock_file.writelines.call_args[0][0])
    assert write_args == [f"{match}\n", f"{rule.text}\n", "other line\n"]
    assert result == expected_path


def test_line_exists_no_newline():
    expected_path = Mock()
    expected_text = "apple tree"

    rule, mock_file = get_line_exists_rule(
        path=expected_path,
        match="$",
        text=expected_text,
        lines=["some", "lines"],
        ensure_trailing_newline=True,
    )

    result = rule.task()

    # Although this test seems bit odd, we must ensure that
    # developers can use `$` regexp for end of file even if the
    # file has no newline char at the end of it.
    write_args = list(mock_file.writelines.call_args[0][0])
    assert write_args == ["some\n", "lines\n", "\n", f"{expected_text}\n"]
    assert result == expected_path


def test_line_exists_insert_before():
    expected_path = Mock()
    match = "match"

    rule, mock_file = get_line_exists_rule(
        path=expected_path, match=match, lines=[match, "other line"], position=0
    )

    rule.task()

    write_args = list(mock_file.writelines.call_args[0][0])
    assert write_args == [f"{rule.text}\n", f"{match}\n", "other line\n"]


def test_line_exists_with_indentation():
    expected_path = Mock()
    match = "\tmatch"

    rule, mock_file = get_line_exists_rule(
        path=expected_path, match=match, lines=[match, "other line"]
    )

    rule.task()

    write_args = list(mock_file.writelines.call_args[0][0])
    assert write_args == [f"{match}\n", f"{rule.text}\n", "other line\n"]


@patch("hammurabi.rules.text.re")
def test_line_exists_re_compiled(mocked_re):
    expected_path = Mock()
    match = "match"

    get_line_exists_rule(path=expected_path, match=match)

    mocked_re.compile.assert_has_calls([call(match), call(r"^\s+")])


def test_line_exists_empty_file():
    expected_path = Mock()
    match = "match"

    rule, mock_file = get_line_exists_rule(path=expected_path, match=match)

    rule.task()

    write_args = list(mock_file.writelines.call_args[0][0])
    assert write_args == [f"{rule.text}\n"]


def test_line_exists_no_match():
    expected_path = Mock()
    match = "match"

    rule, mock_file = get_line_exists_rule(
        path=expected_path, match=match, lines=["nothing", "to see", "here"]
    )

    with pytest.raises(LookupError) as exc:
        rule.task()

    assert str(exc.value).startswith("No matching line for")
    assert mock_file.writelines.called is False


def test_line_exists_multiple_matches():
    expected_path = Mock()
    match = "match"

    rule, mock_file = get_line_exists_rule(
        path=expected_path, match=match, lines=["match", "match"]
    )

    result = rule.task()

    write_args = list(mock_file.writelines.call_args[0][0])
    assert write_args == [f"{match}\n", "match\n", f"{rule.text}\n"]
    assert result == expected_path


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
        match="\treplace me",
        lines=["\treplace me", "other line"],
    )

    rule.task()

    write_args = list(mock_file.writelines.call_args[0][0])
    assert write_args == [f"\t{replacement}\n", "other line\n"]


@patch("hammurabi.rules.text.re")
def test_line_replaced_re_compiled(mocked_re):
    expected_path = Mock()
    match = "match"

    get_line_replaced_rule(path=expected_path, match=match)

    mocked_re.compile.assert_has_calls([call(match), call(r"^\s+")])


def test_line_replaced_empty_file():
    expected_path = Mock()
    replacement = "replacement"

    rule, mock_file = get_line_replaced_rule(
        path=expected_path, text=replacement, lines=[]
    )

    with pytest.raises(LookupError):
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

    assert mock_file.writelines.called is False
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


def test_line_replaced_both_match_and_text():
    expected_path = Mock()
    match = "match"
    text = "apple tree"

    rule, mock_file = get_line_replaced_rule(
        path=expected_path, lines=["no", match, text], match=match, text=text
    )

    with pytest.raises(LookupError) as exc:
        rule.task()

    # Use rule.match because of transformations on it
    assert str(exc.value) == f'Both "{rule.match}" and "{rule.text}" exists'
    assert mock_file.writelines.called is False
