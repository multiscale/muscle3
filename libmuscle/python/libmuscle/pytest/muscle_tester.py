import os
from types import TracebackType
from pathlib import Path
import multiprocessing as mp
from unittest.mock import patch
from typing import Any, Optional, Tuple, Union
from multiprocessing.connection import Connection

import ymmsl.v0_2
from ymmsl.v0_2 import (
    Component,
    Conduit,
    Ports,
    Configuration,
    Reference,
    Program,
    ExecutionModel,
    Implementation,
    Model,
    ThreadedResReq,
)

from libmuscle.pytest.implementation_tester import ImplementationTester
from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir
from libmuscle.receive_timeout_handler import ReceiveTimeoutHandler


def raise_error(*args: object) -> None:
    raise RuntimeError(args)


class MuscleTester:
    """Helper class to test an implementation."""

    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.implementation_tester: Optional[ImplementationTester] = None
        self.control_pipe: Optional[Tuple[Connection, Connection]] = None
        self.process: Optional[mp.Process] = None
        self._patcher: Optional[Any] = None

    def __enter__(self) -> "MuscleTester":
        """Allows usage in a with-statement"""
        return self

    def __exit__(
        self,
        typ: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        """Allows usage in a with-statement"""
        self.cleanup()

    def _add_tester_component(
            self, config: Configuration, implementation_name: str
            ) -> Configuration:
        """
        Add a 'muscle3_implementation_tester' as a tester component.
        - Finds the implementation (model or program) by name.
        - Finds the component using that implementation.
        - Adds tester ports and conduits.
        - Adds a tester component with MANUAL execution.
        """

        implementation: Implementation
        if implementation_name in config.models:
            implementation = config.models[Reference(implementation_name)]
        elif implementation_name in config.programs:
            implementation = config.programs[Reference(implementation_name)]
        else:
            raise ValueError(
                f"No implementation '{implementation_name}' found in the yMMSL"
            )

        tester_name = "muscle3_implementation_tester"
        test_model_name = "muscle3_test_model"
        tester_o_i_ports = []
        tester_s_ports = []

        tester_model = Model(name=test_model_name)

        # Inputs of target → tester sends (O_I)
        for port_name in implementation.ports.receiving_port_names():
            tester_o_i_ports.append(f"{port_name}")
            tester_model.conduits.append(
                Conduit(
                    f"{tester_name}.{port_name}",
                    f"{implementation_name}.{port_name}"
                )
            )

        # Outputs of target → tester receives (S)
        for port_name in implementation.ports.sending_port_names():
            tester_s_ports.append(f"{port_name}")
            tester_model.conduits.append(
                Conduit(
                    f"{implementation_name}.{port_name}",
                    f"{tester_name}.{port_name}"
                )
            )

        tester_model.components[Reference(tester_name)] = Component(
            name=tester_name,
            ports=Ports(o_i=tester_o_i_ports, s=tester_s_ports),
            description="Tester component for implementation testing",
            implementation=tester_name,
            optional=False,
        )

        tester_model.components[Reference(implementation_name)] = Component(
            name=implementation_name,
            ports=implementation.ports,
            description="The tested implementation",
            implementation=implementation_name,
            optional=False,
        )

        config.programs[Reference(tester_name)] = Program(
            name=tester_name,
            ports=Ports(o_i=tester_o_i_ports, s=tester_s_ports),
            execution_model=ExecutionModel.MANUAL,
            description="Manual tester program for implementation testing",
        )

        config.resources[Reference(tester_name)] = ThreadedResReq(
                name=Reference(tester_name),
                threads=1
            )

        config.models[Reference(test_model_name)] = tester_model
        return config

    def start_implementation(
        self, ymmsl_source: Union[str, Path], implementation: str,
        *, default_timeout: float = 60
    ) -> ImplementationTester:
        """Start a MUSCLE3 manager and return an ImplementationTester for a given
        implementation from a yMMSL source.
        - A tester component is added and connected to all ports of the implementation
        defined in the ymmsl source.
        - A process is generated where the MUSCLE3 manager will be started and the
        address is derived.
        - A monkeypatch is used to overwrite ReceiveTimeoutHandler.on_timeout so
        that a RuntimeError is raised when a receive timeout is reached, causing the
        test simulation to quit.
        - The ImplementationTester is then created based on the manager address and the
        generated test yMMSL configuration.

        Args:
            ymmsl_source: Either a str containing the yMMSL, or a pathlib.Path
            pointing to a file containing the yMMSL.
            implementation: Name of the implementation under test.
            default_timeout: Timeout (seconds) for message operations (default: 60).

        Returns:
            An ImplementationTester connected to the running manager.
        """
        ymmsl_config = ymmsl.load_as(ymmsl.v0_2.Configuration, ymmsl_source)
        test_ymmsl_config = self._add_tester_component(ymmsl_config, implementation)

        # Save the test configuration to a temporary file
        test_ymmsl_path = self.run_dir / "test_config.ymmsl"
        ymmsl.save(test_ymmsl_config, test_ymmsl_path)

        muscle_manager_address, self.control_pipe, self.process = make_server_process(
            test_ymmsl_config, RunDir(self.run_dir))
        # monkeypatch ReceiveTimeoutHandler so we can (ab)use it for our timeouts:
        self._patcher = patch.object(ReceiveTimeoutHandler, 'on_timeout', raise_error)
        self._patcher.start()
        self.implementation_tester = ImplementationTester(default_timeout,
                                                          muscle_manager_address,
                                                          test_ymmsl_config)
        return self.implementation_tester

    def cleanup(self) -> None:
        if self.implementation_tester is not None:
            self.implementation_tester.cleanup()
            self.implementation_tester = None
        if self._patcher is not None:
            self._patcher.stop()
            self._patcher = None
        if self.control_pipe is not None and self.process is not None:
            self.control_pipe[0].send(True)
            self.control_pipe[0].close()
            self.process.join()
            self.control_pipe = None
            self.process = None


def start_mmp_server(control_pipe: Tuple[Connection, Connection],
                     ymmsl_config: Configuration, run_dir: RunDir,
                     env: dict[str, str]) -> None:
    os.environ.clear()
    os.environ.update(env)

    control_pipe[0].close()
    manager = Manager(ymmsl_config, run_dir, 'DEBUG')
    control_pipe[1].send(manager.get_server_location())
    manager.start_instances()
    control_pipe[1].recv()
    control_pipe[1].close()
    manager.stop()


def make_server_process(ymmsl_config: Configuration, run_dir: RunDir
                        ) -> Tuple[str, Tuple[Connection, Connection], mp.Process]:
    env = os.environ.copy()

    control_pipe = mp.Pipe()
    process = mp.Process(
        target=start_mmp_server,
        args=(control_pipe, ymmsl_config, run_dir, env),
        name='Manager'
    )
    process.start()
    control_pipe[1].close()
    muscle_manager_address = control_pipe[0].recv()
    return muscle_manager_address, control_pipe, process
