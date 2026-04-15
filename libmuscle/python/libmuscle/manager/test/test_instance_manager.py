"""Tests for InstanceManager with ExecutionModel.MANUAL support."""
import logging
from queue import Empty
from unittest.mock import patch

import pytest

import ymmsl
from ymmsl.v0_2 import (Configuration, Reference)

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

    def start(self):
        # Send fake resources
        resources = Resources()
        cores = CoreSet([Core(i, {i}) for i in range(4)])
        node = OnNodeResources('localhost', cores)
        resources.add_node(node)
        self._resources_queue.put(resources)

    def join(self):
        pass


def _drain_instantiation_requests(queue):
    """
    Drain all InstantiationRequests currently in the queue.
    """
    requests = []
    while True:
        try:
            item = queue.get(timeout=0.1)
            if isinstance(item, InstantiationRequest):
                requests.append(item)
        except Empty:
            break
    return requests


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

        instantiation_requests = _drain_instantiation_requests(
            instance_manager._instantiator._requests_queue
        )

        instance_manager.shutdown()

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
