import logging

from libmuscle.logging import LogLevel, Timestamp
from libmuscle.operator import Operator
from libmuscle.manager.logger import Logger


def test_log_level():
    assert LogLevel.CRITICAL.as_python_level() == logging.CRITICAL
    assert LogLevel.CRITICAL.value > LogLevel.DEBUG.value


def test_create_logger():
    Logger()


def test_log_message(logger, caplog):
    logger.log_message(
            'test_log_message', Timestamp(123.0),
            LogLevel.CRITICAL, 'Testing the logging system')

    assert caplog.records[0].name == 'test_log_message'
    assert caplog.records[0].time_stamp == '1970-01-01T00:02:03Z'
    assert caplog.records[0].levelname == 'CRITICAL'
    assert caplog.records[0].message == 'Testing the logging system'
