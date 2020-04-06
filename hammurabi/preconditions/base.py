"""
This module contains the definition of Preconditions which describes what to do with
the received parameter and does the necessary changes. The preconditions are used to
enable developers skipping or enabling rules based on a set of conditions.

.. warning::

    The precondition is for checking that a rule should or shouldn't run, not for
    breaking/aborting the execution. To indicate a precondition failure as an error
    in the logs, create a precondition which raises an exception if the requirements
    doesn't match.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import logging
from typing import Any, Optional

from hammurabi.rules.abstract import AbstractRule


class Precondition(AbstractRule, ABC):
    """
    This class which describes the bare minimum and helper functions for Preconditions.
    A precondition defines what and how should be checked/validated before executing a Rule.
    Since preconditions are special rules, all the functions available what can be used for
    :class:`hammurabi.rules.base.AbstractRule`.

    As said, preconditions are special from different angles. While this is not true for
    Rules, Preconditions will always have a name, hence giving a name to a Precondition is not
    necessary. In case no name given to a precondition, the name will be the name of the class
    and " precondition" suffix.

    Example usage:

    .. code-block:: python

        >>> import logging
        >>> from typing import Optional
        >>> from pathlib import Path
        >>> from hammurabi import Precondition
        >>>
        >>> class IsFileExists(Precondition):
        >>>     def __init__(self, path: Optional[Path] = None, **kwargs) -> None:
        >>>         super().__init__(param=path, **kwargs)
        >>>
        >>>     def task(self) -> bool:
        >>>         return self.param and self.param.exists()

    :param name: Name of the rule which will be used for printing
    :type name: Optional[str]

    :param param: Input parameter of the rule will be used as ``self.param``
    :type param: Any

    .. note:

        Since ``Precondition`` inherits from ``Rule``, the parameter after the name of the
        precondition will be used for ``self.param``. This can be handy for interacting
        with input parameters.

    .. warning:

        Although ``Precondition`` inherits from ``Rule``, the pipe and children execution
        is intentionally not implemented.
    """

    def __init__(self, name: Optional[str] = None, param: Optional[Any] = None) -> None:
        name = name or f"{self.__class__.__name__} precondition"
        super().__init__(name, param)

    @abstractmethod
    def task(self) -> bool:
        """
        Abstract method representing how a :func:`hammurabi.rules.base.Precondition.task`
        must be parameterized. Any difference in the parameters or return type will result
        in pylint/mypy errors.

        To be able to use the power of ``pipe`` and ``children``, return
        something which can be generally used for other rules as in input.

        :return: Returns an output which can be used as an input for other rules
        :rtype: Any (usually same as `self.param`'s type)
        """

    def execute(self) -> bool:
        """
        Execute the precondition.

        :raise: ``AssertionError``
        :return: None
        """

        logging.info('Running task for "%s"', self.name)

        self.pre_task_hook()
        result = self.task()
        self.post_task_hook()

        return result
