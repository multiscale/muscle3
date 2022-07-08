import logging
import multiprocessing as mp
import os
from pathlib import Path

import pytest
import yatiml
import ymmsl

import integration_test.include_libmuscle   # noqa: F401

from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir


skip_if_python_only = pytest.mark.skipif(
        'MUSCLE_TEST_PYTHON_ONLY' in os.environ,
        reason='Python-only tests requested')


@pytest.fixture
def yatiml_log_warning():
    yatiml.logger.setLevel(logging.WARNING)


def start_mmp_server(control_pipe, ymmsl_doc, run_dir):
    control_pipe[0].close()
    manager = Manager(ymmsl_doc, run_dir)
    control_pipe[1].send(manager.get_server_location())
    control_pipe[1].recv()
    control_pipe[1].close()
    manager.stop()


def make_server_process(ymmsl_doc, tmpdir):
    run_dir = RunDir(Path(tmpdir))
    control_pipe = mp.Pipe()
    process = mp.Process(target=start_mmp_server,
                         args=(control_pipe, ymmsl_doc, run_dir),
                         name='Manager')
    process.start()
    control_pipe[1].close()
    # wait for start
    yield control_pipe[0].recv()
    control_pipe[0].send(True)
    control_pipe[0].close()
    process.join()


@pytest.fixture
def mmp_server_process(yatiml_log_warning, tmpdir):
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

    yield from make_server_process(ymmsl_doc, tmpdir)


@pytest.fixture
def mmp_server_process_simple(tmpdir, yatiml_log_warning):
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

    yield from make_server_process(ymmsl_doc, tmpdir)


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

    manager = Manager(ymmsl_doc)
    yield manager._server
    manager.stop()


@pytest.fixture
def log_file_in_tmpdir(tmpdir):
    old_workdir = os.getcwd()
    os.chdir(tmpdir)

    yield None

    os.chdir(old_workdir)
