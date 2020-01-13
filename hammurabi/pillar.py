import logging
from pathlib import Path
from typing import List, Set

from hammurabi.config import config
from hammurabi.law import Law
from hammurabi.mixins import GitActionsMixin
from hammurabi.rules.base import Rule


class Pillar(GitActionsMixin):
    """
    Collection of :class:`Law`s which will be executed.
    """

    def __init__(self):
        self.__laws: Set[Law] = set()
        self.__lock_file = Path(config.working_dir, "hammurabi.lock")

    @property
    def laws(self) -> Set[Law]:
        """
        Get :class:`Law`s registered.
        """

        return self.__laws

    @property
    def rules(self) -> List[Rule]:
        """
        Get direct :class:`hammurabi.rules.base.Rule`s registered on the :class:`Law`.
        This will not return piped :class:`hammurabi.rules.base.Rule`s.
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
        Releaseing the lock file.
        """

        if self.__lock_file.exists():
            logging.debug("Releasing lock file")
            self.__lock_file.unlink()

    def get_law(self, name: str) -> Law:
        """
        TODO:
        """

        return next(filter(lambda l: l.name == name, self.laws))

    def get_rule(self, name: str) -> Rule:
        """
        Get a registered rule (and its pipe/children) by the rule's name.

        This helper function is useful in debugging and information
        gathering.

        :param name: Name of the rule which will be used for the lookup
        :type name: str

        :raises: StopIteration exception if Rule is not found
        :return: Return the rule in case of a match for the name
        :rtype: Rule
        """

        return next(filter(lambda r: r.name == name, self.rules))

    def register(self, law: Law):
        """
        Register a :class:`Law` to the :class:`Pillar`.
        """

        self.__laws.add(law)

    def enforce(self):
        """
        Run all registered :class:`Law`.
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
