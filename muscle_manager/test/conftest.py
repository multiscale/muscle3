import pytest

from muscle_manager.logger import Logger
from muscle_manager.mmp_server import MMPServicer


@pytest.fixture
def logger():
    return Logger()


@pytest.fixture
def mmp_servicer(logger):
    return MMPServicer(logger)
