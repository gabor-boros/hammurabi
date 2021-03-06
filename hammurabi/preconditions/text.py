"""
This module contains the definition of Preconditions which are related
to general text files.
"""

from pathlib import Path
import re

from hammurabi.preconditions.base import Precondition


class IsLineExist(Precondition):
    """
    Check if the given line exists.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, Renamed, IsLineExist
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
        >>>                 IsLineExist(path=Path("other-file"), criteria=r"^string=some-value$")
        >>>             ]
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)

    :param path: Input files's path
    :type path: Path

    :param criteria: Regexp of the desired line
    :type criteria: str

    .. warning::

        When using ``criteria`` be aware that partial matches will be recognized
        as well. This means you must be as strict with regular expressions as
        it is needed. Example of a partial match:

        >>> import re
        >>> pattern = re.compile(r"apple")
        >>> text = "appletree"
        >>> pattern.match(text).group()
        >>> 'apple'
    """

    def __init__(self, path: Path, criteria: str, **kwargs) -> None:
        self.criteria = re.compile(self.validate(criteria, required=True))
        super().__init__(param=path, **kwargs)

    def task(self) -> bool:
        """
        Check if the given line exists.

        :return: Returns True if the line exists
        :rtype: bool
        """

        self.param: Path
        lines = self.param.read_text().splitlines()
        return any(filter(self.criteria.match, lines))


class IsLineNotExist(IsLineExist):
    """
    Opposite of :class:`hammurabi.preconditions.text.IsLineExist`.
    """

    def task(self) -> bool:
        """
        Check if the given line not exists.

        :return: Returns True if the line not exists
        :rtype: bool
        """

        return not super().task()
