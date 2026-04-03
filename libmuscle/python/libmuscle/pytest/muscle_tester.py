from types import TracebackType
from pathlib import Path
import subprocess
import multiprocessing as mp
from typing import Optional, Tuple
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
    Model
)

from libmuscle.pytest.implementation_tester import ImplementationTester
from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir


class MuscleTester:
    """Helper class to test an implementation."""

    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self._manager_process: Optional[subprocess.Popen] = None

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

    def add_tester_component(
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
            raise ValueError(f"No implementation '{implementation}' found in the yMMSL")

        tester_name = "muscle3_implementation_tester"
        tester_o_i_ports = []
        tester_s_ports = []

        tester_model = Model(
            name=tester_name,
            ports=Ports(o_i=[], s=[]),
            components=[],
            conduits=[]
        )

        # Inputs of target → tester sends (O_I)
        for port_name in implementation.ports.receiving_port_names():
            tester_o_i_ports.append(f"{port_name}")
            tester_model.conduits.append(
                Conduit(
                    f"{tester_name}.{port_name}",
                    f"{implementation}.{port_name}"
                )
            )

        # Outputs of target → tester receives (S)
        for port_name in implementation.ports.sending_port_names():
            tester_s_ports.append(f"{port_name}")
            tester_model.conduits.append(
                Conduit(
                    f"{implementation}.{port_name}",
                    f"{tester_name}.{port_name}"
                )
            )

        tester_model.components[Reference(tester_name)] = Component(
            name=tester_name,
            ports=Ports(o_i=tester_o_i_ports, s=tester_s_ports),
            description="Manual tester component for implementation testing",
            implementation=tester_name,
            optional=False,
        )

        config.programs[Reference(tester_name)] = Program(
            name=tester_name,
            execution_model=ExecutionModel.MANUAL,
            description="Manual tester program for implementation testing",
        )

        config.models[Reference(tester_name)] = tester_model
        return config

    def start_implementation(
        self, ymmsl_path: str, implementation: str, *, default_timeout: float = 60
    ) -> ImplementationTester:
        ymmsl_config = ymmsl.load_as(ymmsl.v0_2.Configuration, Path(ymmsl_path))
        test_ymmsl_config = self.add_tester_component(ymmsl_config, implementation)

        # Save the test configuration to a temporary file
        test_ymmsl_path = self.run_dir / "test_config.ymmsl"
        ymmsl.save(test_ymmsl_config, test_ymmsl_path)

        muscle_manager_address, self.control_pipe, self.process = make_server_process(
            test_ymmsl_config, RunDir(self.run_dir))
        self.implementation_tester = ImplementationTester(default_timeout,
                                                          muscle_manager_address,
                                                          test_ymmsl_config)
        return self.implementation_tester

    def cleanup(self) -> None:
        self.implementation_tester.cleanup()
        self.control_pipe[0].send(True)
        self.control_pipe[0].close()
        self.process.join()


def start_mmp_server(control_pipe: Tuple[Connection, Connection],
                     ymmsl_config: Configuration, run_dir: RunDir) -> None:
    control_pipe[0].close()
    manager = Manager(ymmsl_config, run_dir, 'DEBUG')
    control_pipe[1].send(manager.get_server_location())
    manager.start_instances()
    control_pipe[1].recv()
    control_pipe[1].close()
    manager.stop()


def make_server_process(ymmsl_config: Configuration, run_dir: RunDir
                        ) -> Tuple[str, Tuple[Connection, Connection], mp.Process]:
    control_pipe = mp.Pipe()
    process = mp.Process(
        target=start_mmp_server,
        args=(control_pipe, ymmsl_config, run_dir),
        name='Manager'
    )
    process.start()
    control_pipe[1].close()
    muscle_manager_address = control_pipe[0].recv()
    return muscle_manager_address, control_pipe, process
