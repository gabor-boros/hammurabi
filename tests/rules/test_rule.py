from typing import Any

from hypothesis import given
from hypothesis import strategies as st
from mock import Mock, call, patch
import pytest

from tests.helpers import FAILING_PRECONDITION, PASSING_PRECONDITION, TestRule


@patch("hammurabi.rules.base.full_strip")
def test_get_description(mock_full_strip):
    expected_description = "test description"
    mock_full_strip.return_value = expected_description

    rule = TestRule(name="Test", param="Rule")

    assert rule.description == expected_description
    mock_full_strip.assert_called_once_with("TestRule task docstring")

@patch("hammurabi.rules.base.full_strip")
def test_get_documentation(mock_full_strip):
    expected_description = "test description"
    expected_documentation = "test docstring"
    mock_full_strip.side_effect = [
        expected_description,
        expected_documentation
    ]

    rule = TestRule(name="Test", param="Rule")

    assert rule.documentation == f"{rule.name}\n{expected_description}\n{expected_documentation}"
    mock_full_strip.has_calls([
        call(expected_description),
        call(expected_documentation)
    ])

@given(name=st.text(), param=st.one_of(st.text(), st.integers()))
def test_rule_executed(name: str, param: Any):
    rule = TestRule(name=name, param=param)

    rule.pre_task_hook = Mock()
    rule.post_task_hook = Mock()
    rule.task = Mock()

    rule.execute(param)

    rule.task.assert_called_once_with(param)
    rule.pre_task_hook.assert_called_once_with()
    rule.post_task_hook.assert_called_once_with()

def test_rule_executed_no_direct_param():
    """
    This test case covers the situation of piped and child rules
    which has no direct parameter (it is set to None), but getting
    it from the output of the previous rule as an input.
    """

    rule = TestRule(name="Test", param=None)
    rule.param = "Rule"

    rule.pre_task_hook = Mock()
    rule.post_task_hook = Mock()
    rule.task = Mock()

    rule.execute()

    rule.task.assert_called_once_with(rule.param)
    rule.pre_task_hook.assert_called_once_with()
    rule.post_task_hook.assert_called_once_with()

@patch("hammurabi.rules.base.config")
def test_rule_cannot_proceed_dry_run(config):
    config.dry_run = True
    rule = TestRule(name="Test", param="Rule")

    rule.pre_task_hook = Mock()
    rule.post_task_hook = Mock()

    with pytest.raises(AssertionError) as exc:
        rule.execute("Rule")

    assert str(exc.value) == '"Test" cannot proceed'
    assert not rule.pre_task_hook.called
    assert not rule.post_task_hook.called

def test_rule_cannot_proceed_precondition():
    rule = TestRule(name="Test", param="Rule", preconditions=(
        FAILING_PRECONDITION,
        PASSING_PRECONDITION
    ))

    rule.pre_task_hook = Mock()
    rule.post_task_hook = Mock()

    with pytest.raises(AssertionError) as exc:
        rule.execute("Rule")

    assert str(exc.value) == '"Test" cannot proceed'
    assert not rule.pre_task_hook.called
    assert not rule.post_task_hook.called

def test_rule_cannot_proceed_pipe_and_children():
    piped_rule = TestRule(name="Test", param=None)
    piped_rule.execute = Mock()

    child_rule = TestRule(name="Test", param=None)
    child_rule.execute = Mock()

    with pytest.raises(ValueError) as exc:
        TestRule(
            name="Test",
            param="Rule",
            pipe=piped_rule,
            children=[child_rule]
        )

    assert str(exc.value) == 'pipe and children cannot be set at the same time'
    assert not piped_rule.execute.called
    assert not child_rule.execute.called

def test_rule_execute_pipe():
    piped_rule = TestRule(name="Test", param=None)
    piped_rule.execute = Mock()

    rule = TestRule(name="Test", param="Rule", pipe=piped_rule)
    rule.execute()

    # Asserting that the output of the original rule - which in this case
    # the input as well - is passed to the piped rule as an input.
    piped_rule.execute.assert_called_once_with(rule.param)

def test_rule_execute_children():
    child_rule_1 = TestRule(name="Test", param=None)
    child_rule_1.execute = Mock()

    child_rule_2 = TestRule(name="Test", param=None)
    child_rule_2.execute = Mock()

    child_rule_3 = TestRule(name="Test", param=None)
    child_rule_3.execute = Mock()

    rule = TestRule(name="Test", param="Rule", children=[
        child_rule_1,
        child_rule_2,
        child_rule_3
    ])

    rule.execute()

    child_rule_1.execute.assert_called_once_with(rule.param)
    child_rule_2.execute.assert_called_once_with(rule.param)
    child_rule_3.execute.assert_called_once_with(rule.param)

@given(
    value=st.one_of(
        st.text(),
        st.integers(),
        st.iterables(st.one_of(
            st.text(),
            st.integers()
        ))
    )
)
def test_rule_validate_param(value):
    rule = TestRule(name="Test", param="Rule")

    # Casting to string is the safest
    result = rule.validate(value, cast_to=str)

    assert result == str(value)

@given(
    value=st.one_of(
        st.text(),
        st.integers(),
        st.iterables(st.one_of(
            st.text(),
            st.integers()
        ))
    )
)
def test_rule_validate_no_casting(value):
    rule = TestRule(name="Test", param="Rule")

    result = rule.validate(val=value)

    assert result is value

def test_rule_validate_param_empty():
    rule = TestRule(name="Test", param="Rule")

    result = rule.validate(val=None, cast_to=str)

    assert result == "None"

def test_rule_validate_param_required():
    rule = TestRule(name="Test", param="Rule")

    with pytest.raises(ValueError) as exc:
        rule.validate(val=None, cast_to=str, required=True)

    assert str(exc.value) == 'The given value is empty'
