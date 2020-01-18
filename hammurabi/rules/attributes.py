"""
Attributes module contains file and directory attribute manipulation
rules which can be handy after creating new files or directories or
even when adding execute permissions for a script in the project.
"""

from abc import abstractmethod
import logging
import os
from pathlib import Path
import shutil
from typing import Optional

from hammurabi.mixins import GitMixin
from hammurabi.rules.base import Rule


class SingleAttributeRule(Rule, GitMixin):
    """
    Extend :class:`hammurabi.rules.base.Rule` to handle attributes of a single
    file or directory.
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
    Change the ownership of a file or directory.

    The new ownership of a file or directory can be set in three ways.
    To set only the user use ``new_value="username"``. To set only the
    group use ``new_value=":group_name"`` (please note the colon ``:``).
    It is also possible to set both username and group at the same time
    by using ``new_value="username:group_name"``.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, OwnerChanged
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         OwnerChanged(
        >>>             name="Change ownership of nginx config",
        >>>             path=Path("./nginx.conf"),
        >>>             new_value="www:web_admin"
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """

    def task(self, param: Path) -> Path:
        """
        Change the ownership of the given file or directory.
        None of the new username or group name can contain colons,
        otherwise only the first two colon separated values will be
        used as username and group name.

        :param param: Input parameter of the task
        :type param: Path

        :return: Return the input path as an output
        :rtype: Path
        """

        user, group = self.new_value.partition(":")[::2]

        logging.debug('Changing owner of "%s" to "%s"', param, self.new_value)
        shutil.chown(str(param), user=user or None, group=group or None)

        return param


class ModeChanged(SingleAttributeRule):
    """
    Change the mode of a file or directory.

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

    Example usage:

    .. code-block:: python

        >>> import stat
        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, ModeChanged
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         ModeChanged(
        >>>             name="Update script must be executable",
        >>>             path=Path("./scripts/update.sh"),
        >>>             new_value=stat.S_IXGRP | stat.S_IXGRP | stat.S_IXOTH
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        new_value: Optional[int] = None,
        **kwargs
    ):
        # Passing the new value and then re-defining it is ugly, but needed
        # because the super class already has a validation on the new_value
        # field. For the first time it will be casted to string and then in
        # this __init__ it will be casted to integer. This logic can be
        # changed when it became frustrating.
        super().__init__(name, path, new_value=str(new_value), **kwargs)
        self.new_value = self.validate(self.new_value, cast_to=int, required=True)

    def task(self, param: Path) -> Path:
        """
        Change the mode of the given file or directory.

        :param param: Input parameter of the task
        :type param: Path

        :return: Return the input path as an output
        :rtype: Path
        """

        logging.debug('Changing mode of "%s" to "%s"', param, self.new_value)
        os.chmod(str(param), self.new_value)
        return param
