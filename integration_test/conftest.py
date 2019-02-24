import sys
from typing import Generator

import pytest
from ruamel import yaml
from ymmsl import loader

import integration_test.include_libmuscle

from libmuscle.configuration import Configuration
from muscle_manager.instance_registry import InstanceRegistry
from muscle_manager.logger import Logger
from muscle_manager.mmp_server import MMPServer
from muscle_manager.muscle_manager import config_for_experiment
from muscle_manager.topology_store import TopologyStore


@pytest.fixture
def mmp_server(tmpdir):
    ymmsl_text = (
            'version: v0.1\n'
            'simulation:\n'
            '  name: test_model\n'
            '  compute_elements:\n'
            '    macro: macro_implementation\n'
            '    micro:\n'
            '      implementation: micro_implementation\n'
            '      multiplicity: [10, 10]\n'
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
    instance_registry = InstanceRegistry()
    topology_store = TopologyStore(ymmsl_text)
    server = MMPServer(logger, configuration, instance_registry,
                       topology_store)
    yield server
    server.stop()


@pytest.fixture
def mmp_server_qmc(tmpdir):
    ymmsl_text = (
            'version: v0.1\n'
            'simulation:\n'
            '  name: test_model\n'
            '  compute_elements:\n'
            '    qmc: muscle.qmc\n'
            '    macro:\n'
            '      implementation: macro_implementation\n'
            '      multiplicity: [100]\n'
            '    micro:\n'
            '      implementation: micro_implementation\n'
            '      multiplicity: [100]\n'
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

    logger = Logger()
    ymmsl = yaml.load(ymmsl_text, Loader=loader)
    configuration = config_for_experiment(ymmsl.experiment)
    instance_registry = InstanceRegistry()
    topology_store = TopologyStore(ymmsl_text)
    server = MMPServer(logger, configuration, instance_registry,
                       topology_store)
    yield server
    server.stop()


@pytest.fixture
def sys_argv_manager() -> Generator[None, None, None]:
    old_argv = sys.argv
    sys.argv = ['', '--muscle-manager=localhost:9000']
    yield None
    sys.argv = old_argv
