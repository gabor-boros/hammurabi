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
        pass


class DirectoryExists(SingleDirectoryRule):
    """
    Ensure that a directory exists. If the directory does not exists,
    this :class:`hammurabi.rules.base.Rule` will create it.
    """

    def task(self, param: Path) -> Path:
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
        """

        if param.exists():
            logging.debug('Removing directory "%s"', str(param))
            shutil.rmtree(param)

        return param


class DirectoryEmptied(SingleDirectoryRule):
    """
    Ensure that the given directory's content is removed.
    """

    def task(self, param: Path) -> Path:
        """
        Remove the content of the given directory.
        """

        with os.scandir(param) as entries:
            for entry in map(Path, entries):
                logging.debug('Removing "%s"', str(entry))

                if entry.is_file() or entry.is_symlink():
                    entry.unlink()

                elif entry.is_dir():
                    shutil.rmtree(entry)

        return param
