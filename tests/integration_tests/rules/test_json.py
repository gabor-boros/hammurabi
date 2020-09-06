from pathlib import Path

import pytest

from hammurabi.rules.json import (
    JsonKeyExists,
    JsonKeyNotExists,
    JsonKeyRenamed,
    JsonValueExists,
    JsonValueNotExists,
)
from tests.fixtures import temporary_file

assert temporary_file


@pytest.mark.integration
def test_key_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("{}")

    rule = JsonKeyExists(name="Ensure key exists", path=expected_file, key="stack")

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"stack":null}'
    expected_file.unlink()


@pytest.mark.integration
def test_key_nested_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("{}")

    rule = JsonKeyExists(
        name="Ensure key exists",
        path=expected_file,
        key="development.supported",
        value=True,
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"development":{"supported":true}}'
    expected_file.unlink()


@pytest.mark.integration
def test_key_nested_already_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text(
        '{"apple":"banana","dict":{"value":"exists","development":{"supported":true}}}'
    )

    rule = JsonKeyExists(
        name="Ensure key exists",
        path=expected_file,
        key="dict.development.supported",
        value=True,
    )

    rule.pre_task_hook()
    rule.task()

    assert (
        expected_file.read_text()
        == '{"apple":"banana","dict":{"value":"exists","development":{"supported":true}}}'
    )
    expected_file.unlink()


@pytest.mark.integration
def test_key_exists_with_value(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("{}")

    rule = JsonKeyExists(
        name="Ensure key exists", path=expected_file, key="stack", value="python"
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"stack":"python"}'
    expected_file.unlink()


@pytest.mark.integration
def test_key_exists_with_root_dot(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("{}")

    rule = JsonKeyExists(
        name="Ensure key exists", path=expected_file, key=".stack", value="python"
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"stack":"python"}'
    expected_file.unlink()


@pytest.mark.integration
def test_key_not_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"python","dependencies":[]}')

    rule = JsonKeyNotExists(
        name="Ensure key not exists", path=expected_file, key="stack"
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"dependencies":[]}'
    expected_file.unlink()


@pytest.mark.integration
def test_key_not_exists_no_key(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"dependencies":[]}')

    rule = JsonKeyNotExists(
        name="Ensure key not exists", path=expected_file, key="stack"
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"dependencies":[]}'
    expected_file.unlink()


@pytest.mark.integration
def test_key_not_exists_empty_file(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("{}")

    rule = JsonKeyNotExists(
        name="Ensure key not exists", path=expected_file, key="stack"
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "{}"
    expected_file.unlink()


@pytest.mark.integration
def test_key_renamed(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"python","depends_on":[]}')

    rule = JsonKeyRenamed(
        name="Ensure key renamed",
        path=expected_file,
        key="depends_on",
        new_name="dependencies",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"stack":"python","dependencies":[]}'
    expected_file.unlink()


@pytest.mark.integration
def test_key_renamed_no_old_key(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"python","dependencies":[]}')

    rule = JsonKeyRenamed(
        name="Ensure key renamed",
        path=expected_file,
        key="depends_on",
        new_name="dependencies",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"stack":"python","dependencies":[]}'
    expected_file.unlink()


@pytest.mark.integration
def test_key_renamed_no_old_or_new_key(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"python"}')

    rule = JsonKeyRenamed(
        name="Ensure key renamed",
        path=expected_file,
        key="depends_on",
        new_name="dependencies",
    )

    rule.pre_task_hook()

    with pytest.raises(LookupError):
        rule.task()

    assert expected_file.read_text() == '{"stack":"python"}'
    expected_file.unlink()


@pytest.mark.integration
def test_key_renamed_has_old_and_new_key(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"python","dependencies":[], "depends_on":[]}')

    rule = JsonKeyRenamed(
        name="Ensure key renamed",
        path=expected_file,
        key="depends_on",
        new_name="dependencies",
    )

    rule.pre_task_hook()

    with pytest.raises(LookupError):
        rule.task()

    assert (
        expected_file.read_text()
        == '{"stack":"python","dependencies":[], "depends_on":[]}'
    )
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"scala"}')

    rule = JsonValueExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="stack",
        value="python",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"stack":"python"}'
    expected_file.unlink()


@pytest.mark.integration
def test_value_nested_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"development":{"apple":true}}')

    rule = JsonValueExists(
        name="Ensure local development is supported",
        path=expected_file,
        key="development.supported",
        value=True,
    )

    rule.pre_task_hook()
    rule.task()

    assert (
        expected_file.read_text() == '{"development":{"apple":true,"supported":true}}'
    )
    expected_file.unlink()


