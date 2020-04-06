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
from typing import Iterable, List, Tuple, Union

from hammurabi.config import config
from hammurabi.exceptions import AbortLawError, PreconditionFailedError
from hammurabi.helpers import full_strip
from hammurabi.mixins import GitMixin
from hammurabi.rules.base import Precondition, Rule


class Law(GitMixin):
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

    def __init__(
        self,
        name: str,
        description: str,
        rules: Iterable[Rule],
        preconditions: Iterable[Precondition] = (),
    ) -> None:
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
        self.preconditions = preconditions
        self._failed_rules: Tuple[Rule, ...] = tuple()

        for rule in rules:
            self.rules += (rule,)

    @property
    def passed_rules(self) -> Tuple[Rule, ...]:
        """
        Return the rules which did modifications and not failed.

        :return: Return the passed rules
        :rtype: Tuple[Rule, ...]
        """

        return tuple(r for r in self.rules if r.made_changes)

    @property
    def failed_rules(self) -> Tuple[Rule, ...]:
        """
        Return the rules which did modifications and failed.

        :return: Return the failed rules
        :rtype: Union[Tuple[()], Tuple[Rule]]
        """

        return self._failed_rules

    @property
    def skipped_rules(self) -> Tuple[Rule, ...]:
        """
        Return the rules which neither modified the code nor failed.

        :return: Return the skipped rules
        :rtype: Tuple[Rule, ...]
        """

        def is_skipped(rule) -> bool:
            """
            Return the evaluation if the rule is skipped or not.

            :return: Evaluation if the rule is skipped
            :rtype: bool
            """
            not_passed = rule not in self.passed_rules
            not_failed = rule not in self.failed_rules
            return not_passed and not_failed

        return tuple(r for r in self.rules if is_skipped(r))

    @property
    def documentation(self) -> str:
        """
        Get the name and description of the Law object.

        :return: Return the name and description of the law as its documentation
        :rtype: str
        """

        return f"{self.name}\n{self.description}"

    @property
    def can_proceed(self) -> bool:
        """
        Evaluate if the execution can be continued. If preconditions are set,
        those will be evaluated by this method.

        :return: Return with the result of evaluation
        :rtype: bool

        .. warning::

            :func:`hammurabi.rules.base.Rule.can_proceed` checks the result of
            ``self.preconditions``, which means the preconditions are executed.
            Make sure that you are not doing any modifications within rules used
            as preconditions, otherwise take extra attention for those rules.
        """

        logging.debug('Checking if "%s" can proceed with execution', self.name)
        return all([condition.execute() for condition in self.preconditions])

    def get_execution_order(self) -> List[Union[Rule, Precondition]]:
        """
        Get the execution order of the registered rules. The order will
        contain the pipes and children as well.

        This helper function is useful in debugging and information
        gathering.

        :return: Return the execution order of the rules
        :rtype: List[Rule]
        """

        order: List[Union[Rule, Precondition]] = list()

        for rule in self.rules:
            order.extend(rule.get_execution_order())

        return order

    def commit(self) -> None:
        """
        Commit the changes made by registered rules and add a
        meaningful commit message.

        Example commit message:

        .. code-block:: text

            Migrate to next generation project template
            * Create pyproject.toml
            * Add meta info from setup.py to pyproject.toml
            * Add existing dependencies
            * Remove requirements.txt
            * Remove setup.py
        """

        order = self.get_execution_order()
        rules = [f"* {rule.name}" for rule in order if rule.made_changes]
        rules_commit_message = "\n".join(rules)

        logging.debug('Committing changes made by "%s"', self.name)
        self.git_commit(f"{self.documentation}\n\n{rules_commit_message}")

    @staticmethod
    def __execute_rule(rule: Rule) -> None:
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
        except PreconditionFailedError:
            logging.warning(
                'Cancelling execution of "%s", the preconditions are not fulfilled',
                rule.name,
            )
        except Exception as exc:  # pylint: disable=broad-except
            logging.error('Execution of "%s" is aborted: %s', rule.name, str(exc))

            chained_rules = filter(
                lambda r: isinstance(r, Rule), rule.get_rule_chain(rule)
            )
            for chain in chained_rules:
                logging.error('Due to errors "%s" is aborted', chain.name)

            raise AbortLawError(str(exc)) from exc

    def enforce(self) -> None:
        """
        Execute all registered rule. If ``rule_can_abort`` config option
        is set to ``True``, all the rules will be aborted and an exception
        will be raised.

        When the whole execution chain is finished, the changes will be
        committed except the failed ones.

        .. note::

            Failed rules and their chain (excluding prerequisites) will be added
            to the pull request description.

        :raises: ``AbortLawError``
        """

        if not self.can_proceed:
            logging.warning(
                'Cancelling execution of "%s", the preconditions are not fulfilled',
                self.name,
            )
            return

        logging.info('Executing law "%s"', self.name)

        for rule in self.rules:
            try:
                self.__execute_rule(rule)
            except AbortLawError as exc:
                logging.error(str(exc))
                self._failed_rules += (rule,)

                if config.settings.rule_can_abort:
                    raise exc

        # We are allowing laws with empty rules, expecting that there will be
        # scenarios when the rules will be populated later. Hence we need to
        # make sure we are not wasting time on trying to commit if the law did
        # not get any rule at the end.
        if self.passed_rules:
            self.commit()
