from pathlib import Path

import pytest

from hammurabi.rules.yaml import (
    YamlKeyExists,
    YamlKeyNotExists,
    YamlKeyRenamed,
    YamlValueExists,
    YamlValueNotExists,
)
from tests.fixtures import temporary_file

assert temporary_file


@pytest.mark.integration
def test_key_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("")

    rule = YamlKeyExists(name="Ensure key exists", path=expected_file, key="stack")

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "stack:\n"
    expected_file.unlink()


@pytest.mark.integration
def test_key_nested_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("")

    rule = YamlKeyExists(
        name="Ensure key exists",
        path=expected_file,
        key="development.supported",
        value=True,
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "development:\n  supported: true\n"
    expected_file.unlink()


@pytest.mark.integration
def test_key_nested_already_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text(
        "apple: banana\ndict:\n  value: exists\ndevelopment:\n  supported: true\n"
    )

    rule = YamlKeyExists(
        name="Ensure key exists",
        path=expected_file,
        key="development.supported",
        value=True,
    )

    rule.pre_task_hook()
    rule.task()

    assert (
        expected_file.read_text()
        == "apple: banana\ndict:\n  value: exists\ndevelopment:\n  supported: true\n"
    )
    expected_file.unlink()


@pytest.mark.integration
def test_key_exists_with_value(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("")

    rule = YamlKeyExists(
        name="Ensure key exists", path=expected_file, key="stack", value="python"
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "stack: python\n"
    expected_file.unlink()


@pytest.mark.integration
def test_key_exists_with_root_dot(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("")

    rule = YamlKeyExists(
        name="Ensure key exists", path=expected_file, key=".stack", value="python"
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "stack: python\n"
    expected_file.unlink()


@pytest.mark.integration
def test_key_exists_keeping_comment(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("test: apple  # test comment")

    rule = YamlKeyExists(
        name="Ensure key exists", path=expected_file, key="stack", value="python"
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "test: apple  # test comment\nstack: python\n"
    expected_file.unlink()


@pytest.mark.integration
def test_key_not_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndependencies: []")

    rule = YamlKeyNotExists(
        name="Ensure key not exists", path=expected_file, key="stack"
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "dependencies: []\n"
    expected_file.unlink()


@pytest.mark.integration
def test_key_not_exists_no_key(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("dependencies: []")

    rule = YamlKeyNotExists(
        name="Ensure key not exists", path=expected_file, key="stack"
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "dependencies: []"
    expected_file.unlink()


@pytest.mark.integration
def test_key_not_exists_empty_file(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("")

    rule = YamlKeyNotExists(
        name="Ensure key not exists", path=expected_file, key="stack"
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == ""
    expected_file.unlink()


@pytest.mark.integration
def test_key_renamed(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndepends_on: []")

    rule = YamlKeyRenamed(
        name="Ensure key renamed",
        path=expected_file,
        key="depends_on",
        new_name="dependencies",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "stack: python\ndependencies: []\n"
    expected_file.unlink()


@pytest.mark.integration
def test_key_renamed_no_old_key(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndependencies: []")

    rule = YamlKeyRenamed(
        name="Ensure key renamed",
        path=expected_file,
        key="depends_on",
        new_name="dependencies",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "stack: python\ndependencies: []"
    expected_file.unlink()


@pytest.mark.integration
def test_key_renamed_no_old_or_new_key(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\n")

    rule = YamlKeyRenamed(
        name="Ensure key renamed",
        path=expected_file,
        key="depends_on",
        new_name="dependencies",
    )

    rule.pre_task_hook()

    with pytest.raises(LookupError):
        rule.task()

    assert expected_file.read_text() == "stack: python\n"
    expected_file.unlink()


@pytest.mark.integration
def test_key_renamed_has_old_and_new_key(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndependencies: []\ndepends_on: []")

    rule = YamlKeyRenamed(
        name="Ensure key renamed",
        path=expected_file,
        key="depends_on",
        new_name="dependencies",
    )

    rule.pre_task_hook()

    with pytest.raises(LookupError):
        rule.task()

    assert (
        expected_file.read_text() == "stack: python\ndependencies: []\ndepends_on: []"
    )
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: scala")

    rule = YamlValueExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="stack",
        value="python",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "stack: python\n"
    expected_file.unlink()


@pytest.mark.integration
def test_value_nested_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("development:\n  apple: true\n")

    rule = YamlValueExists(
        name="Ensure local development is supported",
        path=expected_file,
        key="development.supported",
        value=True,
    )

    rule.pre_task_hook()
    rule.task()

    assert (
        expected_file.read_text() == "development:\n  apple: true\n  supported: true\n"
    )
    expected_file.unlink()


@pytest.mark.integration
def test_value_nested_already_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("development:\n  supported: true\n")

    rule = YamlValueExists(
        name="Ensure local development is supported",
        path=expected_file,
        key="development.supported",
        value=True,
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "development:\n  supported: true\n"
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists_no_value(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: scala")

    rule = YamlValueExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="stack",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "stack:\n"
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists_list(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndependencies: []")

    rule = YamlValueExists(
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
        == "stack: python\ndependencies:\n- service1\n- service2\n"
    )
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists_list_single_item(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndependencies: []")

    rule = YamlValueExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value="service1",
    )

    rule.pre_task_hook()
    rule.task()

    # Because of the default flow style False, the result will be block-styled
    assert expected_file.read_text() == "stack: python\ndependencies:\n- service1\n"
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists_nested_list_single_item(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\nnested:\n  dependencies: []")

    rule = YamlValueExists(
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
        == "stack: python\nnested:\n  dependencies:\n  - service1\n"
    )
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists_list_already_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndependencies: [service3]")

    rule = YamlValueExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value=["service1", "service2"],
    )

    rule.pre_task_hook()
    rule.task()

    assert (
        expected_file.read_text()
        == "stack: python\ndependencies: [service3, service1, service2]\n"
    )
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists_list_already_exists_single_item(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndependencies: [service2]")

    rule = YamlValueExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value="service1",
    )

    rule.pre_task_hook()
    rule.task()

    assert (
        expected_file.read_text()
        == "stack: python\ndependencies: [service2, service1]\n"
    )
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists_dict(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndependencies: {}")

    rule = YamlValueExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value={"service1": True, "service2": True},
    )

    rule.pre_task_hook()
    rule.task()

    assert (
        expected_file.read_text()
        == "stack: python\ndependencies:\n  service1: true\n  service2: true\n"
    )
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists_dict_already_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndependencies: {service3: true}")

    rule = YamlValueExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value={"service1": True},
    )

    rule.pre_task_hook()
    rule.task()

    assert (
        expected_file.read_text()
        == "stack: python\ndependencies: {service3: true, service1: true}\n"
    )
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python")

    rule = YamlValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="stack",
        value="python",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "stack:\n"
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_nested(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("development:\n  stack: python\n")

    rule = YamlValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="development.stack",
        value="python",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "development:\n  stack:\n"
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_not_changed(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: scala")

    rule = YamlValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="stack",
        value="python",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "stack: scala"
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_nested_not_changed(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("development:\n  stack: scala\n")

    rule = YamlValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="development.stack",
        value="python",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "development:\n  stack: scala\n"
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_no_key(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("dependencies: []")

    rule = YamlValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="stack",
        value="python",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "dependencies: []"
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_nested_no_key(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("dependencies:\n  supported:\n  apple: banana\n")

    rule = YamlValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies.supported.stack",
        value="python",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "dependencies:\n  supported:\n  apple: banana\n"
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_list(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndependencies: [service1, service2]")

    rule = YamlValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value="service1",
    )

    rule.pre_task_hook()
    rule.task()

    # Because of the default flow style False, the result will be block-styled
    assert expected_file.read_text() == "stack: python\ndependencies: [service2]\n"
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_list_no_item(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndependencies: [service3]")

    rule = YamlValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value="service1",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "stack: python\ndependencies: [service3]"
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_dict(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndependencies: {service1: true}")

    rule = YamlValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value="service1",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "stack: python\ndependencies: {}\n"
    expected_file.unlink()


@pytest.mark.integration
def test_value_not_exists_dict_no_key(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndependencies: {service3: true}")

    rule = YamlValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value="service1",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "stack: python\ndependencies: {service3: true}"
    expected_file.unlink()
