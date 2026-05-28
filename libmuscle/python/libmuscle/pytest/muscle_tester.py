import os
from contextlib import contextmanager
from types import TracebackType
from pathlib import Path
import multiprocessing as mp
from unittest.mock import patch
from typing import Callable, Generator, Optional, Tuple, Union
from multiprocessing.connection import Connection
from contextlib import ExitStack

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
from libmuscle.mcp.tcp_transport_client import TcpTransportClient, _RECONNECT_TIMEOUT
from libmuscle.receive_timeout_handler import ReceiveTimeoutHandler
from libmuscle.util import Retrier


def raise_error(*args: object) -> None:
    raise RuntimeError(args)


def make_connection_error_handler(default_timeout: float) -> Callable[..., None]:
    """Create a replacement for TcpTransportClient._handle_disconnect.

    A lost TCP connection triggers reconnection retries for up to _RECONNECT_TIMEOUT.
    During testing we want reconnection retries to be bounded by at least 
    _RECONNECT_TIMEOUT seconds, or default_timeout if that is longer.  The returned
    handler uses a Retrier initialised with max(_RECONNECT_TIMEOUT, default_timeout) so
    that it gives up (and raises ConnectionError) once that deadline has been reached.
    """
    retrier = Retrier(max(_RECONNECT_TIMEOUT, default_timeout))

    def _handle_disconnect(self: object, _retrier: object) -> None:
        if retrier.should_give_up():
            raise ConnectionError(
                'Connection with the tested component was lost '
                '(component may have crashed).'
            )
        retrier.sleep()

    return _handle_disconnect


class MuscleTester:
    """Helper class to test an implementation.

    Note: You don't need to construct a MuscleTester directly; use the
    ``muscle3_tester`` pytest fixture instead.
    """

    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.implementation_tester: Optional[ImplementationTester] = None
        self._exitstack = ExitStack()

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
        """Start a MUSCLE3 manager and return an ImplementationTester.

        A tester component is added and connected to all ports of the
        implementation defined in the yMMSL source. A subprocess is started in
        which the MUSCLE3 manager runs, and its address is retrieved. A
        monkeypatch overwrites :meth:`ReceiveTimeoutHandler.on_timeout` so that
        a :exc:`RuntimeError` is raised when a receive timeout is reached,
        causing the test simulation to quit. Finally, an
        :class:`ImplementationTester` is created from the manager address and
        the generated test yMMSL configuration.

        Args:
            ymmsl_source: Either a string containing the yMMSL, or a
                :class:`pathlib.Path` pointing to a file containing the yMMSL.
            implementation: Name of the implementation to test.
            default_timeout: Timeout (seconds) for message operations.

        Returns:
            An ImplementationTester connected to the running manager.
        """
        ymmsl_config = ymmsl.load_as(ymmsl.v0_2.Configuration, ymmsl_source)
        test_ymmsl_config = self._add_tester_component(ymmsl_config, implementation)

        # Save the test configuration to a temporary file
        test_ymmsl_path = self.run_dir / "test_config.ymmsl"
        ymmsl.save(test_ymmsl_config, test_ymmsl_path)

        server_ctx = make_server_process(
            test_ymmsl_config,self.run_dir, True)
        muscle_manager_address = self._exitstack.enter_context(server_ctx)

        # patch ReceiveTimeoutHandler so we can (ab)use it for our timeouts:
        self._exitstack.enter_context(patch.object(ReceiveTimeoutHandler, 'on_timeout',
                                                    raise_error))
        self._exitstack.enter_context(patch.object(TcpTransportClient,
                                                    '_handle_disconnect',
                                                    make_connection_error_handler(
                                                        default_timeout)))
        self.implementation_tester = ImplementationTester(default_timeout,
                                                          muscle_manager_address,
                                                          test_ymmsl_config)
        self._exitstack.callback(self.implementation_tester.cleanup)
        return self.implementation_tester

    def cleanup(self) -> None:
        """Stop the manager process and clean up all resources.

        Stops the :class:`ImplementationTester`, restores the monkeypatched
        :meth:`ReceiveTimeoutHandler.on_timeout`, and shuts down the manager
        subprocess.
        """
        self._exitstack.close()
        self.implementation_tester = None


def start_mmp_server(control_pipe: Tuple[Connection, Connection],
                     ymmsl_config: Configuration, run_dir: RunDir,
                     env: dict[str, str], start_instances: bool) -> None:
    if start_instances:
        os.environ.clear()
        os.environ.update(env)

    control_pipe[0].close()
    manager = Manager(ymmsl_config, run_dir, 'DEBUG')
    control_pipe[1].send(manager.get_server_location())

    if start_instances:
        manager.start_instances()
    
    control_pipe[1].recv()
    control_pipe[1].close()
    manager.stop()


@contextmanager
def make_server_process(ymmsl_config: Configuration, run_dir: Path,
                        start_instances: bool
                        ) -> Generator[str, None, None]:
    run_dir_obj = RunDir(run_dir)
    env = os.environ.copy()
    control_pipe = mp.Pipe()
    process = mp.Process(
        target=start_mmp_server,
        args=(control_pipe, ymmsl_config, run_dir_obj, env, start_instances),
        name='Manager'
    )
    process.start()
    control_pipe[1].close()
    muscle_manager_address = control_pipe[0].recv()
    try:
        yield muscle_manager_address
    finally:
        control_pipe[0].send(True)
        control_pipe[0].close()
        process.join()
