from typing import Any

from hammurabi.mixins import GitHubMixin, GitMixin
from hammurabi.rules.base import Rule


class ExamplePrecondition(Rule):
    def task(self) -> bool:
        return self.param


class ExampleRule(Rule):
    """ExampleRule docstring"""

    def task(self) -> Any:
        """ExampleRule task docstring"""
        return self.param


class ExampleExceptionRule(Rule):
    def task(self) -> Any:
        raise Exception(self.param)


class ExampleGitMixinRule(ExampleRule, GitMixin):
    pass


class ExampleGitHubMixinRule(ExampleRule, GitHubMixin):
    pass


PASSING_PRECONDITION = ExamplePrecondition(name="Passing", param=True)
FAILING_PRECONDITION = ExamplePrecondition(name="Failing", param=False)


def get_passing_rule():
    return ExampleRule(name="Passing", param="passing rule")


def get_failing_rule():
    return ExampleExceptionRule(name="Failing", param="raise exception")


def get_git_mixin_consumer():
    return ExampleGitMixinRule(name="Passing", param="passing rule")


def get_github_mixin_consumer():
    return ExampleGitHubMixinRule(name="Passing", param="passing rule")
