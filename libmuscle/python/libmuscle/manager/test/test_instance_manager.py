"""Tests for InstanceManager with ExecutionModel.MANUAL support."""
import logging
from unittest.mock import patch

import ymmsl
from ymmsl.v0_2 import (Configuration, Reference)

from libmuscle.manager.instance_manager import InstanceManager
from libmuscle.manager.instance_registry import InstanceRegistry
from libmuscle.manager.instantiator import InstantiationRequest
from libmuscle.manager.run_dir import RunDir
from libmuscle.planner.resources import Core, CoreSet, OnNodeResources, Resources


def make_configuration() -> Configuration:
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
      macro:
        threads: 1

      micro:
        threads: 1
    """

    return ymmsl.load_as(Configuration, ymmsl_text)


class MockNativeInstantiator:
    """Mock for NativeInstantiator that records requests and returns fake results."""

    def __init__(self, resources_queue, requests_queue, results_queue,
                 log_records_queue, run_dir):
        self._resources_queue = resources_queue
        self._requests_queue = requests_queue
        self._results_queue = results_queue
        self._log_records_queue = log_records_queue
        self._run_dir = run_dir
        self._started = False

    def start(self):
        self._started = True
        # Send fake resources
        resources = Resources()
        cores = CoreSet([Core(i, {i}) for i in range(4)])
        node = OnNodeResources('localhost', cores)
        resources.add_node(node)
        self._resources_queue.put(resources)

    def join(self):
        pass


def test_start_all_skips_manual_instances(tmp_path, caplog):
    """Test that start_all() skips instances with ExecutionModel.MANUAL."""
    config = make_configuration()

    instance_registry = InstanceRegistry()
    run_dir = RunDir(tmp_path / 'run')

    with patch(
        'libmuscle.manager.instance_manager.NativeInstantiator',
        MockNativeInstantiator
    ):
        instance_manager = InstanceManager(config, run_dir, instance_registry)
        instance_manager.set_manager_location('localhost:9000')

        sent_requests = []
        original_put = instance_manager._requests_out.put

        def capture_put(item):
            sent_requests.append(item)
            original_put(item)

        instance_manager._requests_out.put = capture_put

        with caplog.at_level(logging.INFO):
            instance_manager.start_all()

        instance_manager.shutdown()

    instantiation_requests = [
        r for r in sent_requests if isinstance(r, InstantiationRequest)
        ]
    assert len(instantiation_requests) == 1
    assert instantiation_requests[0].instance == Reference('micro')

    manual_requests = [
        r for r in instantiation_requests if r.instance == Reference('macro')
        ]
    assert len(manual_requests) == 0

    manual_log_messages = [
        r.message for r in caplog.records
        if 'macro' in r.message and 'manual' in r.message.lower()
    ]
    assert len(manual_log_messages) > 0


def test_manual_instances_not_counted_in_num_running(tmp_path):
    """Test that MANUAL instances are not counted in _num_running."""
    config = make_configuration()

    instance_registry = InstanceRegistry()
    run_dir = RunDir(tmp_path / 'run')

    with patch(
        'libmuscle.manager.instance_manager.NativeInstantiator',
        MockNativeInstantiator
    ):
        instance_manager = InstanceManager(config, run_dir, instance_registry)
        instance_manager.set_manager_location('localhost:9000')
        instance_manager.start_all()
        num_running = instance_manager._num_running
        instance_manager.shutdown()

    assert num_running == 1
