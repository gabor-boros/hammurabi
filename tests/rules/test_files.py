from unittest.mock import Mock

from hammurabi.rules.files import (
    FileEmptied,
    FileExists,
    FileNotExists,
    FilesExist,
    FilesNotExist,
)


def test_file_exists():
    expected_path = Mock()

    rule = FileExists(name="File exists rule", path=expected_path)
    result = rule.task()

    assert result == expected_path
    expected_path.touch.assert_called_once_with()


def test_files_exist():
    expected_path_1 = Mock()
    expected_paths = [expected_path_1]

    rule = FilesExist(name="Files exist rule", paths=expected_paths)
    result = rule.task()

    assert result == expected_paths
    expected_path_1.touch.assert_called_once_with()


def test_file_not_exists():
    expected_path = Mock()
    expected_path.exists.return_value = True

    rule = FileNotExists(name="File not exists rule", path=expected_path)
    rule.git_remove = Mock()

    result = rule.task()
    rule.post_task_hook()

    assert result == expected_path
    expected_path.exists.assert_called_once_with()
    expected_path.unlink.assert_called_once_with()
    rule.git_remove.assert_called_once_with(expected_path)


def test_no_file_can_be_removed():
    expected_path = Mock()
    expected_path.exists.return_value = False

    rule = FileNotExists(name="File not exists rule", path=expected_path)
    rule.git_remove = Mock()

    result = rule.task()
    rule.post_task_hook()

    assert result == expected_path
    expected_path.exists.assert_called_once_with()
    assert expected_path.unlink.called is False
    rule.git_remove.assert_called_once_with(expected_path)


def test_files_not_exist():
    expected_path_1 = Mock()
    expected_path_1.exists.return_value = True
    expected_paths = [expected_path_1]

    rule = FilesNotExist(name="Files not exist rule", paths=expected_paths)
    rule.git_remove = Mock()

    result = rule.task()
    rule.post_task_hook()

    assert result == expected_paths
    expected_path_1.exists.assert_called_once_with()
    expected_path_1.unlink.assert_called_once_with()
    rule.git_remove.assert_called_once_with(expected_path_1)


def test_no_files_can_be_removed():
    expected_path_1 = Mock()
    expected_path_1.exists.return_value = False
    expected_paths = [expected_path_1]

    rule = FilesNotExist(name="Files not exist rule", paths=expected_paths)
    rule.git_remove = Mock()

    result = rule.task()
    rule.post_task_hook()

    assert result == expected_paths
    expected_path_1.exists.assert_called_once_with()
    assert expected_path_1.unlink.called is False
    rule.git_remove.assert_called_once_with(expected_path_1)


def test_emptied():
    expected_path = Mock()

    rule = FileEmptied(name="File emptied rule", path=expected_path)
    result = rule.task()

    assert result == expected_path
    expected_path.write_text.assert_called_once_with("")
