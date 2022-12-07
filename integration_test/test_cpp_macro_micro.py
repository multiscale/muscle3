from pathlib import Path
import sqlite3

import numpy as np

from libmuscle import Instance, Message
from ymmsl import Operator

from .conftest import skip_if_python_only, run_manager_with_actors


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


def check_profile_output(tmp_path):
    conn = sqlite3.connect(tmp_path / 'performance.sqlite')
    cur = conn.cursor()

    def check(instance: str, typ: str, port: str, operator: str) -> None:
        cur.execute(
                "SELECT * FROM all_events"
                f"    WHERE instance = '{instance}' AND type = '{typ}'"
                "    ORDER BY start_time")
        res = cur.fetchall()
        assert len(res) == 2
        assert res[0][4:8] == (port, operator, None, None)
        assert res[0][8] > 0
        assert res[0][9] == 0.0

        assert res[1][4:8] == (port, operator, None, None)
        assert res[1][8] > 0
        assert res[1][9] == 10.0

    check('macro', 'SEND', 'out', 'O_I')
    check('micro', 'RECEIVE_TRANSFER', 'in', 'F_INIT')
    check('micro', 'SEND', 'out', 'O_F')
    check('macro', 'RECEIVE_DECODE', 'in', 'S')

    cur.close()
    conn.close()


@skip_if_python_only
def test_cpp_macro_micro(mmp_server_config_simple, tmp_path):
    # create C++ micro model
    # see libmuscle/cpp/src/libmuscle/tests/micro_model_test.cpp
    run_manager_with_actors(
            mmp_server_config_simple,
            tmp_path,
            {'micro': Path('libmuscle') / 'tests' / 'micro_model_test'},
            {},
            {'macro': macro})

    check_profile_output(tmp_path)
