"""
This module adds YAML file support. YAML module is an extension for text rules
tailor made for .yaml/.yml files. The main difference lies in the way it works.
First, the .yaml/.yml file is parsed, then the modifications are made on the
already parsed file.
"""

from abc import abstractmethod
from pathlib import Path
from typing import Any, Optional

from ruamel.yaml import YAML

from hammurabi.rules.dictionaries import (
    DictKeyExists,
    DictKeyNotExists,
    DictKeyRenamed,
    DictValueExists,
    DictValueNotExists,
    SinglePathDictParsedRule,
)


class SingleDocumentYAMLFileRule(SinglePathDictParsedRule):
    """
    Extend :class:`hammurabi.rules.dictionaries.SinglePathDictParsedRule`
    to handle parsed content manipulations on a single YAML file.
    """

    def __init__(
        self, name: str, path: Optional[Path] = None, key: str = "", **kwargs
    ) -> None:
        self.yaml = YAML()
        self.yaml.default_flow_style = False

        super().__init__(name, path, key, loader=self.yaml.load, **kwargs)

    def _write_dump(self, data: Any, delete: bool = False) -> None:
        """
        Helper function to write the dump into file.

        :param data: The modified data
        :type data: :class:``hammurabi.rules.mixins.Any`

        :param delete: Indicate if the key should be deleted
        :type delete: bool
        """

        self.param: Path

        self.yaml.dump(
            self.set_by_selector(self.loaded_data, self.split_key, data, delete),
            self.param,
        )

    @abstractmethod
    def task(self) -> Path:
        """
        Abstract method representing how a :func:`hammurabi.rules.base.Rule.task`
        must be parameterized. Any difference in the parameters will result in
        pylint/mypy errors.

        For more details please check :func:`hammurabi.rules.base.Rule.task`.
        """


class YAMLKeyExists(DictKeyExists, SingleDocumentYAMLFileRule):
    """
    Ensure that the given key exists. If needed, the rule will create a key with the
    given name, and optionally the specified value. In case the value is set, the value
    will be assigned to the key. If no value is set, the key will be created with an empty
    value.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, YAMLKeyExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         YAMLKeyExists(
        >>>             name="Ensure service descriptor has stack",
        >>>             path=Path("./service.yaml"),
        >>>             key="stack",
        >>>             value="my-awesome-stack",
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)

    .. warning::

        Compared to :mod:`hammurabi.rules.text.LineExists`, this rule is NOT able to add a
        key before or after a target.
    """


class YAMLKeyNotExists(DictKeyNotExists, SingleDocumentYAMLFileRule):
    """
    Ensure that the given key not exists. If needed, the rule will remove a key with the
    given name, including its value.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, YAMLKeyNotExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         YAMLKeyNotExists(
        >>>             name="Ensure outdated_key is removed",
        >>>             path=Path("./service.yaml"),
        >>>             key="outdated_key",
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """


class YAMLKeyRenamed(DictKeyRenamed, SingleDocumentYAMLFileRule):
    """
    Ensure that the given key is renamed. In case the key can not be found,
    a ``LookupError`` exception will be raised to stop the execution. The
    execution must be stopped at this point, because if other rules depending
    on the rename they will fail otherwise.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, YAMLKeyRenamed
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         YAMLKeyRenamed(
        >>>             name="Ensure service descriptor has dependencies",
        >>>             path=Path("./service.yaml"),
        >>>             key="development.depends_on",
        >>>             value="dependencies",
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """


class YAMLValueExists(DictValueExists, SingleDocumentYAMLFileRule):
    """
    Ensure that the given key has the expected value(s). In case the key cannot
    be found, a ``LookupError`` exception will be raised to stop the execution.

    This rule is special in the way that the value can be almost anything. For
    more information please read the warning below.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, YAMLValueExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         YAMLValueExists(
        >>>             name="Ensure service descriptor has dependencies",
        >>>             path=Path("./service.yaml"),
        >>>             key="development.dependencies",
        >>>             value=["service1", "service2", "service3"],
        >>>         ),
        >>>         # Or
        >>>         YAMLValueExists(
        >>>             name="Add infra alerting to existing alerting components",
        >>>             path=Path("./service.yaml"),
        >>>             key="development.alerting",
        >>>             value={"infra": "#slack-channel-2"},
        >>>         ),
        >>>         # Or
        >>>         YAMLValueExists(
        >>>             name="Add support info",
        >>>             path=Path("./service.yaml"),
        >>>             key="development.supported",
        >>>             value=True,
        >>>         ),
        >>>         # Or even
        >>>         YAMLValueExists(
        >>>             name="Make sure that no development branch is set",
        >>>             path=Path("./service.yaml"),
        >>>             key="development.branch",
        >>>             value=None,
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)

    .. warning::

        Since the value can be anything from ``None`` to a list of lists, and
        rule piping passes the 1st argument (``path``) to the next rule the ``value``
        parameter can not be defined in ``__init__`` before the ``path``. Hence
        the ``value`` parameter must have a default value. The default value is
        set to ``None``, which translates to the following:

        Using the ``YAMLValueExists`` rule and not assigning value to ``value``
        parameter will set the matching ``key``'s value to `None`` by default in
        the document.
    """


class YAMLValueNotExists(DictValueNotExists, SingleDocumentYAMLFileRule):
    """
    Ensure that the key has no value given. In case the key cannot be found,
    a ``LookupError`` exception will be raised to stop the execution.

    Compared to ``hammurabi.rules.yaml.YAMLValueExists``, this rule can only
    accept simple value for its ``value`` parameter. No ``list``, ``dict``, or
    ``None`` can be used.

    Based on the key's value's type if the value contains (or equals for simple types)
    value provided in the ``value`` parameter the value is:

    1. Set to None (if the key's value's type is not a dict or list)
    2. Removed from the list (if the key's value's type is a list)
    3. Removed from the dict (if the key's value's type is a dict)

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, YAMLValueNotExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         YAMLValueNotExists(
        >>>             name="Remove decommissioned service from dependencies",
        >>>             path=Path("./service.yaml"),
        >>>             key="development.dependencies",
        >>>             value="service4",
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """
