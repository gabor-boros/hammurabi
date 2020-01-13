from abc import abstractmethod
import logging
from pathlib import Path
from typing import Iterable, Optional

from hammurabi.mixins import GitActionsMixin
from hammurabi.rules.base import Rule


class SingleFileRule(Rule, GitActionsMixin):
    """
    Abstract class which extends :class:`hammurabi.rules.base.Rule` to handle operations on a
    single file.
    """

    def __init__(self, name: str, path: Optional[Path] = None, **kwargs):
        super().__init__(name, path, **kwargs)

    def post_task_hook(self):
        self.git_add(self.param)

    @abstractmethod
    def task(self, param: Path) -> Path:
        pass


class MultipleFilesRule(Rule, GitActionsMixin):
    """
    Abstract class which extends :class:`hammurabi.rules.base.Rule` to handle operations on
    multiple files.
    """

    def __init__(self, name: str, paths: Optional[Iterable[Path]] = (), **kwargs):
        super().__init__(name, paths, **kwargs)

    def post_task_hook(self):
        for path in self.param:
            self.git_add(path)

    @abstractmethod
    def task(self, param: Iterable[Path]) -> Iterable[Path]:
        pass


class FileExists(SingleFileRule):
    """
    Ensure that a file exists. If the file does not exists,
    this :class:`hammurabi.rules.base.Rule` will create it.
    """

    def task(self, param: Path) -> Path:
        """
        If the target file not exists, create the file to make sure we
        can manipulate it.
        """

        logging.debug('Creating file "%s" if not exists', str(param))
        param.touch()

        return param


class FilesExist(MultipleFilesRule):
    """
    Ensure that all files exists. If the files does not exists,
    this :class:`hammurabi.rules.base.Rule` will create them.
    """

    def task(self, param: Iterable[Path]) -> Iterable[Path]:
        """
        If the target files not exist, create the files to make sure we
        can manipulate them.
        """

        for path in param:
            logging.debug('Creating file "%s" if not exists', str(param))
            path.touch()

        return param


class FileNotExists(SingleFileRule):
    """
    Ensure that the given file does not exists.
    """

    def post_task_hook(self):
        """
        Remove the given file from git index.
        """

        self.git_remove(self.param)

    def task(self, param: Path) -> Path:
        """
        Remove the given file.
        """

        if self.can_proceed and param.exists():
            logging.debug('Unlinking "%s"', str(param))
            param.unlink()

        return param


class FilesNotExist(MultipleFilesRule):
    """
    Ensure that the given files does not exist.
    """

    def post_task_hook(self):
        """
        Remove the given files from git index.
        """

        for path in self.param:
            self.git_remove(path)

    def task(self, param: Iterable[Path]) -> Iterable[Path]:
        """
        Remove all existing files.
        """

        if self.can_proceed:
            for path in param:
                if path.exists():
                    logging.debug('Unlinking "%s"', str(path))
                    path.unlink()

        return param


class FileEmptied(SingleFileRule):
    """
    TODO: Fill
    """

    def task(self, param: Path) -> Path:
        logging.debug('Emptying "%s"', str(param))
        param.write_text("")

        return param
