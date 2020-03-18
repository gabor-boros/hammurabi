from hammurabi.rules.common import SinglePathRule as SinglePathRule
from pathlib import Path
from typing import Any, Optional

class Moved(SinglePathRule):
    destination: Any = ...
    def __init__(self, name: str, path: Optional[Path]=..., destination: Optional[Path]=..., **kwargs: Any) -> Any: ...
    def post_task_hook(self) -> None: ...
    def task(self) -> Path: ...

class Renamed(Moved):
    def __init__(self, name: str, path: Optional[Path]=..., new_name: Optional[str]=..., **kwargs: Any) -> Any: ...

class Copied(SinglePathRule):
    destination: Any = ...
    def __init__(self, name: str, path: Optional[Path]=..., destination: Optional[Path]=..., **kwargs: Any) -> Any: ...
    def post_task_hook(self) -> None: ...
    def task(self) -> Path: ...