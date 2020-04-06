"""
This module adds YAML file support. YAML module is an extension for text rules
tailor made for .yaml/.yml files. The main difference lies in the way it works.
First, the .yaml/.yml file is parsed, then the modifications are made on the
already parsed file.
"""

from abc import abstractmethod
from copy import deepcopy
import logging
from pathlib import Path
from typing import Any, Dict, Hashable, List, Optional, Union

from ruamel.yaml import YAML

from hammurabi.rules.common import SinglePathRule
from hammurabi.rules.mixins import SelectorMixin


class SingleDocumentYAMLFileRule(SinglePathRule, SelectorMixin):
    """
    Extend :class:`hammurabi.rules.base.Rule` to handle parsed content
    manipulations on a single file.
    """

    def __init__(
        self, name: str, path: Optional[Path] = None, key: str = "", **kwargs
    ) -> None:
        self.yaml = YAML()
        self.yaml.default_flow_style = False

        self.selector = self.validate(key, required=True)
        self.split_key = self.selector.split(".")
        self.key_name: str = self.split_key[-1]
        self.loaded_yaml = Union[Dict[Hashable, Any], List[Any], None]

        super().__init__(name, path, **kwargs)

    def _get_parent(self) -> Dict[str, Any]:
        """
        Get the parent of the given key by its selector.

        :return: Return the parent if there is any
        :rtype: Dict[str, Any]
        """

        # Get the parent for modifications. If there is no parent,
        # then the parent is the document root
        return self.get_by_selector(self.loaded_yaml, self.split_key[:-1])

    def _write_dump(self, data: Any, delete: bool = False) -> None:
        """
        Helper function to write the dump into file.

        :param data: The modified data
        :type data: :class:``hammurabi.rules.mixins.Any`

        :param delete: Indicate if the key should be deleted
        :type delete: bool
        """

        updated_data = self.set_by_selector(
            self.loaded_yaml, self.split_key, data, delete
        )
        self.yaml.dump(updated_data, self.param)

    def pre_task_hook(self) -> None:
        """
        Parse the yaml file for later use.
        """

        logging.debug('parsing "%s" yaml file', self.param)
        self.loaded_yaml = self.yaml.load(self.param)

    @abstractmethod
    def task(self) -> Path:
        """
        Abstract method representing how a :func:`hammurabi.rules.base.Rule.task`
        must be parameterized. Any difference in the parameters will result in
        pylint/mypy errors.

        For more details please check :func:`hammurabi.rules.base.Rule.task`.
        """


class YAMLKeyExists(SingleDocumentYAMLFileRule):
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

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        key: str = "",
        value: Union[None, list, dict, str, int, float] = None,
        **kwargs,
    ) -> None:
        self.value = value
        super().__init__(name, path, key, **kwargs)

    def task(self) -> Path:
        """
        Ensure that the given key exists in the yaml file. If needed, create the
        key with the given name, and optionally the specified value.

        :return: Return the input path as an output
        :rtype: Path
        """

        parent = self._get_parent()
        inserted = parent.setdefault(self.key_name, self.value)

        # Only write the changes if we did any change
        if inserted == parent[self.key_name]:
            self._write_dump(inserted)

        return self.param


class YAMLKeyNotExists(SingleDocumentYAMLFileRule):
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

    def task(self) -> Path:
        """
        Ensure that the given key does not exists in the yaml file.

        :return: Return the input path as an output
        :rtype: Path
        """

        parent = self._get_parent()

        if self.key_name in parent.keys():
            parent.pop(self.key_name)
            self._write_dump(parent, delete=True)

        return self.param


