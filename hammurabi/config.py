# pylint: disable=too-few-public-methods

from importlib.util import module_from_spec, spec_from_file_location
import logging
import os
from pathlib import Path
import re
from typing import Any, Dict, Optional

from git import InvalidGitRepositoryError, Repo
from github3 import GitHub, login
from pydantic import BaseSettings
import toml


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
    report_name: Path = Path("hammurabi_report.json")

    class Config:
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
    pillar_config: Path = Path("pillar.conf.py")
    pillar_name: str = "pillar"


class Settings(CommonSettings):
    """
    CLI related settings which are directly needed for the
    execution.
    """

    pillar: object = None


class Config:
    """
    Simple configuration object which used across Hammurabi.
    The :class:`Config` loads the given ``pyproject.toml`` according
    to PEP-518.

    .. warning::

        When trying to use GitHub based laws without an initialized GitHub
        client (or invalid token), a warning will be thrown at the beginning
        of the execution. In case a PR open is attempted, a ``RuntimeError``
        will be raised
    """

    def __init__(self) -> None:
        try:
            repo = Repo(self.__get_repo_path())
        except InvalidGitRepositoryError as exc:
            logging.error('"%s" is not a git repository', str(exc))
            repo = None

        self.repo: Repo = repo
        self.github: Optional[GitHub] = None
        self.settings: Settings = Settings()

    @staticmethod
    def __get_repo_path() -> Path:
        """
        Get repository path which is the current working directory.
        :return: Current working directory where Hammurabi is executed
        :rtype: Path
        """

        return Path(".").absolute()

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
        pillar_config = project_config.pillar_config.expanduser()

        # Load the configuration from pillar config module to runtime
        spec = spec_from_file_location(
            pillar_config.name.replace(".py", ""), os.path.expandvars(pillar_config)
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

            1. CLI arguments (set by the CLI)
            2. ENV Variables (handled by pydantic settings)
            3. Config from file (handled by ``Config`` object)
            4. Default config (handled by pydantic settings)

        :param loaded_settings:
        :type loaded_settings: Dict[str, Any]
        """

        merge_result = {}

        for setting, value in loaded_settings.items():
            merge_result[setting] = self.__get_settings_value(setting, value)

        return Settings(**merge_result)

    def __get_fallback_repository(self) -> str:
        """
        Figure out the fallback owner/repository based on the remote url of the git repo.
        :return: Returns the owner/repository pair
        :rtype: str
        """

        repo_url: str = self.repo.remote().url

        if re.match(r"^http(s)?://", repo_url):
            repo = "/".join(repo_url.split("/")[-2:])
        else:
            repo = repo_url.split(":")[-1]

        return repo.replace(".git", "")

    def load(self):
        """
        Handle configuration loading from project toml file and make sure
        the configuration are initialized and merged. Also, make sure that
        logging is set properly. Before loading the configuration, it is a
        requirement to set the ``HAMMURABI_SETTINGS_PATH`` as it will contain
        the path to the ``toml`` file what Hammurabi expects. This is needed
        for cases when the 3rd party rules would like to read the configuration
        of Hammurabi.

        ... note:

            The ``HAMMURABI_SETTINGS_PATH`` environment variable is set by the CLI
            by default, so there is no need to set if no 3rd party rules are used
            or those rules are not loading config.

        :raises: Runtime error if ``HAMMURABI_SETTINGS_PATH`` environment variable is not
                 set or an invalid git repository was given.

        """

        if not self.repo:
            raise RuntimeError(f'"{self.__get_repo_path()}" is not a git repository.')

        settings_path = Path(
            os.path.expandvars(
                os.environ.get("HAMMURABI_SETTINGS_PATH", "pyproject.toml")
            )
        ).expanduser()

        if not settings_path.exists():
            raise RuntimeError(
                f'Environment variable "HAMMURABI_SETTINGS_PATH" ({settings_path}) '
                "does not exists. Please make sure that you set the environment variable "
                "or CLI ``-c/--config`` flag properly. You must either define the"
                "environment variable or use hammurabi as a CLI tool."
            )

        # Hammurabi CLI configuration file
        project_config = self.__load_pyproject_toml(settings_path)

        # Merge settings and make sure we keep config priority
        # Override the default settings by the merged ones
        self.settings = self.__merge_settings(
            {
                "pillar": self.__load_pillar_config(project_config),
                "git_base_name": project_config.git_base_name,
                "git_branch_name": project_config.git_branch_name,
                "dry_run": project_config.dry_run,
                "rule_can_abort": project_config.rule_can_abort,
                "report_name": project_config.report_name,
            }
        )

        if not project_config.repository:
            self.settings.repository = self.__get_fallback_repository()

        # Set after self.settings is set since the following
        # may depend on settings read from environment or config file
        self.github = login(token=project_config.github_token)

        # Set logging
        logging.root.setLevel(project_config.log_level)

        logging.debug('Successfully loaded "%s"', settings_path)
        logging.debug(
            'Successfully loaded "%s"', project_config.pillar_config.expanduser()
        )

        if not self.github:
            logging.warning(
                "GitHub client is not initialized. Missing or invalid token."
            )


config = Config()  # pylint: disable=invalid-name
