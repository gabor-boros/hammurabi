import tempfile

import pytest


@pytest.fixture
def temporary_file():
    return tempfile.NamedTemporaryFile(delete=False)


@pytest.fixture
def temporary_dir():
    return tempfile.mkdtemp()


@pytest.fixture
def temporary_file_generator():
    def return_file(suffix: str = ""):
        return tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

    return return_file
