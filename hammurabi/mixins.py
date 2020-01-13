import logging
from pathlib import Path

from github3.repos.repo import Repository  # type: ignore

from hammurabi.config import config


class GitActionsMixin:
    """
    TODO:
    """

    @property
    def has_changes(self) -> bool:
        """
        TODO:
        """

        if config.repo and config.repo.is_dirty():  # pylint: disable=no-member
            self.made_changes = True

        # Not only rules can use this class. If the class which
        # uses this mixin has no attrubute `made_changes`, do not
        # raise attribute error, but return False.
        return getattr(self, "made_changes", False)

    @staticmethod
    def checkout_branch():
        """
        TODO:
        """

        if not config.dry_run:
            branch = config.git_branch_name
            logging.info('Checkout branch "%s"', branch)
            config.repo.git.checkout("HEAD", B=branch)  # pylint: disable=no-member

    @staticmethod
    def push_changes():
        """
        TODO:
        """

        if not config.dry_run:
            logging.info("Pushing changes")
            branch = config.git_branch_name
            config.repo.remotes.origin.push(branch)  # pylint: disable=no-member

    @staticmethod
    def create_pull_request():
        """
        TODO:
        """

        if not config.dry_run:
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

    def git_commit(self, message: str):
        """
        TODO:
        """

        if not config.dry_run and self.has_changes and config.repo:
            logging.debug("Creating git commit for the changes")
            # Disabling no-member pylint error, due to the has_changes
            # function will return false if the target directory is not
            # a git repository.
            config.repo.index.commit(message)  # pylint: disable=no-member

    @staticmethod
    def git_add(param: Path):
        """
        TODO:
        """

        if not config.dry_run and config.repo:
            logging.debug('Git add "%s"', str(param))
            # Disabling no-member pylint error, due to the has_changes
            # function will return false if the target directory is not
            # a git repository.
            config.repo.git.add(param)  # pylint: disable=no-member

    @staticmethod
    def git_remove(param: Path):
        """
        TODO:
        """

        if not config.dry_run and config.repo:
            logging.debug('Git remove "%s"', str(param))
            # Disabling no-member pylint error, due to the has_changes
            # function will return false if the target directory is not
            # a git repository.
            config.repo.index.remove(param)  # pylint: disable=no-member
