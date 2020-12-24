import logging
import multiprocessing as mp
import os
import sys
from typing import Generator

import pytest
import yatiml
import ymmsl

import integration_test.include_libmuscle   # noqa: F401

from libmuscle.manager.instance_registry import InstanceRegistry
from libmuscle.manager.logger import Logger
from libmuscle.manager.mmp_server import MMPServer
from libmuscle.manager.manager import elements_for_model
from libmuscle.manager.topology_store import TopologyStore


skip_if_python_only = pytest.mark.skipif(
        'MUSCLE_TEST_PYTHON_ONLY' in os.environ,
        reason='Python-only tests requested')


@pytest.fixture
def yatiml_log_warning():
    yatiml.logger.setLevel(logging.WARNING)


def make_server(ymmsl_doc: ymmsl.Configuration):
    logger = Logger()
    expected_elements = elements_for_model(ymmsl_doc.model)
    instance_registry = InstanceRegistry(expected_elements)
    topology_store = TopologyStore(ymmsl_doc)
    server = MMPServer(logger, ymmsl_doc.settings, instance_registry,
                       topology_store)
    return server


def start_mmp_server(control_pipe, ymmsl_doc):
    control_pipe[0].close()
    server = make_server(ymmsl_doc)
    control_pipe[1].send(True)
    control_pipe[1].recv()
    control_pipe[1].close()
    server.stop()


def make_server_process(ymmsl_doc):
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
def mmp_server_process(yatiml_log_warning):
    ymmsl_text = (
            'ymmsl_version: v0.1\n'
            'model:\n'
            '  name: test_model\n'
            '  components:\n'
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
            'implementations:\n'
            '  macro_implementation: macro.py\n'
            '  micro_implementation: micro.py\n'
            )
    ymmsl_doc = ymmsl.load(ymmsl_text)

    yield from make_server_process(ymmsl_doc)


@pytest.fixture
def mmp_server_process_simple(yatiml_log_warning):
    ymmsl_text = (
            'ymmsl_version: v0.1\n'
            'model:\n'
            '  name: test_model\n'
            '  components:\n'
            '    macro: macro_implementation\n'
            '    micro: micro_implementation\n'
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

    yield from make_server_process(ymmsl_doc)


@pytest.fixture
def mmp_server(yatiml_log_warning):
    ymmsl_text = (
            'ymmsl_version: v0.1\n'
            'model:\n'
            '  name: test_model\n'
            '  components:\n'
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

    server = make_server(ymmsl_doc)
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
