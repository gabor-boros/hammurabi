from importlib.util import module_from_spec, spec_from_file_location
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from git import Repo
from github3 import GitHub, login
from pydantic import BaseSettings
import toml


def dummy_callable():
    pass


class CommonSettings(BaseSettings):
    """
    Common settings which applies to both TOML and CLI
    configuration of Hammurabi.

    ``Pillar`` configuration is intentionally not listed since
    it is represented as a string in the TOML configuration, but
    used the parsed variable in the CLI configuration.
    """

    dry_run: bool = False
    rule_can_abort: bool = False
    git_branch_name: str = "hammurabi"
    git_base_name: str = "master"
    repository: str = ""

    class Config:  # pylint: disable=too-few-public-methods
        """
        BaseSettings' config describing how the settings will be handled.
        The given ``env_prefix`` will make sure that settings can be read from
        environment variables starting with ``HAMMURABI_``.
        """

        env_prefix = "hammurabi_"


class TOMLSettings(CommonSettings):
    """
    TOML Project configuration settings. Most of the fields
    are used to compose other configuration fields like
    ``github_token`` or ``pillar``.
    """

    github_token: str = ""
    log_level: str = "INFO"
    pillar_config: Path
    pillar_name: str = "pillar"
    target: Path


class Settings(CommonSettings):
    """
    CLI related settings which are directly needed for the
    execution.
    """

    pillar: object = None
    working_dir: Path = Path(".")


class Config:
    """
    Simple configuration object which used across Hammurabi.
    The :class:`Config` loads the given ``pyproject.toml`` according
    to PEP-518.
    """

    def __init__(self):
        self.__repo: Repo = None
        self.github: Optional[GitHub] = None
        self.settings: Settings = Settings()

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

        self.settings.working_dir = repository.absolute()
        os.chdir(str(self.settings.working_dir))

        self.__repo = Repo(self.settings.working_dir)

    @staticmethod
    def __load_pyproject_toml(config_file: Path) -> TOMLSettings:
        """
        Load and parse the given ``pyproject.toml`` file.

        :param config_file: Path of the pyproject.toml file
        :type config_file: Path

        :return: Returns the parsed configuration
        :rtype: :class:`hammurabi.config.TOMLSettings`
        """

        return TOMLSettings(
            **toml.load(config_file).get("tool", {}).get("hammurabi", {})
        )

    @staticmethod
    def __load_pillar_config(project_config: TOMLSettings) -> object:
        """
        Load ``pillar`` configuration based on the dotted style path in the
        ``pyproject.toml``, set by ``config`` configuration section.

        :param project_config: Parsed TOMLSettings
        :type project_config: :class:`hammurabi.config.TOMLSettings`

        :return: Returns the initialized :class:`hammurabi.pillar.Pillar`
        :rtype: :class:`pydantic.PyObject`
        """

        # Pillar configuration file
        pillar_config = Path(project_config.pillar_config).expanduser()

        # Load the configuration from pillar config module to runtime
        spec = spec_from_file_location(
            pillar_config.name.replace(".py", ""), pillar_config
        )

        module = module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore

        # Pillar config variable name
        return getattr(module, project_config.pillar_name)

    @staticmethod
    def __get_settings_value(parameter: str, fallback: Any) -> Any:
        """
        Get a specific setting parameter's value. This helper function
        will prefer environment variables over the fallback value, to
        keep the configuration order.

        :param parameter: Name of the setting
        :type parameter: str

        :param fallback: Value set in the configuration file
        :type fallback: Any

        :return: Returns the value read from environment or config file
        :rtype: Any
        """

        prefix = Settings.Config.env_prefix
        return os.environ.get(f"{prefix}{parameter}", fallback)

    def __merge_settings(self, loaded_settings: Dict[str, Any]) -> Settings:
        """
        Merge the configuration parsed from pyproject.toml and set by
        environment variables. To keep the configuration loading order,
        the environment settings will be used over those found in the
        TOML file.

        Config priority:

            1. CLI arguments
            2. ENV Variables
            3. Config from file
            4. Default config

        :param loaded_settings:
        :type loaded_settings: Dict[str, Any]
        """

        merge_result = {}

        for setting, value in loaded_settings.items():
            merge_result[setting] = self.__get_settings_value(setting, value)

        return Settings(**merge_result)

    def load(self, file: Union[str, Path]):
        """
        Handle configuration loading from project toml file and make sure
        the configuration are initialized and merged. Also, make sure that
        logging is set properly.

        :param file: Path of the ``pyproject.toml`` file
        :type file:  Union[str, Path]
        """

        # Hammurabi CLI configuration file
        toml_file = Path(file).expanduser()
        project_config = self.__load_pyproject_toml(toml_file)

        # Merge settings and make sure we keep config priority
        # Override the default settings by the merged ones
        self.settings = self.__merge_settings(
            {
                "pillar": self.__load_pillar_config(project_config),
                "git_base_name": project_config.git_base_name,
                "git_branch_name": project_config.git_branch_name,
                "dry_run": project_config.dry_run,
                "rule_can_abort": project_config.rule_can_abort,
                "repository": project_config.repository,
            }
        )

        # Set after self.settings is set since the following
        # may depend on settings read from environment or config file
        self.github = login(project_config.github_token)
        self.repo = project_config.target

        # Set logging
        logging.root.setLevel(project_config.log_level)

        logging.debug('Successfully loaded "%s"', toml_file)
        logging.debug(
            'Successfully loaded "%s"', project_config.pillar_config.absolute()
        )


config = Config()  # pylint: disable=invalid-name
