import copy
from typing import Any
from unittest.mock import Mock, call, patch

from hypothesis import given
from hypothesis import strategies as st
import pytest

from tests.helpers import FAILING_PRECONDITION, PASSING_PRECONDITION, ExampleRule


@patch("hammurabi.rules.base.full_strip")
def test_description(mock_full_strip):
    expected_description = "test description"
    mock_full_strip.return_value = expected_description

    rule = ExampleRule(name="Test", param="Rule")

    assert rule.description == expected_description
    mock_full_strip.assert_called_once_with("ExampleRule task docstring")


@patch("hammurabi.rules.base.full_strip")
def test_documentation(mock_full_strip):
    expected_description = "test description"
    expected_documentation = "test docstring"
    mock_full_strip.side_effect = [expected_description, expected_documentation]

    rule = ExampleRule(name="Test", param="Rule")

    documentation = f"{rule.name}\n{expected_description}\n{expected_documentation}"
    assert rule.documentation == documentation

    mock_full_strip.has_calls(
        [call(expected_description), call(expected_documentation)]
    )


@patch("hammurabi.rules.base.config")
@given(name=st.text(), param=st.one_of(st.text(), st.integers()))
def test_executed(name: str, param: Any, mocked_config):
    mocked_config.settings.dry_run = False

    rule = ExampleRule(name=name, param=param)

    rule.pre_task_hook = Mock()
    rule.post_task_hook = Mock()
    rule.task = Mock()

    rule.execute(param)

    rule.task.assert_called_once_with()
    rule.pre_task_hook.assert_called_once_with()
    rule.post_task_hook.assert_called_once_with()


@patch("hammurabi.rules.base.config")
def test_executed_no_direct_param(mocked_config):
    """
    This test case covers the situation of piped and child rules
    which has no direct parameter (it is set to None), but getting
    it from the output of the previous rule as an input.
    """

    mocked_config.settings.dry_run = False

    rule = ExampleRule(name="Test", param=None)
    rule.param = "Rule"

    rule.pre_task_hook = Mock()
    rule.post_task_hook = Mock()
    rule.task = Mock()

    rule.execute()

    rule.task.assert_called_once_with()
    rule.pre_task_hook.assert_called_once_with()
    rule.post_task_hook.assert_called_once_with()


@patch("hammurabi.rules.base.config")
def test_cannot_proceed_dry_run(config):
    config.dry_run = True
    rule = ExampleRule(name="Test", param="Rule")

    rule.pre_task_hook = Mock()
    rule.post_task_hook = Mock()

    with pytest.raises(AssertionError) as exc:
        rule.execute("Rule")

    assert str(exc.value) == '"Test" cannot proceed'
    assert not rule.pre_task_hook.called
    assert not rule.post_task_hook.called


@patch("hammurabi.rules.base.config")
def test_cannot_proceed_precondition(mocked_config):
    mocked_config.settings.dry_run = False

    rule = ExampleRule(
        name="Test",
        param="Rule",
        preconditions=(
            copy.deepcopy(FAILING_PRECONDITION),
            copy.deepcopy(PASSING_PRECONDITION),
        ),
    )

    rule.pre_task_hook = Mock()
    rule.post_task_hook = Mock()

    with pytest.raises(AssertionError) as exc:
        rule.execute("Rule")

    assert str(exc.value) == '"Test" cannot proceed'
    assert not rule.pre_task_hook.called
    assert not rule.post_task_hook.called


def test_cannot_proceed_pipe_and_children():
    piped_rule = ExampleRule(name="Test", param=None)
    piped_rule.execute = Mock()

    child_rule = ExampleRule(name="Test", param=None)
    child_rule.execute = Mock()

    with pytest.raises(ValueError) as exc:
        ExampleRule(name="Test", param="Rule", pipe=piped_rule, children=[child_rule])

    assert str(exc.value) == "pipe and children cannot be set at the same time"
    assert not piped_rule.execute.called
    assert not child_rule.execute.called


@patch("hammurabi.rules.base.config")
def test_execute_pipe(mocked_config):
    mocked_config.settings.dry_run = False

    piped_rule = ExampleRule(name="Test", param=None)
    piped_rule.execute = Mock()

    rule = ExampleRule(name="Test", param="Rule", pipe=piped_rule)
    rule.execute()

    # Asserting that the output of the original rule - which in this case
    # the input as well - is passed to the piped rule as an input.
    piped_rule.execute.assert_called_once_with(rule.param)