@pytest.mark.integration
def test_value_nested_already_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"development":{"supported":true}}')

    rule = JsonValueExists(
        name="Ensure local development is supported",
        path=expected_file,
        key="development.supported",
        value=True,
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"development":{"supported":true}}'
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists_no_value(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"scala"}')

    rule = JsonValueExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="stack",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"stack":null}'
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists_list(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"python","dependencies":[]}')

    rule = JsonValueExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value=["service1", "service2"],
    )

    rule.pre_task_hook()
    rule.task()

    # Because of the default flow style False, the result will be block-styled
    assert (
        expected_file.read_text()
        == '{"stack":"python","dependencies":["service1","service2"]}'
    )
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists_list_single_item(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"python","dependencies":[]}')

    rule = JsonValueExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value="service1",
    )

    rule.pre_task_hook()
    rule.task()

    # Because of the default flow style False, the result will be block-styled
    assert expected_file.read_text() == '{"stack":"python","dependencies":["service1"]}'
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists_nested_list_single_item(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"python","nested":{"dependencies":[]}}')

    rule = JsonValueExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="nested.dependencies",
        value="service1",
    )

    rule.pre_task_hook()
    rule.task()

    # Because of the default flow style False, the result will be block-styled
    assert (
        expected_file.read_text()
        == '{"stack":"python","nested":{"dependencies":["service1"]}}'
    )
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists_list_already_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"python","dependencies":["service3"]}')

    rule = JsonValueExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value=["service1", "service2"],
    )

    rule.pre_task_hook()
    rule.task()

    assert (
        expected_file.read_text()
        == '{"stack":"python","dependencies":["service3","service1","service2"]}'
    )
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists_list_already_exists_single_item(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"python","dependencies":["service2"]}')

    rule = JsonValueExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value="service1",
    )

    rule.pre_task_hook()
    rule.task()

    assert (
        expected_file.read_text()
        == '{"stack":"python","dependencies":["service2","service1"]}'
    )
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists_dict(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"python","dependencies":[]}')

    rule = JsonValueExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value={"service1": True, "service2": True},
    )

    rule.pre_task_hook()
    rule.task()

    assert (
        expected_file.read_text()
        == '{"stack":"python","dependencies":[{"service1":true,"service2":true}]}'
    )
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists_dict_already_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"python","dependencies":{"service3":true}}')

    rule = JsonValueExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value={"service1": True},
    )

    rule.pre_task_hook()
    rule.task()

    assert (
        expected_file.read_text()
        == '{"stack":"python","dependencies":{"service3":true,"service1":true}}'
    )
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"python"}')

    rule = JsonValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="stack",
        value="python",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"stack":null}'
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_nested(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"development":{"stack":"python"}}')

    rule = JsonValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="development.stack",
        value="python",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"development":{"stack":null}}'
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_not_changed(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"scala"}')

    rule = JsonValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="stack",
        value="python",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"stack":"scala"}'
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_nested_not_changed(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"development":{"stack":"scala"}}')

    rule = JsonValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="development.stack",
        value="python",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"development":{"stack":"scala"}}'
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_no_key(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"dependencies":[]}')

    rule = JsonValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="stack",
        value="python",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"dependencies":[]}'
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_nested_no_key(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"development":{"supported":{"apple":"banana"}}}')

    rule = JsonValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies.supported.stack",
        value="python",
    )

    rule.pre_task_hook()
    rule.task()

    assert (
        expected_file.read_text() == '{"development":{"supported":{"apple":"banana"}}}'
    )
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_list(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text(
        '{"stack":"python","dependencies":["service1","service2"]}'
    )

    rule = JsonValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value="service1",
    )

    rule.pre_task_hook()
    rule.task()

    # Because of the default flow style False, the result will be block-styled
    assert expected_file.read_text() == '{"stack":"python","dependencies":["service2"]}'
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_list_no_item(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"python","dependencies":["service3"]}')

    rule = JsonValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value="service1",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"stack":"python","dependencies":["service3"]}'
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_dict(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"python","dependencies":{"service1":true}}')

    rule = JsonValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value="service1",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == '{"stack":"python","dependencies":{}}'
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_dict_no_key(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text('{"stack":"python","dependencies":{"service3":true}}')

    rule = JsonValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value="service1",
    )

    rule.pre_task_hook()
    rule.task()

    assert (
        expected_file.read_text()
        == '{"stack":"python","dependencies":{"service3":true}}'
    )
    expected_file.unlink()
