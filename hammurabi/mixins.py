"""
Mixins module contains helpers for both laws and rules. Usually this file
will contain Git commands related helpers. Also, this module contains the
extensions for several online git based VCS.
"""

import logging
from pathlib import Path
from typing import Any, Iterable, List, Union

from github3.repos.repo import Repository  # type: ignore

from hammurabi.config import config
from hammurabi.preconditions.base import Precondition
from hammurabi.rules.base import Rule


class GitMixin:
    """
    Simple mixin which contains all the common git commands which are needed
    to push a change to an online VCS like GitHub or GitLab. This mixin could
    be used by :class:`hammurabi.law.Law`s, :class:`hammurabi.rules.base` or
    any rules which can make modifications during its execution.
    """

    @staticmethod
    def __can_proceed() -> bool:
        """
        Determine if the next change can be done or not. For git related
        operations it is extremely important to abort or skip an execution
        if not needed.

        :return: Returns True if the next changes should be done
        :rtype: bool
        """

        return config.repo and not config.settings.dry_run and config.repo.is_dirty()

    @staticmethod
    def checkout_branch() -> None:
        """
        Perform a simple git checkout, to not pollute the default branch and
        use that branch for the pull request later. The branch name can be
        changed in the config by setting the ``git_branch_name`` config option.

        The following command is executed:

        .. code-block:: shell

            git checkout -b <branch name>
        """

        if config.repo and not config.settings.dry_run:
            branch = config.settings.git_branch_name
            logging.info('Checkout branch "%s"', branch)
            config.repo.git.checkout("HEAD", B=branch)  # pylint: disable=no-member

    def git_add(self, param: Path) -> None:
        """
        Add file contents to the index.

        :param param: Path to add to the index
        :type param: Path

        The following command is executed:

        .. code-block:: shell

            git add <path>
        """

        if self.__can_proceed():
            logging.debug('Git add "%s"', str(param))
            config.repo.git.add(str(param))  # pylint: disable=no-member
            self.made_changes = True

    def git_remove(self, param: Path) -> None:
        """
        Remove files from the working tree and from the index.

        :param param: Path to remove from the working tree and the index
        :type param: Path

        The following command is executed:

        .. code-block:: shell

            git rm <path>
        """

        if self.__can_proceed():
            logging.debug('Git remove "%s"', str(param))
            config.repo.index.remove(
                (str(param),), ignore_unmatch=True
            )  # pylint: disable=no-member
            self.made_changes = True

    def git_commit(self, message: str) -> None:
        """
        Commit the changes on the checked out branch.

        :param message: Git commit message
        :type message: str

        The following command is executed:

        .. code-block:: shell

            git commit -m "<commit message>"
        """

        if self.__can_proceed():
            logging.debug("Creating git commit for the changes")
            config.repo.index.commit(message)  # pylint: disable=no-member

    @staticmethod
    def push_changes() -> None:
        """
        Push the changes with the given branch set by ``git_branch_name``
        config option to the remote origin.

        The following command is executed:

        .. code-block:: shell

            git push origin <branch name>
        """

        if config.repo and not config.settings.dry_run:
            logging.info("Pushing changes")
            branch = config.settings.git_branch_name
            config.repo.remotes.origin.push(branch)  # pylint: disable=no-member


