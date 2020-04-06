"""
This module contains the definition of Preconditions which are related
to directories.
"""

from pathlib import Path

from hammurabi.preconditions.base import Precondition


class IsDirectoryExists(Precondition):
    """
    Check if the given directory exists.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, Renamed, IsDirectoryExists
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
        >>> pillar = Pillar()
        >>> pillar.register(example_law)

    :param path: Input directory's path
    :type path: Path
    """

    def __init__(self, path: Path, **kwargs) -> None:
        super().__init__(param=path, **kwargs)

    def task(self) -> bool:
        """
        Check if the given directory exists.

        :return: Returns True if the directory exists
        :rtype: bool
        """

        self.param: Path
        return self.param.exists() and self.param.is_dir()


class IsDirectoryNotExists(IsDirectoryExists):
    """
    Opposite of :class:`hammurabi.preconditions.directories.IsDirectoryExists`.
    """

    def task(self) -> bool:
        """
        Check if the given directory not exists.

        :return: Returns True if the directory not exists
        :rtype: bool
        """

        return not super().task()
