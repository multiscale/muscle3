import sys
from typing import Generator

import pytest

import integration_test.include_libmuscle

from libmuscle.configuration import Configuration
from muscle_manager.instance_registry import InstanceRegistry
from muscle_manager.logger import Logger
from muscle_manager.mmp_server import MMPServer
from muscle_manager.topology_store import TopologyStore


@pytest.fixture
def mmp_server(tmpdir):
    ymmsl_text = (
            'version: v0.1\n'
            'simulation:\n'
            '  name: test_model\n'
            '  compute_elements:\n'
            '    macro: macro_implementation\n'
            '    micro:\n'
            '      implementation: micro_implementation\n'
            '      multiplicity: [10, 10]\n'
            '  conduits:\n'
            '    macro.out: micro.in\n'
            '    micro.out: macro.in\n')

    logger = Logger()
    configuration = Configuration()
    instance_registry = InstanceRegistry()
    topology_store = TopologyStore(ymmsl_text)
    server = MMPServer(logger, configuration, instance_registry,
                       topology_store)
    yield server
    server.stop()


@pytest.fixture
def replaced_sys_argv() -> Generator[None, None, None]:
    old_argv = sys.argv
    sys.argv = ['', '--muscle-manager=localhost:9000']
    yield None
    sys.argv = old_argv
