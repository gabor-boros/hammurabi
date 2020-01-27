"""
Directories module contains directory specific manipulation rules. Please
note that those rules which can be used for files and directories are
located in other modules like :module:`hammurabi.rules.operations` or
:module:`hammurabi.rules.attributes`.
"""

from abc import abstractmethod
import logging
import os
from pathlib import Path
import shutil
from typing import Optional

from hammurabi.mixins import GitMixin
from hammurabi.rules.base import Rule


class SingleDirectoryRule(Rule, GitMixin):
    """
    Abstract class which extends :class:`hammurabi.rules.base.Rule` to handle operations on a
    single directory.
    """

    def __init__(self, name: str, path: Optional[Path] = None, **kwargs):
        super().__init__(name, path, **kwargs)

    def post_task_hook(self):
        self.git_add(self.param)

    @abstractmethod
    def task(self, param: Path) -> Path:
        """
        Abstract method which does nothing and must be implemented by inheritors.

        :param param: The path of the target file which will be changed
        :type param: Path

        :return: Path of the directory which was changed
        :rtype: Path
        """


class DirectoryExists(SingleDirectoryRule):
    """
    Ensure that a directory exists. If the directory does not exists,
    make sure the directory is created.
    """

    def task(self, param: Path) -> Path:
        """
        Create the given directory if not exists.

        :param param: Input parameter of the task
        :type param: Path

        :return: Return the input path as an output
        :rtype: Path
        """

        logging.debug('Creating directory "%s" if not exists', str(self.param))
        param.mkdir()

        return param


class DirectoryNotExists(SingleDirectoryRule):
    """
    Ensure that the given directory does not exists.
    """

    def post_task_hook(self):
        """
        Remove the given directory from git index.
        """

        self.git_remove(self.param)

    def task(self, param: Path) -> Path:
        """
        Remove the given directory.

        :param param: Input parameter of the task
        :type param: Path

        :return: Return the input path as an output
        :rtype: Path
        """

        if param.exists():
            logging.debug('Removing directory "%s"', str(param))
            shutil.rmtree(param)

        return param


class DirectoryEmptied(SingleDirectoryRule):
    """
    Ensure that the given directory's content is removed. Please note the
    difference between emptying a directory and recreating it. The latter
    results in lost ACLs, permissions and modes.
    """

    def task(self, param: Path) -> Path:
        """
        Iterate through the entries of the given directory and remove them.
        If an entry is a file simply remove it, otherwise remove the whole
        subdirectory and its content.

        :param param: Input parameter of the task
        :type param: Path

        :return: Return the input path as an output
        :rtype: Path
        """

        with os.scandir(param) as entries:
            for entry in map(Path, entries):
                logging.debug('Removing "%s"', str(entry))

                if entry.is_file() or entry.is_symlink():
                    entry.unlink()

                elif entry.is_dir():
                    shutil.rmtree(entry)

        return param
