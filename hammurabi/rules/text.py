import logging
from pathlib import Path
import re
from typing import Optional

from hammurabi.rules.files import SingleFileRule


class LineExists(SingleFileRule):
    """
    Make sure that the given file contains the required line.
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
    ):
        """
        TODO: Fill this
        """

        self.text = self.validate(text, required=True)
        self.criteria = re.compile(self.validate(criteria, required=True))
        self.target = re.compile(self.validate(target, required=True))
        self.position = position
        self.respect_indentation = respect_indentation

        self.indentation_pattern = re.compile(r"^\s+")

        super().__init__(name, path, **kwargs)

    def task(self, param: Path) -> Path:
        """
        :raises: -
        """

        with param.open("r") as file:
            lines = file.read().splitlines()

            if not lines:
                logging.debug('File "%s" is empty. Adding "%s"', str(param), self.text)
                lines.append(self.text)

        if not any(filter(self.criteria.match, lines)):
            target_match = list(filter(self.target.match, lines))

            if not any(target_match):
                raise LookupError(f'No matching line for "{self.target}"')

            if len(target_match) > 1:
                raise LookupError(f'Multiple matching lines for "{self.target}"')

            target_match_index = lines.index(target_match.pop())
            insert_position = target_match_index + self.position

            logging.debug('Inserting "%s" to position "%d"', self.text, insert_position)

            indentation = self.indentation_pattern.match(lines[target_match_index])
            if self.respect_indentation and indentation:
                self.text = indentation.group() + self.text

            lines.insert(insert_position, self.text)

        with param.open("w") as file:
            file.writelines((f"{line}\n" for line in lines))

        return param


class LineNotExists(SingleFileRule):
    """
    Make sure that the given file not contains the specified line.
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        criteria: Optional[str] = None,
        **kwargs,
    ):
        """
        TODO: Fill this
        """

        self.criteria = re.compile(self.validate(criteria, cast_to=str, required=True))

        super().__init__(name, path, **kwargs)

    def task(self, param: Path) -> Path:
        """
        :raises: -
        """

        with param.open("r") as file:
            lines = file.read().splitlines()

        lines = list(filter(lambda l: not self.criteria.match(l), lines))

        with param.open("w") as file:
            file.writelines((f"{line}\n" for line in lines))

        return param


class LineReplaced(SingleFileRule):
    """
    Replace a given line in a file
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        text: Optional[str] = None,
        target: Optional[str] = None,
        respect_indentation: bool = True,
        **kwargs,
    ):
        """
        TODO: Fill this
        """

        self.text = self.validate(text, required=True)
        self.target = re.compile(self.validate(target, required=True))
        self.respect_indentation = respect_indentation

        self.indentation_pattern = re.compile(r"^\s+")

        super().__init__(name, path, **kwargs)

    def task(self, param: Path) -> Path:
        """
        :raises: -
        """

        with param.open("r") as file:
            lines = file.read().splitlines()

            if not lines:
                logging.debug('File "%s" is empty. Adding "%s"', str(param), self.text)
                lines.append(self.text)

        target_match = list(filter(self.target.match, lines))

        if not any(target_match):
            raise LookupError(f'No matching line for "{self.target}"')

        if len(target_match) > 1:
            raise LookupError(f'Multiple matching lines for "{self.target}"')

        for target in target_match:
            target_index = lines.index(target)

            indentation = self.indentation_pattern.match(lines[target_index])
            if self.respect_indentation and indentation:
                self.text = indentation.group() + self.text

            lines[target_index] = self.text

        with param.open("w") as file:
            file.writelines((f"{line}\n" for line in lines))

        return param
