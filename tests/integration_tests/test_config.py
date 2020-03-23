import os
from pathlib import Path

from git import Repo
import pytest
import toml

from hammurabi.config import Config, Settings
from hammurabi.config import config as initialized_config
from tests.fixtures import temporary_dir, temporary_file_generator

assert temporary_file_generator
assert temporary_dir


@pytest.mark.integration
def test_config_not_loaded():
    assert initialized_config.github is None
    assert initialized_config.repo == Repo(Path(".").absolute())
    assert initialized_config.settings.dict() == Settings().dict()


@pytest.mark.integration
def test_no_settings_path():
    os.environ["HAMMURABI_SETTINGS_PATH"] = "fake path"
    config = Config()

    with pytest.raises(RuntimeError):
        config.load()


@pytest.mark.integration
def test_not_a_git_repository_path(temporary_dir, caplog):
    os.chdir(temporary_dir)

    Config()
    record = caplog.records[0]

    assert len(caplog.records)
    assert record.levelname == "ERROR"
    assert record.message == f'"{os.getcwd()}" is not a git repository'


@pytest.mark.integration
def test_configuration_loading(temporary_file_generator, temporary_dir):
    toml_file = temporary_file_generator()
    config_file = temporary_file_generator(".py")

    temporary_dir_repo = Repo.init(temporary_dir)
    temporary_dir_repo.create_remote(
        "origin", "git@github.com:gabor-boros/hammurabi.git"
    )

    os.chdir(temporary_dir)

    pillar_configuration = """from unittest.mock import Mock
pillar = Mock()
"""

    toml_configuration = {"tool": {"hammurabi": {"pillar_config": config_file.name}}}

    with config_file as f:
        f.write(pillar_configuration.encode("ascii"))

    with toml_file as f:
        f.write(toml.dumps(toml_configuration).encode("ascii"))

    os.environ["HAMMURABI_SETTINGS_PATH"] = toml_file.name
    config = Config()
    config.load()

    # Make sure to remove the file before going forward. In case
    # of an assert failure the fill will be deleted for sure
    os.unlink(config_file.name)
    os.unlink(toml_file.name)

    assert config.github is None
    assert (
        config.repo.working_dir.replace("/private", "")
        == temporary_dir_repo.working_dir
    )
    assert config.settings.dict() == {
        "dry_run": False,
        "git_base_name": "master",
        "git_branch_name": "hammurabi",
        "pillar": config.settings.pillar,
        "repository": "gabor-boros/hammurabi",
        "rule_can_abort": False,
    }


@pytest.mark.integration
def test_configuration_loading_no_fallback_repo(
    temporary_file_generator, temporary_dir
):
    toml_file = temporary_file_generator()
    config_file = temporary_file_generator(".py")

    temporary_dir_repo = Repo.init(temporary_dir)
    temporary_dir_repo.create_remote("origin", "")

    os.chdir(temporary_dir)

    pillar_configuration = """from unittest.mock import Mock
pillar = Mock()
"""

    toml_configuration = {"tool": {"hammurabi": {"pillar_config": config_file.name}}}

    with config_file as f:
        f.write(pillar_configuration.encode("ascii"))

    with toml_file as f:
        f.write(toml.dumps(toml_configuration).encode("ascii"))

    os.environ["HAMMURABI_SETTINGS_PATH"] = toml_file.name
    config = Config()
    config.load()

    # Make sure to remove the file before going forward. In case
    # of an assert failure the fill will be deleted for sure
    os.unlink(config_file.name)
    os.unlink(toml_file.name)

    assert config.github is None
    assert (
        config.repo.working_dir.replace("/private", "")
        == temporary_dir_repo.working_dir
    )
    assert config.settings.dict() == {
        "dry_run": False,
        "git_base_name": "master",
        "git_branch_name": "hammurabi",
        "pillar": config.settings.pillar,
        "repository": "",
        "rule_can_abort": False,
    }


@pytest.mark.integration
def test_configuration_loading_https_repo_url(temporary_file_generator, temporary_dir):
    """
    Load only the necessary configs and check for default settings
    """

    toml_file = temporary_file_generator()
    config_file = temporary_file_generator(".py")

    temporary_dir_repo = Repo.init(temporary_dir)
    temporary_dir_repo.create_remote(
        "origin", "https://github.com/gabor-boros/hammurabi.git"
    )

    os.chdir(temporary_dir)

    pillar_configuration = """from unittest.mock import Mock
pillar = Mock()
"""

    toml_configuration = {"tool": {"hammurabi": {"pillar_config": config_file.name}}}

    with config_file as f:
        f.write(pillar_configuration.encode("ascii"))

    with toml_file as f:
        f.write(toml.dumps(toml_configuration).encode("ascii"))

    os.environ["HAMMURABI_SETTINGS_PATH"] = toml_file.name
    config = Config()
    config.load()

    # Make sure to remove the file before going forward. In case
    # of an assert failure the fill will be deleted for sure
    os.unlink(config_file.name)
    os.unlink(toml_file.name)

    assert config.github is None
    assert (
        config.repo.working_dir.replace("/private", "")
        == temporary_dir_repo.working_dir
    )
    assert config.settings.dict() == {
        "dry_run": False,
        "git_base_name": "master",
        "git_branch_name": "hammurabi",
        "pillar": config.settings.pillar,
        "repository": "gabor-boros/hammurabi",
        "rule_can_abort": False,
    }
