import multiprocessing as mp

from ruamel import yaml
from ymmsl import loader

from libmuscle.logging import LogLevel, LogMessage, Timestamp
from libmuscle.mmp_client import MMPClient
from libmuscle.operator import Operator
from muscle_manager.instance_registry import InstanceRegistry
from muscle_manager.logger import Logger
from muscle_manager.mmp_server import MMPServer
from muscle_manager.muscle_manager import (
        config_for_experiment, elements_for_simulation)
from muscle_manager.topology_store import TopologyStore


def do_logging_test(caplog):
    ymmsl_text = (
            'version: v0.1\n'
            'simulation:\n'
            '  name: test_model\n'
            '  compute_elements:\n'
            '    macro: macro_implementation\n'
            '    micro:\n'
            '      implementation: micro_implementation\n'
            '      multiplicity: [10]\n'
            '  conduits:\n'
            '    macro.out: micro.in\n'
            '    micro.out: macro.in\n'
            'experiment:\n'
            '  model: test_model\n'
            '  parameter_values:\n'
            '    test1: 13\n'
            '    test2: 13.3\n'
            '    test3: testing\n'
            # '    test4: True\n'
            '    test5: [2.3, 5.6]\n'
            '    test6:\n'
            '      - [1.0, 2.0]\n'
            '      - [3.0, 1.0]\n'
            )

    # create server
    logger = Logger()
    ymmsl = yaml.load(ymmsl_text, Loader=loader)
    configuration = config_for_experiment(ymmsl.experiment)
    expected_elements = elements_for_simulation(ymmsl.simulation)
    instance_registry = InstanceRegistry(expected_elements)
    topology_store = TopologyStore(ymmsl)
    server = MMPServer(logger, configuration, instance_registry,
                       topology_store)

    # create client
    client = MMPClient('localhost:9000')
    message = LogMessage(
            instance_id='test_logging',
            timestamp=Timestamp(2.0),
            level=LogLevel.CRITICAL,
            text='Integration testing')

    # log and check
    client.submit_log_message(message)
    assert caplog.records[0].name == 'test_logging'
    assert caplog.records[0].time_stamp == '1970-01-01T00:00:02Z'
    assert caplog.records[0].levelname == 'CRITICAL'
    assert caplog.records[0].message == 'Integration testing'

    server.stop()


def test_logging(log_file_in_tmpdir, caplog):
    process = mp.Process(target=do_logging_test, args=(caplog,))
    process.start()
    process.join()
    assert process.exitcode == 0
