"""
This module contains the definition of Law which is responsible for
the execution of its registered Rules. Every Law can have multiple rules to execute.

In case a rule raises an exception the execution may abort and none of
the remaining rules will be executed neither pipes or children. An abort
can cause an inconsistent state or a dirty git branch. If ``rule_can_abort``
config is set to True, the whole execution of the :class:``hammurabi.pillar.Pillar``
will be aborted and the original exception will be re-raised.
"""

import logging
from typing import Iterable, List

from hammurabi.config import config
from hammurabi.exceptions import AbortLawError
from hammurabi.helpers import full_strip
from hammurabi.mixins import GitActionsMixin
from hammurabi.rules.base import Rule


class Law(GitActionsMixin):
    """
    A Law is a collection of Rules which is responsible for the rule execution
    and git committing.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, FileExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         FileExists(
        >>>             name="Create pyproject.toml",
        >>>             path=Path("./pyproject.toml")
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """

    def __init__(self, name: str, description: str, rules: Iterable[Rule]):
        """
        :param name: Name of the law
        :type name: str

        :param description: Detailed description what kind of rules are included
        :type description: str

        :param rules: List of those rules which should be included in the law
        :type rules: Iterable[Rule]
        """

        super().__init__()

        self.name = name.strip()
        self.description = full_strip(description)
        self.rules: Iterable[Rule] = tuple()

        for rule in rules:
            self.rules += (rule,)

    @property
    def documentation(self) -> str:
        """
        Get the name and description of the Law object.

        :return: Return the name and description of the law as its documentation
        :rtype: str
        """

        return f"{self.name}\n{self.description}"

    def get_execution_order(self) -> List[Rule]:
        """
        Get the execution order of the registered rules. The order will
        contain the pipes and children as well.

        This helper function is useful in debugging and information
        gathering.

        :return: Return the execution order of the rules
        :rtype: List[Rule]
        """

        order: List[Rule] = list()

        for rule in self.rules:
            order.extend(rule.get_execution_order())

        return order

    def commit(self):
        """
        Commit the changes made by registered rules
        and add a meaningful commit message.

        Example commit message:

        .. code-block:: text

            Migrate to next generation project template
            - Create pyproject.toml
            - Add meta info from setup.py to pyproject.toml
            - Add existing dependencies
            - Remove requirements.txt
            - Remove setup.py
        """

        order = self.get_execution_order()
        rules = "\n".join([f"* {r.name}" for r in order if r.made_changes])

        if rules:
            self.git_commit(f"{self.documentation}\n\n{rules}")

    @staticmethod
    def __execute_rule(rule: Rule):
        """
        Execute the given rule. In case of an exception, the execution of rules
        will continue except the failing one. The failed rule's pipe and children
        will not be executed.

        :param rule: A registered rule
        :type rule: Rule

        :raises: ``AbortLawError``
        """

        try:
            rule.execute()
        except Exception as exc:  # pylint: disable=broad-except
            logging.error('Execution of "%s" is aborted: %s', rule.name, str(exc))

            for chain in rule.get_rule_chain(rule):
                logging.warning('Due to errors "%s" is aborted', chain.name)

            raise AbortLawError(str(exc)) from exc

    def enforce(self):
        """
        Execute all registered rule. If ``rule_can_abort`` config option
        is set to ``True``, all the rules will be aborted and an exception
        will be raised.

        When the whole execution chain is finished, the changes will be
        committed except the failed ones.

        :raises: ``AbortLawError``
        """

        logging.info('Executing law "%s"', self.name)

        for rule in self.rules:
            try:
                self.__execute_rule(rule)
            except AbortLawError as exc:
                if config.rule_can_abort:
                    raise exc

        # We are allowing laws with empty rules, expecting that there will be
        # scenarios when the rules will be populated later. Hence we need to
        # make sure we are not wasting time on trying to commit if the law did
        # not get any rule at the end.
        # TODO: Not call commit when all the rules are failing
        if self.rules:
            self.commit()
