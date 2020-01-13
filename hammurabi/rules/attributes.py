from abc import abstractmethod
import logging
import os
from pathlib import Path
import shutil
from typing import Optional

from hammurabi.mixins import GitActionsMixin
from hammurabi.rules.base import Rule


class SingleAttributeRule(Rule, GitActionsMixin):
    """
    Abstract class which extends :class:`hammurabi.rules.base.Rule` to handle attributes of
    a single directory or file.
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        new_value: Optional[str] = None,
        **kwargs
    ):
        self.new_value = self.validate(new_value, cast_to=str, required=True)
        super().__init__(name, path, **kwargs)

    def post_task_hook(self):
        self.git_add(self.param)

    @abstractmethod
    def task(self, param: Path) -> Path:
        pass


class OwnerChanged(SingleAttributeRule):
    """
    TODO: Rephrase this description.

    Change the ownership of a file or directory.
    The new value can be set as user:group to set both,
    user to set only the user and :group to set only the group.
    """

    def task(self, param: Path) -> Path:
        user, group = self.new_value.partition(":")[::2]

        logging.debug('Changing owner of "%s" to "%s"', str(self.param), self.new_value)
        shutil.chown(param, user=user or None, group=group or None)

        return param


class ModeChanged(SingleAttributeRule):
    """
    TODO:

    Supported modes:

    +-------------------+-------------------------------------+
    | Config option     | Description                         |
    +===================+=====================================+
    | stat.S_ISUID      | Set user ID on execution.           |
    +-------------------+-------------------------------------+
    | stat.S_ISGID      | Set group ID on execution.          |
    +-------------------+-------------------------------------+
    | stat.S_ENFMT      | Record locking enforced.            |
    +-------------------+-------------------------------------+
    | stat.S_ISVTX      | Save text image after execution.    |
    +-------------------+-------------------------------------+
    | stat.S_IREAD      | Read by owner.                      |
    +-------------------+-------------------------------------+
    | stat.S_IWRITE     | Write by owner.                     |
    +-------------------+-------------------------------------+
    | stat.S_IEXEC      | Execute by owner.                   |
    +-------------------+-------------------------------------+
    | stat.S_IRWXU      | Read, write, and execute by owner.  |
    +-------------------+-------------------------------------+
    | stat.S_IRUSR      | Read by owner.                      |
    +-------------------+-------------------------------------+
    | stat.S_IWUSR      | Write by owner.                     |
    +-------------------+-------------------------------------+
    | stat.S_IXUSR      | Execute by owner.                   |
    +-------------------+-------------------------------------+
    | stat.S_IRWXG      | Read, write, and execute by group.  |
    +-------------------+-------------------------------------+
    | stat.S_IRGRP      | Read by group.                      |
    +-------------------+-------------------------------------+
    | stat.S_IWGRP      | Write by group.                     |
    +-------------------+-------------------------------------+
    | stat.S_IXGRP      | Execute by group.                   |
    +-------------------+-------------------------------------+
    | stat.S_IRWXO      | Read, write, and execute by others. |
    +-------------------+-------------------------------------+
    | stat.S_IROTH      | Read by others.                     |
    +-------------------+-------------------------------------+
    | stat.S_IWOTH      | Write by others.                    |
    +-------------------+-------------------------------------+
    | stat.S_IXOTH      | Execute by others.                  |
    +-------------------+-------------------------------------+
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        new_value: Optional[int] = None,
        **kwargs
    ):
        self.new_value = self.validate(new_value, cast_to=int, required=True)
        super().__init__(name, path, **kwargs)

    def task(self, param: Path) -> Path:
        logging.debug('Changing mode of "%s" to "%s"', str(self.param), self.new_value)
        os.chmod(param, self.new_value)
        return param
