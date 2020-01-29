from mock import Mock, patch

from hammurabi.rules.directories import (
    DirectoryEmptied,
    DirectoryExists,
    DirectoryNotExists,
)


def test_exists():
    mocked_path = Mock()
    rule = DirectoryExists(name="Test dir exists", path=mocked_path)

    result = rule.task()

    mocked_path.mkdir.assert_called_once_with()
    assert result == mocked_path


@patch("hammurabi.rules.directories.shutil")
def test_not_exists(mocked_shutil):
    mocked_path = Mock()
    mocked_path.exists.return_value = True
    rule = DirectoryNotExists(name="Test dir not exists", path=mocked_path)
    rule.git_remove = Mock()

    rule.execute()

    mocked_shutil.rmtree.assert_called_once_with(mocked_path)
    rule.git_remove.assert_called_once_with(mocked_path)


@patch("hammurabi.rules.directories.shutil")
def test_not_exists_no_remove(mocked_shutil):
    mocked_path = Mock()
    mocked_path.exists.return_value = False
    rule = DirectoryNotExists(name="Test dir not exists", path=mocked_path)

    result = rule.task()

    assert mocked_shutil.rmtree.called is False
    assert result == mocked_path


@patch("hammurabi.rules.directories.Path")
@patch("hammurabi.rules.directories.shutil")
@patch("hammurabi.rules.directories.os")
def test_emptied_files_or_symlinks(mocked_os, mocked_shutil, mocked_path):
    fake_path = Mock()
    rule = DirectoryEmptied(name="Test dir emptied", path=fake_path)

    mock_file = Mock(
        is_file=Mock(return_value=True), is_symlink=Mock(return_value=False)
    )

    mock_symlink = Mock(
        is_file=Mock(return_value=False), is_symlink=Mock(return_value=True)
    )

    expected_entries = [mock_file, mock_symlink]

    mocked_path.side_effect = expected_entries
    mocked_os.scandir.return_value.__enter__.return_value = expected_entries

    result = rule.task()

    mock_file.unlink.assert_called_once_with()
    mock_symlink.unlink.assert_called_once_with()
    assert mocked_shutil.rmtree.called is False
    assert result == fake_path


@patch("hammurabi.rules.directories.Path")
@patch("hammurabi.rules.directories.shutil")
@patch("hammurabi.rules.directories.os")
def test_emptied_subdirectory(mocked_os, mocked_shutil, mocked_path):
    fake_path = Mock()
    rule = DirectoryEmptied(name="Test dir emptied", path=fake_path)

    mock_dir = Mock(
        is_dir=Mock(return_value=True),
        is_file=Mock(return_value=False),
        is_symlink=Mock(return_value=False),
    )

    expected_entries = [mock_dir]

    mocked_path.side_effect = expected_entries
    mocked_os.scandir.return_value.__enter__.return_value = expected_entries

    result = rule.task()

    assert mock_dir.unlink.called is False
    mocked_shutil.rmtree.assert_called_once_with(mock_dir)
    assert result == fake_path
