from unittest.mock import Mock

from hammurabi.preconditions.base import Precondition


class Example(Precondition):
    def task(self) -> bool:
        return True


def test_repr():
    expected = 'Example(name="Test", param="precondition")'
    rule = Example(name="Test", param="precondition")

    assert repr(rule) == expected
    # The repr should be used with eval
    assert repr(eval(repr(rule))) == expected


def test_str():
    expected = "Example precondition"
    rule = Example(param="precondition")

    assert str(rule) == expected


def test_str_with_name():
    expected = "Test precondition"
    rule = Example(name="Test", param="precondition")

    assert str(rule) == expected


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
