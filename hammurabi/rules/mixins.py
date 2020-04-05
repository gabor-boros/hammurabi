from typing import Any, Dict, List, Union


class SelectorMixin:  # pylint: disable=too-few-public-methods
    """
    This mixin contains the helper function to get a value from dict by
    a css selector like selector path. (``.example.path.to.key``)
    """

    @staticmethod
    def __normalize_key_path(key_path: Union[str, List[str]]) -> List[str]:
        """
        Normalize the key_path and make sure we return the list
        representation of it.

        :param key_path: Path to the key in a selector format
            (``.path.to.the.key`` or ``["path", "to", "the", "key"]``)
        :type key_path: Union[str, List[str]]

        :return: List representation of key type
        :rtype: List[str]
        """

        if isinstance(key_path, str):
            key_path = key_path.split(".")

        return list(filter(lambda key: key, key_path))

    def get_by_selector(
        self, data: Any, key_path: Union[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Get a key's value by a selector and traverse the path.

        :param data: The loaded YAML data into dict
        :type data: :class:`hammurabi.rules.mixins.Any`

        :param key_path: Path to the key in a selector format
            (``.path.to.the.key`` or ``["path", "to", "the", "key"]``)
        :type key_path: Union[str, List[str]]

        :return: Return the value belonging to the selector
        :rtype: :class:`hammurabi.rules.mixins.Any`
        """

        if not data:
            return dict()

        key_path = self.__normalize_key_path(key_path)
        entry = data or dict()

        for item in key_path:
            entry = entry.get(item, None)
            if not entry:
                return dict()

        return entry

    def set_by_selector(
        self,
        loaded_data: Any,
        key_path: Union[str, List[str]],
        value: Union[None, list, dict, str, int, float],
        delete: bool = False,
    ) -> Any:
        """
        Set a value by the key selector and traverse the path.

        :param loaded_data: The loaded YAML data into dict
        :type loaded_data: :class:`hammurabi.rules.mixins.Any`

        :param key_path: Path to the key in a selector format
            (``.path.to.the.key`` or ``["path", "to", "the", "key"]``)
        :type key_path: Union[str, List[str]]

        :param value: The value set for the key
        :type value: Union[None, list, dict, str, int, float]

        :param delete: Indicate if the key should be deleted
        :type delete: bool

        :return: The modified YAML data
        :rtype: :class:`hammurabi.rules.mixins.Any`
        """

        key_path = self.__normalize_key_path(key_path)
        data: Dict[str, Any] = loaded_data or dict()

        entry = data

        for item in key_path[:-1]:
            current = entry.get(item)

            if current and not isinstance(current, dict):
                entry[item] = {}

            entry = entry.setdefault(item, {})

        if not delete:
            entry[key_path[-1]] = value

        return data
