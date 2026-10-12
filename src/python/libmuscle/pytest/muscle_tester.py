import multiprocessing as mp
import os
from collections.abc import Generator
from contextlib import ExitStack, contextmanager
from multiprocessing.connection import Connection
from pathlib import Path
from types import TracebackType
from unittest.mock import patch

import ymmsl.v0_2
from ymmsl.v0_2 import (
    Component,
    Conduit,
    Configuration,
    ExecutionModel,
    Identifier,
    Implementation,
    MatchingTimelines,
    Model,
    Operator,
    Port,
    Ports,
    Program,
    Reference,
    Timeline,
    resolve_timelines,
)

from libmuscle.manager.hammer import flatten
from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir
from libmuscle.mcp.tcp_transport_client import RECONNECT_TIMEOUT
from libmuscle.mcp.tcp_transport_server import TcpTransportServer
from libmuscle.mmp_client import PEER_TIMEOUT
from libmuscle.pytest.implementation_tester import (
    PARENT_SETTINGS_PORT_NAME,
    PARENT_TESTER_NAME,
    SIBLING_SETTINGS_PORT_NAME,
    SIBLING_TESTER_NAME,
    ImplementationTester,
)
from libmuscle.receive_timeout_handler import ReceiveTimeoutHandler

TEST_MODEL_NAME = "muscle3_test_model"


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
        self.implementation_tester: ImplementationTester | None = None
        self._exitstack = ExitStack()

    def __enter__(self) -> "MuscleTester":
        """Allows usage in a with-statement"""
        return self

    def __exit__(
        self,
        typ: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Allows usage in a with-statement"""
        self.cleanup()

    def _add_test_model(self, config: Configuration, testee_name: str) -> None:
        """
        Add a test model in which tester components are connected to the testee,
        the implementation under test.
        - Finds the testee (model or program) by name.
        - Adds a test model containing the testee and the tester
          components, and adds MANUAL programs for the testers.

        The ports of the testee are connected to two tester components:
        - F_INIT and O_F ports are connected to the O_I and S ports of the
          'muscle3_tester_parent', which acts as the parent of the
          testee.
        - O_I and S ports are connected to the S and O_I ports of the
          'muscle3_tester_sibling', like in an interact coupling,
          and their timelines are declared to match. The parent nests the sibling
          in its timeline through the sibling's muscle_settings_in, so that it is
          on the same level as the testee.
        """

        testee: Implementation
        if testee_name in config.models:
            testee = config.models[Reference(testee_name)]
        elif testee_name in config.programs:
            testee = config.programs[Reference(testee_name)]
        else:
            raise ValueError(f"No implementation '{testee_name}' found in the yMMSL")

        test_model = Model(name=TEST_MODEL_NAME)

        # A sibling is only needed if the testee has O_I or S ports
        has_sibling = any(
            port.operator in (Operator.O_I, Operator.S)
            for port in testee.ports.values()
        )

        self._add_parent_tester(config, test_model, testee)
        if has_sibling:
            self._add_sibling_tester(config, test_model, testee)

            # Nest the sibling in the parent's timeline, next to the testee
            test_model.conduits.append(
                Conduit(
                    f"{PARENT_TESTER_NAME}.{SIBLING_SETTINGS_PORT_NAME}",
                    f"{SIBLING_TESTER_NAME}.muscle_settings_in",
                )
            )
            port = Port(Identifier(SIBLING_SETTINGS_PORT_NAME), Operator.O_I)
            parent = Reference(PARENT_TESTER_NAME)
            test_model.components[parent].ports[port.name] = port
            config.programs[parent].ports[port.name] = port

        test_model.components[testee.name] = Component(
            name=str(testee.name),
            ports=testee.ports,
            description="The testee",
            implementation=str(testee.name),
            optional=False,
        )

        config.models[Reference(TEST_MODEL_NAME)] = test_model

    @staticmethod
    def _add_parent_tester(
        config: Configuration, test_model: Model, testee: Implementation
    ) -> None:
        """Add the parent tester, connected to the F_INIT and O_F ports.

        Args:
            config: The configuration to add the tester program to.
            test_model: The test model to add the component and conduits to.
            testee: The testee.
        """
        parent_ports = [
            MuscleTester._connect_mirrored_port(
                test_model, PARENT_TESTER_NAME, testee, port
            )
            for port in testee.ports.values()
            if port.operator in (Operator.F_INIT, Operator.O_F)
        ]

        if not any(p.operator is Operator.F_INIT for p in testee.ports.values()):
            # We'll connect muscle_settings_in to make the timeline logic work
            test_model.conduits.append(
                Conduit(
                    f"{PARENT_TESTER_NAME}.{PARENT_SETTINGS_PORT_NAME}",
                    f"{testee.name}.muscle_settings_in",
                )
            )
            parent_ports.append(
                Port(Identifier(PARENT_SETTINGS_PORT_NAME), Operator.O_I)
            )

        MuscleTester._add_tester(config, test_model, PARENT_TESTER_NAME, parent_ports)

    @staticmethod
    def _add_sibling_tester(
        config: Configuration, test_model: Model, testee: Implementation
    ) -> None:
        """Add the sibling tester, connected to the O_I and S ports.

        The timelines of the connected ports are declared to match.

        Args:
            config: The configuration to add the tester program to.
            test_model: The test model to add the component, conduits and
                matching timelines to.
            testee: The testee.
        """
        testee_ports = [
            port
            for port in testee.ports.values()
            if port.operator in (Operator.O_I, Operator.S)
        ]

        sibling_ports = [
            MuscleTester._connect_mirrored_port(
                test_model, SIBLING_TESTER_NAME, testee, port
            )
            for port in testee_ports
        ]

        def port_timeline(component: str, timeline: Timeline | None) -> Timeline:
            if timeline is None:
                return Timeline([PARENT_TESTER_NAME, component])
            return Timeline(
                [PARENT_TESTER_NAME, *(f"{component}.{p}" for p in timeline)]
            )

        timelines: list[Timeline | None] = []
        for port in testee_ports:
            if (port.timeline or None) not in timelines:
                timelines.append(port.timeline or None)

        test_model.matching_timelines = [
            MatchingTimelines(
                port_timeline(str(testee.name), timeline),
                port_timeline(SIBLING_TESTER_NAME, timeline),
            )
            for timeline in timelines
        ]

        MuscleTester._add_tester(config, test_model, SIBLING_TESTER_NAME, sibling_ports)

    @staticmethod
    def _add_tester(
        config: Configuration, test_model: Model, name: str, ports: list[Port]
    ) -> None:
        """Add a tester component and its MANUAL program.

        Args:
            config: The configuration to add the program to.
            test_model: The test model to add the component to.
            name: Name of the tester component and program.
            ports: The ports of the tester.
        """
        test_model.components[Reference(name)] = Component(
            name=name,
            ports=Ports(ports),
            description="Tester component for implementation testing",
            implementation=name,
            optional=False,
        )
        config.programs[Reference(name)] = Program(
            name=name,
            ports=Ports(ports),
            execution_model=ExecutionModel.MANUAL,
            description="Manual tester program for implementation testing",
        )

    @staticmethod
    def _connect_mirrored_port(
        test_model: Model, tester_name: str, testee: Implementation, port: Port
    ) -> Port:
        """Connect a port of the testee to a mirrored port of a tester.

        Args:
            test_model: The test model to add the conduit to.
            tester_name: Name of the tester component.
            testee: The testee.
            port: The port of the testee.

        Returns:
            The port of the tester, which sends if the testee receives and
            vice versa.
        """
        tester_port = f"{tester_name}.{port.name}"
        testee_port = f"{testee.name}.{port.name}"
        if port.operator.allows_receiving():
            conduit = Conduit(tester_port, testee_port)
            tester_operator = Operator.O_I
        else:
            conduit = Conduit(testee_port, tester_port)
            tester_operator = Operator.S

        test_model.conduits.append(conduit)
        return Port(port.name, tester_operator, port.timeline)

    def start_implementation(
        self,
        ymmsl_source: str | Path,
        implementation: str,
        *,
        default_timeout: float = 60,
    ) -> ImplementationTester:
        """Start a MUSCLE3 manager and return an ImplementationTester.

        Tester components are added and connected to all ports of the
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
        test_ymmsl_config = ymmsl.load_as(ymmsl.v0_2.Configuration, ymmsl_source)
        self._add_test_model(test_ymmsl_config, implementation)

        # Save the test configuration to a temporary file
        test_ymmsl_path = self.run_dir / "test_config.ymmsl"
        ymmsl.save(test_ymmsl_config, test_ymmsl_path)

        # The manager needs a flat configuration with resolved timelines
        for model in test_ymmsl_config.models.values():
            resolve_timelines(model)
        test_ymmsl_config = flatten(test_ymmsl_config, Reference(TEST_MODEL_NAME))

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
        try:
            self.implementation_tester = ImplementationTester(
                default_timeout, muscle_manager_address, test_ymmsl_config
            )
        except RuntimeError as exc:
            raise RuntimeError(
                f"Could not connect to the implementation '{implementation}'. Please"
                " check that it starts and runs correctly, e.g. that its executable"
                " exists. Its output can be found in"
                f" {self.run_dir / 'instances'}."
            ) from exc
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
