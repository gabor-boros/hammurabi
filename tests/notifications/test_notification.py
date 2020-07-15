from typing import Optional
from unittest.mock import Mock, patch

import pytest

from hammurabi.exceptions import NotificationSendError
from hammurabi.helpers import full_strip
from hammurabi.notifications.base import Notification


class TestNotification(Notification):
    def notify(self, message: str, changes_link: Optional[str]) -> None:
        pass


@patch("hammurabi.notifications.base.config")
def test_notification_send(mock_config):
    expected_repo = "gabor-boros/hammurabi"
    mock_config.settings.repository = expected_repo

    channel = "APPLE"
    link = "https://github.com/gabor-boros/hammurabi"
    message_template = full_strip(
        """
    Hello team,

    You got a new Hammurabi update for {repository}.
    You can check the changes by clicking *<{changes_link}|here>*.
    """
    )

    notification = TestNotification([channel], message_template)
    notification.notify = Mock()
    notification.send(link)

    notification.notify.assert_called_once_with(
        message_template.format(repository=expected_repo, changes_link=link), link
    )


@patch("hammurabi.notifications.base.config")
def test_notification_unexpected_error(mock_config):
    expected_exception = ValueError("well, that was unexpected")

    expected_repo = "gabor-boros/hammurabi"
    mock_config.settings.repository = expected_repo

    channel = "APPLE"
    link = "https://github.com/gabor-boros/hammurabi"
    message_template = full_strip(
        """
    Hello team,

    You got a new Hammurabi update for {repository}.
    You can check the changes by clicking *<{changes_link}|here>*.
    """
    )

    notification = TestNotification([channel], message_template)
    notification.notify = Mock()
    notification.notify.side_effect = expected_exception

    with pytest.raises(ValueError):
        notification.send(link)

    notification.notify.assert_called_once_with(
        message_template.format(repository=expected_repo, changes_link=link), link
    )


@patch("hammurabi.notifications.base.config")
def test_notification_expected_error(mock_config):
    expected_exception = NotificationSendError("that's expected")

    expected_repo = "gabor-boros/hammurabi"
    mock_config.settings.repository = expected_repo

    channel = "APPLE"
    link = "https://github.com/gabor-boros/hammurabi"
    message_template = full_strip(
        """
    Hello team,

    You got a new Hammurabi update for {repository}.
    You can check the changes by clicking *<{changes_link}|here>*.
    """
    )

    notification = TestNotification([channel], message_template)
    notification.notify = Mock()
    notification.notify.side_effect = expected_exception

    notification.send(link)

    notification.notify.assert_called_once_with(
        message_template.format(repository=expected_repo, changes_link=link), link
    )
