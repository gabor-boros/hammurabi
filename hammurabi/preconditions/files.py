"""
Files preconditions module contains simple preconditions used for checking
file existence.
"""

from pathlib import Path

from hammurabi.preconditions.base import Precondition


class IsFileExists(Precondition):
    """
    Check if the given file exists.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, Renamed, IsFileExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         Renamed(
        >>>             name="Rename the file if an other one exists",
        >>>             path=Path("old-name"),
        >>>             new_name="new-name",
        >>>             preconditions=[
        >>>                 IsFileExists(path=Path("other-file"))
        >>>             ]
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)

    :param path: Input files's path
    :type path: Path
    """

    def __init__(self, path: Path, **kwargs) -> None:
        super().__init__(param=path, **kwargs)

    def task(self) -> bool:
        """
        Check if the given file exists.

        :return: Returns True if the file exists
        :rtype: bool
        """

        self.param: Path
        return self.param.exists() and self.param.is_file()


class IsFileNotExists(IsFileExists):
    """
    Opposite of :class:`hammurabi.preconditions.files.IsFileExists`.
    """

    def task(self) -> bool:
        """
        Check if the given file not exists.

        :return: Returns True if the file not exists
        :rtype: bool
        """

        return not super().task()
