import pytest

from muscle_manager.logger import Logger
from muscle_manager.mmp_server import MMPServer


@pytest.fixture
def logger():
    return Logger()


@pytest.fixture
def mmp_server(logger):
    return MMPServer(logger)
