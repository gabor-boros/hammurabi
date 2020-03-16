from unittest.mock import Mock, patch

import pytest

from hammurabi import Pillar
from tests.helpers import get_passing_rule


@patch("hammurabi.pillar.config")
def test_register(mocked_config):
    mocked_config.settings.working_dir = "."
    mocked_config.settings.dry_run = False

    expected_law = Mock()
    pillar = Pillar()
    pillar.register(expected_law)

    assert expected_law in pillar.laws


@patch("hammurabi.pillar.config")
def test_return_laws(mocked_config):
    mocked_config.settings.working_dir = "."
    mocked_config.settings.dry_run = False

    expected_law = Mock()
    pillar = Pillar()
    pillar.register(expected_law)

    assert list(pillar.laws) == [expected_law]


@patch("hammurabi.pillar.config")
def test_return_rules(mocked_config):
    mocked_config.settings.working_dir = "."
    mocked_config.settings.dry_run = False

    expected_law = Mock(rules=(get_passing_rule(),))
    pillar = Pillar()
    pillar.register(expected_law)

    assert list(pillar.rules) == list(expected_law.rules)


@patch("hammurabi.pillar.config")
def test_get_law(mocked_config):
    mocked_config.settings.working_dir = "."
    mocked_config.settings.dry_run = False

    expected_law = Mock(name="Mocked law")
    pillar = Pillar()
    pillar.register(expected_law)

    result = pillar.get_law(expected_law.name)

    assert result == expected_law


@patch("hammurabi.pillar.config")
def test_get_law_not_registered(mocked_config):
    mocked_config.settings.working_dir = "."
    mocked_config.settings.dry_run = False

    expected_law = Mock(name="Mocked law")
    pillar = Pillar()
    pillar.register(expected_law)

    with pytest.raises(StopIteration):
        pillar.get_law("no law with this name")


@patch("hammurabi.pillar.config")
def test_get_rule(mocked_config):
    mocked_config.settings.working_dir = "."
    mocked_config.settings.dry_run = False

    rule = get_passing_rule()
    expected_law = Mock(name="Mocked law", rules=(rule,))
    pillar = Pillar()
    pillar.register(expected_law)

    result = pillar.get_rule(rule.name)

    assert result == rule


@patch("hammurabi.pillar.config")
def test_get_rule_not_registered(mocked_config):
    mocked_config.settings.working_dir = "."
    mocked_config.settings.dry_run = False

    expected_law = Mock(name="Mocked law", rules=(get_passing_rule(),))
    pillar = Pillar()
    pillar.register(expected_law)

    with pytest.raises(StopIteration):
        pillar.get_rule("no rule with this name")


@patch("hammurabi.pillar.config")
@patch("hammurabi.pillar.Path")
def test_create_lock_file(mocked_path, mocked_config):
    expected_path = Mock()
    mocked_path.return_value = expected_path
    mocked_config.settings.working_dir = "pwd"
    mocked_config.settings.dry_run = False
    expected_path.exists.return_value = False
    pillar = Pillar()

    pillar.create_lock_file()

    mocked_path.assert_called_once_with(mocked_config.settings.working_dir, "hammurabi.lock")
    expected_path.exists.assert_called_once_with()
    expected_path.touch.assert_called_once_with()


@patch("hammurabi.pillar.config")
@patch("hammurabi.pillar.Path")
def test_double_create_lock_file(mocked_path, mocked_config):
    expected_path = Mock()
    mocked_path.return_value = expected_path
    mocked_config.settings.working_dir = "pwd"
    mocked_config.settings.dry_run = False
    expected_path.exists.return_value = True
    pillar = Pillar()

    with pytest.raises(RuntimeError):
        pillar.create_lock_file()

    mocked_path.assert_called_once_with(mocked_config.settings.working_dir, "hammurabi.lock")
    expected_path.exists.assert_called_once_with()
    assert expected_path.touch.called is False


@patch("hammurabi.pillar.config")
@patch("hammurabi.pillar.Path")
def test_release_lock_file(mocked_path, mocked_config):
    expected_path = Mock()
    mocked_path.return_value = expected_path
    mocked_config.settings.working_dir = "pwd"
    mocked_config.settings.dry_run = False
    expected_path.exists.return_value = True
    pillar = Pillar()

    pillar.release_lock_file()

    mocked_path.assert_called_once_with(mocked_config.settings.working_dir, "hammurabi.lock")
    expected_path.exists.assert_called_once_with()
    expected_path.unlink.assert_called_once_with()


@patch("hammurabi.pillar.config")
def test_enforce(mocked_config):
    mocked_config.settings.working_dir = "."
    mocked_config.settings.dry_run = False

    expected_law = Mock()
    pillar = Pillar()
    pillar.register(expected_law)
    pillar.create_lock_file = Mock()
    pillar.release_lock_file = Mock()
    pillar.checkout_branch = Mock()
    pillar.push_changes = Mock()
    pillar.create_pull_request = Mock()

    pillar.enforce()

    expected_law.enforce.assert_called_once_with()
    pillar.create_lock_file.assert_called_once_with()
    pillar.release_lock_file.assert_called_once_with()
    pillar.checkout_branch.assert_called_once_with()
    pillar.push_changes.assert_called_once_with()
    pillar.create_pull_request.assert_called_once_with()


@patch("hammurabi.pillar.config")
def test_enforce_failed(mocked_config):
    mocked_config.settings.working_dir = "."
    mocked_config.settings.dry_run = False

    expected_law = Mock()
    expected_law.enforce.side_effect = Exception()

    pillar = Pillar()
    pillar.register(expected_law)
    pillar.create_lock_file = Mock()
    pillar.release_lock_file = Mock()
    pillar.checkout_branch = Mock()
    pillar.push_changes = Mock()
    pillar.create_pull_request = Mock()

    with pytest.raises(Exception):
        pillar.enforce()

    expected_law.enforce.assert_called_once_with()
    pillar.create_lock_file.assert_called_once_with()
    pillar.release_lock_file.assert_called_once_with()
    pillar.checkout_branch.assert_called_once_with()
