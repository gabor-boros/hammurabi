"""
This module adds TOML file support. TOML module is an extension for text rules
tailor made for .toml files. The main difference lies in the way it works.
First, the .toml file is parsed, then the modifications are made on the
already parsed file.

.. warning::

    In case of a single line toml file, the parser used in hammurabi will only
    keep the comment if the file contains a newline character.

"""

from abc import abstractmethod
from pathlib import Path
from typing import Any, MutableMapping, Optional

import toml

from hammurabi.rules.dictionaries import (
    DictKeyExists,
    DictKeyNotExists,
    DictKeyRenamed,
    DictValueExists,
    DictValueNotExists,
    SinglePathDictParsedRule,
)


class SingleDocumentTomlFileRule(SinglePathDictParsedRule):
    """
    Extend :class:`hammurabi.rules.dictionaries.SinglePathDictParsedRule`
    to handle parsed content manipulations on a single TOML file.
    """

    def __init__(
        self, name: str, path: Optional[Path] = None, key: str = "", **kwargs
    ) -> None:
        super().__init__(name, path, key, loader=self.__loader, **kwargs)

    @staticmethod
    def __loader(toml_str: str) -> MutableMapping[str, Any]:
        return toml.loads(  # type: ignore
            toml_str, decoder=toml.TomlPreserveCommentDecoder()  # type: ignore
        )

    def _write_dump(self, data: Any, delete: bool = False) -> None:
        """
        Helper function to write the dump into file.

        :param data: The modified data
        :type data: :class:``hammurabi.rules.mixins.Any``

        :param delete: Indicate if the key should be deleted
        :type delete: bool
        """

        # TOML file cannot handle None as value, hence we need to set
        # something for that field if the user forgot to fill the value.

        self.param.write_text(
            toml.dumps(  # type: ignore
                self.set_by_selector(self.loaded_data, self.split_key, data, delete),
                encoder=toml.TomlPreserveCommentEncoder(),  # type: ignore
            )
        )

    @abstractmethod
    def task(self) -> Path:
        """
        Abstract method representing how a :func:`hammurabi.rules.base.Rule.task`
        must be parameterized. Any difference in the parameters will result in
        pylint/mypy errors.

        For more details please check :func:`hammurabi.rules.base.Rule.task`.
        """


class TomlKeyExists(DictKeyExists, SingleDocumentTomlFileRule):
    """
    Ensure that the given key exists. If needed, the rule will create a key with the
    given name, and optionally the specified value. In case the value is set, the value
    will be assigned to the key. If no value is set, the key will be created with an empty
    value.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, TomlKeyExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         TomlKeyExists(
        >>>             name="Ensure service descriptor has stack",
        >>>             path=Path("./service.toml"),
        >>>             key="stack",
        >>>             value="my-awesome-stack",
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)

    .. note::

        The difference between KeyExists and ValueExists rules is the approach and the
        possibilities. While KeyExists is able to create values if provided, ValueExists
        rules are not able to create keys if any of the missing. KeyExists ``value`` parameter
        is a shorthand for creating a key and then adding a value to that key.

    .. warning::

        Setting a value to None will result in a deleted key as per the documentation of how
        null/nil values should be handled. More info: https://github.com/toml-lang/toml/issues/30

    .. warning::

        Compared to :mod:`hammurabi.rules.text.LineExists`, this rule is NOT able to add a
        key before or after a match.
    """


class TomlKeyNotExists(DictKeyNotExists, SingleDocumentTomlFileRule):
    """
    Ensure that the given key not exists. If needed, the rule will remove a key with the
    given name, including its value.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, TomlKeyNotExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         TomlKeyNotExists(
        >>>             name="Ensure outdated_key is removed",
        >>>             path=Path("./service.toml"),
        >>>             key="outdated_key",
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """


class TomlKeyRenamed(DictKeyRenamed, SingleDocumentTomlFileRule):
    """
    Ensure that the given key is renamed. In case the key can not be found,
    a ``LookupError`` exception will be raised to stop the execution. The
    execution must be stopped at this point, because if other rules depending
    on the rename they will fail otherwise.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, TomlKeyRenamed
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         TomlKeyRenamed(
        >>>             name="Ensure service descriptor has dependencies",
        >>>             path=Path("./service.toml"),
        >>>             key="development.depends_on",
        >>>             value="dependencies",
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """


class TomlValueExists(DictValueExists, SingleDocumentTomlFileRule):
    """
    Ensure that the given key has the expected value(s). In case the key cannot
    be found, a ``LookupError`` exception will be raised to stop the execution.

    This rule is special in the way that the value can be almost anything. For
    more information please read the warning below.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, TomlValueExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         TomlValueExists(
        >>>             name="Ensure service descriptor has dependencies",
        >>>             path=Path("./service.toml"),
        >>>             key="development.dependencies",
        >>>             value=["service1", "service2", "service3"],
        >>>         ),
        >>>         # Or
        >>>         TomlValueExists(
        >>>             name="Add infra alerting to existing alerting components",
        >>>             path=Path("./service.toml"),
        >>>             key="development.alerting",
        >>>             value={"infra": "#slack-channel-2"},
        >>>         ),
        >>>         # Or
        >>>         TomlValueExists(
        >>>             name="Add support info",
        >>>             path=Path("./service.toml"),
        >>>             key="development.supported",
        >>>             value=True,
        >>>         ),
        >>>         # Or even
        >>>         TomlValueExists(
        >>>             name="Make sure that no development branch is set",
        >>>             path=Path("./service.toml"),
        >>>             key="development.branch",
        >>>             value=None,
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)

    .. note::

        The difference between KeyExists and ValueExists rules is the approach and the
        possibilities. While KeyExists is able to create values if provided, ValueExists
        rules are not able to create keys if any of the missing. KeyExists ``value`` parameter
        is a shorthand for creating a key and then adding a value to that key.

    .. warning::

        Since the value can be anything from ``None`` to a list of lists, and
        rule piping passes the 1st argument (``path``) to the next rule the ``value``
        parameter can not be defined in ``__init__`` before the ``path``. Hence
        the ``value`` parameter must have a default value. The default value is
        set to ``None``, which translates to the following:

        Using the ``TomlValueExists`` rule and not assigning value to ``value``
        parameter will set the matching ``key``'s value to `None`` by default in
        the document.
    """


class TomlValueNotExists(DictValueNotExists, SingleDocumentTomlFileRule):
    """
    Ensure that the key has no value given. In case the key cannot be found,
    a ``LookupError`` exception will be raised to stop the execution.

    Compared to ``hammurabi.rules.Toml.TomlValueExists``, this rule can only
    accept simple value for its ``value`` parameter. No ``list``, ``dict``, or
    ``None`` can be used.

    Based on the key's value's type if the value contains (or equals for simple types)
    value provided in the ``value`` parameter the value is:

    1. Set to None (if the key's value's type is not a dict or list)
    2. Removed from the list (if the key's value's type is a list)
    3. Removed from the dict (if the key's value's type is a dict)

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, TomlValueNotExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         TomlValueNotExists(
        >>>             name="Remove decommissioned service from dependencies",
        >>>             path=Path("./service.toml"),
        >>>             key="development.dependencies",
        >>>             value="service4",
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """
