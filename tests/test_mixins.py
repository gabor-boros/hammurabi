from pathlib import Path
from unittest.mock import Mock, PropertyMock, patch

from hammurabi import Law
from tests.helpers import ExampleRule, get_git_mixin_consumer, get_github_mixin_consumer


@patch("hammurabi.mixins.config")
def test_checkout_branch(mocked_config):
    expected_branch_name = "awesome_branch"
    git_mixin = get_git_mixin_consumer()
    mocked_config.settings.dry_run = False
    mocked_config.settings.git_branch_name = expected_branch_name

    git_mixin.checkout_branch()

    mocked_config.repo.git.checkout.assert_called_once_with(
        "HEAD", B=expected_branch_name
    )


@patch("hammurabi.mixins.config")
def test_checkout_branch_dry_run(mocked_config):
    git_mixin = get_git_mixin_consumer()
    mocked_config.settings.dry_run = True

    git_mixin.checkout_branch()

    assert mocked_config.repo.git.checkout.called is False


@patch("hammurabi.mixins.config")
def test_checkout_no_repo(mocked_config):
    git_mixin = get_git_mixin_consumer()
    mocked_config.settings.dry_run = False
    mocked_repo_prop = PropertyMock(return_value=None)
    type(mocked_config).repo = mocked_repo_prop

    git_mixin.checkout_branch()

    mocked_repo_prop.assert_called_once_with()


@patch("hammurabi.mixins.config")
def test_git_add(mocked_config):
    expected_path = Path("/tmp/path")
    git_mixin = get_git_mixin_consumer()
    mocked_config.settings.dry_run = False

    git_mixin.git_add(expected_path)

    mocked_config.repo.git.add.assert_called_once_with(expected_path)


@patch("hammurabi.mixins.config")
def test_git_add_dry_run(mocked_config):
    expected_path = Path("/tmp/path")
    git_mixin = get_git_mixin_consumer()
    mocked_config.settings.dry_run = True

    git_mixin.git_add(expected_path)

    assert mocked_config.repo.git.add.called is False


@patch("hammurabi.mixins.config")
def test_git_add_no_repo(mocked_config):
    expected_path = Path("/tmp/path")
    git_mixin = get_git_mixin_consumer()
    mocked_config.settings.dry_run = False
    mocked_repo_prop = PropertyMock(return_value=None)
    type(mocked_config).repo = mocked_repo_prop

    git_mixin.git_add(expected_path)

    mocked_repo_prop.assert_called_once_with()


@patch("hammurabi.mixins.config")
def test_git_remove(mocked_config):
    expected_path = Path("/tmp/path")
    git_mixin = get_git_mixin_consumer()
    mocked_config.settings.dry_run = False

    git_mixin.git_remove(expected_path)

    mocked_config.repo.index.remove.assert_called_once_with(expected_path)


@patch("hammurabi.mixins.config")
def test_git_remove_dry_run(mocked_config):
    expected_path = Path("/tmp/path")
    git_mixin = get_git_mixin_consumer()
    mocked_config.settings.dry_run = True

    git_mixin.git_remove(expected_path)

    assert mocked_config.repo.index.remove.called is False


@patch("hammurabi.mixins.config")
def test_git_remove_no_repo(mocked_config):
    expected_path = Path("/tmp/path")
    git_mixin = get_git_mixin_consumer()
    mocked_config.settings.dry_run = False
    mocked_repo_prop = PropertyMock(return_value=None)
    type(mocked_config).repo = mocked_repo_prop

    git_mixin.git_remove(expected_path)

    mocked_repo_prop.assert_called_once_with()


@patch("hammurabi.mixins.config")
def test_git_commit(mocked_config):
    expected_path = "message"
    git_mixin = get_git_mixin_consumer()
    mocked_config.settings.dry_run = False

    git_mixin.git_commit(expected_path)

    mocked_config.repo.index.commit.assert_called_once_with(expected_path)


@patch("hammurabi.mixins.config")
def test_git_commit_dry_run(mocked_config):
    git_mixin = get_git_mixin_consumer()
    mocked_config.settings.dry_run = True

    git_mixin.git_commit("message")

    assert mocked_config.repo.index.commit.called is False


