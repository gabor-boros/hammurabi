"""
Mixins module contains helpers for both laws and rules. Usually this file
will contain Git commands related helpers. Also, this module contains the
extensions for several online git based VCS.
"""

import logging
from pathlib import Path

from github3.repos.repo import Repository  # type: ignore

from hammurabi.config import config


class GitMixin:
    """
    Simple mixin which contains all the common git commands which are needed
    to push a change to an online VCS like GitHub or GitLab. This mixin could
    be used by :class:`hammurabi.law.Law`s, :class:`hammurabi.rules.base` or
    any rules which can make modifications during its execution.
    """

    @property
    def has_changes(self) -> bool:
        """
        Check if the rule made any changes. The check will return True if the
        git branch is dirty after the rule execution or the Rule set the
        ``made_changes`` attribute directly. In usual cases, the ``made_changes``
        attribute will not be set directly by any rule.

        :return: True if the git branch is dirty or ``made_changes`` attribute is True
        :rtype: bool
        """

        if config.repo and config.repo.is_dirty():  # pylint: disable=no-member
            # The made_changes attribute defined by rules. If a rule not
            # defines the attribute or made changes set this attribute
            # to true. This will indicate to the law that the rule's
            # description should be used in the commit message.
            self.made_changes = True  # pylint: disable=attribute-defined-outside-init

        # Not only rules can use this class. If the class which uses this mixin
        # has no attribute ``made_changes``, do not raise attribute error, but
        # return False.
        return getattr(self, "made_changes", False)

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

        if config.repo and not config.dry_run:
            branch = config.git_branch_name
            logging.info('Checkout branch "%s"', branch)
            config.repo.git.checkout("HEAD", B=branch)  # pylint: disable=no-member

    @staticmethod
    def git_add(param: Path):
        """
        Add file contents to the index.

        :param param: Path to add to the index
        :type param: Path

        The following command is executed:

        .. code-block:: shell

            git add <path>
        """

        if config.repo and not config.dry_run:
            logging.debug('Git add "%s"', str(param))
            # Disabling no-member pylint error, due to the has_changes
            # function will return false if the target directory is not
            # a git repository.
            config.repo.git.add(param)  # pylint: disable=no-member

    @staticmethod
    def git_remove(param: Path):
        """
        Remove files from the working tree and from the index.

        :param param: Path to remove from the working tree and the index
        :type param: Path

        The following command is executed:

        .. code-block:: shell

            git rm <path>
        """

        if config.repo and not config.dry_run:
            logging.debug('Git remove "%s"', str(param))
            # Disabling no-member pylint error, due to the has_changes
            # function will return false if the target directory is not
            # a git repository.
            config.repo.index.remove(param)  # pylint: disable=no-member

    def git_commit(self, message: str):
        """
        Commit the changes on the checked out branch.

        :param message: Git commit message
        :type message: str

        The following command is executed:

        .. code-block:: shell

            git commit -m "<commit message>"
        """

        if config.repo and not config.dry_run and self.has_changes:
            logging.debug("Creating git commit for the changes")
            # Disabling no-member pylint error, due to the has_changes
            # function will return false if the target directory is not
            # a git repository.
            config.repo.index.commit(message)  # pylint: disable=no-member

    @staticmethod
    def push_changes():
        """
        Push the changes with the given branch set by ``git_branch_name``
        config option to the remote origin.

        The following command is executed:

        .. code-block:: shell

            git push origin <branch name>
        """

        if config.repo and not config.dry_run:
            logging.info("Pushing changes")
            branch = config.git_branch_name
            config.repo.remotes.origin.push(branch)  # pylint: disable=no-member


class GitHubMixin(GitMixin):
    """
    Extending :class:`hammurabi.mixins.GitMixin` to be able to open pull requests
    on GitHub after changes are pushed to remote.
    """

    @staticmethod
    def create_pull_request():
        """
        Create a PR on GitHub after the changes are pushed to remote. The pull
        request details (repository, branch) are set by the project
        configuration. The mapping of the details and configs:

        +------------+--------------------------------------+
        | Detail     | Configuration                        |
        +============+======================================+
        | repo       | repository (owner/repository format) |
        +------------+--------------------------------------+
        | branch     | git_branch_name                      |
        +------------+--------------------------------------+

        TODO: The PR description is not filled yet.
        """

        if config.repo and not config.dry_run:
            owner, repository = config.repository.split("/")
            github_repo: Repository = config.github.repository(owner, repository)

            logging.info("Checking for opened pull request")
            opened_pull_request = github_repo.pull_requests(
                state="open", head=config.git_branch_name, base="master"
            )

            if not opened_pull_request:
                logging.info("Opening pull request")
                github_repo.create_pull(
                    title="[hammurabi] Update to match the latest baseline",
                    base="master",
                    head=config.git_branch_name,
                    body="TODO",
                )
