from pathlib import Path
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest

from hammurabi.rules.ini import (
    SectionExists,
    SectionNotExists,
    SectionRenamed,
    SingleConfigFileRule,
)


class ExampleSingleConfigFileRule(SingleConfigFileRule):
    def task(self) -> Path:
        return self.param


@patch("hammurabi.rules.ini.ConfigUpdater")
def test_single_config_file_rule(mocked_updater_class):
    """
    Since SingleConfigFileRule's base classes are tested from
    different angles, the only valuable thing to test on the
    class is that the post_task hook does what we expect.
    """

    mocked_updater_instance = Mock()
    mocked_updater_class.return_value = mocked_updater_instance

    expected_path = Mock()

    rule = ExampleSingleConfigFileRule(
        name="Single config file base rule", path=expected_path, section="test_section"
    )

    rule.git_add = Mock()
    rule.pre_task_hook()
    rule.post_task_hook()

    rule.git_add.assert_called_once_with(expected_path)
    mocked_updater_instance.read.assert_called_once_with(expected_path)


@patch("hammurabi.rules.ini.ConfigUpdater")
def test_section_exists(mocked_updater_class):
    mock_file = Mock()
    expected_path = Mock()
    expected_path.open.return_value.__enter__ = Mock(return_value=mock_file)
    expected_path.open.return_value.__exit__ = Mock()

    expected_section = Mock()

    mock_add_after_return = Mock()
    expected_target = Mock()

    mocked_prop = PropertyMock(return_value=mock_add_after_return)
    type(expected_target).add_after = mocked_prop

    mocked_updater = MagicMock()
    mocked_updater.__getitem__.return_value = expected_target
    mocked_updater.sections.return_value = [expected_target]
    mocked_updater.has_section.return_value = False

    mocked_updater_class.return_value = mocked_updater

    rule = SectionExists(
        name="Section exists rule",
        path=expected_path,
        section=expected_section,
        target=expected_target,
    )

    result = rule.task()

    mocked_updater.sections.assert_called_once_with()
    mocked_updater.has_section.assert_called_once_with(expected_section)
    mocked_prop.assert_called_once_with()
    mock_add_after_return.space.assert_called_once_with(rule.space)
    mock_add_after_return.space.return_value.section.assert_called_once_with(
        expected_section
    )
    assert result == expected_path


@patch("hammurabi.rules.ini.ConfigUpdater")
def test_section_exists_add_before(mocked_updater_class):
    mock_file = Mock()
    expected_path = Mock()
    expected_path.open.return_value.__enter__ = Mock(return_value=mock_file)
    expected_path.open.return_value.__exit__ = Mock()

    expected_section = Mock()

    mock_add_before_return = Mock()
    expected_target = Mock()

    mocked_prop = PropertyMock(return_value=mock_add_before_return)
    type(expected_target).add_before = mocked_prop

    mocked_updater = MagicMock()
    mocked_updater.__getitem__.return_value = expected_target
    mocked_updater.sections.return_value = [expected_target]
    mocked_updater.has_section.return_value = False

    mocked_updater_class.return_value = mocked_updater

    rule = SectionExists(
        name="Section exists rule",
        path=expected_path,
        section=expected_section,
        target=expected_target,
        add_after=False,
    )

    result = rule.task()

    mocked_updater.sections.assert_called_once_with()
    mocked_updater.has_section.assert_called_once_with(expected_section)
    mocked_prop.assert_called_once_with()
    mock_add_before_return.section.assert_called_once_with(expected_section)
    assert mock_add_before_return.section.return_value.space.called is False
    assert result == expected_path


@patch("hammurabi.rules.ini.ConfigUpdater")
def test_section_exists_no_sections(mocked_updater_class):
    mock_file = Mock()
    expected_path = Mock()
    expected_path.open.return_value.__enter__ = Mock(return_value=mock_file)
    expected_path.open.return_value.__exit__ = Mock()

    expected_section = Mock()
    expected_target = Mock()

    mocked_updater = MagicMock()
    mocked_updater.sections.return_value = []
    mocked_updater.has_section.return_value = False

    mocked_updater_class.return_value = mocked_updater

    rule = SectionExists(
        name="Section exists rule",
        path=expected_path,
        section=expected_section,
        target=expected_target,
    )

    rule.task()

    mocked_updater.sections.assert_called_once_with()
    mocked_updater.has_section.assert_called_once_with(expected_section)
    mocked_updater.add_section.assert_called_once_with(expected_section)


@patch("hammurabi.rules.ini.ConfigUpdater")
def test_section_exists_no_target(mocked_updater_class):
    mock_file = Mock()
    expected_path = Mock()
    expected_path.open.return_value.__enter__ = Mock(return_value=mock_file)
    expected_path.open.return_value.__exit__ = Mock()

    expected_section = Mock()
    expected_target = Mock()

    mocked_updater = MagicMock()
    mocked_updater.sections.return_value = [Mock(), Mock()]
    mocked_updater.has_section.return_value = False

    mocked_updater_class.return_value = mocked_updater

    rule = SectionExists(
        name="Section exists rule",
        path=expected_path,
        section=expected_section,
        target=expected_target,
    )

    rule.task()

    mocked_updater.sections.assert_called_once_with()
    mocked_updater.has_section.assert_called_once_with(expected_section)
    mocked_updater.add_section.assert_called_once_with(expected_section)


