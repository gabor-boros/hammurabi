"""
Ini module is an extension for text rules tailor made for .ini/.cfg files.
The main difference lies in the way it works. First, the .ini/.cfg file is
parsed, then the modifications are made on the already parsed file.
"""

from abc import abstractmethod
import logging
from pathlib import Path
from typing import Any, Iterable, Optional, Tuple

from configupdater import ConfigUpdater  # type: ignore
from configupdater.configupdater import Section  # type: ignore

from hammurabi.rules.common import SinglePathRule


class SingleConfigFileRule(SinglePathRule):
    """
    Extend :class:`hammurabi.rules.base.Rule` to handle parsed content
    manipulations on a single file.
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        section: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.section = self.validate(section, required=True)
        self.updater = ConfigUpdater()

        super().__init__(name, path, **kwargs)

    def pre_task_hook(self) -> None:
        """
        Parse the configuration file for later use.
        """

        logging.debug('parsing "%s" configuration file', self.param)
        self.updater.read(self.param)

    @abstractmethod
    def task(self) -> Any:
        """
        Abstract method representing how a :func:`hammurabi.rules.base.Rule.task`
        must be parameterized. Any difference in the parameters will result in
        pylint/mypy errors.

        For more details please check :func:`hammurabi.rules.base.Rule.task`.
        """


class SectionExists(SingleConfigFileRule):
    """
    Ensure that the given config section exists. If needed, the rule will create
    a config section with the given name, and optionally the specified options. In
    case options are set, the config options will be assigned to that config sections.

    Similarly to :mod:`hammurabi.rules.text.LineExists`, this rule is able to add a
    section before or after a target section. The limitation compared to ``LineExists``
    is that the ``SectionExists`` rule is only able to add the new entry exactly before
    or after its target.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, SectionExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         SectionExists(
        >>>             name="Ensure section exists",
        >>>             path=Path("./config.ini"),
        >>>             section="polling",
        >>>             target="add_after_me",
        >>>             options=(
        >>>                 ("interval", "2s"),
        >>>                 ("abort_on_error", True),
        >>>             ),
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)

    .. warning::

        When ``options`` parameter is set, make sure you are using an iterable tuple.
        The option keys must be strings, but there is no limitation for the value. It can
        be set to anything what the parser can handle. For more information on the parser,
        please visit the documentation of  configupdater_.

        .. _configupdater: https://configupdater.readthedocs.io/en/latest/
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        target: Optional[str] = None,
        options: Iterable[Tuple[str, Any]] = (),
        add_after: bool = True,
        **kwargs,
    ) -> None:
        self.target = target
        self.options = options
        self.add_after = add_after

        self.space = 1

        super().__init__(name, path, **kwargs)

    def __get_target(self) -> Section:
        """
        Get the target of the insert. If the target is not
        specified directly add as the last section.
        """

        if self.updater.has_section(self.target):
            return self.updater[self.target]

        return self.updater.sections_blocks()[-1]

    def task(self) -> Path:
        """
        Ensure that the given config section exists. If needed, create a config section with
        the given name, and optionally the specified options.

        :return: Return the input path as an output
        :rtype: Path
        """

        sections = self.updater.sections()

        if not sections:
            logging.debug('adding section "%s"', self.section)

            self.updater.add_section(self.section)

            for option, value in self.options:
                self.updater[self.section][option] = value

        if not self.updater.has_section(self.section):
            logging.debug('adding section "%s"', self.section)

            target = self.__get_target()

            if self.add_after:
                target.add_after.space(self.space).section(self.section)
            else:
                target.add_before.section(self.section)

            for option, value in self.options:
                self.updater[self.section][option] = value

        with self.param.open("w") as file:
            self.updater.write(file)

        return self.param


class SectionNotExists(SingleConfigFileRule):
    """
    Make sure that the given file not contains the specified line. When a section
    removed, all the options belonging to it will be removed too.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, SectionNotExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         SectionNotExists(
        >>>             name="Ensure section removed",
        >>>             path=Path("./config.ini"),
        >>>             section="invalid",
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """

    def task(self) -> Path:
        """
        Remove the given section including its options from the config file.

        :return: Return the input path as an output
        :rtype: Path
        """

        if self.updater.has_section(self.section):

            logging.debug('Removing section "%s"', self.section)
            self.updater.remove_section(self.section)

            with self.param.open("w") as file:
                self.updater.write(file)

        return self.param


