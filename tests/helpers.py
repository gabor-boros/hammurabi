from typing import Any

from hammurabi.rules.base import Rule


class TestPrecondition(Rule):
    def task(self, param: bool) -> bool:
        return param


class TestRule(Rule):
    """TestRule docstring"""

    def task(self, param: Any) -> Any:
        """TestRule task docstring"""
        return param


class TestExceptionRule(Rule):
    def task(self, param: Any) -> Any:
        raise Exception(param)


PASSING_PRECONDITION = TestPrecondition(name="Passing", param=True)
FAILING_PRECONDITION = TestPrecondition(name="Failing", param=False)

PASSING_RULE = TestRule(name="Passing", param="passing rule")
FAILING_RULE = TestExceptionRule(name="Failing", param="raise exception")
