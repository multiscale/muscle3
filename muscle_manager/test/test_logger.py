import logging

from libmuscle.logging import LogLevel
from libmuscle.operator import Operator
from muscle_manager.logger import Logger


def test_log_level():
    assert LogLevel.CRITICAL.as_python_level() == logging.CRITICAL
    assert LogLevel.PROFILE.as_python_level() == logging.INFO
    assert LogLevel.CRITICAL.value > LogLevel.DEBUG.value


def test_create_logger():
    logger = Logger()


def test_log_message(logger):
    logger.log_message(
            'logger_test', Operator.F_INIT,
            '123',
            LogLevel.INFO, 'Testing the logging system')
