from pathlib import Path
from typing import Iterable
from unittest.mock import Mock, call

from hammurabi.rules.common import MultiplePathRule, SinglePathRule


class ExampleSingleFileRule(SinglePathRule):
    def task(self) -> Path:
        return self.param


class ExampleMultipleFilesRule(MultiplePathRule):
    def task(self) -> Iterable[Path]:
        return self.param


def test_single_file_rule():
    """
    Since SingleFileRule's base classes are tested from
    different angles, the only valuable thing to test on the
    class is that the post_task hook does what we expect.
    """

    expected_param = Path("test/path")

    rule = ExampleSingleFileRule(name="Single file base rule", path=expected_param)

    rule.git_add = Mock()
    rule.post_task_hook()

    rule.git_add.assert_called_once_with(expected_param)


def test_multiple_files_rule():
    """
    Since MultipleFilesRule's base classes are tested from
    different angles, the only valuable thing to test on the
    class is that the post_task hook does what we expect.
    """

    expected_path_1 = Path("test/path1")
    expected_path_2 = Path("test/path2")
    expected_param = [expected_path_1, expected_path_2]

    rule = ExampleMultipleFilesRule(
        name="Multiple files base rule", paths=expected_param
    )

    rule.git_add = Mock()
    rule.post_task_hook()

    rule.git_add.has_calls(call(expected_path_1), call(expected_path_2))
