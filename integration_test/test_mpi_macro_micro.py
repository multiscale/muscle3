import multiprocessing as mp
import os
from pathlib import Path
import pytest
import subprocess
import sys

from libmuscle import Instance, Message
from ymmsl import Operator

from .conftest import skip_if_python_only


def run_macro(instance_id: str):
    sys.argv.append('--muscle-instance={}'.format(instance_id))
    macro()


def macro():
    instance = Instance({
            Operator.O_I: ['out'],
            Operator.S: ['in']})

    while instance.reuse_instance():
        # f_init
        assert instance.get_setting('test1') == 13

        for i in range(2):
            # o_i
            instance.send('out', Message(i * 10.0, (i + 1) * 10.0, 'testing'))

            # s/b
            msg = instance.receive('in')
            assert msg.data == 'testing back {}'.format(i)
            assert msg.timestamp == i * 10.0


@skip_if_python_only
def test_mpi_macro_micro(tmpdir, mmp_server_process_simple):
    # only run this if MPI is enabled
    if 'MUSCLE_ENABLE_CPP_MPI' not in os.environ:
        pytest.skip('MPI support was not detected')

    # create C++ micro model
    # see libmuscle/cpp/src/libmuscle/tests/micro_model_test.cpp
    cpp_build_dir = Path(__file__).parents[1] / 'libmuscle' / 'cpp' / 'build'
    env = os.environ.copy()
    lib_paths = [cpp_build_dir / 'msgpack' / 'msgpack' / 'lib']
    if 'LD_LIBRARY_PATH' in env:
        env['LD_LIBRARY_PATH'] += ':' + ':'.join(map(str, lib_paths))
    else:
        env['LD_LIBRARY_PATH'] = ':'.join(map(str, lib_paths))

    env['MUSCLE_MANAGER'] = mmp_server_process_simple

    cpp_test_dir = cpp_build_dir / 'libmuscle' / 'tests'
    mpi_test_micro = cpp_test_dir / 'mpi_micro_model_test'
    out_file = tmpdir + '/mpi_micro.log'
    micro_result = subprocess.Popen(
            ['mpirun', '-np', '2', '--output-filename', out_file,
             str(mpi_test_micro), '--muscle-instance=micro'], env=env)

    # run macro model
    macro_process = mp.Process(target=run_macro, args=('macro',))
    macro_process.start()

    # check results
    micro_result.wait()
    assert micro_result.returncode == 0
    macro_process.join()
    assert macro_process.exitcode == 0
