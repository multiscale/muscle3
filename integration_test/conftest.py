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

skip_if_no_fortran = pytest.mark.skipif(
        'MUSCLE_DISABLE_FORTRAN' in os.environ,
        reason='No Fortran compiler available')

skip_if_no_mpi_cpp = pytest.mark.skipif(
        'MUSCLE_ENABLE_CPP_MPI' not in os.environ,
        reason='MPI support was not detected')


@pytest.fixture
def yatiml_log_warning():
    yatiml.logger.setLevel(logging.WARNING)


def ls_snapshots(run_dir, instance=None):
    """List all snapshots of the instance or workflow"""
    return sorted(run_dir.snapshot_dir(instance).iterdir(),
                  key=lambda path: tuple(map(int, path.stem.split("_")[1:])))


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
    try:
        yield control_pipe[0].recv()
    finally:
        control_pipe[0].send(True)
        control_pipe[0].close()
        process.join()


def _python_wrapper(instance_name, muscle_manager, callable):
    sys.argv.append(f'--muscle-instance={instance_name}')
    sys.argv.append(f'--muscle-manager={muscle_manager}')
    callable()


def run_manager_with_actors(ymmsl_text, tmpdir, actors):
    """Start muscle_manager along with C++ and python actors.

    Args:
        actors: a dictionary of lists containing details for each actor:
            ``{"instance_name": ("language", "details", ...)}``.

            Language can be ``"python"``, ``"cpp"``, ``"mpi_cpp"`` or ``"fortran"``.
            Details differ per language.

            For python actors, details is a single callable which is executed
            in a ``multiprocessing.Process``.

            For cpp actors, details is an executable path with optional arguments.
            The executable paths are assumed to be relative to
            ``../libmuscle/cpp/build/libmuscle/tests``.

            For mpi cpp actors, details is an executable path (see cpp), then number of
            processes and optionally arguments passed to the executable.

            For fortran actors, details is an executable path. Executable paths are
            assumed to be relative to ``../libmuscle/fortran/build/libmuscle/tests``.

            For both cpp and Fortran actors, LD_LIBRARY_PATH is automatically updated
            to include the msgpack library path.
    """
    env = os.environ.copy()
    ymmsl_doc = ymmsl.load(ymmsl_text)
    libmuscle_dir = Path(__file__).parents[1] / 'libmuscle'
    cpp_build_dir = libmuscle_dir / 'cpp' / 'build' / 'libmuscle' / 'tests'
    fortran_build_dir = libmuscle_dir / 'fortran' / 'build' / 'libmuscle' / 'tests'

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
        python_processes = []
        # start actors
        for instance_name, (language, actor, *args) in actors.items():
            if language == "python":
                # start python actor
                proc = mp.Process(
                        target=_python_wrapper,
                        args=(instance_name, env['MUSCLE_MANAGER'], actor),
                        name=instance_name)
                proc.start()
                python_processes.append(proc)
                continue
            elif language == "cpp":
                # executable = 'gdb'
                # args = ('--batch', '-ex', 'run', '-ex', 'bt', '--args',
                #         cpp_build_dir / actor)
                executable = cpp_build_dir / actor
            elif language == "mpicpp":
                assert len(args) > 0, "must provide at least number of mpi instances"
                executable = 'mpirun'
                out_file = tmpdir / f'mpi_{instance_name}.log'
                args = ('-np', args[0], mpirun_outfile_arg(), str(out_file),
                        str(cpp_build_dir / actor), *args[1:])
            elif language == "fortran":
                executable = fortran_build_dir / actor
            else:
                raise ValueError(f"Unknown language: {language}")
            # start native code actor
            f_out = stack.enter_context(
                    (tmpdir / f'{instance_name}_stdout.txt').open('w'))
            f_err = stack.enter_context(
                    (tmpdir / f'{instance_name}_stderr.txt').open('w'))
            native_processes.append(subprocess.Popen(
                    [str(executable), *args, f'--muscle-instance={instance_name}'],
                    env=env, stdout=f_out, stderr=f_err))

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
            '  test_with_a_longer_name: 1\n'
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


def mpi_is_intel():
    if 'MUSCLE_ENABLE_CPP_MPI' not in os.environ:
        return None

    result = subprocess.run(
            ['mpirun', '--version'], capture_output=True, check=True)
    return 'Intel' in result.stdout.decode('utf-8')


def mpirun_outfile_arg():
    if mpi_is_intel():
        return '-outfile-pattern'
    else:
        return '--output-filename'


@pytest.fixture
def mpi_exec_model():
    if mpi_is_intel():
        return 'intelmpi'
    else:
        return 'openmpi'
