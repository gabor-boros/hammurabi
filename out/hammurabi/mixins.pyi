from github3.repos.repo import Repository as Repository
from hammurabi.config import config as config
from pathlib import Path
from typing import Any

class GitMixin:
    @staticmethod
    def checkout_branch() -> None: ...
    made_changes: bool = ...
    def git_add(self, param: Path) -> Any: ...
    def git_remove(self, param: Path) -> Any: ...
    @staticmethod
    def git_commit(message: str) -> Any: ...
    @staticmethod
    def push_changes() -> None: ...

class GitHubMixin(GitMixin):
    @staticmethod
    def generate_pull_request_body(pillar: Any) -> str: ...
    def create_pull_request(self) -> None: ...