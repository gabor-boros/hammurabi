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
    target line, and respect its indentation. Please note that ``text``and
    ``target`` parameters are required.

    Example usage:

    .. code-block:: python

            >>> from pathlib import Path
            >>> from hammurabi import Law, Pillar, LineExists, IsLineNotExists
            >>>
            >>> gunicorn_config = Path("./gunicorn.conf.py")
            >>> example_law = Law(
            >>>     name="Name of the law",
            >>>     description="Well detailed description what this law does.",
            >>>     rules=(
            >>>         LineExists(
            >>>             name="Extend gunicorn config",
            >>>             path=gunicorn_config,
            >>>             text="keepalive = 65",
            >>>             target=r"^bind.*",
            >>>             preconditions=[
            >>>                 IsLineNotExists(path=gunicorn_config, criteria=r"^keepalive.*")
            >>>             ]
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
        target: Optional[str] = None,
        position: int = 1,
        respect_indentation: bool = True,
        ensure_trailing_newline: bool = False,
        **kwargs,
    ) -> None:
        self.text = self.validate(text, required=True)
        self.target = re.compile(self.validate(target, required=True))
        self.position = position
        self.respect_indentation = respect_indentation

        self.indentation_pattern = re.compile(r"^\s+")
        self.ensure_trailing_newline = ensure_trailing_newline

        super().__init__(name, path, **kwargs)

    def __get_target_match(self, lines: List[str]) -> str:
        """
        Get the matching target from the content of the given file.
        In case the matching number of lines are more than one or no
        match found, an exception will be raised accordingly.

        :param lines: Content of the given file
        :type lines: List[str]

        :raises: ``LookupError`` if no matching line can be found for target

        :return: List of the matching line
        :rtype: str
        """

        target_match = list(filter(self.target.match, lines))

        if not target_match:
            raise LookupError(f'No matching line for "{self.target}"')

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
            lines: List[str] = file.read().splitlines()

            if self.ensure_trailing_newline and lines[-1].strip() != "":
                lines.append("")

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

    def __add_line(self, lines: List[str]) -> None:
        """
        Make sure that the expected line is added to the list
        of lines.

        :param lines: Lines read from the input file
        :type lines: List[str]
        """

        target_match = self.__get_target_match(lines)

        # Get the index of the element from the right
        target_match_index = len(lines) - lines[::-1].index(target_match) - 1

        insert_position = target_match_index + self.position

        logging.debug('Inserting "%s" to position "%d"', self.text, insert_position)

        indentation = self.indentation_pattern.match(lines[target_match_index])
        if self.respect_indentation and indentation:
            self.text = indentation.group() + self.text

        lines.insert(insert_position, self.text)

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

        if not file_was_empty:
            self.__add_line(lines)

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
        Make sure that the given file not contains the specified line.

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
    exact same indentation that the "match" line has. This behaviour
    can be turned off by setting the ``respect_indentation`` parameter
    to False.  Please note that ``text`` and ``match`` parameters are
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
            >>>             match=r"^kepalive.*",
            >>>         ),
            >>>     )
            >>> )
            >>>
            >>> pillar = Pillar()
            >>> pillar.register(example_law)

    .. note::

        The indentation of the `text` will be extracted by a simple
        regular expression. If a more complex regexp is required, please
        inherit from this class.

    .. warning::

        This rule will replace all the matching lines in the given file.
        Make sure the given `match` regular expression is tested before
        the rule used against production code.
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        text: Optional[str] = None,
        match: Optional[str] = None,
        respect_indentation: bool = True,
        **kwargs,
    ) -> None:
        self.text = self.validate(text, required=True)
        self.match = re.compile(self.validate(match, required=True))
        self.respect_indentation = respect_indentation

        self.indentation_pattern = re.compile(r"^\s+")

        super().__init__(name, path, **kwargs)

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

    def __replace_line(self, lines: List[str], match: str):
        """
        Replace the match texts with the given text.

        :param lines: The new content of the original file
        :type lines: List[str]

        :param match: The matching target in the given file's content
        :type match: str
        """

        match_index = lines.index(match)

        indentation = self.indentation_pattern.match(lines[match_index])
        if self.respect_indentation and indentation:
            self.text = indentation.group() + self.text

        lines[match_index] = self.text

    def task(self) -> Path:
        """
        Make sure that the given text is replaced in the given file.

        :raises: ``LookupError`` if we can not decide or can not find what should be replaced
        :return: Returns the path of the modified file
        :rtype: Path
        """

        lines, _ = self.__get_lines_from_file()

        match_match = list(filter(self.match.match, lines))
        text = list(filter(lambda l: l.strip() == self.text, lines))

        if match_match and text:
            raise LookupError(f'Both "{self.match}" and "{self.text}" exists')

        if text:
            return self.param

        if not match_match:
            raise LookupError(f'No matching line for "{self.match}"')

        for match in match_match:
            self.__replace_line(lines, match)

        self.__write_content_to_file(lines)

        return self.param
