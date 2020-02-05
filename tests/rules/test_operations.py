from pathlib import Path
from unittest.mock import Mock, patch

from hammurabi.rules.operations import Copied, Moved, Renamed


@patch("hammurabi.rules.operations.shutil")
def test_moved(mocked_shutil):
    source = Mock()
    destination = Mock()

    rule = Moved(name="Moved rule", path=source, destination=destination)
    rule.git_add = Mock()
    rule.git_remove = Mock()

    result = rule.task()
    rule.post_task_hook()

    assert result == destination
    mocked_shutil.move.assert_called_once_with(source, destination)
    rule.git_remove.assert_called_once_with(source)
    rule.git_add.assert_called_once_with(destination)


@patch("hammurabi.rules.operations.shutil")
def test_renamed(mocked_shutil):
    source = Path("/tmp/apple/tree")
    new_name = "tree2"
    destination = Path("/tmp/apple/", new_name)

    rule = Renamed(name="Renamed rule", path=source, new_name=new_name)
    rule.git_add = Mock()
    rule.git_remove = Mock()

    result = rule.task()
    rule.post_task_hook()

    assert result == destination
    mocked_shutil.move.assert_called_once_with(source, destination)
    rule.git_remove.assert_called_once_with(source)
    rule.git_add.assert_called_once_with(destination)


@patch("hammurabi.rules.operations.shutil")
def test_file_copied(mocked_shutil):
    source = Mock()
    destination = Mock()
    source.is_dir.return_value = False

    rule = Copied(name="Copied rule", path=source, destination=destination)
    rule.git_add = Mock()

    result = rule.task()
    rule.post_task_hook()

    assert result == destination
    mocked_shutil.copy2.assert_called_once_with(source, destination)
    rule.git_add.assert_called_once_with(destination)


@patch("hammurabi.rules.operations.shutil")
def test_directory_copied(mocked_shutil):
    source = Mock()
    destination = Mock()
    source.is_dir.return_value = True

    rule = Copied(name="Copied rule", path=source, destination=destination)
    rule.git_add = Mock()

    result = rule.task()
    rule.post_task_hook()

    assert result == destination
    mocked_shutil.copytree.assert_called_once_with(source, destination)
    rule.git_add.assert_called_once_with(destination)
