from typing import Any

from hammurabi.mixins import GitHubMixin, GitMixin
from hammurabi.rules.base import Rule


class ExamplePrecondition(Rule):
    def task(self, param: bool) -> bool:
        return param


class ExampleRule(Rule):
    """ExampleRule docstring"""

    def task(self, param: Any) -> Any:
        """ExampleRule task docstring"""
        return param


class ExampleExceptionRule(Rule):
    def task(self, param: Any) -> Any:
        raise Exception(param)


class ExampleGitMixinRule(ExampleRule, GitMixin):
    pass


class ExampleGitHubMixinRule(ExampleRule, GitHubMixin):
    pass


PASSING_PRECONDITION = ExamplePrecondition(name="Passing", param=True)
FAILING_PRECONDITION = ExamplePrecondition(name="Failing", param=False)

PASSING_RULE = ExampleRule(name="Passing", param="passing rule")
FAILING_RULE = ExampleExceptionRule(name="Failing", param="raise exception")


def get_git_mixin_consumer():
    return ExampleGitMixinRule(name="Passing", param="passing rule")


def get_github_mixin_consumer():
    return ExampleGitHubMixinRule(name="Passing", param="passing rule")
