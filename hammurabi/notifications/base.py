"""
Notifications are responsible for letting the end users/owners that a change
happened on a git repository. Notifications describes where to send the
notification but not responsible for delivering it. For example, you can use
an email notification method, but the notification method is not responsible
for handling emails and delivering the message.
"""


from abc import ABC, abstractmethod
import logging
from typing import List, Optional

from hammurabi.config import config
from hammurabi.exceptions import NotificationSendError
from hammurabi.helpers import full_strip


class Notification(ABC):
    """
    A ``git push`` notification which serves as a base for different kind
    of notifications like Slack or E-mail notification.
    """

    def __init__(self, recipients: List[str], message_template: str) -> None:
        self.recipients = recipients
        self.message_template = full_strip(message_template)

    def __format_message(self, changes_link: Optional[str]) -> str:
        """
        Fill the message template with actual values, such as repository owner/name
        and link to changes.

        :param changes_link: Link to the list of changes
        :type changes_link: Optional[str]

        :return: Returns the formatted message will be sent to the recipients
        :rtype: str
        """

        return self.message_template.format(
            repository=config.settings.repository, changes_link=changes_link
        )

    @abstractmethod
    def notify(self, message: str, changes_link: Optional[str]) -> None:
        """
        Handle sending the desired message to the recipients.

        :param message: Message to send
        :type message: str

        :param changes_link: Link to the list of changes
        :type changes_link: Optional[str]

        :raise: ``NotificationSendError`` if the notification cannot be delivered
        """

    def send(self, changes_link: Optional[str]) -> None:
        """
        Notify the users/owners about a change on the git repository. In case change
        link is provided, the user will be able to go directly checking the changes.

        :param changes_link: Link to the list of changes
        :type changes_link: Optional[str]
        """

        message = self.__format_message(changes_link)
        recipients = ", ".join(self.recipients)

        try:
            logging.info("Sending notification to %s", recipients)
            self.notify(message, changes_link)
        except NotificationSendError as exc:
            logging.error("Sending notification to %s failed: %s", recipients, str(exc))
