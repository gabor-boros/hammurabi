from importlib.util import module_from_spec, spec_from_file_location
import logging
import os
from pathlib import Path
import sys
from typing import Optional, Union

from git import Repo
from github3 import GitHub, login
import toml


class Config:
    """
    Simple configuration object which used across Hammurabi.
    The :class:`Config` loads the given ``pyproject.toml`` according
    to PEP-518.
    """

    def __init__(self):
        self.__repo: Optional[Repo] = None
        self.github: Optional[GitHub] = None

        self.dry_run: bool = False
        self.pillar = None
        self.working_dir = Path(".")
        self.log_level: str = "INFO"
        self.rule_can_abort: bool = False
        self.git_branch_name = "hammurabi"
        self.repository: str = ""

        logging.basicConfig(
            stream=sys.stdout,
            format="[%(levelname)s]\t%(asctime)s - %(message)s",
            datefmt="%Y-%M-%d %H:%S",
        )

    @property
    def repo(self) -> Union[Repo, None]:
        """
        Get the target directory.
        """

        return self.__repo

    @repo.setter
    def repo(self, repository):
        """
        Set the target and change the working directory. If the target is a git
        repository.
        """

        self.working_dir = repository.absolute()
        os.chdir(self.working_dir)

        self.__repo = Repo(self.working_dir)

    def load(self, file: Union[str, Path]):
        """
        Load and parse the given ``pyproject.toml`` file.
        """

        file = Path(file)

        pyproject = toml.load(file.expanduser())
        project_config = pyproject.get("tool", {}).get("hammurabi", {})

        config_file = Path(project_config.get("config")).expanduser()
        pillar_var = project_config.get("pillar", "pillar")

        spec = spec_from_file_location(config_file.name.replace(".py", ""), config_file)

        module = module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore

        self.pillar = getattr(module, pillar_var)
        self.log_level = project_config.get("log_level", "INFO")
        self.github = login(token=project_config.get("github_token", ""))
        self.repo = Path(project_config.get("target", ""))
        self.repository = project_config.get("repository", "")
        self.git_branch_name = project_config.get("git_branch_name", "hammurabi")
        self.dry_run = bool(project_config.get("dry_run", ""))
        self.rule_can_abort = bool(project_config.get("rule_can_abort", ""))

        logging.root.setLevel(config.log_level)

        logging.debug('Successfully loaded "%s"', file.absolute())
        logging.debug('Successfully loaded "%s"', config_file.absolute())


config = Config()  # pylint: disable=invalid-name
