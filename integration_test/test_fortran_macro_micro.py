from pathlib import Path

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
            assert msg.data['test_grid'].array.shape == (2, 3)
            assert msg.data['test_grid'].array.flags.f_contiguous
            assert (msg.data['test_grid'].array ==
                    np.array([[1, 2, 3], [4, 5, 6]])).all()
            assert msg.timestamp == i * 10.0


@skip_if_python_only
def test_fortran_macro_micro(mmp_server_config_simple, tmp_path):
    # create Fortran micro model
    # see libmuscle/fortran/src/libmuscle/tests/fortran_micro_model_test.f90
    run_manager_with_actors(
            mmp_server_config_simple,
            tmp_path,
            {},
            {'micro': Path('libmuscle') / 'tests' / 'fortran_micro_model_test'},
            {'macro': macro})
