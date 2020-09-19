# flake8: noqa
import logging

from hammurabi.config import config
from hammurabi.law import Law
from hammurabi.notifications.base import Notification
from hammurabi.pillar import Pillar
from hammurabi.preconditions.attributes import (
    HasMode,
    HasNoMode,
    IsNotOwnedBy,
    IsOwnedBy,
)
from hammurabi.preconditions.base import Precondition
from hammurabi.preconditions.directories import IsDirectoryExist, IsDirectoryNotExist
from hammurabi.preconditions.files import IsFileExist, IsFileNotExist
from hammurabi.preconditions.text import IsLineExist, IsLineNotExist
from hammurabi.reporters.base import Reporter
from hammurabi.reporters.json import JsonReporter
from hammurabi.rules.attributes import ModeChanged, OwnerChanged
from hammurabi.rules.base import Rule
from hammurabi.rules.directories import (
    DirectoryEmptied,
    DirectoryExists,
    DirectoryNotExists,
)
from hammurabi.rules.files import (
    FileEmptied,
    FileExists,
    FileNotExists,
    FilesExist,
    FilesNotExist,
)
from hammurabi.rules.json import (
    JsonKeyExists,
    JsonKeyNotExists,
    JsonKeyRenamed,
    JsonValueExists,
    JsonValueNotExists,
)
from hammurabi.rules.operations import Copied, Moved, Renamed
from hammurabi.rules.templates import TemplateRendered
from hammurabi.rules.text import LineExists, LineNotExists, LineReplaced
from hammurabi.rules.toml import (
    TomlKeyExists,
    TomlKeyNotExists,
    TomlKeyRenamed,
    TomlValueExists,
    TomlValueNotExists,
)

try:
    from hammurabi.notifications.slack import SlackNotification
except ImportError:
    logging.debug("import of slack notification is skipped")


try:
    from hammurabi.rules.ini import (
        OptionRenamed,
        OptionsExist,
        OptionsNotExist,
        SectionExists,
        SectionNotExists,
        SectionRenamed,
    )
except ImportError:
    logging.debug("import of ini file based rules is skipped")


try:
    from hammurabi.rules.yaml import (
        YamlKeyExists,
        YamlKeyNotExists,
        YamlKeyRenamed,
        YamlValueExists,
        YamlValueNotExists,
    )
except ImportError:
    logging.debug("import of yaml file based rules is skipped")

__version__ = "0.11.0"
