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


FAILING_PRECONDITION = TestPrecondition(name="Failing", param=False)
PASSING_PRECONDITION = TestPrecondition(name="Passing", param=True)
