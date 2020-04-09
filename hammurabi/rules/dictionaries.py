"""
Extend :class:`hammurabi.rules.base.Rule` to handle parsed content manipulations dictionaries.
Standalone these rules are not useful, but they are very handy when files should be manipulated
like YAML or JSON which will be parsed as dict.

These rules are intentionally not exported directly through hammurabi as it is done for YAML or
JSON rules. The reason, as it is mentioned above, these rules are not standalone rules. Also, it
is intentional that these rules are not represented in the documentation's `Rules section`_.

.. _`Rules section`: https://hammurabi.readthedocs.io/en/latest/rules.html
"""

from abc import ABC, abstractmethod
from copy import deepcopy
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Hashable, List, Optional, Union

from hammurabi.rules.common import SinglePathRule
from hammurabi.rules.mixins import SelectorMixin


class SinglePathDictParsedRule(SinglePathRule, SelectorMixin):
    """
    Extend :class:`hammurabi.rules.base.Rule` to handle parsed content
    manipulations dictionaries. Standalone this rule is not useful, but
    it is very handy when files should be manipulated like YAML or
    JSON which will be parsed as dict. This rule ensures that the implementation
    will be the same for these rules, so the maintenance cost and effort
    is reduced.

    Although this rule is not that powerful on its own, we would not
    like to make it an abstract class like :class:`hammurabi.rules.base.Rule`
    because it can easily happen that at some point this rule will be
    a standalone rule.
    """

    def __init__(
        self,
        name: str,
        path: Optional[Path] = None,
        key: str = "",
        loader: Callable[[Any], Dict[str, Any]] = dict,
        **kwargs,
    ) -> None:
        self.selector = self.validate(key, required=True)
        self.split_key = self.selector.split(".")
        self.key_name: str = self.split_key[-1]
        self.loaded_data = Union[Dict[Hashable, Any], List[Any], None]
        self.loader = loader

        super().__init__(name, path, **kwargs)

    def _get_parent(self) -> Dict[str, Any]:
        """
        Get the parent of the given key by its selector.

        :return: Return the parent if there is any
        :rtype: Dict[str, Any]
        """

        # Get the parent for modifications. If there is no parent,
        # then the parent is the document root
        return self.get_by_selector(self.loaded_data, self.split_key[:-1])

    def _write_dump(self, data: Any, delete: bool = False) -> None:
        """
        This is a dummy class which should be overridden. This method
        does nothing.

        :param data: The modified data
        :type data: :class:``hammurabi.rules.mixins.Any`

        :param delete: Indicate if the key should be deleted
        :type delete: bool
        """

    def pre_task_hook(self) -> None:
        """
        Parse the file for later use.
        """

        logging.debug('Parsing "%s" file', self.param)
        self.loaded_data = self.loader(self.param.read_text())

    @abstractmethod
    def task(self) -> Path:
        """
        Abstract method representing how a :func:`hammurabi.rules.base.Rule.task`
        must be parameterized. Any difference in the parameters will result in
        pylint/mypy errors.

        For more details please check :func:`hammurabi.rules.base.Rule.task`.
        """


class DictKeyExists(SinglePathDictParsedRule, ABC):
    """
    Ensure that the given key exists. If needed, the rule will create a key with the
    given name, and optionally the specified value. In case the value is set, the value
    will be assigned to the key. If no value is set, the key will be created with an empty
    value.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar
        >>> from hammurabi.rules.dictionaries import DictKeyExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         DictKeyExists(
        >>>             name="Ensure service descriptor has stack",
        >>>             path=Path("./service.dictionary"),
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
        Ensure that the given key exists in the parsed file. If needed, create the
        key with the given name, and optionally the specified value.

        :return: Return the input path as an output
        :rtype: Path
        """

        parent = self._get_parent()

        logging.debug(
            'Set default value "%s" for "%s" if no value set', self.key_name, self.value
        )
        inserted = parent.setdefault(self.key_name, self.value)

        # Only write the changes if we did any change
        if inserted == parent[self.key_name]:
            self._write_dump(inserted)

        return self.param


class DictKeyNotExists(SinglePathDictParsedRule, ABC):
    """
    Ensure that the given key not exists. If needed, the rule will remove a key with the
    given name, including its value.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar
        >>> from hammurabi.rules.dictionaries import DictKeyNotExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         DictKeyNotExists(
        >>>             name="Ensure outdated_key is removed",
        >>>             path=Path("./service.dictionary"),
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
        Ensure that the given key does not exists in the parsed file.

        :return: Return the input path as an output
        :rtype: Path
        """

        parent = self._get_parent()

        if self.key_name in parent.keys():
            logging.debug('Removing key "%s"', self.key_name)
            parent.pop(self.key_name)
            self._write_dump(parent, delete=True)

        return self.param


