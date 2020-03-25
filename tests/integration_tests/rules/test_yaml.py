from pathlib import Path

import pytest

from hammurabi.rules.yaml import (
    YAMLKeyExists,
    YAMLKeyNotExists,
    YAMLKeyRenamed,
    YAMLValueExists,
    YAMLValueNotExists,
)
from tests.fixtures import temporary_file

assert temporary_file


@pytest.mark.integration
def test_key_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("")

    rule = YAMLKeyExists(name="Ensure key exists", path=expected_file, key="stack")

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "stack:\n"
    expected_file.unlink()


@pytest.mark.integration
def test_key_nested_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("")

    rule = YAMLKeyExists(
        name="Ensure key exists",
        path=expected_file,
        key="development.supported.enabled",
        value=True,
    )

    rule.pre_task_hook()
    rule.task()

    assert (
        expected_file.read_text() == "development:\n  supported:\n    enabled: true\n"
    )
    expected_file.unlink()


@pytest.mark.integration
def test_key_exists_with_value(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("")

    rule = YAMLKeyExists(
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

    rule = YAMLKeyExists(
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

    rule = YAMLKeyExists(
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

    rule = YAMLKeyNotExists(
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

    rule = YAMLKeyNotExists(
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

    rule = YAMLKeyNotExists(
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

    rule = YAMLKeyRenamed(
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

    rule = YAMLKeyRenamed(
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

    rule = YAMLKeyRenamed(
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

    rule = YAMLKeyRenamed(
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

    rule = YAMLValueExists(
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
def test_value_exists_no_key(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("dependencies: []")

    rule = YAMLValueExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="stack",
        value="python",
    )

    rule.pre_task_hook()

    with pytest.raises(LookupError):
        rule.task()

    assert expected_file.read_text() == "dependencies: []"
    expected_file.unlink()


@pytest.mark.integration
def test_value_exists_list(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndependencies: []")

    rule = YAMLValueExists(
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
def test_value_exists_list_already_exists(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndependencies: [service3]")

    rule = YAMLValueExists(
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
def test_value_exists_dict(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndependencies: {}")

    rule = YAMLValueExists(
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

    rule = YAMLValueExists(
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

    rule = YAMLValueNotExists(
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
def test_value_not_exists_not_changed(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: scala")

    rule = YAMLValueNotExists(
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
def test_value_not_exists_no_key(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("dependencies: []")

    rule = YAMLValueNotExists(
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
def test_value_not_exists_list(temporary_file):
    expected_file = Path(temporary_file.name)
    expected_file.write_text("stack: python\ndependencies: [service1, service2]")

    rule = YAMLValueNotExists(
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

    rule = YAMLValueNotExists(
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

    rule = YAMLValueNotExists(
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

    rule = YAMLValueNotExists(
        name="Ensure service descriptor has dependencies",
        path=expected_file,
        key="dependencies",
        value="service1",
    )

    rule.pre_task_hook()
    rule.task()

    assert expected_file.read_text() == "stack: python\ndependencies: {service3: true}"
    expected_file.unlink()
