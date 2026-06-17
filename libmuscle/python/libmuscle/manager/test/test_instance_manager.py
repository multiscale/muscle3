"""Tests for InstanceManager with ExecutionModel.MANUAL support."""
import logging
from queue import Empty
from unittest.mock import patch

import pytest
import ymmsl
from ymmsl.v0_2 import Configuration, Reference

from libmuscle.manager.instance_manager import InstanceManager
from libmuscle.manager.instance_registry import InstanceRegistry
from libmuscle.manager.instantiator import InstantiationRequest
from libmuscle.manager.run_dir import RunDir
from libmuscle.planner.resources import Core, CoreSet, OnNodeResources, Resources


@pytest.fixture
def configuration() -> Configuration:
    """Create a test configuration using yMMSL (macro=MANUAL, micro=DIRECT)."""

    ymmsl_text = """
    ymmsl_version: v0.2

    description: test_config

    models:
        test_model:
            description: A test model
            components:
                macro:
                    ports:
                        o_i: out
                        s: in
                    description: Macro component
                    implementation: macro_implementation

                micro:
                    ports:
                        f_init: in
                        o_f: out
                    description: Micro component
                    implementation: micro_implementation

            conduits:
                macro.out: micro.in
                micro.out: macro.in

    programs:
      macro_implementation:
        execution_model: manual

      micro_implementation:
        execution_model: direct
        executable: /usr/bin/micro

    resources:
      test_model.macro:
        threads: 1

      test_model.micro:
        threads: 1
    """

    return ymmsl.load_as(Configuration, ymmsl_text)


class MockNativeInstantiator:
    """Mock for NativeInstantiator that records requests and returns fake results."""

    def __init__(self, resources_queue, requests_queue, results_queue,
                 log_records_queue, run_dir):
        self._resources_queue = resources_queue
        self._requests_queue = requests_queue

    def start(self):
        # Send fake resources
        resources = Resources()
        cores = CoreSet([Core(i, {i}) for i in range(4)])
        node = OnNodeResources('localhost', cores)
        resources.add_node(node)
        self._resources_queue.put(resources)

    def join(self):
        pass


def test_start_all_skips_manual_instances(tmp_path, caplog, configuration):
    """Test that start_all() skips instances with ExecutionModel.MANUAL."""
    instance_registry = InstanceRegistry()
    run_dir = RunDir(tmp_path / 'run')

    with patch(
        'libmuscle.manager.instance_manager.NativeInstantiator',
        MockNativeInstantiator
    ):
        instance_manager = InstanceManager(configuration, run_dir, instance_registry)
        instance_manager.set_manager_location('localhost:9000')

        with caplog.at_level(logging.INFO):
            instance_manager.start_all()

        request = instance_manager._instantiator._requests_queue.get(timeout=0.1)
        with pytest.raises(Empty):
            instance_manager._instantiator._requests_queue.get(timeout=0.1)
        instance_manager.shutdown()

        assert isinstance(request, InstantiationRequest)
        assert request.instance == Reference('micro')

        manual_log_messages = [
            r.message for r in caplog.records
            if 'macro' in r.message and 'manual' in r.message.lower()
        ]
        assert len(manual_log_messages) > 0


def test_manual_instances_not_counted_in_num_running(tmp_path, configuration):
    """Test that MANUAL instances are not counted in _num_running."""
    instance_registry = InstanceRegistry()
    run_dir = RunDir(tmp_path / 'run')

    with patch(
        'libmuscle.manager.instance_manager.NativeInstantiator',
        MockNativeInstantiator
    ):
        instance_manager = InstanceManager(configuration, run_dir, instance_registry)
        instance_manager.set_manager_location('localhost:9000')
        instance_manager.start_all()
        num_running = instance_manager._num_running
        instance_manager.shutdown()

    assert num_running == 1
