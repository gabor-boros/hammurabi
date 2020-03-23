from typing import Any

from hammurabi.mixins import GitHubMixin, GitMixin, PullRequestHelperMixin
from hammurabi.rules.base import Precondition, Rule


class ExamplePrecondition(Precondition):
    def task(self) -> bool:
        return self.param


class ExampleRule(Rule):
    """ExampleRule docstring"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.made_changes = True

    def task(self) -> Any:
        """ExampleRule task docstring"""
        return self.param


class ExampleExceptionRule(Rule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.made_changes = False

    def task(self) -> Any:
        raise Exception(self.param)


class ExampleGitMixinRule(ExampleRule, GitMixin):
    pass


class ExamplePullRequestHelperMixinRule(ExampleRule, GitMixin, PullRequestHelperMixin):
    pass


class ExampleGitHubMixinRule(ExampleRule, GitHubMixin):
    pass


PASSING_PRECONDITION = ExamplePrecondition(name="Passing", param=True)
FAILING_PRECONDITION = ExamplePrecondition(name="Failing", param=False)


def get_passing_rule(name: str = "Passing"):
    return ExampleRule(name=name, param="passing rule")


def get_failing_rule():
    return ExampleExceptionRule(name="Failing", param="raise exception")


def get_git_mixin_consumer():
    return ExampleGitMixinRule(name="Passing", param="passing rule")


def get_pull_request_helper_mixin_consumer():
    return ExamplePullRequestHelperMixinRule(name="Passing", param="passing rule")


def get_github_mixin_consumer():
    return ExampleGitHubMixinRule(name="Passing", param="passing rule")
