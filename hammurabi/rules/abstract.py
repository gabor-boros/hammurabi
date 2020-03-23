"""
This module contains the definition of the AbstractRule which describes what is shared between
Rules and Preconditions.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from hammurabi.helpers import full_strip


class AbstractRule(ABC):
    """
    Abstract class which describes the common behaviour for any kind of rule even
    it is a :class:`hammurabi.rules.base.Rule` or :class:`hammurabi.rules.base.Precondition`

    :param name: Name of the rule which will be used for printing
    :type name: str

    :param param: Input parameter of the rule will be used as ``self.param``
    :type param: Any
    """

    __slots__ = ("param", "name", "made_changes")

    def __init__(self, name: str, param: Any) -> None:
        self.param = param
        self.name = name.strip()

        # Set by GitMixin or other mixins to indicate that the rule did changes.
        # Rules can set this flag directly too. Only those rules will be indicated on
        # Git commit which are made changes.
        self.made_changes = False

    @staticmethod
    def validate(val: Any, cast_to: Optional[Any] = None, required=False) -> Any:
        """

        Validate and/or cast the given value to another type. In case the
        existence of the value is required or casting failed an exception
        will be raised corresponding to the failure.

        :param val: Value to validate
        :type val: Any

        :param cast_to: Type in which the value should be returned
        :type cast_to: Any

        :param required: Check that the value is not falsy
        :type required: bool

        :raise: ``ValueError`` if the given value is required but falsy
        :return: Returns the value in its original or casted type
        :rtype: Any

        Example usage:

        .. code-block:: python

            >>> from typing import Optional
            >>> from pathlib import Path
            >>> from hammurabi import Rule
            >>>
            >>> class MyAwesomeRule(Rule):
            >>>     def __init__(self, name: str, param: Optional[Path] = None):
            >>>         self.param = self.validate(param, required=True)
            >>>
            >>>     # Other method definitions ...
            >>>
        """

        if required and not val:
            raise ValueError(f"The given value is empty")

        if not cast_to:
            return val

        return cast_to(val)

    @property
    def description(self) -> str:
        """
        Return the description of the :func:`hammurabi.rules.base.Rule.task`
        based on its docstring.

        :return: Stripped description of :func:`hammurabi.rules.base.Rule.task`
        :rtype: str

        .. note::

            As of this property returns the docstring of :func:`hammurabi.rules.base.Rule.task`
            method, it worth to take care of its description when initialized.
        """

        return full_strip(getattr(self.task, "__doc__", ""))

    @property
    def documentation(self) -> str:
        """
        Return the documentation of the rule based on its name, docstring and
        the description of its task.

        :return: Concatenation of the rule's name, docstring, and task description
        :rtype: str

        .. note::

            As of this method returns the name and docstring of the rule
            it worth to take care of its name and description when initialized.
        """

        doc = full_strip(getattr(self, "__doc__", ""))
        return f"{self.name}\n{doc}\n{self.description}"

    def pre_task_hook(self):
        """
        Run code before performing the :func:`hammurabi.rules.base.Rule.task`.
        To access the parameter passed to the rule, always use ``self.param``
        for :func:`hammurabi.rules.base.Rule.pre_task_hook`.

        .. warning::

            This method is not called in dry run mode.
        """

    def post_task_hook(self):
        """
        Run code after the :func:`hammurabi.rules.base.Rule.task` has been
        performed. To access the parameter passed to the rule, always use
        ``self.param`` for :func:`hammurabi.rules.base.Rule.post_task_hook`.

        .. note::

            This method can be used for execution of git commands
            like git add, or double checking a modification made.

        .. warning::

            This method is not called in dry run mode.
        """

    @abstractmethod
    def task(self) -> Any:
        """
        Abstract method representing how a :func:`hammurabi.rules.base.Rule.task`
        or :func:`hammurabi.preconditions.base.Precondition.task` must be parameterized.
        Any difference in the parameters will result in pylint/mypy errors.

        To be able to use the power of ``pipe`` and ``children``, return
        something which can be generally used for other rules as in input.

        :return: Returns an output which can be used as an input for other rules
        :rtype: Any (usually same as `self.param`'s type)

        .. note::

            Although it is a good practice to return the same type for the output
            that the input has, but this is not the case for "Boolean Rules".
            "Boolean Rules" should return True (or truthy) or False (or falsy) values.
        """
