import logging
import multiprocessing as mp
import sys
from typing import Generator

import pytest
from ruamel import yaml
import yatiml
from ymmsl import loader

import integration_test.include_libmuscle

from muscle_manager.instance_registry import InstanceRegistry
from muscle_manager.logger import Logger
from muscle_manager.mmp_server import MMPServer
from muscle_manager.muscle_manager import (
        config_for_experiment, elements_for_simulation)
from muscle_manager.topology_store import TopologyStore


@pytest.fixture
def yatiml_log_warning():
    yatiml.logger.setLevel(logging.WARNING)


def start_mmp_server(control_pipe, ymmsl):
    control_pipe[0].close()

    logger = Logger()
    configuration = config_for_experiment(ymmsl.experiment)
    expected_elements = elements_for_simulation(ymmsl.simulation)
    instance_registry = InstanceRegistry(expected_elements)
    topology_store = TopologyStore(ymmsl)
    server = MMPServer(logger, configuration, instance_registry,
                       topology_store)
    control_pipe[1].send(True)
    control_pipe[1].recv()
    control_pipe[1].close()
    server.stop()


@pytest.fixture
def mmp_server_process(tmpdir, yatiml_log_warning):
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
    ymmsl = yaml.load(ymmsl_text, Loader=loader)

    control_pipe = mp.Pipe()
    process = mp.Process(target=start_mmp_server,
                         args=(control_pipe, ymmsl),
                         name='MMPServer')
    process.start()
    control_pipe[1].close()
    # wait for start
    control_pipe[0].recv()
    yield None
    control_pipe[0].send(True)
    control_pipe[0].close()
    process.join()


@pytest.fixture
def mmp_server(tmpdir, yatiml_log_warning):
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

    logger = Logger()
    ymmsl = yaml.load(ymmsl_text, Loader=loader)
    configuration = config_for_experiment(ymmsl.experiment)
    expected_elements = elements_for_simulation(ymmsl.simulation)
    instance_registry = InstanceRegistry(expected_elements)
    topology_store = TopologyStore(ymmsl)
    server = MMPServer(logger, configuration, instance_registry,
                       topology_store)
    yield server
    server.stop()


@pytest.fixture
def mmp_server_process_qmc(tmpdir, yatiml_log_warning):
    ymmsl_text = (
            'version: v0.1\n'
            'simulation:\n'
            '  name: test_model\n'
            '  compute_elements:\n'
            '    qmc: muscle.qmc\n'
            '    macro:\n'
            '      implementation: macro_implementation\n'
            '      multiplicity: [10]\n'
            '    micro:\n'
            '      implementation: micro_implementation\n'
            '      multiplicity: [10]\n'
            '  conduits:\n'
            '    qmc.parameters_out: macro.muscle_parameters_in\n'
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
    ymmsl = yaml.load(ymmsl_text, Loader=loader)

    control_pipe = mp.Pipe()
    process = mp.Process(target=start_mmp_server,
                         args=(control_pipe, ymmsl),
                         name='MMPServer')
    process.start()
    control_pipe[1].close()
    # wait for start
    control_pipe[0].recv()
    yield None
    control_pipe[0].send(True)
    control_pipe[0].close()
    process.join()


@pytest.fixture
def mmp_server_dm(tmpdir, yatiml_log_warning):
    ymmsl_text = (
            'version: v0.1\n'
            'simulation:\n'
            '  name: test_model\n'
            '  compute_elements:\n'
            '    dm: muscle.duplication_mapper\n'
            '    first: first_step\n'
            '    second: second_step\n'
            '  conduits:\n'
            '    dm.out1: first.in\n'
            '    dm.out2: second.in\n'
            'experiment:\n'
            '  model: test_model\n'
            )
    ymmsl = yaml.load(ymmsl_text, Loader=loader)

    control_pipe = mp.Pipe()
    process = mp.Process(target=start_mmp_server,
                         args=(control_pipe, ymmsl),
                         name='MMPServer')
    process.start()
    control_pipe[1].close()
    # wait for start
    control_pipe[0].recv()
    yield None
    control_pipe[0].send(True)
    control_pipe[0].close()
    process.join()


@pytest.fixture
def sys_argv_manager() -> Generator[None, None, None]:
    old_argv = sys.argv
    sys.argv = ['', '--muscle-manager=localhost:9000']
    yield None
    sys.argv = old_argv
