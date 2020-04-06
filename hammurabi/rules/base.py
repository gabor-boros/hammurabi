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
from typing import Any, Iterable, List, Optional, Union

from hammurabi.config import config
from hammurabi.exceptions import PreconditionFailedError
from hammurabi.preconditions.base import Precondition
from hammurabi.rules.abstract import AbstractRule


class Rule(AbstractRule, ABC):
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
        >>>     def __init__(self, name: str, path: Optional[Path] = None, **kwargs) -> None:
        >>>         super().__init__(name, path, **kwargs)
        >>>
        >>>     def post_task_hook(self):
        >>>         self.git_add(self.param)
        >>>
        >>>     @abstractmethod
        >>>     def task(self) -> Path:
        >>>         pass

    :param name: Name of the rule which will be used for printing
    :type name: str

    :param param: Input parameter of the rule will be used as ``self.param``
    :type param: Any

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
        preconditions: Iterable[Precondition] = (),
        pipe: Optional["Rule"] = None,
        children: Iterable["Rule"] = (),
    ) -> None:
        self.pipe = pipe
        self.children = children
        self.preconditions = preconditions

        super().__init__(name, param)

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

    def get_rule_chain(self, rule: "Rule") -> List[Union["Rule", Precondition]]:
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

        rules: List[Union[Rule, Precondition]] = list(rule.preconditions)
        rules.append(rule)

        if rule.pipe:
            rules.extend(self.get_rule_chain(rule.pipe))

        for child in rule.children:
            rules.extend(self.get_rule_chain(child))

        return rules

    def get_execution_order(self) -> List[Union["Rule", Precondition]]:
        """
        Same as :func:`hammurabi.rules.base.Rule.get_rule_chain` but
        for the root rule.
        """

        order: List[Union[Rule, Precondition]] = list(self.preconditions)
        order.append(self)

        if self.pipe:
            order.extend(self.get_rule_chain(self.pipe))

        for child in self.children:
            order.extend(self.get_rule_chain(child))

        return order

    @abstractmethod
    def task(self) -> Any:
        """
        See the documentation of :func:`hammurabi.rules.base.AbstractRule.task`
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
            if config.settings.dry_run:
                raise AssertionError(f'"{self.name}" cannot proceed because of dry run')

            raise PreconditionFailedError(f'"{self.name}" cannot proceed')

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
