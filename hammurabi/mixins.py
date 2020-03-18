"""
Mixins module contains helpers for both laws and rules. Usually this file
will contain Git commands related helpers. Also, this module contains the
extensions for several online git based VCS.
"""

import logging
from pathlib import Path
from typing import List

from github3.repos.repo import Repository  # type: ignore

from hammurabi.config import config


class GitMixin:
    """
    Simple mixin which contains all the common git commands which are needed
    to push a change to an online VCS like GitHub or GitLab. This mixin could
    be used by :class:`hammurabi.law.Law`s, :class:`hammurabi.rules.base` or
    any rules which can make modifications during its execution.
    """

    @staticmethod
    def checkout_branch():
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

    def git_add(self, param: Path):
        """
        Add file contents to the index.

        :param param: Path to add to the index
        :type param: Path

        The following command is executed:

        .. code-block:: shell

            git add <path>
        """

        if config.repo and not config.settings.dry_run:
            logging.debug('Git add "%s"', str(param))
            config.repo.git.add(str(param))  # pylint: disable=no-member
            self.made_changes = True

    def git_remove(self, param: Path):
        """
        Remove files from the working tree and from the index.

        :param param: Path to remove from the working tree and the index
        :type param: Path

        The following command is executed:

        .. code-block:: shell

            git rm <path>
        """

        if config.repo and not config.settings.dry_run:
            logging.debug('Git remove "%s"', str(param))
            config.repo.index.remove(
                (str(param),), ignore_unmatch=True
            )  # pylint: disable=no-member
            self.made_changes = True

    @staticmethod
    def git_commit(message: str):
        """
        Commit the changes on the checked out branch.

        :param message: Git commit message
        :type message: str

        The following command is executed:

        .. code-block:: shell

            git commit -m "<commit message>"
        """

        if config.repo and not config.settings.dry_run:
            logging.debug("Creating git commit for the changes")
            config.repo.index.commit(
                message, author="Hammurabi"
            )  # pylint: disable=no-member

    @staticmethod
    def push_changes():
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


class GitHubMixin(GitMixin):
    """
    Extending :class:`hammurabi.mixins.GitMixin` to be able to open pull requests
    on GitHub after changes are pushed to remote.
    """

    @staticmethod
    def generate_pull_request_body(pillar) -> str:
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

        for law in pillar.laws:
            body.append(f"\n### {law.name}")
            body.append(law.description)
            body.append("\n#### Rules")

            for rule in law.rules:
                body.append(f"* {rule.name}")

        return "\n".join(body)

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

        if config.repo and not config.settings.dry_run:
            owner, repository = config.settings.repository.split("/")
            github_repo: Repository = config.github.repository(owner, repository)

            logging.info("Checking for opened pull request")
            opened_pull_request = github_repo.pull_requests(
                state="open", head=config.settings.git_branch_name, base="master"
            )

            if not opened_pull_request:
                description = self.generate_pull_request_body(config.settings.pillar)

                logging.info("Opening pull request")
                github_repo.create_pull(
                    title="[hammurabi] Update to match the latest baseline",
                    base=config.settings.git_base_name,
                    head=config.settings.git_branch_name,
                    body=description,
                )
