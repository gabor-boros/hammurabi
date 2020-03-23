"""
Pillar module is responsible for handling the whole execution chain including
managing a lock file, executing the registered laws, pushing the changes to
the VCS and creating a pull request. All the laws registered to the pillar
will be executed in the order of the registration.
"""


import logging
from pathlib import Path
from typing import List

from hammurabi.law import Law
from hammurabi.mixins import GitHubMixin
from hammurabi.rules.base import Rule


class Pillar(GitHubMixin):
    """
    Pillar is responsible for the execution of the chain of laws and rules.
    During the execution process a lock file will be created at the beginning
    of the process and at the end, the lock file will be released.

    All the registered laws and rules can be retrieved using the ``laws`` and
    ``rules`` properties, or if necessary single laws and rules can be accessed
    using the resource's name as a parameter for ``get_law`` or ``get_rule``
    methods.
    """

    def __init__(self) -> None:
        self.__laws: List[Law] = list()
        self.__lock_file = Path("hammurabi.lock")

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

    def create_lock_file(self):
        """
        Create a lock file. If the lock file presents, the execution for
        the same target will be prevented.
        """

        if self.__lock_file.exists():
            raise RuntimeError(f"{self.__lock_file} already exists")

        logging.debug("Creating lock file")
        self.__lock_file.touch()

    def release_lock_file(self):
        """
        Releasing the previously created lock file if exists.
        """

        if self.__lock_file.exists():
            logging.debug("Releasing lock file")
            self.__lock_file.unlink()

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

    def enforce(self):
        """
        Run all the registered laws and rules one by one. This method is responsible
        for creating and releasing the lock file, executing the registered laws, push
        changes to the git origin and open the pull request.

        This method glues together the lower level components and makes sure that the
        execution of laws and rules can not be called more than once at the same time
        for a target.
        """

        self.create_lock_file()
        self.checkout_branch()

        try:
            for law in self.laws:
                law.enforce()
        finally:
            self.release_lock_file()

        self.push_changes()
        self.create_pull_request()
