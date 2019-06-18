import logging
import multiprocessing as mp
import sys
from typing import Generator

import pytest
import yatiml
import ymmsl

import integration_test.include_libmuscle

from libmuscle.manager.instance_registry import InstanceRegistry
from libmuscle.manager.logger import Logger
from libmuscle.manager.mmp_server import MMPServer
from libmuscle.manager.manager import elements_for_model
from libmuscle.manager.topology_store import TopologyStore


@pytest.fixture
def yatiml_log_warning():
    yatiml.logger.setLevel(logging.WARNING)


def start_mmp_server(control_pipe, ymmsl):
    control_pipe[0].close()

    logger = Logger()
    expected_elements = elements_for_model(ymmsl.model)
    instance_registry = InstanceRegistry(expected_elements)
    topology_store = TopologyStore(ymmsl)
    server = MMPServer(logger, ymmsl.settings, instance_registry,
                       topology_store)
    control_pipe[1].send(True)
    control_pipe[1].recv()
    control_pipe[1].close()
    server.stop()


@pytest.fixture
def mmp_server_process(yatiml_log_warning):
    ymmsl_text = (
            'ymmsl_version: v0.1\n'
            'model:\n'
            '  name: test_model\n'
            '  compute_elements:\n'
            '    macro: macro_implementation\n'
            '    micro:\n'
            '      implementation: micro_implementation\n'
            '      multiplicity: [10]\n'
            '  conduits:\n'
            '    macro.out: micro.in\n'
            '    micro.out: macro.in\n'
            'settings:\n'
            '  test1: 13\n'
            '  test2: 13.3\n'
            '  test3: testing\n'
            '  test4: True\n'
            '  test5: [2.3, 5.6]\n'
            '  test6:\n'
            '    - [1.0, 2.0]\n'
            '    - [3.0, 1.0]\n'
            )
    ymmsl_doc = ymmsl.load(ymmsl_text)

    control_pipe = mp.Pipe()
    process = mp.Process(target=start_mmp_server,
                         args=(control_pipe, ymmsl_doc),
                         name='MMPServer')
    process.start()
    control_pipe[1].close()
    # wait for start
    control_pipe[0].recv()
    yield None
    control_pipe[0].send(True)
    control_pipe[0].close()
    process.join()


@pytest.fixture
def mmp_server(yatiml_log_warning):
    ymmsl_text = (
            'ymmsl_version: v0.1\n'
            'model:\n'
            '  name: test_model\n'
            '  compute_elements:\n'
            '    macro: macro_implementation\n'
            '    micro:\n'
            '      implementation: micro_implementation\n'
            '      multiplicity: [10]\n'
            '  conduits:\n'
            '    macro.out: micro.in\n'
            '    micro.out: macro.in\n'
            'settings:\n'
            '  test1: 13\n'
            '  test2: 13.3\n'
            '  test3: testing\n'
            '  test4: True\n'
            '  test5: [2.3, 5.6]\n'
            '  test6:\n'
            '    - [1.0, 2.0]\n'
            '    - [3.0, 1.0]\n'
            )

    logger = Logger()
    ymmsl_doc = ymmsl.load(ymmsl_text)
    expected_elements = elements_for_model(ymmsl_doc.model)
    instance_registry = InstanceRegistry(expected_elements)
    topology_store = TopologyStore(ymmsl_doc)
    server = MMPServer(logger, ymmsl_doc.settings, instance_registry,
                       topology_store)
    yield server
    server.stop()


@pytest.fixture
def sys_argv_manager() -> Generator[None, None, None]:
    old_argv = sys.argv
    sys.argv = sys.argv + ['--muscle-manager=localhost:9000']
    yield None
    sys.argv = old_argv


@pytest.fixture
def log_file_in_tmpdir(tmpdir):
    old_argv = sys.argv
    sys.argv = sys.argv + ['--muscle-log-file={}'.format(tmpdir)]
    yield None
    sys.argv = old_argv
