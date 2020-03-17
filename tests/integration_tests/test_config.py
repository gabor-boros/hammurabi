import os
from pathlib import Path

from git import Repo
import pytest
import toml

from hammurabi.config import config
from tests.fixtures import temporary_dir, temporary_file_generator

assert temporary_file_generator
assert temporary_dir


@pytest.mark.integration
def test_config_not_loaded():
    assert config.github is None
    assert config.repo is None
    assert config.settings is None


@pytest.mark.integration
def test_configuration_loading(temporary_file_generator, temporary_dir):
    """
    Load only the necessary configs and check for default settings
    """

    toml_file = temporary_file_generator()
    config_file = temporary_file_generator(".py")

    temporary_dir_repo = Repo.init(temporary_dir)

    pillar_configuration = """from unittest.mock import Mock
pillar = Mock()
"""

    toml_configuration = {
        "tool": {
            "hammurabi": {"pillar_config": config_file.name, "target": temporary_dir}
        }
    }

    with config_file as f:
        f.write(pillar_configuration.encode("ascii"))

    with toml_file as f:
        f.write(toml.dumps(toml_configuration).encode("ascii"))

    config.load(toml_file.name)

    # Make sure to remove the file before going forward. In case
    # of an assert failure the fill will be deleted for sure
    os.unlink(config_file.name)
    os.unlink(toml_file.name)

    assert config.github is None
    assert config.repo == temporary_dir_repo
    assert config.settings.dict() == {
        "dry_run": False,
        "git_base_name": "master",
        "git_branch_name": "hammurabi",
        "pillar": config.settings.pillar,
        "repository": "",
        "rule_can_abort": False,
        "working_dir": Path(temporary_dir),
    }
