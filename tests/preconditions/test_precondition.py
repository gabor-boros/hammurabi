from unittest.mock import Mock

from hammurabi.preconditions.base import Precondition


class Example(Precondition):
    def task(self) -> bool:
        return True


def test_precondition_with_name():
    expected_name = "Test"
    rule = Example(name=expected_name)
    assert rule.name == expected_name


def test_precondition_without_name():
    expected_name = "Example precondition"
    rule = Example()
    assert rule.name == expected_name


def test_executed():
    rule = Example()
    rule.task = Mock(return_value=True)
    rule.pre_task_hook = Mock()
    rule.post_task_hook = Mock()

    result = rule.execute()

    rule.task.assert_called_once_with()
    rule.pre_task_hook.assert_called_once_with()
    rule.post_task_hook.assert_called_once_with()

    assert result is True