@patch("hammurabi.mixins.config")
def test_git_commit_no_changes(mocked_config):
    git_mixin = get_git_mixin_consumer()
    mocked_config.settings.dry_run = False
    mocked_config.repo.is_dirty.return_value = False

    git_mixin.git_commit("message")

    assert mocked_config.repo.index.commit.called is False


@patch("hammurabi.mixins.config")
def test_push_changes(mocked_config):
    expected_branch_name = "awesome_branch"
    git_mixin = get_git_mixin_consumer()
    mocked_config.settings.dry_run = False
    mocked_config.settings.git_branch_name = expected_branch_name

    git_mixin.push_changes()

    mocked_config.repo.remotes.origin.push.assert_called_once_with(expected_branch_name)


@patch("hammurabi.mixins.config")
def test_push_changes_dry_run(mocked_config):
    git_mixin = get_git_mixin_consumer()
    mocked_config.settings.dry_run = True

    git_mixin.push_changes()

    assert mocked_config.repo.remotes.origin.push.called is False


@patch("hammurabi.mixins.config")
def test_push_changes_no_repo(mocked_config):
    git_mixin = get_git_mixin_consumer()
    mocked_config.settings.dry_run = False
    mocked_repo_prop = PropertyMock(return_value=None)
    type(mocked_config).repo = mocked_repo_prop

    git_mixin.push_changes()

    mocked_repo_prop.assert_called_once_with()


def test_generate_pull_request_body():
    mocked_pillar = Mock()
    mocked_pillar.laws = [
        Law(
            name="Test law 1",
            description="Test description 1",
            rules=[ExampleRule(name="Test rule 1", param=Mock())],
        ),
        Law(
            name="Test law 2",
            description="Test description 2",
            rules=[ExampleRule(name="Test rule 2", param=Mock())],
        ),
        Law(
            name="Test law 3",
            description="Test description 3",
            rules=[
                ExampleRule(name="Test rule 3", param=Mock()),
                ExampleRule(name="Test rule 4", param=Mock()),
            ],
        ),
    ]

    expected_body = """## Description
Below you can find the executed laws and information about them.

### Test law 1
Test description 1

#### Rules
* Test rule 1

### Test law 2
Test description 2

#### Rules
* Test rule 2

### Test law 3
Test description 3

#### Rules
* Test rule 3
* Test rule 4"""

    github = get_github_mixin_consumer()

    body = github.generate_pull_request_body(mocked_pillar)

    assert body == expected_body


@patch("hammurabi.mixins.config")
def test_github_pull_request(mocked_config):
    expected_branch_name = "awesome_branch"
    expected_owner = "gabor-boros"
    expected_repo_name = "hammurabi"
    expected_pull_request_body = "test pull body"
    mocked_repository = Mock()
    mocked_repository.pull_requests.return_value = []

    github = get_github_mixin_consumer()
    github.generate_pull_request_body = Mock()
    github.generate_pull_request_body.return_value = expected_pull_request_body

    mocked_config.settings.dry_run = False
    mocked_config.settings.git_branch_name = expected_branch_name
    mocked_config.settings.git_base_name = "master"
    mocked_config.settings.repository = f"{expected_owner}/{expected_repo_name}"
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
        body=expected_pull_request_body,
    )


@patch("hammurabi.mixins.config")
def test_github_pull_request_dry_run(mocked_config):
    github = get_github_mixin_consumer()
    mocked_repository = Mock()

    mocked_config.settings.dry_run = True
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

    mocked_config.settings.dry_run = False
    mocked_repo_prop = PropertyMock(return_value=None)
    type(mocked_config).repo = mocked_repo_prop
    mocked_config.github.repository.return_value = mocked_repository

    github.create_pull_request()

    assert mocked_repo_prop.called is True
    assert mocked_config.settings.repository.called is False
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

    mocked_config.settings.dry_run = False
    mocked_config.settings.git_branch_name = expected_branch_name
    mocked_config.settings.repository = f"{expected_owner}/{expected_repo_name}"
    mocked_config.github.repository.return_value = mocked_repository

    github.create_pull_request()

    mocked_config.github.repository.assert_called_once_with(
        expected_owner, expected_repo_name
    )

    mocked_repository.pull_requests.assert_called_once_with(
        state="open", head=expected_branch_name, base="master"
    )

    assert mocked_repository.create_pull.called is False
