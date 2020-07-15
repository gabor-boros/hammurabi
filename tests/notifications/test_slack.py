from unittest.mock import Mock, patch

from hammurabi.exceptions import NotificationSendError
from hammurabi.notifications.slack import SlackNotification


@patch("hammurabi.notifications.slack.Slack")
def test_send_notification(mock_client_class):
    mock_client = Mock()
    mock_client_class.return_value = mock_client

    recipient = "https://slack.com"
    message_template = "message template"
    changes_link = "https://github.com/gabor-boros/hammurabi/pull/1"

    notification = SlackNotification([recipient], message_template)
    notification.send(changes_link)

    mock_client_class.assert_called_once_with(url=recipient)
    mock_client.post.assert_called_once_with(text=message_template)


@patch("hammurabi.notifications.slack.Slack")
def test_send_notification_error(mock_client_class):
    mock_client = Mock()
    mock_client.post.side_effect = NotificationSendError("fake notification")

    mock_client_class.return_value = mock_client

    recipient = "https://slack.com"
    message_template = "message template"
    changes_link = "https://github.com/gabor-boros/hammurabi/pull/1"

    notification = SlackNotification([recipient], message_template)
    notification.send(changes_link)

    mock_client_class.assert_called_once_with(url=recipient)
    mock_client.post.assert_called_once_with(text=message_template)
