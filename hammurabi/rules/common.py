from abc import abstractmethod
from pathlib import Path
from typing import Any, Iterable, Optional

from hammurabi.mixins import GitMixin
from hammurabi.rules.base import Rule


class SinglePathRule(Rule, GitMixin):
    """
    Abstract class which extends :class:`hammurabi.rules.base.Rule` to handle operations on a
    single directory.
    """

    def __init__(self, name: str, path: Optional[Path] = None, **kwargs) -> None:
        super().__init__(name, path, **kwargs)

    def post_task_hook(self):
        self.git_add(self.param)

    @abstractmethod
    def task(self) -> Any:
        """
        Abstract method representing how a :func:`hammurabi.rules.base.Rule.task`
        must be parameterized. Any difference in the parameters will result in
        pylint/mypy errors.

        For more details please check :func:`hammurabi.rules.base.Rule.task`.
        """


class MultiplePathRule(Rule, GitMixin):
    """
    Abstract class which extends :class:`hammurabi.rules.base.Rule` to handle operations on
    multiple files.
    """

    def __init__(
        self, name: str, paths: Optional[Iterable[Path]] = (), **kwargs
    ) -> None:
        super().__init__(name, paths, **kwargs)

    def post_task_hook(self):
        for path in self.param:
            self.git_add(path)

    @abstractmethod
    def task(self) -> Any:
        """
        Abstract method representing how a :func:`hammurabi.rules.base.Rule.task`
        must be parameterized. Any difference in the parameters will result in
        pylint/mypy errors.

        For more details please check :func:`hammurabi.rules.base.Rule.task`.
        """
