from pathlib import Path
from unittest.mock import Mock, PropertyMock, patch

from tests.helpers import get_git_mixin_consumer, get_github_mixin_consumer


@patch("hammurabi.mixins.config")
def test_has_changes(mocked_config):
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = False
    mocked_config.repo.is_dirty.return_value = True

    has_changes = git_mixin.has_changes

    mocked_config.repo.is_dirty.assert_called_once_with()
    assert has_changes is True


@patch("hammurabi.mixins.config")
def test_has_no_changes(mocked_config):
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = False
    mocked_config.repo.is_dirty.return_value = False

    has_changes = git_mixin.has_changes

    mocked_config.repo.is_dirty.assert_called_once_with()
    assert has_changes is False


@patch("hammurabi.mixins.config")
def test_has_changes_no_repo(mocked_config):
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = False
    mocked_repo_prop = PropertyMock(return_value=None)
    type(mocked_config).repo = mocked_repo_prop

    has_changes = git_mixin.has_changes

    assert has_changes is False
    mocked_repo_prop.assert_called_once_with()


@patch("hammurabi.mixins.config")
def test_has_changes_no_repo_but_changes(mocked_config):
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = False
    mocked_repo_prop = PropertyMock(return_value=None)
    type(mocked_config).repo = mocked_repo_prop
    git_mixin.made_changes = True

    has_changes = git_mixin.has_changes

    assert has_changes is True
    mocked_repo_prop.assert_called_once_with()


@patch("hammurabi.mixins.config")
def test_checkout_branch(mocked_config):
    expected_branch_name = "awesome_branch"
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = False
    mocked_config.git_branch_name = expected_branch_name

    git_mixin.checkout_branch()

    mocked_config.repo.git.checkout.assert_called_once_with(
        "HEAD", B=expected_branch_name
    )


@patch("hammurabi.mixins.config")
def test_checkout_branch_dry_run(mocked_config):
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = True

    git_mixin.checkout_branch()

    assert mocked_config.repo.git.checkout.called is False


@patch("hammurabi.mixins.config")
def test_checkout_no_repo(mocked_config):
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = False
    mocked_repo_prop = PropertyMock(return_value=None)
    type(mocked_config).repo = mocked_repo_prop

    git_mixin.checkout_branch()

    mocked_repo_prop.assert_called_once_with()


@patch("hammurabi.mixins.config")
def test_git_add(mocked_config):
    expected_path = Path("/tmp/path")
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = False

    git_mixin.git_add(expected_path)

    mocked_config.repo.git.add.assert_called_once_with(expected_path)


@patch("hammurabi.mixins.config")
def test_git_add_dry_run(mocked_config):
    expected_path = Path("/tmp/path")
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = True

    git_mixin.git_add(expected_path)

    assert mocked_config.repo.git.add.called is False


@patch("hammurabi.mixins.config")
def test_git_add_no_repo(mocked_config):
    expected_path = Path("/tmp/path")
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = False
    mocked_repo_prop = PropertyMock(return_value=None)
    type(mocked_config).repo = mocked_repo_prop

    git_mixin.git_add(expected_path)

    mocked_repo_prop.assert_called_once_with()


@patch("hammurabi.mixins.config")
def test_git_remove(mocked_config):
    expected_path = Path("/tmp/path")
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = False

    git_mixin.git_remove(expected_path)

    mocked_config.repo.index.remove.assert_called_once_with(expected_path)


@patch("hammurabi.mixins.config")
def test_git_remove_dry_run(mocked_config):
    expected_path = Path("/tmp/path")
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = True

    git_mixin.git_remove(expected_path)

    assert mocked_config.repo.index.remove.called is False


@patch("hammurabi.mixins.config")
def test_git_remove_no_repo(mocked_config):
    expected_path = Path("/tmp/path")
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = False
    mocked_repo_prop = PropertyMock(return_value=None)
    type(mocked_config).repo = mocked_repo_prop

    git_mixin.git_remove(expected_path)

    mocked_repo_prop.assert_called_once_with()


@patch("hammurabi.mixins.config")
def test_git_commit(mocked_config):
    expected_path = "message"
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = False

    git_mixin.git_commit(expected_path)

    mocked_config.repo.index.commit.assert_called_once_with(expected_path)


