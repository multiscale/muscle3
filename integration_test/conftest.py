import pytest

import include_libmuscle

from muscle_manager.instance_registry import InstanceRegistry
from muscle_manager.logger import Logger
from muscle_manager.mmp_server import MMPServer


@pytest.fixture
def mmp_server(tmpdir):
    logger = Logger()
    instance_registry = InstanceRegistry()
    server = MMPServer(logger, instance_registry)
    yield server
    server.stop()