class SectionRenamed(SingleConfigFileRule):
    """
    Ensure that a section is renamed. None of its options will be changed.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, SectionRenamed
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         SectionRenamed(
        >>>             name="Ensure section renamed",
        >>>             path=Path("./config.ini"),
        >>>             section="polling",
        >>>             new_name="fetching",
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
        self.new_name = self.validate(new_name, required=True)

        super().__init__(name, path, **kwargs)

    def task(self) -> Path:
        """
        Rename the given section to a new name. None of its options will be
        changed. In case a section can not be found, a ``LookupError`` exception
        will be raised to stop the execution. The execution must be stopped at
        this point, because if other rules depending on the rename they will fail
        otherwise.

        :raises: ``LookupError`` if we can not decide or can not find what should be renamed
        :return: Return the input path as an output
        :rtype: Path
        """

        has_old_section = self.updater.has_section(self.section)
        has_new_section = self.updater.has_section(self.new_name)

        if has_old_section and has_new_section:
            raise LookupError(f'Both "{self.section}" and "{self.new_name}" set')

        if has_new_section:
            return self.param

        if not has_old_section:
            raise LookupError(f'No matching section for "{self.section}"')

        logging.debug('Renaming "%s" to "%s"', self.section, self.new_name)
        self.updater[self.section].name = self.new_name

        with self.param.open("w") as file:
            self.updater.write(file)

        return self.param


class OptionsExist(SingleConfigFileRule):
    """
    Ensure that the given config option exists. If needed, the rule will create
    a config option with the given value. In case the ``force_value`` parameter is
    set to True, the original values will be replaced by the give ones.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, OptionsExist
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         OptionsExist(
        >>>             name="Ensure options are changed",
        >>>             path=Path("./config.ini"),
        >>>             section="fetching",
        >>>             options=(
        >>>                 ("interval", "2s"),
        >>>                 ("abort_on_error", True),
        >>>             ),
        >>>             force_value=True,
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)

    .. warning::

        When using the ``force_value`` parameter, please note that all the existing
        option values will be replaced by those set in ``options`` parameter.
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        options: Iterable[Tuple[str, Any]] = None,
        force_value: bool = False,
        **kwargs,
    ) -> None:
        self.options = self.validate(options, required=True)
        self.force_value = force_value

        super().__init__(name, path, **kwargs)

    def task(self) -> Path:
        """
        Remove one or more option from a section. In case a section can not be
        found, a ``LookupError`` exception will be raised to stop the execution.
        The execution must be stopped at this point, because if dependant rules
        will fail otherwise.

        :raises: ``LookupError`` raised if no section can be renamed
        :return: Return the input path as an output
        :rtype: Path
        """

        if not self.updater.has_section(self.section):
            raise LookupError(f'No matching section for "{self.section}"')

        for option, value in self.options:
            if not self.updater.has_option(self.section, option) or self.force_value:
                logging.debug('Adding option "%s" = "%s"', option, value)
                self.updater[self.section][option] = value

        with self.param.open("w") as file:
            self.updater.write(file)

        return self.param


class OptionsNotExist(SingleConfigFileRule):
    """
    Remove one or more option from a section.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, OptionsNotExist
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         OptionsNotExist(
        >>>             name="Ensure options are removed",
        >>>             path=Path("./config.ini"),
        >>>             section="invalid",
        >>>             options=(
        >>>                 "remove",
        >>>                 "me",
        >>>                 "please",
        >>>             )
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
        options: Iterable[str] = (),
        **kwargs,
    ) -> None:
        self.options = self.validate(options, required=True)

        super().__init__(name, path, **kwargs)

    def task(self) -> Path:
        """
        Remove one or more option from a section. In case a section can not be
        found, a ``LookupError`` exception will be raised to stop the execution.
        The execution must be stopped at this point, because if dependant rules
        will fail otherwise.

        :raises: ``LookupError`` raised if no section can be renamed
        :return: Return the input path as an output
        :rtype: Path
        """

        if not self.updater.has_section(self.section):
            raise LookupError(f'No matching section for "{self.section}"')

        for option in self.options:
            logging.debug('Removing option "%s"', option)
            self.updater.remove_option(self.section, option)

        with self.param.open("w") as file:
            self.updater.write(file)

        return self.param


class OptionRenamed(SingleConfigFileRule):
    """
    Ensure that an option of a section is renamed.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, OptionRenamed
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         OptionRenamed(
        >>>             name="Rename an option",
        >>>             path=Path("./config.ini"),
        >>>             section="my_section",
        >>>             option="typo",
        >>>             new_name="correct",
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
        option: Optional[str] = None,
        new_name: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.option = self.validate(option, required=True)
        self.new_name = self.validate(new_name, required=True)

        super().__init__(name, path, **kwargs)

    def task(self) -> Path:
        """
        Rename an option of a section. In case a section can not be
        found, a ``LookupError`` exception will be raised to stop the execution.
        The execution must be stopped at this point, because if dependant rules
        will fail otherwise.

        :raises: ``LookupError`` raised if no section found or both the old and new
                 option names are found
        :return: Return the input path as an output
        :rtype: Path
        """

        if not self.updater.has_section(self.section):
            raise LookupError(f'No matching section for "{self.section}"')

        has_old_option = self.updater[self.section].get(self.option)
        has_new_option = self.updater[self.section].get(self.new_name)

        if has_old_option and has_new_option:
            raise LookupError(f'Both "{self.option}" and "{self.new_name}" set')

        if has_new_option:
            return self.param

        if not has_old_option:
            raise LookupError(f'No matching option for "{self.section}"')

        logging.debug(
            'Replacing option "%s" with "%s"', str(self.option), self.new_name
        )

        self.updater[self.section][self.option].name = self.new_name

        with self.param.open("w") as file:
            self.updater.write(file)

        return self.param
