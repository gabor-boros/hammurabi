# pylint: disable=too-few-public-methods

"""
This module contains the definition of Reporters which is responsible for
exposing the execution results in several formats.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, List

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from hammurabi.config import config
from hammurabi.law import Law
from hammurabi.rules.base import Rule


class LawItem(BaseModel):
    """
    LawItem represents the basic summary of a low attached to a rule.
    """

    name: str
    description: str


class RuleItem(BaseModel):
    """
    RuleItem represents the registered rule and its status.

    The rule (as normally) has the status of the execution which can be
    passed, failed or skipped.
    """

    name: str
    law: LawItem


class AdditionalData(BaseModel):
    """
    Additional data which may not be set for every execution.
    """

    # Add the execution start and finish datetime
    # to the report for statistic purposes
    started: str = datetime.min.isoformat()
    finished: str = datetime.min.isoformat()

    # When PR is not created, still do the reporting
    pull_request_url: str = ""


class Report(BaseModel):
    """
    The report object which contains all the necessary and optional
    data for the report will be generated.
    """

    passed: List[RuleItem] = list()
    failed: List[RuleItem] = list()
    skipped: List[RuleItem] = list()
    additional_data: AdditionalData = AdditionalData()


class Reporter(ABC):
    """
    Abstract class which describes the bare minimum and helper functions for Reporters.
    A reporter can generate different outputs from the results of the execution. Also,
    reporters can be extended by additional data which may not contain data for every
    execution like GitHub pull request url. The report file's name set by ``report_name``
    config parameter.

    .. note::

        Reporters measures the execution time for the complete execution from checking
        out the git branch until the pull request creation finished. Although the
        completion time is measured, it is not detailed for the rules. At this moment
        measuring execution time of rules is not planned.

    Example usage:

    .. code-block:: python

        >>> from hammurabi.reporters.base import Reporter
        >>>
        >>>
        >>> class JSONReporter(Reporter):
        >>>     def report(self) -> str:
        >>>         return self._get_report().json()

    :param laws: Iterable Law objects which will be included to the report
    :type laws: Iterable[Law]
    """

    def __init__(self, laws: List[Law]) -> None:
        self.laws = laws
        self.additional_data: AdditionalData = AdditionalData()
        self.report_path: Path = config.settings.report_name

    @staticmethod
    def __get_rule_item_from_rule(law: Law, rule: Rule, **kwargs) -> RuleItem:
        """
        Get a rule item from a combination of a Rule and a Law.

        :param law: The parent law of the rule
        :type law: ``hammurabi.law.Law``

        :param rule: The rule which should be transformed
        :type rule: ``hammurabi.rules.base.Rule``

        :return: Return the transformed RuleItem from the given law and rule
        :rtype: RuleItem
        """

        return RuleItem(
            name=rule.name,
            law=LawItem(name=law.name, description=law.description),
            **kwargs
        )

    def __get_rule_items(
        self, law: Law, rules: Iterable[Rule], **kwargs
    ) -> List[RuleItem]:
        """
        Get all the passed rule items for a law.

        :param law: The parent law of the rule
        :type law: ``hammurabi.law.Law``

        :return: Return all the passed rules transformed to ``RuleItem``s
        :rtype: List[RuleItem]
        """

        items: List[RuleItem] = list()

        for rule in rules:
            items += (self.__get_rule_item_from_rule(law, rule, **kwargs),)

        return items

    def _get_report(self) -> Report:
        """
        Get and prepare the report for actual reporting.

        :return: Return the assembled report object
        :rtype: ``hammurabi.reporters.base.Report``
        """

        report = Report(additional_data=self.additional_data)

        for law in self.laws:
            report.passed += self.__get_rule_items(law, law.passed_rules)
            report.failed += self.__get_rule_items(law, law.failed_rules)
            report.skipped += self.__get_rule_items(law, law.skipped_rules)

        return report

    @abstractmethod
    def report(self) -> Any:
        """
        Do the actual reporting based on the report assembled.
        """