class YAMLKeyRenamed(SingleDocumentYAMLFileRule):
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

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        key: str = "",
        new_name: str = "",
        **kwargs,
    ) -> None:
        self.new_name = self.validate(new_name, required=True)
        super().__init__(name, path, key, **kwargs)

    def task(self) -> Path:
        """
        Ensure that the given key is renamed. In case the key can not be found,
        a ``LookupError`` exception will be raised to stop the execution. The
        execution must be stopped at this point, because if other rules depending
        on the rename they will fail otherwise.

        :raises: ``LookupError`` raised if no key can be renamed or both the new and
                 old keys are in the config file
        :return: Return the input path as an output
        :rtype: Path
        """

        parent = self._get_parent()

        has_old_key = self.key_name in parent
        has_new_key = self.new_name in parent

        if has_old_key and has_new_key:
            raise LookupError(f'Both "{self.key_name}" and "{self.new_name}" set')

        if has_new_key:
            return self.param

        if not has_old_key:
            raise LookupError(f'No matching key for "{self.selector}"')

        parent[self.new_name] = deepcopy(parent[self.key_name])
        parent.pop(self.key_name)

        # Delete is True since we need to delete the old key
        self._write_dump(parent, delete=True)

        return self.param


class YAMLValueExists(SingleDocumentYAMLFileRule):
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

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        key: str = "",
        value: Union[None, list, dict, str, int, float] = None,
        **kwargs,
    ) -> None:
        self.value = value
        super().__init__(name, path, key, **kwargs)

    def task(self) -> Path:
        """
        Ensure that the given key has the expected value(s). In case the key cannot
        be found, a ``LookupError`` exception will be raised to stop the execution.

        .. warning::

            Since the value can be anything from ``None`` to a list of lists, and
            rule piping passes the 1st argument (``path``) to the next rule the ``value``
            parameter can not be defined in ``__init__`` before the ``path``. Hence
            the ``value`` parameter must have a default value. The default value is
            set to ``None``, which translates to the following:

            Using the ``YAMLValueExists`` rule and not assigning value to ``value``
            parameter will set the matching ``key``'s value to `None`` by default in
            the document.

        :raises: ``LookupError`` raised if no key can be renamed or both the new and
                 old keys are in the config file
        :return: Return the input path as an output
        :rtype: Path
        """

        parent = self._get_parent()

        if self.value is None:
            parent[self.key_name] = self.value
        elif isinstance(parent.get(self.key_name), list):
            if isinstance(self.value, list):
                parent[self.key_name].extend(self.value)
            else:
                parent[self.key_name].append(self.value)
        elif isinstance(parent.get(self.key_name), dict):
            parent[self.key_name].update(self.value)
        else:
            parent[self.key_name] = self.value

        self._write_dump(parent[self.key_name])
        return self.param


class YAMLValueNotExists(SingleDocumentYAMLFileRule):
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

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        key: str = "",
        value: Union[str, int, float] = None,
        **kwargs,
    ) -> None:
        self.value = self.validate(value, required=True)
        super().__init__(name, path, key, **kwargs)

    def task(self) -> Path:
        """
        Ensure that the key has no value given. In case the key cannot be found,
        a ``LookupError`` exception will be raised to stop the execution.

        Based on the key's value's type if the value contains (or equals for simple types)
        value provided in the ``value`` parameter the value is:
        1. Set to None (if the key's value's type is not a dict or list)
        2. Removed from the list (if the key's value's type is a list)
        3. Removed from the dict (if the key's value's type is a dict)

        :return: Return the input path as an output
        :rtype: Path
        """

        parent = self._get_parent()
        write_needed = False

        if self.key_name not in parent:
            return self.param

        current_value = parent.get(self.key_name)

        if isinstance(current_value, list):
            if self.value in current_value:
                parent[self.key_name].remove(self.value)
                write_needed = True
        elif isinstance(current_value, dict):
            if self.value in current_value:
                del parent[self.key_name][self.value]
                write_needed = True
        else:
            if current_value == self.value:
                parent[self.key_name] = None
                write_needed = True

        if write_needed:
            self._write_dump(parent[self.key_name])

        return self.param
