import time
import math

import logging
from random import random, choice, uniform
from socket import SHUT_RD, SHUT_RDWR, SHUT_WR, SocketType
from unittest.mock import patch

import pytest

from ymmsl import (
        Component, Conduit, Configuration, Operator, Model, Settings)

from libmuscle import Instance, Message
from libmuscle.runner import run_simulation


_FAULT_PROB_MAX = 0.1


_start_time = 0
_repeat_period = 0.0


def _inject_fault(socket: SocketType) -> None:
    """Randomly closes the socket to simulate a dropped connection."""
    t = math.fmod((time.monotonic_ns() - _start_time) / 1e9, _repeat_period)
    fault_prob = 0.0
    if 0.5 < t and t < 1.5:
        fault_prob = (t - 0.5) * _FAULT_PROB_MAX
    elif 1.5 < t and t < 3.0:
        fault_prob = _FAULT_PROB_MAX
    elif 3.0 < t and t < 4.0:
        fault_prob = (4.0 - t) * _FAULT_PROB_MAX

    if random() < fault_prob:
        mode = choice((SHUT_RD, SHUT_WR, SHUT_RDWR))
        socket.shutdown(mode)


@pytest.fixture
def tcp_fault_injection():
    with (
            patch('libmuscle.mark.before_tcp_receive', _inject_fault),
            patch('libmuscle.mark.before_tcp_send', _inject_fault)):
        yield


def component():
    _logger = logging.getLogger()

    _logger.info('starting instance')
    instance = Instance({
        Operator.F_INIT: ['init'],
        Operator.O_I: ['out'],
        Operator.S: ['in'],
        Operator.O_F: ['result']})

    j = 0
    _logger.info('starting pre-receive')
    while instance.reuse_instance():
        _logger.info('top of reuse loop')
        init_msg = instance.receive('init', default=Message(0.0, data=None))
        assert init_msg.data is None or init_msg.data == [j] * (j * 1000)

        if instance.is_connected('out'):
            for i in range(200):
                _logger.info(f'i = {i}')
                data = [i] * (i * 1000)
                out_msg = Message(float(i), data=data)
                instance.send('out', out_msg)

                in_msg = instance.receive('in', default=out_msg)
                assert in_msg.data == data

        _logger.info('sending final result')
        instance.send('result', init_msg)
        j += 1


# def test_python_tcp_reconnect(log_file_in_tmpdir):
def test_python_tcp_reconnect(tcp_fault_injection, log_file_in_tmpdir):
    global _start_time, _repeat_period
    _start_time = time.monotonic_ns()
    _repeat_period = uniform(4.0, 6.0)

    elements = [
            Component('macro', 'component'),
            Component('micro', 'component')]

    conduits = [
                Conduit('macro.out', 'micro.init'),
                Conduit('micro.result', 'macro.in')]

    model = Model('test_python_tcp_reconnect', elements, conduits)
    settings = Settings()
    settings['muscle_remote_log_level'] = 'warning'
    settings['muscle_local_log_level'] = 'debug'
    settings['muscle_deadlock_receive_timeout'] = -1.0

    configuration = Configuration(model, settings)

    implementations = {'component': component}

    run_simulation(configuration, implementations)
