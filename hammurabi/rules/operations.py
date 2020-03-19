"""
Operations module contains common file/directory operation which can be
handy when need to move, rename or copy files.
"""

import logging
from pathlib import Path
import shutil
from typing import Optional

from hammurabi.rules.common import SinglePathRule


class Moved(SinglePathRule):
    """
    Move a file or directory from "A" to "B".

    Example usage:

    .. code-block:: python

            >>> from pathlib import Path
            >>> from hammurabi import Law, Pillar, Moved
            >>>
            >>> example_law = Law(
            >>>     name="Name of the law",
            >>>     description="Well detailed description what this law does.",
            >>>     rules=(
            >>>         Moved(
            >>>             name="Move pyproject.toml to its place",
            >>>             path=Path("/tmp/generated/pyproject.toml.template"),
            >>>             destination=Path("./pyproject.toml"),  # Notice the rename!
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
        destination: Optional[Path] = None,
        **kwargs,
    ) -> None:
        self.destination = self.validate(destination, required=True)
        super().__init__(name, path, **kwargs)

    def post_task_hook(self):
        """
        Add both the new and old git objects.
        """

        self.git_remove(self.param)
        self.git_add(self.destination)

    def task(self) -> Path:
        """
        Move the given path to the destination. In case the file got a
        new name when destination is provided, the file/directory will
        be moved to its new place with its new name.

        :return: Returns the new destination of the file/directory
        :rtype: Path
        """

        logging.debug('Moving "%s" to "%s"', str(self.param), str(self.destination))
        shutil.move(self.param, self.destination)

        return self.destination


class Renamed(Moved):
    """
    This rule is a shortcut for :class:`hammurabi.rules.operations.Moved`.
    Instead of destination path a new name is required.

    Example usage:

    .. code-block:: python

            >>> from pathlib import Path
            >>> from hammurabi import Law, Pillar, Renamed
            >>>
            >>> example_law = Law(
            >>>     name="Name of the law",
            >>>     description="Well detailed description what this law does.",
            >>>     rules=(
            >>>         Renamed(
            >>>             name="Rename pyproject.toml.bkp",
            >>>             path=Path("/tmp/generated/pyproject.toml.bkp"),
            >>>             new_name="pyproject.toml",
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
        new_name: Optional[str] = None,
        **kwargs,
    ) -> None:
        path_name: str = self.validate(new_name, required=True)
        destination = Path((path or self.param).parent, path_name)
        super().__init__(name, path, destination, **kwargs)


class Copied(SinglePathRule):
    """
    Ensure that the given file or directory is copied to the new path.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, Copied
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         Copied(
        >>>             name="Create backup file",
        >>>             path=Path("./service.yaml"),
        >>>             destination=Path("./service.bkp.yaml")
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
        destination: Optional[Path] = None,
        **kwargs,
    ) -> None:
        self.destination = self.validate(destination, required=True)
        super().__init__(name, path, **kwargs)

    def post_task_hook(self):
        """
        Add the destination and not the original path.
        """

        self.git_add(self.destination)

    def task(self) -> Path:
        """
        Copy the given file or directory to a new place.

        :return: Returns the path of the copied file/directory
        :rtype: Path
        """

        logging.debug('Copying "%s" to "%s"', str(self.param), str(self.destination))

        if self.param.is_dir():
            shutil.copytree(self.param, self.destination)
        else:
            shutil.copy2(self.param, self.destination)

        return self.destination
