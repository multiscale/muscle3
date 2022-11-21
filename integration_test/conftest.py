import logging
import multiprocessing as mp
import os
import subprocess
import sys
from contextlib import contextmanager, ExitStack
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


def _python_wrapper(instance_name, muscle_manager, callable):
    sys.argv.append(f'--muscle-instance={instance_name}')
    sys.argv.append(f'--muscle-manager={muscle_manager}')
    callable()


def run_manager_with_actors(
        ymmsl_text, tmpdir,
        cpp_actors={}, fortran_actors={}, python_actors={}):
    """Start muscle_manager along with C++ and python actors.

    C++ actors are a dict of instance->executable_path. Executable paths are
    assumed to be relative to ../libmuscle/cpp/build/. LD_LIBRARY_PATH is
    automatically updated to include the msgpack library path.

    Fortran actors are a dict of instance->executable_path. Executable paths are
    assumed to be relative to ../libmuscle/fortran/build/. LD_LIBRARY_PATH is
    automatically updated to include the msgpack library path.

    Python actors are a dict of instance->callable, where the callable
    implements the python actor.
    """
    env = os.environ.copy()
    ymmsl_doc = ymmsl.load(ymmsl_text)
    libmuscle_dir = Path(__file__).parents[1] / 'libmuscle'
    cpp_build_dir = libmuscle_dir / 'cpp' / 'build'
    fortran_build_dir = libmuscle_dir / 'fortran' / 'build'

    with ExitStack() as stack:
        # start muscle_manager and extract manager location
        ctx = contextmanager(make_server_process)(ymmsl_doc, tmpdir)
        env['MUSCLE_MANAGER'] = stack.enter_context(ctx)

        lib_paths = [cpp_build_dir / 'msgpack' / 'msgpack' / 'lib']
        if 'LD_LIBRARY_PATH' in env:
            env['LD_LIBRARY_PATH'] += ':' + ':'.join(map(str, lib_paths))
        else:
            env['LD_LIBRARY_PATH'] = ':'.join(map(str, lib_paths))

        native_processes = []
        # start native actors
        for actors, build_dir in ((cpp_actors, cpp_build_dir),
                                  (fortran_actors, fortran_build_dir)):
            for instance_name, executable_path in actors.items():
                executable = build_dir / executable_path
                f_out = stack.enter_context(
                        (tmpdir / f'{instance_name}_stdout.txt').open('w'))
                f_err = stack.enter_context(
                        (tmpdir / f'{instance_name}_stderr.txt').open('w'))
                native_processes.append(subprocess.Popen(
                        [str(executable), f'--muscle-instance={instance_name}'],
                        env=env, stdout=f_out, stderr=f_err))

        # start python actors
        python_processes = []
        for instance_name, callable in python_actors.items():
            proc = mp.Process(
                    target=_python_wrapper,
                    args=(instance_name, env['MUSCLE_MANAGER'], callable))
            proc.start()
            python_processes.append(proc)

        # check results
        for proc in native_processes:
            proc.wait()
            assert proc.returncode == 0
        for proc in python_processes:
            proc.join()
            assert proc.exitcode == 0


@pytest.fixture
def mmp_server_config(yatiml_log_warning):
    return (
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


@pytest.fixture
def mmp_server_process(mmp_server_config, tmpdir):
    ymmsl_doc = ymmsl.load(mmp_server_config)
    yield from make_server_process(ymmsl_doc, tmpdir)


@pytest.fixture
def mmp_server_config_simple(yatiml_log_warning):
    return (
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


@pytest.fixture
def mmp_server_process_simple(mmp_server_config_simple, tmpdir):
    ymmsl_doc = ymmsl.load(mmp_server_config_simple)
    yield from make_server_process(ymmsl_doc, tmpdir)


@pytest.fixture
def mmp_server(mmp_server_config_simple, yatiml_log_warning):
    ymmsl_doc = ymmsl.load(mmp_server_config_simple)

    manager = Manager(ymmsl_doc)
    yield manager._server
    manager.stop()


@pytest.fixture
def log_file_in_tmpdir(tmpdir):
    old_workdir = os.getcwd()
    os.chdir(tmpdir)

    yield None

    os.chdir(old_workdir)
