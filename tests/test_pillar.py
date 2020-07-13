from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from hammurabi import Pillar
from tests.helpers import get_passing_rule


@patch("hammurabi.pillar.JSONReporter")
def test_register(mocked_reporter):
    mock_reporter = Mock()
    mock_reporter.laws = list()
    mocked_reporter.return_value = mock_reporter

    expected_law = Mock()
    pillar = Pillar(mocked_reporter)
    pillar.register(expected_law)

    assert expected_law in pillar.laws
    assert len(pillar.laws) == 1
    assert mock_reporter.laws == pillar.laws


@patch("hammurabi.pillar.JSONReporter")
def test_return_laws(mocked_reporter):
    mock_reporter = Mock()
    mock_reporter.laws = list()
    mocked_reporter.return_value = mock_reporter

    expected_law = Mock()
    pillar = Pillar(mocked_reporter)
    pillar.register(expected_law)

    assert list(pillar.laws) == [expected_law]
    assert mock_reporter.laws == [expected_law]


@patch("hammurabi.pillar.JSONReporter")
def test_return_rules(_):
    expected_law = Mock(rules=(get_passing_rule(),))
    pillar = Pillar()
    pillar.register(expected_law)

    assert list(pillar.rules) == list(expected_law.rules)


@patch("hammurabi.pillar.JSONReporter")
def test_get_law(_):
    expected_law = Mock(name="Mocked law")
    pillar = Pillar()
    pillar.register(expected_law)

    result = pillar.get_law(expected_law.name)

    assert result == expected_law


@patch("hammurabi.pillar.JSONReporter")
def test_get_law_not_registered(_):
    expected_law = Mock(name="Mocked law")
    pillar = Pillar()
    pillar.register(expected_law)

    with pytest.raises(StopIteration):
        pillar.get_law("no law with this name")


@patch("hammurabi.pillar.JSONReporter")
def test_get_rule(_):
    rule = get_passing_rule()
    expected_law = Mock(name="Mocked law", rules=(rule,))
    pillar = Pillar()
    pillar.register(expected_law)

    result = pillar.get_rule(rule.name)

    assert result == rule


@patch("hammurabi.pillar.JSONReporter")
def test_get_rule_not_registered(_):
    expected_law = Mock(name="Mocked law", rules=(get_passing_rule(),))
    pillar = Pillar()
    pillar.register(expected_law)

    with pytest.raises(StopIteration):
        pillar.get_rule("no rule with this name")


@patch("hammurabi.pillar.datetime")
@patch("hammurabi.pillar.JSONReporter")
def test_enforce(mocked_reporter, mocked_datetime):
    mock_started = datetime.min
    mock_finished = datetime.max
    mocked_datetime.now.side_effect = [mock_started, mock_finished]

    mock_reporter = Mock()
    mock_reporter.laws = list()
    mocked_reporter.return_value = mock_reporter

    mock_notification = Mock()

    expected_law = Mock()
    expected_pr_url = "expected_pr_url"
    pillar = Pillar(mocked_reporter, notifications=[mock_notification])
    pillar.register(expected_law)
    pillar.checkout_branch = Mock()
    pillar.push_changes = Mock()
    pillar.create_pull_request = Mock()
    pillar.create_pull_request.return_value = expected_pr_url

    pillar.enforce()

    expected_law.enforce.assert_called_once_with()
    pillar.checkout_branch.assert_called_once_with()
    pillar.push_changes.assert_called_once_with()
    pillar.create_pull_request.assert_called_once_with()
    mock_notification.send.assert_called_once_with(expected_pr_url)
    assert mock_reporter.laws == pillar.laws
    assert mock_reporter.additional_data.started == mock_started.isoformat()
    assert mock_reporter.additional_data.finished == mock_finished.isoformat()
    assert mock_reporter.additional_data.pull_request_url == expected_pr_url


@patch("hammurabi.pillar.JSONReporter")
def test_enforce_failed(_):
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
    pillar.checkout_branch.assert_called_once_with()
    assert pillar.push_changes.called is False
    assert pillar.create_pull_request.called is False
