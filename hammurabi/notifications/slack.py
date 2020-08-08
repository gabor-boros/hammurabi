"""
Send notification to a slack channel when Hammurabi creates/updates a pull request.
"""

import logging
from typing import Optional

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
        >>>         recipients=["https://slack.webhook.url"],
        >>>         message_template="Dear team, the {repository} has new update.",
        >>>     )
        >>> ])
        >>> pillar.register(example_law)

    .. warning::

        This notification requires the ``slack-notifications`` extra to be installed.
    """

    def notify(self, message: str, changes_link: Optional[str]) -> None:
        """
        Handle notification send through Slack webhooks.

        :param message: Message to send
        :type message: str

        :param changes_link: Link to the list of changes
        :type changes_link: Optional[str]
        """

        try:
            # Every recipient is a slack webhook URL
            for hook in self.recipients:
                logging.debug('Sending to hook "%s"', hook)
                Slack(url=hook).post(text=message)
                logging.debug("Notification sent")
        except Exception as exc:
            raise NotificationSendError(str(exc))
