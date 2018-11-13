import pytest

from muscle_manager.instance_registry import InstanceRegistry
from muscle_manager.logger import Logger
from muscle_manager.mmp_server import MMPServicer


@pytest.fixture
def logger():
    return Logger()


@pytest.fixture
def instance_registry():
    return InstanceRegistry()


@pytest.fixture
def mmp_servicer(logger, instance_registry):
    return MMPServicer(logger, instance_registry)
