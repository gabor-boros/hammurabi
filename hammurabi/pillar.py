"""
Pillar module is responsible for handling the whole execution chain including
executing the registered laws, pushing the changes to the VCS and creating a
pull request. All the laws registered to the pillar will be executed in the
order of the registration.
"""


from datetime import datetime
from typing import List, Type

from hammurabi.law import Law
from hammurabi.mixins import GitHubMixin
from hammurabi.reporters.base import Reporter
from hammurabi.reporters.json import JSONReporter
from hammurabi.rules.base import Rule


class Pillar(GitHubMixin):
    """
    Pillar is responsible for the execution of the chain of laws and rules.

    All the registered laws and rules can be retrieved using the ``laws`` and
    ``rules`` properties, or if necessary single laws and rules can be accessed
    using the resource's name as a parameter for ``get_law`` or ``get_rule``
    methods.

    As a final step, pillar will prepare its ``reporter`` for report generation.
    For more information about reporters, check :class:`hammurabi.reporters.base.Reporter`
    and :class:`hammurabi.reporters.json.JSONReporter`.

    :param reporter_class: The reporter class used for generating the reports
    :type reporter_class: Type[Reporter]
    """

    def __init__(self, reporter_class: Type[Reporter] = JSONReporter) -> None:
        self.__laws: List[Law] = list()

        self.reporter: Reporter = reporter_class(list())

    @property
    def laws(self) -> List[Law]:
        """
        Return the registered laws in order of the registration.
        """

        return self.__laws

    @property
    def rules(self) -> List[Rule]:
        """
        Return all the registered laws' rules.
        """

        return [rule for law in self.laws for rule in law.rules]

    def get_law(self, name: str) -> Law:
        """
        Get a law by its name. In case of no Laws are registered or
        the law can not be found by its name, a ``StopIteration``
        exception will be raised.

        :param name: Name of the law which will be used for the lookup
        :type name: str

        :raises: ``StopIteration`` exception if Law not found
        :return: Return the searched law
        :rtype: :class:`hammurabi.law.Law`
        """

        return next(filter(lambda l: l.name == name, self.laws))

    def get_rule(self, name: str) -> Rule:
        """
        Get a registered rule (and its pipe/children) by the rule's name.

        This helper function is useful in debugging and information
        gathering.

        :param name: Name of the rule which will be used for the lookup
        :type name: str

        :raises: ``StopIteration`` exception if Rule not found
        :return: Return the rule in case of a match for the name
        :rtype: Rule
        """

        return next(filter(lambda r: r.name == name, self.rules))

    def register(self, law: Law):
        """
        Register the given Law to the Pillar. The order of the registration
        does not matter. The laws should never depend on each other.

        :param law: Initialized Law which should be registered
        :type law: ``hammurabi.law.Law``

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

        .. warning::

            The laws should never depend on each other, because the execution
            may not happen in the same order the laws were registered. Instead,
            organize the depending rules in one law to resolve any dependency
            conflicts.
        """

        self.__laws.append(law)
        self.reporter.laws = self.__laws

    def enforce(self):
        """
        Run all the registered laws and rules one by one. This method is responsible
        for executing the registered laws, push changes to the git origin and open
        the pull request.

        This method glues together the lower level components and makes sure that the
        execution of laws and rules can not be called more than once at the same time
        for a target.
        """

        self.reporter.additional_data.started = datetime.now().isoformat()
        self.checkout_branch()

        for law in self.laws:
            law.enforce()

        self.push_changes()
        pull_request_url = self.create_pull_request()

        self.reporter.additional_data.finished = datetime.now().isoformat()
        self.reporter.additional_data.pull_request_url = pull_request_url
