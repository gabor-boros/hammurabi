"""
Text module contains simple but powerful general file content manipulations.
Combined with other simple rules like :class:`hammurabi.rules.files.FileExists`
or :class:`hammurabi.rules.attributes.ModeChanged` almost anything can be
achieved. Although any file's content can be changed using these rules, for
common file formats like ``ini``, ``yaml`` or ``json`` dedicated rules are
created.
"""


import logging
from pathlib import Path
import re
from typing import List, Optional, Tuple

from hammurabi.rules.common import SinglePathRule


class LineExists(SinglePathRule):
    """
    Make sure that the given file contains the required line. This rule is
    capable for inserting the expected text before or after the unique target
    text respecting the indentation of its context.

    The default behaviour is to insert the required text exactly after the
    target line, and respect its indentation. Please note that ``text``,
    ``criteria`` and ``target`` parameters are required.

    Example usage:

    .. code-block:: python

            >>> from pathlib import Path
            >>> from hammurabi import Law, Pillar, LineExists
            >>>
            >>> example_law = Law(
            >>>     name="Name of the law",
            >>>     description="Well detailed description what this law does.",
            >>>     rules=(
            >>>         LineExists(
            >>>             name="Extend gunicorn config",
            >>>             path=Path("./gunicorn.conf.py"),
            >>>             text="keepalive = 65",
            >>>             criteria=r"^keepalive.*",
            >>>             target=r"^bind.*",
            >>>         ),
            >>>     )
            >>> )
            >>>
            >>> pillar = Pillar()
            >>> pillar.register(example_law)

    .. note::

        The indentation of the target text will be extracted by a simple
        regular expression. If a more complex regexp is required, please
        inherit from this class.
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        text: Optional[str] = None,
        criteria: Optional[str] = None,
        target: Optional[str] = None,
        position: int = 1,
        respect_indentation: bool = True,
        **kwargs,
    ) -> None:
        self.text = self.validate(text, required=True)
        self.criteria = re.compile(self.validate(criteria, required=True))
        self.target = re.compile(self.validate(target, required=True))
        self.position = position
        self.respect_indentation = respect_indentation

        self.indentation_pattern = re.compile(r"^\s+")

        super().__init__(name, path, **kwargs)

    def __get_target_match(self, lines: List[str]) -> str:
        """
        Get the matching target from the content of the given file.
        In case the matching number of lines are more than one or no
        match found, an exception will be raised accordingly.

        :param lines: Content of the given file
        :type lines: List[str]

        :raises: ``LookupError``

        :return: List of the matching line
        :rtype: str
        """

        target_match = list(filter(self.target.match, lines))

        if not any(target_match):
            raise LookupError(f'No matching line for "{self.target}"')

        if len(target_match) > 1:
            raise LookupError(f'Multiple matching lines for "{self.target}"')

        return target_match.pop()

    def __get_lines_from_file(self) -> Tuple[List[str], bool]:
        """
        Get the lines from the given file. In case of the file is empty, then
        append the expected line.

        :return: Returns the parsed lines and an indicator if the file was empty
        :rtype: tuple
        """

        file_was_empty = False

        with self.param.open("r") as file:
            logging.debug('Reading from "%s"', str(self.param))
            lines = file.read().splitlines()

        if not lines:
            logging.debug('Adding "%s" to "%s"', self.text, str(self.param))
            lines.append(self.text)
            file_was_empty = True

        return lines, file_was_empty

    def __write_content_to_file(self, lines: List[str]):
        """
        Write the extended content of the file back. When writing the lines it is
        important to watch out for the new line character at the end of every line.

        :param lines: The new content of the original file
        :type lines: List[str]
        """

        with self.param.open("w") as file:
            file.writelines((f"{line}\n" for line in lines))

    def task(self) -> Path:
        """
        Make sure that the given file contains the required line. This rule is
        capable for inserting the expected rule before or after the unique target
        text respecting the indentation of its context.

        :raises: ``LookupError``

        :return: Returns the path of the modified file
        :rtype: Path
        """

        lines, file_was_empty = self.__get_lines_from_file()

        no_criteria_match = not any(filter(self.criteria.match, lines))

        if not file_was_empty and no_criteria_match:
            target_match = self.__get_target_match(lines)
            target_match_index = lines.index(target_match)

            insert_position = target_match_index + self.position

            logging.debug('Inserting "%s" to position "%d"', self.text, insert_position)

            indentation = self.indentation_pattern.match(lines[target_match_index])
            if self.respect_indentation and indentation:
                self.text = indentation.group() + self.text

            lines.insert(insert_position, self.text)

        if file_was_empty or no_criteria_match:
            self.__write_content_to_file(lines)

        return self.param


class LineNotExists(SinglePathRule):
    """
    Make sure that the given file not contains the specified line.

    Example usage:

    .. code-block:: python

            >>> from pathlib import Path
            >>> from hammurabi import Law, Pillar, LineNotExists
            >>>
            >>> example_law = Law(
            >>>     name="Name of the law",
            >>>     description="Well detailed description what this law does.",
            >>>     rules=(
            >>>         LineNotExists(
            >>>             name="Remove keepalive",
            >>>             path=Path("./gunicorn.conf.py"),
            >>>             text="keepalive = 65",
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
        text: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.text = re.compile(self.validate(text, cast_to=str, required=True))

        super().__init__(name, path, **kwargs)

    def task(self) -> Path:
        """
        Make sure that the given file not contains the specified line based
        on the given criteria.

        :return: Returns the path of the modified file
        :rtype: Path
        """

        with self.param.open("r") as file:
            lines = file.read().splitlines()

        new_lines = list(filter(lambda l: not self.text.match(l), lines))

        if new_lines != lines:
            with self.param.open("w") as file:
                file.writelines((f"{line}\n" for line in new_lines))

        return self.param


class LineReplaced(SinglePathRule):
    """
    Make sure that the given text is replaced in the given file.

    The default behaviour is to replace the required text with the
    exact same indentation that the target line has. This behaviour
    can be turned off by setting the ``respect_indentation`` parameter
    to False.  Please note that ``text`` and ``target`` parameters are
    required.

    Example usage:

    .. code-block:: python

            >>> from pathlib import Path
            >>> from hammurabi import Law, Pillar, LineReplaced
            >>>
            >>> example_law = Law(
            >>>     name="Name of the law",
            >>>     description="Well detailed description what this law does.",
            >>>     rules=(
            >>>         LineReplaced(
            >>>             name="Replace typo using regex",
            >>>             path=Path("./gunicorn.conf.py"),
            >>>             text="keepalive = 65",
            >>>             target=r"^kepalive.*",
            >>>         ),
            >>>     )
            >>> )
            >>>
            >>> pillar = Pillar()
            >>> pillar.register(example_law)

    .. note::

        The indentation of the target text will be extracted by a simple
        regular expression. If a more complex regexp is required, please
        inherit from this class.

    .. warning::

        This rule will replace all the matching lines in the given file.
        Make sure the given target regular expression is tested before
        the rule used against production code.
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        text: Optional[str] = None,
        target: Optional[str] = None,
        respect_indentation: bool = True,
        **kwargs,
    ) -> None:
        self.text = self.validate(text, required=True)
        self.target = re.compile(self.validate(target, required=True))
        self.respect_indentation = respect_indentation

        self.indentation_pattern = re.compile(r"^\s+")

        super().__init__(name, path, **kwargs)

    def __get_target_match(self, lines: List[str]) -> List[str]:
        """
        Get the matching target lines from the content of the given file.
        In case no match found, an exception will be raised accordingly.

        :param lines: Content of the given file
        :type lines: List[str]

        :raises: ``LookupError``

        :return: List of the matching line
        :rtype: List[str]
        """

        target_match = list(filter(self.target.match, lines))

        if not any(target_match):
            raise LookupError(f'No matching line for "{self.target}"')

        return target_match

    def __get_lines_from_file(self) -> Tuple[List[str], bool]:
        """
        Get the lines from the given file.

        :return: Returns the parsed lines and an indicator if the file was empty
        :rtype: tuple
        """

        with self.param.open("r") as file:
            logging.debug('Reading from "%s"', str(self.param))
            lines = file.read().splitlines()

        return lines, not lines

    def __write_content_to_file(self, lines: List[str]):
        """
        Write the extended content of the file back. When writing the lines it is
        important to watch out for the new line character at the end of every line.

        :param lines: The new content of the original file
        :type lines: List[str]
        """

        with self.param.open("w") as file:
            file.writelines((f"{line}\n" for line in lines))

    def __replace_line(self, lines: List[str], target: str):
        """
        Replace the target texts with the given text.

        :param lines: The new content of the original file
        :type lines: List[str]

        :param target: The matching target in the given file's content
        :type target: str
        """

        target_index = lines.index(target)

        indentation = self.indentation_pattern.match(lines[target_index])
        if self.respect_indentation and indentation:
            self.text = indentation.group() + self.text

        lines[target_index] = self.text

    def task(self) -> Path:
        """
        Make sure that the given text is replaced in the given file.

        :raises: ``LookupError``

        :return: Returns the path of the modified file
        :rtype: Path
        """

        lines, file_was_empty = self.__get_lines_from_file()

        if not file_was_empty:
            for target in self.__get_target_match(lines):
                self.__replace_line(lines, target)

            self.__write_content_to_file(lines)

        return self.param
