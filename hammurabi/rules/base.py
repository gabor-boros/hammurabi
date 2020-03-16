"""
This module contains the definition of Rule which describes what to do with
the received parameter and does the necessary changes.

The Rule is an abstract class which describes all the required methods and
parameters, but it can be extended and customized easily by inheriting from
it. A good example for this kind of customization is :class:`hammurabi.rules.text.LineExists`
which adds more parameters to :class:`hammurabi.rules.files.SingleFileRule` which
inherits from :class:`hammurabi.rules.base.Rule`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import logging
from typing import Any, Iterable, List, Optional

from hammurabi.config import config
from hammurabi.helpers import full_strip


class Rule(ABC):
    """
    Abstract class which describes the bare minimum and helper functions for Rules.
    A rule defines what and how should be executed. Since a rule can have piped and
    children rules, the "parent" rule is responsible for those executions. This kind
    of abstraction allows to run both piped and children rules sequentially in a given
    order.

    Example usage:

    .. code-block:: python

        >>> from typing import Optional
        >>> from pathlib import Path
        >>> from hammurabi import Rule
        >>> from hammurabi.mixins import GitMixin
        >>>
        >>> class SingleFileRule(Rule, GitMixin):
        >>>     def __init__(self, name: str, path: Optional[Path] = None, **kwargs):
        >>>         super().__init__(name, path, **kwargs)
        >>>
        >>>     def post_task_hook(self):
        >>>         self.git_add(self.param)
        >>>
        >>>     @abstractmethod
        >>>     def task(self, param: Path) -> Path:
        >>>         pass

    :param name: Name of the rule which will be used for printing
    :type name: str

    :param preconditions: "Boolean Rules" which returns a truthy or falsy value
    :type preconditions: Iterable["Rule"]

    :param pipe: Pipe will be called when the rule is executed successfully
    :type pipe: Optional["Rule"]

    :param children: Children will be executed after the piped rule if there is any
    :type children: Iterable["Rule"]

    .. warning::

        Preconditions can be used in several ways. The most common way is to run
        "Boolean Rules" which takes a parameter and returns a truthy or falsy value.
        In case of a falsy return, the precondition will fail and the rule will not be executed.

        If any modification is done by any of the rules which are used as a
        precondition, those changes will be committed.
    """

    def __init__(
        self,
        name: str,
        param: Any,
        preconditions: Iterable["Rule"] = (),
        pipe: Optional["Rule"] = None,
        children: Iterable["Rule"] = (),
    ):
        self.param = param
        self.name = name.strip()
        self.pipe = pipe
        self.children = children
        self.preconditions = preconditions

        if self.pipe and self.children:
            raise ValueError("pipe and children cannot be set at the same time")

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

            As of this method returns the docstring of :func:`hammurabi.rules.base.Rule.task`
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

    @property
    def can_proceed(self) -> bool:
        """
        Evaluate if a rule can continue its execution. In case the execution
        is called with ``dry_run`` config option set to true, this method will
        always return ``False`` to make sure not performing any changes. If
        preconditions are set, those will be evaluated by this method.

        :return: Return with the result of evaluation
        :rtype: bool

        .. warning::

            :func:`hammurabi.rules.base.Rule.can_proceed` checks the result of
            ``self.preconditions``, which means the preconditions are executed.
            Make sure that you are not doing any modifications within rules used
            as preconditions, otherwise take extra attention for those rules.
        """

        logging.debug('Checking if "%s" can proceed with execution', self.name)
        proceed: bool = True

        if self.preconditions:
            proceed = all([condition.execute() for condition in self.preconditions])

        return not config.settings.dry_run and proceed

    def get_rule_chain(self, rule: "Rule") -> List["Rule"]:
        """
        Get the execution chain of the given rule. The execution
        order is the following:

        * task (current rule's :func:`hammurabi.rules.base.Rule.task`)
        * Piped rule
        * Children rules (in the order provided by the iterator used)

        :param rule: The rule which execution chain should be returned
        :type rule: :class:`hammurabi.rules.base.Rule`

        :return: Returns the list of rules in the order above
        :rtype: List[Rule]
        """

        rules: List[Rule] = [rule]

        if rule.pipe:
            rules.extend(self.get_rule_chain(rule.pipe))

        for child in rule.children:
            rules.extend(self.get_rule_chain(child))

        return rules

    def get_execution_order(self) -> List["Rule"]:
        """
        Same as :func:`hammurabi.rules.base.Rule.get_rule_chain` but
        for the root rule.
        """

        order: List[Rule] = [self]

        if self.pipe:
            order.extend(self.get_rule_chain(self.pipe))

        for child in self.children:
            order.extend(self.get_rule_chain(child))

        return order

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
        must be parameterized. Any difference in the parameters will result in
        pylint/mypy errors.

        To be able to use the power of ``pipe`` and ``children``, return
        something which can be generally used for other rules as in input.

        :return: Returns an output which can be used as an input for other rules
        :rtype: Any (usually same as `self.param`'s type)

        .. note::

            Although it is a good practice to return the same type for the output
            that the input has, but this is not the case for "Boolean Rules".
            "Boolean Rules" should return True (or truthy) or False (or falsy) values.

        Example usage:

        .. code-block:: python

            >>> import logging
            >>> from pathlib import Path
            >>> from hammurabi.rules.files import SingleFileRule
            >>>
            >>> class FileExists(SingleFileRule):
            >>>     def task(self) -> Path:
            >>>         logging.debug('Creating file "%s" if not exists', str(self.param))
            >>>         self.param.touch()
            >>>         return self.param
        """

    def execute(self, param: Optional[Any] = None):
        """
        Execute the rule's task, its piped and children rules as well.

        The execution order of task, piped rule and children rules
        described in but not by :func:`hammurabi.rules.base.Rule.get_rule_chain`.

        :param param: Input parameter of the rule given by the user
        :type param: Optional[Any]

        :raise: ``AssertionError``
        :return: None

        .. note::

            The input parameter can be optional because of the piped and
            children rules which are receiving the output of its parent. In
            this case the user is not able to set the param manually, since it
            is calculated.

        .. warning::

            If ``self.can_proceed`` returns ``False`` the whole execution
            will be stopped immediately and ``AssertionError`` will be
            raised.
        """

        # In case of piped execution, the Rule will be called without
        # any additional argument, therefore we must set it manually
        # to be able to work with hooks.
        self.param = param or self.param

        if not self.can_proceed:
            logging.warning(
                'Skipping execution of "%s", the prerequisites are not fulfilled',
                self.name,
            )
            raise AssertionError(f'"{self.name}" cannot proceed')

        logging.debug('Running pre task hook for "%s"', self.name)
        self.pre_task_hook()

        logging.info('Running task for "%s"', self.name)
        result = self.task()

        logging.debug('Running post task hook for" %s"', self.name)
        self.post_task_hook()

        logging.info('Rule "%s" finished successfully', self.name)

        if self.pipe:
            logging.debug('Executing pipe "%s" of "%s"', self.pipe.name, self.name)
            self.pipe.execute(result)

        if self.children:
            logging.debug('Executing children rules of "%s"', self.name)
            for child in self.children:
                logging.debug('Executing child "%s" of "%s"', child.name, self.name)
                child.execute(result)
