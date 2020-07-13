"""
Send notification to a slack channel when Hammurabi creates/updates a pull request.
"""

from typing import Iterable, Optional

from slack_webhook import Slack  # type: ignore

from hammurabi.exceptions import NotificationSendError
from hammurabi.notifications.base import Notification


class SlackNotification(Notification):
    """
    Send slack notification through Slack webhooks.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, Renamed, IsDirectoryExists, SlackNotification
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         Renamed(
        >>>             name="Rename the dir if an other one exists",
        >>>             path=Path("old-name"),
        >>>             new_name="new-name",
        >>>             preconditions=[
        >>>                 IsDirectoryExists(path=Path("other-dir"))
        >>>             ]
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar(notifications=[
        >>>     SlackNotification(
        >>>         recipients=["CHANNEL_ID"],
        >>>         message_template="Dear team, the {repository} has new update.",
        >>>         hook_url="https://slack.webhook.url",
        >>>         owner="MY_BOT",
        >>>     )
        >>> ])
        >>> pillar.register(example_law)
    """

    def __init__(
        self,
        recipients: Iterable[str],
        message_template: str,
        hook_url: str,
        owner: str,
    ) -> None:
        self.hook_url = hook_url
        self.owner = owner
        super(SlackNotification, self).__init__(recipients, message_template)

    def __send_notification(
        self, client, channel: str, message: str, changes_link: Optional[str]
    ) -> None:
        """
        Handle notification send through Slack webhooks.

        :param message: Message to send
        :type message: str

        :param changes_link: Link to the list of changes
        :type changes_link: Optional[str]
        """

        client.post(
            text="Hammurabi opened a new PR",
            channel=channel,
            attachments=[
                {
                    "fallback": "Hammurabi PR",
                    "author_name": self.owner,
                    "title": "Hammurabi Pull Request",
                    "title_link": f"{changes_link or ''}",
                    "type": "mrkdwn",
                    "text": message,
                }
            ],
        )

    def notify(self, message: str, changes_link: Optional[str]) -> None:
        """
        Handle notification send through Slack webhooks.

        :param message: Message to send
        :type message: str

        :param changes_link: Link to the list of changes
        :type changes_link: Optional[str]
        """

        try:
            client = Slack(url=self.hook_url)
            for channel in self.recipients:
                self.__send_notification(client, channel, message, changes_link)
        except Exception as exc:
            raise NotificationSendError(str(exc))