@patch("hammurabi.rules.base.config")
def test_execute_children(mocked_config):
    mocked_config.settings.dry_run = False

    child_rule_1 = ExampleRule(name="Test", param=None)
    child_rule_1.execute = Mock()

    child_rule_2 = ExampleRule(name="Test", param=None)
    child_rule_2.execute = Mock()

    child_rule_3 = ExampleRule(name="Test", param=None)
    child_rule_3.execute = Mock()

    rule = ExampleRule(
        name="Test", param="Rule", children=[child_rule_1, child_rule_2, child_rule_3]
    )

    rule.execute()

    child_rule_1.execute.assert_called_once_with(rule.param)
    child_rule_2.execute.assert_called_once_with(rule.param)
    child_rule_3.execute.assert_called_once_with(rule.param)


@given(
    value=st.one_of(
        st.text(), st.integers(), st.iterables(st.one_of(st.text(), st.integers()))
    )
)
def test_validate_param(value):
    rule = ExampleRule(name="Test", param="Rule")

    # Casting to string is the safest
    result = rule.validate(value, cast_to=str)

    assert result == str(value)


@given(
    value=st.one_of(
        st.text(), st.integers(), st.iterables(st.one_of(st.text(), st.integers()))
    )
)
def test_validate_no_casting(value):
    rule = ExampleRule(name="Test", param="Rule")

    result = rule.validate(val=value)

    assert result is value


def test_validate_param_empty():
    rule = ExampleRule(name="Test", param="Rule")

    result = rule.validate(val=None, cast_to=str)

    assert result == "None"


def test_validate_param_required():
    rule = ExampleRule(name="Test", param="Rule")

    with pytest.raises(ValueError) as exc:
        rule.validate(val=None, cast_to=str, required=True)

    assert str(exc.value) == "The given value is empty"


def test_execution_order():
    rule_1 = ExampleRule(name="rule_1", param="rule_1")
    rule_2 = ExampleRule(name="rule_2", param="rule_2")
    rule_3 = ExampleRule(name="rule_3", param="rule_3")
    rule_4 = ExampleRule(name="rule_4", param="rule_4")

    rule_1.pipe = rule_2
    rule_1.children = [rule_3, rule_4]
    rule_1.get_rule_chain = Mock(side_effect=[[rule_2], [rule_3], [rule_4]])
    expected_execution_order = [rule_1, rule_2, rule_3, rule_4]

    order = rule_1.get_execution_order()

    assert order == expected_execution_order
    rule_1.get_rule_chain.assert_has_calls([call(rule_2), call(rule_3), call(rule_4)])


def test_execution_order_no_chain():
    rule_1 = ExampleRule(name="rule_1", param="rule_1")
    rule_1.get_rule_chain = Mock(return_value=[])
    expected_execution_order = [rule_1]

    order = rule_1.get_execution_order()

    assert order == expected_execution_order
    assert rule_1.get_rule_chain.called is False


def test_rule_chain():
    rule_1 = ExampleRule(name="rule_1", param="rule_1")
    rule_2 = ExampleRule(name="rule_2", param="rule_2")
    rule_3 = ExampleRule(name="rule_3", param="rule_3")
    rule_4 = ExampleRule(name="rule_4", param="rule_4")
    rule_5 = ExampleRule(name="rule_5", param="rule_5")
    rule_6 = ExampleRule(name="rule_6", param="rule_6")
    rule_7 = ExampleRule(name="rule_7", param="rule_7")

    rule_1.pipe = rule_2
    rule_1.children = [rule_3, rule_4, rule_7]
    rule_4.pipe = rule_5
    rule_5.children = [rule_6]

    expected_chain_order = [rule_1, rule_2, rule_3, rule_4, rule_5, rule_6, rule_7]

    chain = rule_1.get_rule_chain(rule_1)

    assert chain == expected_chain_order


def test_rule_chain_no_rule():
    rule_1 = ExampleRule(name="rule_1", param="rule_1")

    chain = rule_1.get_rule_chain(rule_1)

    assert chain == [rule_1]
