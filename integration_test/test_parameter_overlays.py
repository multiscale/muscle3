from collections import OrderedDict

from ymmsl import (Component, Conduit, Configuration, Model, Operator,
                   Settings)

from libmuscle import Instance, Message
from libmuscle.runner import run_simulation


def qmc():
    """qMC implementation.
    """
    instance = Instance({Operator.O_F: ['settings_out[]']})

    while instance.reuse_instance():
        # o_f
        settings0 = Settings({'test2': 14.4})

        assert instance.is_connected('settings_out')
        assert instance.is_vector_port('settings_out')
        assert not instance.is_resizable('settings_out')
        length = instance.get_port_length('settings_out')
        assert length == 10
        for slot in range(length):
            instance.send('settings_out',
                          Message(0.0, None, settings0), slot)


def macro():
    """Macro model implementation.
    """
    instance = Instance({
            Operator.O_I: ['out'], Operator.S: ['in']})

    while instance.reuse_instance():
        # f_init
        assert instance.get_setting('test2') == 14.4
        # o_i
        instance.send('out', Message(0.0, 10.0, 'testing'))
        # s/b
        msg = instance.receive('in')
        assert msg.data == 'testing back'


def explicit_relay():
    """Intermediate component with explicit settings.

    Sends and receives overlay settings explicitly, rather than
    having MUSCLE handle them. This just passes all information on.
    """
    instance = Instance({
            Operator.F_INIT: ['in[]'], Operator.O_F: ['out[]']})

    while instance.reuse_instance(False):
        # f_init
        assert instance.get_setting('test2', 'float') == 13.3
        assert instance.get_port_length('in') == instance.get_port_length(
                'out')

        msgs = list()
        for slot in range(instance.get_port_length('in')):
            msg = instance.receive_with_settings('in', slot)
            assert msg.data.startswith('testing')
            assert msg.settings['test2'] == 14.4
            msgs.append(msg)

        assert instance.get_setting('test2') == 13.3

        # o_f
        for slot in range(instance.get_port_length('out')):
            instance.send('out', msgs[slot], slot)


def micro():
    """Micro model implementation.
    """
    instance = Instance({Operator.F_INIT: ['in'], Operator.O_F: ['out']})

    assert instance.get_setting('test2') == 13.3
    while instance.reuse_instance():
        # f_init
        assert instance.get_setting('test2', 'float') == 14.4
        msg = instance.receive('in')
        assert msg.data == 'testing'

        # with pytest.raises(RuntimeError):
        #     instance.receive_with_settings('in')

        # o_f
        instance.send('out', Message(0.1, None, 'testing back'))


def test_settings_overlays(log_file_in_tmpdir):
    """A positive all-up test of settings overlays.
    """
    elements = [
            Component('qmc', 'qmc'),
            Component('macro', 'macro', [10]),
            Component('relay', 'explicit_relay'),
            Component('relay2', 'explicit_relay'),
            Component('micro', 'micro', [10])]

    conduits = [
                Conduit('qmc.settings_out', 'macro.muscle_settings_in'),
                Conduit('macro.out', 'relay.in'),
                Conduit('relay.out', 'micro.in'),
                Conduit('micro.out', 'relay2.in'),
                Conduit('relay2.out', 'macro.in')]

    model = Model('test_model', elements, conduits)

    settings = Settings(OrderedDict([
                ('test1', 13),
                ('test2', 13.3),
                ('test3', 'testing'),
                ('test4', True),
                ('test5', [2.3, 5.6]),
                ('test6', [[1.0, 2.0], [3.0, 1.0]])]))

    configuration = Configuration(model, settings)

    implementations = {
            'qmc': qmc,
            'macro': macro,
            'explicit_relay': explicit_relay,
            'micro': micro}

    run_simulation(configuration, implementations)
