from abc import abstractmethod
import logging
from pathlib import Path
from typing import Iterable, Optional, Tuple, Union

from hammurabi.rules.files import SingleFileRule

try:
    from configupdater import ConfigUpdater  # type: ignore
except ImportError as exc:
    raise RuntimeError(f"{str(exc)}: Run `pip install hammurabi[ini]`")


class SingleConfigFileRule(SingleFileRule):
    """
    TODO:
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        section: Optional[str] = None,
        **kwargs,
    ):
        """
        TODO
        """

        self.section = self.validate(section, required=True)
        self.updater = ConfigUpdater()

        super().__init__(name, path, **kwargs)

    def pre_task_hook(self):
        """
        Parse the configuration file for later use.
        """

        logging.debug('parsing "%s" configuration file', self.param)
        self.updater.read(self.param)

    @abstractmethod
    def task(self, param: Path) -> Path:
        pass


class SectionExists(SingleConfigFileRule):
    """
    TODO
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        target: Optional[str] = None,
        options: Iterable[Tuple[str, Union[str, int]]] = (),
        add_after: bool = True,
        **kwargs,
    ):
        """
        TODO: Fill this
        """

        self.target = self.validate(target, required=True)
        self.options = options
        self.add_after = add_after

        self.space = 1

        super().__init__(name, path, **kwargs)

    def task(self, param: Path) -> Path:
        """
        TARGET IS NOT REGEXP! HIGHLIGHT THIS IN DOCS.
        """

        sections = self.updater.sections()

        if not sections:
            logging.debug('adding section "%s"', self.section)

            self.updater.add_section(self.section)

            for option, value in self.options:
                self.updater[self.section][option] = value

        if not self.updater.has_section(self.section):

            if self.target not in sections:
                raise LookupError(f'No matching section for "{self.target}"')

            logging.debug('adding section "%s"', self.section)
            target = self.updater[self.target]

            if not self.add_after:
                target.add_before.section(self.section).space(self.space)
            else:
                target.add_after.space(self.space).section(self.section)

            for option, value in self.options:
                self.updater[self.section][option] = value

        with param.open("w") as file:
            self.updater.write(file)

        return param


class SectionNotExists(SingleConfigFileRule):
    """
    Make sure that the given file not contains the specified line.
    """

    def task(self, param: Path) -> Path:
        """
        :raises: -
        """

        if self.section in self.updater.sections():

            logging.debug('Removing section "%s"', self.section)
            self.updater.remove_section(self.section)

            with param.open("w") as file:
                self.updater.write(file)

        return param


class SectionRenamed(SingleConfigFileRule):
    """
    Make sure that the given file not contains the specified line.
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

        self.new_name = self.validate(new_name, required=True)

        super().__init__(name, path, **kwargs)

    def task(self, param: Path) -> Path:
        """
        :raises: -
        """

        if not self.updater.has_section(self.section):
            raise LookupError(f'No matching section for "{self.section}"')

        logging.debug('Renaming "%s" to "%s"', self.section, self.new_name)
        self.updater[self.section].name = self.new_name

        with param.open("w") as file:
            self.updater.write(file)

        return param


class OptionsExist(SingleConfigFileRule):
    """
    TODO
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        options: Iterable[Tuple[str, Union[str, int]]] = None,
        force_value: bool = False,
        **kwargs,
    ):
        """
        TODO: Fill this
        options:
            (
                ("option name", "value IF NOT EXISTS or FORCED")
            )
        """

        self.options = self.validate(options, required=True)
        self.force_value = force_value

        super().__init__(name, path, **kwargs)

    def task(self, param: Path) -> Path:
        """
        TODO:
        """

        for option, value in self.options:
            if not self.updater.has_option(self.section, option) or self.force_value:
                logging.debug('Adding option "%s" = "%s"', option, value)
                self.updater[self.section][option] = value

        with param.open("w") as file:
            self.updater.write(file)

        return param


class OptionsNotExist(SingleConfigFileRule):
    """
    TODO
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        options: Iterable[str] = (),
        **kwargs,
    ):
        """
        TODO: Fill this
        """

        self.options = self.validate(options, required=True)

        super().__init__(name, path, **kwargs)

    def task(self, param: Path) -> Path:
        """
        TODO:
        """

        for option in self.options:
            logging.debug('Removing option "%s"', option)
            self.updater.remove_option(self.section, option)

        with param.open("w") as file:
            self.updater.write(file)

        return param


class OptionRenamed(SingleConfigFileRule):
    """
    TODO
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        option: Optional[str] = None,
        new_name: Optional[str] = None,
        **kwargs,
    ):
        """
        TODO: Fill this
        """

        self.option = self.validate(option, required=True)
        self.new_name = self.validate(new_name, required=True)

        super().__init__(name, path, **kwargs)

    def task(self, param: Path) -> Path:
        """
        TODO:
        """

        if not self.updater.has_option(self.section, self.option):
            raise LookupError(f'No matching option for "{self.option}"')

        logging.debug(
            'Replacing option "%s" with "%s"', str(self.option), self.new_name
        )

        self.updater[self.section][self.option].name = self.new_name

        with param.open("w") as file:
            self.updater.write(file)

        return param