@patch("hammurabi.rules.ini.ConfigUpdater")
def test_section_exists_missing_target(mocked_updater_class):
    mock_file = Mock()
    expected_path = Mock()
    expected_path.open.return_value.__enter__ = Mock(return_value=mock_file)
    expected_path.open.return_value.__exit__ = Mock()

    expected_section = Mock()

    mocked_updater = MagicMock()
    mocked_updater.sections.return_value = [Mock(), Mock()]
    mocked_updater.has_section.return_value = False

    mocked_updater_class.return_value = mocked_updater

    rule = SectionExists(
        name="Section exists rule", path=expected_path, section=expected_section
    )

    rule.task()

    mocked_updater.sections.assert_called_once_with()
    mocked_updater.has_section.assert_called_once_with(expected_section)
    mocked_updater.add_section.assert_called_once_with(expected_section)


@patch("hammurabi.rules.ini.ConfigUpdater")
def test_section_exists_already_exists(mocked_updater_class):
    mock_file = Mock()
    expected_path = Mock()
    expected_path.open.return_value.__enter__ = Mock(return_value=mock_file)
    expected_path.open.return_value.__exit__ = Mock()

    expected_section = Mock()

    mock_add_before_return = Mock()
    mock_add_after_return = Mock()
    expected_target = Mock()

    mocked_before = PropertyMock(return_value=mock_add_before_return)
    mocked_after = PropertyMock(return_value=mock_add_after_return)
    type(expected_target).add_before = mocked_before
    type(expected_target).add_after = mocked_after

    mocked_updater = MagicMock()
    mocked_updater.__getitem__.return_value = expected_target
    mocked_updater.sections.return_value = [expected_target]
    mocked_updater.has_section.return_value = True

    mocked_updater_class.return_value = mocked_updater

    rule = SectionExists(
        name="Section exists rule",
        path=expected_path,
        section=expected_section,
        target=expected_target,
    )

    result = rule.task()

    mocked_updater.sections.assert_called_once_with()
    mocked_updater.has_section.assert_called_once_with(expected_section)
    assert mocked_before.called is False
    assert mocked_after.called is False
    assert result == expected_path


@patch("hammurabi.rules.ini.ConfigUpdater")
def test_section_not_exists(mocked_updater_class):
    mock_file = Mock()
    expected_path = Mock()
    expected_path.open.return_value.__enter__ = Mock(return_value=mock_file)
    expected_path.open.return_value.__exit__ = Mock()

    expected_section = Mock()

    mocked_updater = MagicMock()
    mocked_updater.has_section.return_value = True

    mocked_updater_class.return_value = mocked_updater

    rule = SectionNotExists(
        name="Section not exists rule", path=expected_path, section=expected_section
    )

    result = rule.task()

    mocked_updater.has_section.assert_called_once_with(expected_section)
    mocked_updater.remove_section.assert_called_once_with(expected_section)
    assert result == expected_path


@patch("hammurabi.rules.ini.ConfigUpdater")
def test_section_not_exists_no_section(mocked_updater_class):
    mock_file = Mock()
    expected_path = Mock()
    expected_path.open.return_value.__enter__ = Mock(return_value=mock_file)
    expected_path.open.return_value.__exit__ = Mock()

    expected_section = Mock()

    mocked_updater = MagicMock()
    mocked_updater.has_section.return_value = False

    mocked_updater_class.return_value = mocked_updater

    rule = SectionNotExists(
        name="Section not exists rule", path=expected_path, section=expected_section
    )

    result = rule.task()

    mocked_updater.has_section.assert_called_once_with(expected_section)
    assert mocked_updater.remove_section.called is False
    assert result == expected_path


@patch("hammurabi.rules.ini.ConfigUpdater")
def test_section_renamed(mocked_updater_class):
    mock_file = Mock()
    expected_path = Mock()
    expected_path.open.return_value.__enter__ = Mock(return_value=mock_file)
    expected_path.open.return_value.__exit__ = Mock()

    expected_section = Mock(name="banana")
    new_section_name = "apple"

    mocked_updater = MagicMock()
    mocked_updater.__getitem__.return_value = expected_section
    mocked_updater.sections.return_value = [expected_section]
    mocked_updater.has_section.return_value = True

    mocked_updater_class.return_value = mocked_updater

    rule = SectionRenamed(
        name="Section exists rule",
        path=expected_path,
        section=expected_section,
        new_name=new_section_name,
    )

    result = rule.task()

    mocked_updater.has_section.assert_called_once_with(expected_section)
    assert expected_section.name == new_section_name
    assert result == expected_path


@patch("hammurabi.rules.ini.ConfigUpdater")
def test_section_renamed_no_section(mocked_updater_class):
    mock_file = Mock()
    expected_path = Mock()
    expected_path.open.return_value.__enter__ = Mock(return_value=mock_file)
    expected_path.open.return_value.__exit__ = Mock()

    expected_section = Mock(name="banana")
    original_section_name = expected_section.name
    new_section_name = "apple"

    mocked_updater = MagicMock()
    mocked_updater.has_section.return_value = False

    mocked_updater_class.return_value = mocked_updater

    rule = SectionRenamed(
        name="Section exists rule",
        path=expected_path,
        section=expected_section,
        new_name=new_section_name,
    )

    with pytest.raises(LookupError):
        rule.task()

    mocked_updater.has_section.assert_called_once_with(expected_section)
    assert expected_section.name == original_section_name
