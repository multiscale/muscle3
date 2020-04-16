import multiprocessing as mp
from pathlib import Path
import subprocess
import sys

import numpy as np

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
            test_array = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
            assert test_array.shape == (2, 3)
            assert test_array.flags.c_contiguous
            data = {
                    'message': 'testing',
                    'test_grid': test_array}
            instance.send('out', Message(i * 10.0, (i + 1) * 10.0, data))

            # s/b
            msg = instance.receive('in')
            assert msg.data['reply'] == 'testing back {}'.format(i)
            assert msg.data['test_grid'].array.dtype.kind == 'i'
            assert msg.data['test_grid'].array.dtype.itemsize == 8
            assert msg.data['test_grid'].array[0][1] == 2
            assert msg.timestamp == i * 10.0


@skip_if_python_only
def test_cpp_macro_micro(mmp_server_process_simple):
    # create C++ micro model
    # see libmuscle/cpp/src/libmuscle/tests/micro_model_test.cpp
    cpp_build_dir = Path(__file__).parents[1] / 'libmuscle' / 'cpp' / 'build'
    lib_paths = [
            cpp_build_dir / 'grpc' / 'c-ares' / 'c-ares' / 'lib',
            cpp_build_dir / 'grpc' / 'zlib' / 'zlib' / 'lib',
            cpp_build_dir / 'grpc' / 'openssl' / 'openssl' / 'lib',
            cpp_build_dir / 'protobuf' / 'protobuf' / 'lib',
            cpp_build_dir / 'grpc' / 'grpc' / 'lib',
            cpp_build_dir / 'msgpack' / 'msgpack' / 'lib']
    env = {
            'LD_LIBRARY_PATH': ':'.join(map(str, lib_paths))}
    cpp_test_dir = cpp_build_dir / 'libmuscle' / 'tests'
    cpp_test_micro = cpp_test_dir / 'micro_model_test'
    micro_result = subprocess.Popen(
            [str(cpp_test_micro), '--muscle-instance=micro'], env=env)

    # run macro model
    macro_process = mp.Process(target=run_macro, args=('macro',))
    macro_process.start()

    # check results
    micro_result.wait()
    assert micro_result.returncode == 0
    macro_process.join()
    assert macro_process.exitcode == 0
