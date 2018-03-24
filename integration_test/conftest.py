import pytest

import include_libmuscle

from muscle_manager.logger import Logger
from muscle_manager.mmp_server import MMPServer


@pytest.fixture
def mmp_server(tmpdir):
    logger = Logger()
    server = MMPServer(logger)
    yield server
    server.stop()
