"""
Directories module contains directory specific manipulation rules. Please
note that those rules which can be used for files and directories are
located in other modules like :mod:`hammurabi.rules.operations` or
:mod:`hammurabi.rules.attributes`.
"""

import logging
import os
from pathlib import Path
import shutil

from hammurabi.rules.common import SinglePathRule


class DirectoryExists(SinglePathRule):
    """
    Ensure that a directory exists. If the directory does not exists,
    make sure the directory is created.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, DirectoryExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         DirectoryExists(
        >>>             name="Create secrets directory",
        >>>             path=Path("./secrets")
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """

    def task(self) -> Path:
        """
        Create the given directory if not exists.

        :return: Return the input path as an output
        :rtype: Path
        """

        logging.debug('Creating directory "%s" if not exists', str(self.param))
        self.param.mkdir()

        return self.param


class DirectoryNotExists(SinglePathRule):
    """
    Ensure that the given directory does not exists.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, DirectoryNotExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         DirectoryNotExists(
        >>>             name="Remove unnecessary directory",
        >>>             path=Path("./temp")
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """

    def post_task_hook(self):
        """
        Remove the given directory from git index.
        """

        self.git_remove(self.param)

    def task(self) -> Path:
        """
        Remove the given directory.

        :return: Return the input path as an output
        :rtype: Path
        """

        if self.param.exists():
            logging.debug('Removing directory "%s"', str(self.param))
            shutil.rmtree(self.param)

        return self.param


class DirectoryEmptied(SinglePathRule):
    """
    Ensure that the given directory's content is removed. Please note the
    difference between emptying a directory and recreating it. The latter
    results in lost ACLs, permissions and modes.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, DirectoryEmptied
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         DirectoryEmptied(
        >>>             name="Empty results directory",
        >>>             path=Path("./test-results")
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """

    def task(self) -> Path:
        """
        Iterate through the entries of the given directory and remove them.
        If an entry is a file simply remove it, otherwise remove the whole
        subdirectory and its content.

        :return: Return the input path as an output
        :rtype: Path
        """

        with os.scandir(self.param) as entries:
            for entry in map(Path, entries):
                logging.debug('Removing "%s"', str(entry))

                if entry.is_file() or entry.is_symlink():
                    entry.unlink()

                elif entry.is_dir():
                    shutil.rmtree(entry)

        return self.param
