from libmuscle import Instance, Message
from ymmsl import Operator

from .conftest import run_manager_with_actors, skip_if_python_only, skip_if_no_mpi_cpp


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
@skip_if_no_mpi_cpp
def test_mpi_macro_micro(tmpdir, mmp_server_config_simple):
    actors = {
            'macro': ('python', macro),
            'micro': ('mpicpp', 'mpi_micro_model_test', '2')}  # 2 processes
    run_manager_with_actors(mmp_server_config_simple, tmpdir, actors)