@patch("hammurabi.mixins.config")
def test_git_commit_dry_run(mocked_config):
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = True

    git_mixin.git_commit("message")

    assert mocked_config.repo.index.commit.called is False


@patch("hammurabi.mixins.config")
def test_git_commit_no_changes(mocked_config):
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = False
    mocked_config.repo.is_dirty.return_value = False

    git_mixin.git_commit("message")

    assert mocked_config.repo.index.commit.called is False


@patch("hammurabi.mixins.config")
def test_push_changes(mocked_config):
    expected_branch_name = "awesome_branch"
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = False
    mocked_config.git_branch_name = expected_branch_name

    git_mixin.push_changes()

    mocked_config.repo.remotes.origin.push.assert_called_once_with(expected_branch_name)


@patch("hammurabi.mixins.config")
def test_push_changes_dry_run(mocked_config):
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = True

    git_mixin.push_changes()

    assert mocked_config.repo.remotes.origin.push.called is False


@patch("hammurabi.mixins.config")
def test_push_changes_no_repo(mocked_config):
    git_mixin = get_git_mixin_consumer()
    mocked_config.dry_run = False
    mocked_repo_prop = PropertyMock(return_value=None)
    type(mocked_config).repo = mocked_repo_prop

    git_mixin.push_changes()

    mocked_repo_prop.assert_called_once_with()


@patch("hammurabi.mixins.config")
def test_github_pull_request(mocked_config):
    github = get_github_mixin_consumer()

    expected_branch_name = "awesome_branch"
    expected_owner = "gabor-boros"
    expected_repo_name = "hammurabi"
    mocked_repository = Mock()
    mocked_repository.pull_requests.return_value = []

    mocked_config.dry_run = False
    mocked_config.git_branch_name = expected_branch_name
    mocked_config.repository = f"{expected_owner}/{expected_repo_name}"
    mocked_config.github.repository.return_value = mocked_repository

    github.create_pull_request()

    mocked_config.github.repository.assert_called_once_with(
        expected_owner, expected_repo_name
    )

    mocked_repository.pull_requests.assert_called_once_with(
        state="open", head=expected_branch_name, base="master"
    )

    mocked_repository.create_pull.assert_called_once_with(
        title="[hammurabi] Update to match the latest baseline",
        base="master",
        head=expected_branch_name,
        body="TODO",
    )


@patch("hammurabi.mixins.config")
def test_github_pull_request_dry_run(mocked_config):
    github = get_github_mixin_consumer()
    mocked_repository = Mock()

    mocked_config.dry_run = True
    mocked_config.github.repository.return_value = mocked_repository

    github.create_pull_request()

    assert mocked_config.repository.called is False
    assert mocked_config.github.repository.called is False
    assert mocked_repository.pull_requests.called is False
    assert mocked_repository.create_pull.called is False


@patch("hammurabi.mixins.config")
def test_github_pull_request_no_repo(mocked_config):
    github = get_github_mixin_consumer()
    mocked_repository = Mock()

    mocked_config.dry_run = False
    mocked_repo_prop = PropertyMock(return_value=None)
    type(mocked_config).repo = mocked_repo_prop
    mocked_config.github.repository.return_value = mocked_repository

    github.create_pull_request()

    assert mocked_repo_prop.called is True
    assert mocked_config.repository.called is False
    assert mocked_config.github.repository.called is False
    assert mocked_repository.pull_requests.called is False
    assert mocked_repository.create_pull.called is False


@patch("hammurabi.mixins.config")
def test_github_pull_request_has_opened_pr(mocked_config):
    github = get_github_mixin_consumer()

    expected_branch_name = "awesome_branch"
    expected_owner = "gabor-boros"
    expected_repo_name = "hammurabi"
    mocked_repository = Mock()
    mocked_repository.pull_requests.return_value = [Mock()]

    mocked_config.dry_run = False
    mocked_config.git_branch_name = expected_branch_name
    mocked_config.repository = f"{expected_owner}/{expected_repo_name}"
    mocked_config.github.repository.return_value = mocked_repository

    github.create_pull_request()

    mocked_config.github.repository.assert_called_once_with(
        expected_owner, expected_repo_name
    )

    mocked_repository.pull_requests.assert_called_once_with(
        state="open", head=expected_branch_name, base="master"
    )

    assert mocked_repository.create_pull.called is False
