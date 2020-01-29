import logging
from pathlib import Path
import shutil
from typing import Optional

from hammurabi.rules.common import SinglePathRule


class Moved(SinglePathRule):
    """
    TODO:
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        destination: Optional[Path] = None,
        **kwargs,
    ):
        """
        TODO: Fill this
        """

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
        Move the given path to the destination
        """

        logging.debug('Moving "%s" to "%s"', str(self.param), str(self.destination))
        shutil.move(self.param, self.destination)

        return self.destination


class Renamed(Moved):
    """
    Ensure that the given file or directory is renamed.
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        new_name: Optional[str] = None,
        **kwargs,
    ):
        """
        TODO: Fill this
        """

        path_name: str = self.validate(new_name, required=True)
        destination = Path((path or self.param).parent, path_name)
        super().__init__(name, path, destination, **kwargs)


class Copied(SinglePathRule):
    """
    Ensure that the given file or directory is copied to the new path.
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        destination: Optional[Path] = None,
        **kwargs,
    ):
        """
        TODO: Fill this
        """

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
        """

        logging.debug('Copying "%s" to "%s"', str(self.param), str(self.destination))
        shutil.copytree(self.param, self.destination)

        return self.destination
