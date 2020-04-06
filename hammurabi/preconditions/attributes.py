"""
This module contains the definition of Preconditions which are related
to attributes of a file or directory.
"""

from pathlib import Path

from hammurabi.preconditions.base import Precondition


class IsOwnedBy(Precondition):
    """
    Check if the given file or directory has the required ownership.

    To check only the user use ``owner="username"``. To check only the
    group use ``owner=":group_name"`` (please note the colon ``:``).
    It is also possible to check both username and group at the same time
    by using ``owner="username:group_name"``.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, Renamed, IsOwnedBy
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         Renamed(
        >>>             name="Rename pyproject.toml if owned by gabor",
        >>>             path=Path("./pyproject.toml"),
        >>>             new_name="gabor-pyproject.toml"
        >>>             preconditions=[
        >>>                 IsOwnedBy(path=Path("./pyproject.toml"), owner="gabor")
        >>>             ]
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)

    :param path: Input file's path
    :type path: Path

    :param owner: Owner user and/or group of the file/directory separated by colon
    :type owner: str
    """

    def __init__(self, path: Path, owner: str, **kwargs) -> None:
        self.user, self.group = map(lambda x: x.strip(), owner.partition(":")[::2])
        super().__init__(param=path, **kwargs)

    def task(self) -> bool:
        """
        Check if the ownership meets the requirements.

        :return: Returns True if the owner matches
        :rtype: bool
        """

        self.param: Path

        is_owned = False
        is_owned_by_user = self.user == self.param.owner()
        is_owned_by_group = self.group == self.param.group()

        if self.user and self.group:
            is_owned = is_owned_by_user and is_owned_by_group
        elif self.user:
            is_owned = is_owned_by_user
        elif self.group:
            is_owned = is_owned_by_group

        return is_owned


class IsNotOwnedBy(IsOwnedBy):
    """
    Opposite of :class:`hammurabi.preconditions.attributes.IsOwnedBy`.
    """

    def task(self) -> bool:
        """
        Check if the ownership does not meet the requirements.

        :return: Returns True if the owner matches
        :rtype: bool
        """

        return not super().task()


class HasMode(Precondition):
    """
    Check if the given file or directory has the required permissions/mode.

    You can read more about the available modes at https://docs.python.org/3/library/stat.html.

    Example usage:

    .. code-block:: python

        >>> import stat
        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, Renamed, HasMode
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         Renamed(
        >>>             name="Rename pyproject.toml if owned by gabor",
        >>>             path=Path("./pyproject.toml"),
        >>>             new_name="gabor-pyproject.toml"
        >>>             preconditions=[
        >>>                 HasMode(path=Path("scripts/run_unittests.sh"), mode=stat.S_IXOTH)
        >>>             ]
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)

    :param path: Input file's path
    :type path: Path

    :param mode: The desired mode to check
    :type mode: str
    """

    def __init__(self, path: Path, mode: int, **kwargs) -> None:
        self.mode = mode
        super().__init__(param=path, **kwargs)

    def task(self) -> bool:
        """
        Check if the given mode is set on the file or directory.

        :return: Returns True if the desired mode is set
        :rtype: bool
        """

        self.param: Path
        return bool(self.param.stat().st_mode & self.mode)


class HasNoMode(HasMode):
    """
    Opposite of :class:`hammurabi.preconditions.attributes.HasMode`.
    """

    def task(self) -> bool:
        """
        Check if the given mode is not set on the file or directory.

        :return: Returns True if the desired mode is not set
        :rtype: bool
        """

        return not super().task()
