import multiprocessing as mp
import os
from collections.abc import Generator
from contextlib import ExitStack, contextmanager
from multiprocessing.connection import Connection
from pathlib import Path
from types import TracebackType
from typing import Optional, Union
from unittest.mock import patch

import ymmsl.v0_2
from ymmsl.v0_2 import (
    Component,
    Conduit,
    Configuration,
    ExecutionModel,
    Identifier,
    Implementation,
    Model,
    Operator,
    Port,
    Ports,
    Program,
    Reference,
    Timeline,
)

from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir
from libmuscle.mcp.tcp_transport_client import RECONNECT_TIMEOUT
from libmuscle.mcp.tcp_transport_server import TcpTransportServer
from libmuscle.mmp_client import PEER_TIMEOUT
from libmuscle.pytest.implementation_tester import ImplementationTester
from libmuscle.receive_timeout_handler import ReceiveTimeoutHandler


def raise_error(*args: object) -> None:
    raise RuntimeError(args)


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
        tester_timeline = Timeline(tester_name)
        tester_ports: list[Port] = []
        test_model_name = "muscle3_test_model"

        tester_model = Model(name=test_model_name)

        # Generate ports and conduits
        for port in implementation.ports.values():
            tester_port = f"{tester_name}.{port.name}"
            implementation_port = f"{implementation_name}.{port.name}"
            if port.operator.allows_receiving():
                conduit = Conduit(tester_port, implementation_port)
                tester_operator = Operator.O_I
            else:
                conduit = Conduit(implementation_port, tester_port)
                tester_operator = Operator.S
            if port.operator in (Operator.O_I, Operator.S):
                port_timeline = port.timeline or Timeline(implementation_name)
                timeline = tester_timeline + port_timeline
            else:
                timeline = tester_timeline

            tester_model.conduits.append(conduit)
            tester_ports.append(Port(port.name, tester_operator, timeline))

        if not any(
            p.operator is Operator.F_INIT for p in implementation.ports.values()
        ):
            # We'll connect muscle_settings_in to make the timeline logic work
            tester_model.conduits.append(
                Conduit(
                    f"{tester_name}.__settings_out__",
                    f"{implementation_name}.muscle_settings_in",
                )
            )
            tester_ports.append(
                Port(Identifier("__settings_out__"), Operator.O_I, tester_timeline)
            )

        tester_model.components[Reference(tester_name)] = Component(
            name=tester_name,
            ports=Ports(tester_ports),
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
            ports=Ports(tester_ports),
            execution_model=ExecutionModel.MANUAL,
            description="Manual tester program for implementation testing",
        )

        config.models[Reference(test_model_name)] = tester_model
        return config

    def start_implementation(
        self,
        ymmsl_source: Union[str, Path],
        implementation: str,
        *,
        default_timeout: float = 60,
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

        Raises:
            RuntimeError: If the :class:`ImplementationTester` could not be
                initialized, for example because the executable under test does
                not exist and never registered with the manager.
        """
        ymmsl_config = ymmsl.load_as(ymmsl.v0_2.Configuration, ymmsl_source)
        test_ymmsl_config = self._add_tester_component(ymmsl_config, implementation)

        # Save the test configuration to a temporary file
        test_ymmsl_path = self.run_dir / "test_config.ymmsl"
        ymmsl.save(test_ymmsl_config, test_ymmsl_path)

        server_ctx = make_server_process(test_ymmsl_config, self.run_dir, True)
        muscle_manager_address = self._exitstack.enter_context(server_ctx)

        # patch ReceiveTimeoutHandler so we can (ab)use it for our timeouts:
        self._exitstack.enter_context(
            patch.object(ReceiveTimeoutHandler, "on_timeout", raise_error)
        )
        self._exitstack.enter_context(
            patch(
                "libmuscle.mcp.tcp_transport_client.RECONNECT_TIMEOUT",
                min(RECONNECT_TIMEOUT, default_timeout),
            )
        )
        self._exitstack.enter_context(
            patch(
                "libmuscle.mmp_client.PEER_TIMEOUT", min(PEER_TIMEOUT, default_timeout)
            )
        )
        # Ensure we won't wait forever on our outboxes
        self._exitstack.enter_context(
            patch("libmuscle.post_office.PostOffice.wait_for_receivers")
        )
        # And we close() our TCP Servers ungracefully
        origclose = TcpTransportServer.close
        self._exitstack.enter_context(
            patch.multiple(
                TcpTransportServer,
                close=lambda self, _=True: origclose(self, False),
            )
        )
        self.implementation_tester = ImplementationTester(
            default_timeout, muscle_manager_address, test_ymmsl_config
        )
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


def start_mmp_server(
    control_pipe: tuple[Connection, Connection],
    ymmsl_config: Configuration,
    run_dir: RunDir,
    env: dict[str, str],
    start_instances: bool,
) -> None:
    if start_instances:
        os.environ.clear()
        os.environ.update(env)

    control_pipe[0].close()
    manager = Manager(ymmsl_config, run_dir, "DEBUG")
    control_pipe[1].send(manager.get_server_location())

    if start_instances:
        manager.start_instances()

    control_pipe[1].recv()
    control_pipe[1].close()
    manager.stop()


@contextmanager
def make_server_process(
    ymmsl_config: Configuration, run_dir: Path, start_instances: bool
) -> Generator[str, None, None]:
    run_dir_obj = RunDir(run_dir)
    env = os.environ.copy()
    control_pipe = mp.Pipe()
    process = mp.Process(
        target=start_mmp_server,
        args=(control_pipe, ymmsl_config, run_dir_obj, env, start_instances),
        name="Manager",
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
