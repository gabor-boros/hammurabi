"""
Files module contains file specific manipulation rules. Please note that
those rules which can be used for files and directories are located in
other modules like :mod:`hammurabi.rules.operations` or
:mod:`hammurabi.rules.attributes`.
"""

import logging
from pathlib import Path
from typing import Iterable

from hammurabi.rules.common import MultiplePathRule, SinglePathRule


class FileExists(SinglePathRule):
    """
    Ensure that a file exists. If the file does not exists,
    make sure the file is created.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, FileExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         FileExists(
        >>>             name="Create service descriptor",
        >>>             path=Path("./service.yaml")
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """

    def task(self) -> Path:
        """
        If the target file not exists, create the file to make sure we
        can manipulate it.

        :return: The created/existing file's path
        :rtype: Path
        """

        logging.debug('Creating file "%s" if not exists', str(self.param))
        self.param.touch()

        return self.param


class FilesExist(MultiplePathRule):
    """
    Ensure that all files exists. If the files does not exists,
    make sure the files are created.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, FilesExist
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         FilesExist(
        >>>             name="Create test files",
        >>>             paths=[
        >>>                 Path("./file_1"),
        >>>                 Path("./file_2"),
        >>>                 Path("./file_3"),
        >>>             ]
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """

    def task(self) -> Iterable[Path]:
        """
        If the target files not exist, create the files to make sure we
        can manipulate them.

        :return: The created/existing files' path
        :rtype: Iterable[Path]
        """

        for path in self.param:
            logging.debug('Creating file "%s" if not exists', str(path))
            path.touch()

        return self.param


class FileNotExists(SinglePathRule):
    """
    Ensure that the given file does not exists. If the file exists
    remove it, otherwise do nothing and return the original path.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, FileNotExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         FileNotExists(
        >>>             name="Remove unused file",
        >>>             path=Path("./debug.yaml")
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """

    def post_task_hook(self):
        """
        Remove the given file from git index.
        """

        self.git_remove(self.param)

    def task(self) -> Path:
        """
        Remove the given file if exists, otherwise do nothing and
        return the original path.

        :return: Return the removed file's path
        :rtype: Path
        """

        if self.param.exists():
            logging.debug('Unlinking "%s"', str(self.param))
            self.param.unlink()

        return self.param


class FilesNotExist(MultiplePathRule):
    """
    Ensure that the given files does not exist. If the files exist
    remove them, otherwise do nothing and return the original paths.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, FilesNotExist
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         FilesNotExist(
        >>>             name="Remove several files",
        >>>             paths=[
        >>>                 Path("./file_1"),
        >>>                 Path("./file_2"),
        >>>                 Path("./file_3"),
        >>>             ]
        >>>         ),
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """

    def post_task_hook(self):
        """
        Remove the given files from git index.
        """

        for path in self.param:
            self.git_remove(path)

    def task(self) -> Iterable[Path]:
        """
        Remove all existing files.

        :return: Return the removed files' paths
        :rtype: Iterable[Path]
        """

        for path in self.param:
            if path.exists():
                logging.debug('Unlinking "%s"', str(path))
                path.unlink()

        return self.param


class FileEmptied(SinglePathRule):
    """
    Remove the content of the given file, but keep the file. Please note the
    difference between emptying a file and recreating it. The latter
    results in lost ACLs, permissions and modes.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, FileEmptied
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         FileEmptied(
        >>>             name="Empty the check log file",
        >>>             path=Path("/var/log/service/check.log")
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """

    def task(self) -> Path:
        """
        Remove the content of the given file. If the file does not exists
        this rule will create the file without content.

        :return: Return the emptied/created file's path
        :rtype: Path
        """

        logging.debug('Emptying "%s"', str(self.param))
        self.param.write_text("")

        return self.param
