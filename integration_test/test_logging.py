import multiprocessing as mp

import ymmsl

from libmuscle.logging import LogLevel, LogMessage, Timestamp
from libmuscle.manager.instance_registry import InstanceRegistry
from libmuscle.manager.logger import Logger
from libmuscle.manager.mmp_server import MMPServer
from libmuscle.manager.manager import elements_for_model
from libmuscle.manager.topology_store import TopologyStore
from libmuscle.mmp_client import MMPClient


def do_logging_test(caplog):
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

    # create server
    logger = Logger()
    ymmsl_doc = ymmsl.load(ymmsl_text)
    expected_elements = elements_for_model(ymmsl_doc.model)
    instance_registry = InstanceRegistry(expected_elements)
    topology_store = TopologyStore(ymmsl_doc)
    server = MMPServer(logger, ymmsl_doc.settings, instance_registry,
                       topology_store)

    # create client
    client = MMPClient('localhost:9000')
    message = LogMessage(
            instance_id='test_logging',
            timestamp=Timestamp(2.0),
            level=LogLevel.DEBUG,
            text='Integration testing')

    # log and check
    client.submit_log_message(message)
    for rec in caplog.records:
        if rec.name == 'instances.test_logging':
            assert rec.time_stamp == '1970-01-01T00:00:02Z'
            assert rec.levelname == 'DEBUG'
            assert rec.message == 'Integration testing'
            break

    server.stop()


def test_logging(log_file_in_tmpdir, caplog):
    process = mp.Process(target=do_logging_test, args=(caplog,))
    process.start()
    process.join()
    assert process.exitcode == 0
