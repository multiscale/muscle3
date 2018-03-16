import pytest

from muscle_manager.logger import Logger


@pytest.fixture
def logger():
    return Logger()
