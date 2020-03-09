import tempfile

import pytest


@pytest.fixture
def temporary_file():
    return tempfile.NamedTemporaryFile(delete=False)