class PullRequestHelperMixin:  # pylint: disable=too-few-public-methods
    """
    Give helper classes for pull request related operations
    """

    @staticmethod
    def __get_chained_rules(
        target: Rule, chain: List[Union[Rule, Precondition]]
    ) -> Iterable[Rule]:
        """
        Return all the chained rules excluding the root rule.

        :param target: The root Rule
        :type target: Rule

        :param chain: The whole chain
        :type chain: Iterable[Rule]

        :return: The filtered list of chained rules
        :rtype: Iterable[Rule]
        """

        rules = filter(lambda i: isinstance(i, Rule), chain)
        return filter(lambda r: r != target, rules)  # type: ignore

    def __get_rules_body(self, rules: Iterable[Rule]) -> List[str]:
        """
        Generate the PR body's executed rules section for the root
        and chained rules excluding their preconditions.

        :param rules: List of passing of failed rules
        :type rules: Iterable[Rule]

        :return: Body of the PR section in a list format
        :rtype: List[str]
        """

        body: List[str] = list()

        for rule in rules:
            body.append(f"* {rule.name}")

            for chain in self.__get_chained_rules(rule, rule.get_rule_chain(rule)):
                body.append(f"** {chain.name}")

        return body

    def __get_passed_rules(self, law) -> List[str]:
        """
        Get the passed rules for law if there is any.

        :param law: Target Law which will be checked
        :type law: Law

        :return: Body of the PR section in a list format
        :rtype: List[str]
        """

        #  NOTE: The parameter type can not be hinted, because of circular import,
        #  we must fix this in the future releases.

        body: List[str] = list()

        has_passing_rules = len(law.failed_rules) != len(law.rules)
        rules_with_changes = [rule for rule in law.rules if rule.made_changes]

        if has_passing_rules and rules_with_changes:
            body.append("\n#### Passed rules")
            body.extend(self.__get_rules_body(rules_with_changes))

        return body

    def __get_failed_rules(self, law) -> List[str]:
        """
        Get the failed rules for law if there is any.

        :param law: Target Law which will be checked
        :type law: Law

        :return: Body of the PR section in a list format
        :rtype: List[str]
        """

        #  NOTE: The parameter type can not be hinted, because of circular import,
        #  we must fix this in the future releases.

        body: List[str] = list()

        if law.failed_rules:
            body.append("\n#### Failed rules (manual fix needed)")
            body.extend(self.__get_rules_body(law.failed_rules))

        return body

    @staticmethod
    def __filter_laws_with_modifications(pillar) -> Iterable[Any]:
        """
        Return only those laws which has rules which made modifications.
        """

        def filter_rules(law):
            rules = list()
            rules.extend([r for r in law.rules if r.made_changes])
            rules.extend(law.failed_rules)
            return rules

        return filter(filter_rules, pillar.laws)

    def generate_pull_request_body(self, pillar) -> str:
        """
        Generate the body of the pull request based on the registered laws and rules.
        The pull request body is markdown formatted.

        :param pillar: Pillar configuration
        :type pillar: :class:`hammurabi.pillar.Pillar`

        :return: Returns the generated pull request description
        :rtype: str
        """

        #  NOTE: The parameter type can not be hinted, because of circular import,
        #  we must fix this in the future releases.

        logging.debug("Generating pull request body")

        body: List[str] = [
            "## Description",
            "Below you can find the executed laws and information about them.",
        ]

        for law in self.__filter_laws_with_modifications(pillar):
            body.append(f"\n### {law.name}")
            body.append(law.description)

            body.extend(self.__get_passed_rules(law))
            body.extend(self.__get_failed_rules(law))

        return "\n".join(body)


class GitHubMixin(GitMixin, PullRequestHelperMixin):
    """
    Extending :class:`hammurabi.mixins.GitMixin` to be able to open pull requests
    on GitHub after changes are pushed to remote.
    """

    def create_pull_request(self):
        """
        Create a PR on GitHub after the changes are pushed to remote. The pull
        request details (repository, branch) are set by the project
        configuration. The mapping of the details and configs:

        +------------+--------------------------------------+
        | Detail     | Configuration                        |
        +============+======================================+
        | repo       | repository (owner/repository format) |
        +------------+--------------------------------------+
        | base       | git_base_name                        |
        +------------+--------------------------------------+
        | branch     | git_branch_name                      |
        +------------+--------------------------------------+
        """

        if not config.github:
            raise RuntimeError(
                "The GitHub client is not initialized properly. Make sure that "
                "you set the GITHUB_TOKEN or HAMMURABI_GITHUB_TOKEN before execution. "
            )

        if config.repo and not config.settings.dry_run:
            owner, repository = config.settings.repository.split("/")
            github_repo: Repository = config.github.repository(owner, repository)

            logging.info("Checking for opened pull request")
            opened_pull_request = github_repo.pull_requests(
                state="open", head=config.settings.git_branch_name, base="master"
            )

            if opened_pull_request.count == -1:
                description = self.generate_pull_request_body(config.settings.pillar)

                logging.info("Opening pull request")
                github_repo.create_pull(
                    title="[hammurabi] Update to match the latest baseline",
                    base=config.settings.git_base_name,
                    head=config.settings.git_branch_name,
                    body=description,
                )
