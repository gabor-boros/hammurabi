from hammurabi.rules.common import SinglePathRule as SinglePathRule
from pathlib import Path
from typing import Any, List, Optional, Tuple

class LineExists(SinglePathRule):
    text: Any = ...
    criteria: Any = ...
    target: Any = ...
    position: Any = ...
    respect_indentation: Any = ...
    indentation_pattern: Any = ...
    def __init__(self, name: str, path: Optional[Path]=..., text: Optional[str]=..., criteria: Optional[str]=..., target: Optional[str]=..., position: int=..., respect_indentation: bool=..., **kwargs: Any) -> Any: ...
    def __get_target_match(self, lines: List[str]) -> str: ...
    def __get_lines_from_file(self) -> Tuple[List[str], bool]: ...
    def __write_content_to_file(self, lines: List[str]) -> Any: ...
    def task(self) -> Path: ...

class LineNotExists(SinglePathRule):
    text: Any = ...
    def __init__(self, name: str, path: Optional[Path]=..., text: Optional[str]=..., **kwargs: Any) -> Any: ...
    def task(self) -> Path: ...

class LineReplaced(SinglePathRule):
    text: Any = ...
    target: Any = ...
    respect_indentation: Any = ...
    indentation_pattern: Any = ...
    def __init__(self, name: str, path: Optional[Path]=..., text: Optional[str]=..., target: Optional[str]=..., respect_indentation: bool=..., **kwargs: Any) -> Any: ...
    def __get_target_match(self, lines: List[str]) -> List[str]: ...
    def __get_lines_from_file(self) -> Tuple[List[str], bool]: ...
    def __write_content_to_file(self, lines: List[str]) -> Any: ...
    def __replace_line(self, lines: List[str], target: str) -> Any: ...
    def task(self) -> Path: ...
