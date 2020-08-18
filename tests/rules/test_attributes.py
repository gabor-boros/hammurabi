from pathlib import Path
import stat
from unittest.mock import Mock, patch

from hypothesis import given
from hypothesis import strategies as st

from hammurabi.rules.attributes import ModeChanged, OwnerChanged, SingleAttributeRule


class ExampleSingleAttributeRule(SingleAttributeRule):
    def task(self) -> Path:
        return self.param


def test_single_attribute_rule():
    """
    Since SingleAttributeRule's base classes are tested from
    different angles, the only valuable thing to test on the
    class is that the post_task hook does what we expect.
    """

    expected_path = Path("test/path")

    rule = ExampleSingleAttributeRule(
        name="Single attribute base rule", path=expected_path, new_value="test-val"
    )

    rule.git_add = Mock()
    rule.post_task_hook()

    rule.git_add.assert_called_once_with(expected_path)


@given(user=st.text(alphabet=st.characters(blacklist_characters=":"), min_size=2))
@patch("hammurabi.rules.attributes.shutil")
def test_owner_changed(mocked_shutil, user):
    expected_path = Path("test/path")
    expected_user = user.strip() or None
    expected_group = None

    rule = OwnerChanged(name="Change owner of file", path=expected_path, new_value=user)

    result = rule.task()

    assert result == expected_path
    mocked_shutil.chown.assert_called_once_with(
        str(expected_path), user=expected_user, group=expected_group
    )


@given(group=st.text(min_size=1))
@patch("hammurabi.rules.attributes.shutil")
def test_group_changed(mocked_shutil, group):
    expected_path = Path("test/path")
    expected_user = None
    expected_group = group.strip() or None

    rule = OwnerChanged(
        name="Change owner of file", path=expected_path, new_value=f":{group}"
    )

    result = rule.task()

    assert result == expected_path
    mocked_shutil.chown.assert_called_once_with(
        str(expected_path), user=expected_user, group=expected_group
    )


@patch("hammurabi.rules.attributes.shutil")
def test_owner_and_group_changed(mocked_shutil):
    expected_path = Path("test/path")
    expected_user = "user"
    expected_group = "group"

    rule = OwnerChanged(
        name="Change owner of file",
        path=expected_path,
        new_value=f"{expected_user}:{expected_group}",
    )

    result = rule.task()

    assert result == expected_path
    mocked_shutil.chown.assert_called_once_with(
        str(expected_path), user=expected_user, group=expected_group
    )


@patch("hammurabi.rules.attributes.os")
def test_mode_changed(mocked_os):
    expected_path = Path("test/path")
    expected_mode = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH

    rule = ModeChanged(
        name="Change owner of file", path=expected_path, new_value=expected_mode
    )

    result = rule.task()

    assert result == expected_path
    mocked_os.chmod.assert_called_once_with(str(expected_path), expected_mode)