class DictKeyRenamed(SinglePathDictParsedRule, ABC):
    """
    Ensure that the given key is renamed. In case the key can not be found,
    a ``LookupError`` exception will be raised to stop the execution. The
    execution must be stopped at this point, because if other rules depending
    on the rename they will fail otherwise.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar
        >>> from hammurabi.rules.dictionaries import DictKeyRenamed
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         DictKeyRenamed(
        >>>             name="Ensure service descriptor has dependencies",
        >>>             path=Path("./service.dictionary"),
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

        logging.debug('Renaming key from "%s" to "%s"', self.key_name, self.new_name)
        parent[self.new_name] = deepcopy(parent[self.key_name])
        parent.pop(self.key_name)

        # Delete is True since we need to delete the old key
        self._write_dump(parent, delete=True)

        return self.param


class DictValueExists(SinglePathDictParsedRule, ABC):
    """
    Ensure that the given key has the expected value(s). In case the key cannot
    be found, a ``LookupError`` exception will be raised to stop the execution.

    This rule is special in the way that the value can be almost anything. For
    more information please read the warning below.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar
        >>> from hammurabi.rules.dictionaries import DictValueExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         DictValueExists(
        >>>             name="Ensure service descriptor has dependencies",
        >>>             path=Path("./service.dictionary"),
        >>>             key="development.dependencies",
        >>>             value=["service1", "service2", "service3"],
        >>>         ),
        >>>         # Or
        >>>         DictValueExists(
        >>>             name="Add infra alerting to existing alerting components",
        >>>             path=Path("./service.dictionary"),
        >>>             key="development.alerting",
        >>>             value={"infra": "#slack-channel-2"},
        >>>         ),
        >>>         # Or
        >>>         DictValueExists(
        >>>             name="Add support info",
        >>>             path=Path("./service.dictionary"),
        >>>             key="development.supported",
        >>>             value=True,
        >>>         ),
        >>>         # Or even
        >>>         DictValueExists(
        >>>             name="Make sure that no development branch is set",
        >>>             path=Path("./service.dictionary"),
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

        Using the ``DictValueExists`` rule and not assigning value to ``value``
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

    def _update_simple_value(self, parent: Dict[str, Any]) -> None:
        """
        Update the parent key's value by a simple value.

        :param parent: Parent key of the dict
        :type parent: Dict[str, Any]
        """

        logging.debug('Setting "%s" to "%s"', self.key_name, self.value)
        parent[self.key_name] = self.value

    def _update_list_value(self, parent: Dict[str, Any]) -> None:
        """
        Update the parent key's value which is an array. Depending on the new
        value's type, the exiting list will be extended or the new value will
        be appended to the list.

        :param parent: Parent key of the dict
        :type parent: Dict[str, Any]
        """

        if isinstance(self.value, list):
            logging.debug('Extending "%s" by "%s"', self.key_name, self.value)
            parent[self.key_name].extend(self.value)
        else:
            logging.debug('Appending "%s" to "%s"', self.value, self.key_name)
            parent[self.key_name].append(self.value)

    def _update_dict_value(self, parent: Dict[str, Any]) -> None:
        """
        Update the parent key's value which is a dict.

        :param parent: Parent key of the dict
        :type parent: Dict[str, Any]
        """

        logging.debug('Updating "%s" by "%s"', self.key_name, self.value)
        parent[self.key_name].update(self.value)

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

            Using the ``DictValueExists`` rule and not assigning value to ``value``
            parameter will set the matching ``key``'s value to `None`` by default in
            the document.

        :raises: ``LookupError`` raised if no key can be renamed or both the new and
                 old keys are in the config file
        :return: Return the input path as an output
        :rtype: Path
        """

        parent = self._get_parent()
        value = parent.get(self.key_name)

        is_list_value = isinstance(value, list)
        is_dict_value = isinstance(value, dict)

        logging.debug('Adding value "%s" to key "%s"', self.value, self.key_name)

        if self.value is None or (not is_list_value and not is_dict_value):
            self._update_simple_value(parent)
        elif is_list_value:
            self._update_list_value(parent)
        elif is_dict_value:
            self._update_dict_value(parent)

        self._write_dump(parent[self.key_name])
        return self.param


class DictValueNotExists(SinglePathDictParsedRule, ABC):
    """
    Ensure that the key has no value given. In case the key cannot be found,
    a ``LookupError`` exception will be raised to stop the execution.

    Compared to ``hammurabi.rules.dictionaries.DictValueExists``, this rule can only
    accept simple value for its ``value`` parameter. No ``list``, ``dict``, or
    ``None`` can be used.

    Based on the key's value's type if the value contains (or equals for simple types)
    value provided in the ``value`` parameter the value is:

    1. Set to None (if the key's value's type is not a dict or list)
    2. Removed from the list (if the key's value's type is a list)
    3. Removed from the dict (if the key's value's type is a dict)

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar
        >>> from hammurabi.rules.dictionaries import DictValueNotExists
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         DictValueNotExists(
        >>>             name="Remove decommissioned service from dependencies",
        >>>             path=Path("./service.dictionary"),
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

        value = parent.get(self.key_name)
        value_contains = value and self.value in value

        if self.key_name not in parent:
            return self.param

        write_needed = False
        logging.debug('Removing "%s" from key "%s"', self.value, self.key_name)

        if self.value == value:
            parent[self.key_name] = None
            write_needed = True
        elif isinstance(value, list) and value_contains:
            parent[self.key_name].remove(self.value)
            write_needed = True
        elif isinstance(value, dict) and value_contains:
            del parent[self.key_name][self.value]
            write_needed = True

        if write_needed:
            self._write_dump(parent[self.key_name])

        return self.param
