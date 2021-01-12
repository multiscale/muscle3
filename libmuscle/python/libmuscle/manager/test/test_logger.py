import logging
from pathlib import Path

from libmuscle.logging import LogLevel, Timestamp
from libmuscle.manager.logger import Logger


def test_log_level():
    assert LogLevel.CRITICAL.as_python_level() == logging.CRITICAL
    assert LogLevel.CRITICAL.value > LogLevel.DEBUG.value


def test_create_logger(tmpdir):
    logger = Logger(Path(str(tmpdir)))
    logger.close()


def test_log_message(logger, caplog):
    logger.log_message(
            'test_instance', Timestamp(123.0),
            LogLevel.CRITICAL, 'Testing the logging system')

    assert caplog.records[0].name == 'instances.test_instance'
    assert caplog.records[0].time_stamp == '1970-01-01T00:02:03Z'
    assert caplog.records[0].levelname == 'CRITICAL'
    assert caplog.records[0].message == 'Testing the logging system'
