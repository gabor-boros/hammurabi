from unittest.mock import patch, Mock

from hammurabi.exceptions import NotificationSendError
from hammurabi.notifications.slack import SlackNotification


@patch("hammurabi.notifications.slack.Slack")
def test_send_notification(mock_client_class):
    mock_client = Mock()
    mock_client_class.return_value = mock_client

    url = "https://slack.com"
    recipient = "CH1234"
    owner = "owner"
    message_template = "message template"
    changes_link = "https://github.com/gabor-boros/hammurabi/pull/1"

    notification = SlackNotification([recipient], message_template, url, owner)
    notification.send(changes_link)

    mock_client_class.assert_called_once_with(url=url)
    mock_client.post.assert_called_once_with(
            text="Hammurabi opened a new PR",
            channel=recipient,
            attachments=[
                {
                    "fallback": "Hammurabi PR",
                    "author_name": owner,
                    "title": "Hammurabi Pull Request",
                    "title_link": f"{changes_link or ''}",
                    "type": "mrkdwn",
                    "text": message_template,
                }
            ],
        )


@patch("hammurabi.notifications.slack.Slack")
def test_send_notification_error(mock_client_class):
    mock_client = Mock()
    mock_client.post.side_effect = NotificationSendError("fake notification")

    mock_client_class.return_value = mock_client

    url = "https://slack.com"
    recipient = "CH1234"
    owner = "owner"
    message_template = "message template"
    changes_link = "https://github.com/gabor-boros/hammurabi/pull/1"

    notification = SlackNotification([recipient], message_template, url, owner)
    notification.send(changes_link)

    mock_client_class.assert_called_once_with(url=url)
    mock_client.post.assert_called_once_with(
            text="Hammurabi opened a new PR",
            channel=recipient,
            attachments=[
                {
                    "fallback": "Hammurabi PR",
                    "author_name": owner,
                    "title": "Hammurabi Pull Request",
                    "title_link": f"{changes_link or ''}",
                    "type": "mrkdwn",
                    "text": message_template,
                }
            ],
        )
