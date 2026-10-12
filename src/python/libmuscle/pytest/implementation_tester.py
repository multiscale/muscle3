import logging
import os
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import TypeVar
from unittest.mock import patch

from ymmsl.v0_2 import Configuration, Operator, Program, Reference, Settings

from libmuscle import Instance, Message
from libmuscle.instance import _thread_instance_name

_logger = logging.getLogger(__name__)

T = TypeVar("T")


PARENT_TESTER_NAME = "muscle3_tester_parent"
"""Tester connected to the F_INIT and O_F ports of the testee."""

SIBLING_TESTER_NAME = "muscle3_tester_sibling"
"""Tester connected to the O_I and S ports of the testee."""

PARENT_SETTINGS_PORT_NAME = "__settings_in__"
"""Port of the parent tester connected to the testee's muscle_settings_in."""

SIBLING_SETTINGS_PORT_NAME = "__sibling_settings_out__"
"""Port of the parent tester connected to the sibling's muscle_settings_in."""


def _run_concurrently(
    tasks: dict[str, Callable[[], T]],
) -> tuple[dict[str, T], list[BaseException]]:
    """Run the given tasks concurrently and wait for all of them.

    Each task gets its own thread, since the tasks may wait for each other. A single
    task is run directly in the calling thread.

    Args:
        tasks: The functions to run, by name.

    Returns:
        The results of the tasks that succeeded, by name, and the exceptions raised
        by the tasks that failed.
    """
    if len(tasks) == 1:
        ((name, task),) = tasks.items()
        try:
            return {name: task()}, []
        except Exception as exc:
            return {}, [exc]

    with ThreadPoolExecutor(
        max_workers=len(tasks), thread_name_prefix="ImplementationTester"
    ) as pool:
        futures = {name: pool.submit(task) for name, task in tasks.items()}

    results: dict[str, T] = {}
    errors: list[BaseException] = []
    for name, future in futures.items():
        error = future.exception()
        if error is None:
            results[name] = future.result()
        else:
            errors.append(error)
    return results, errors


class ImplementationTester:
    """
    The ImplementationTester creates the MUSCLE3 Instances that act as the "tester"
    components, which are connected to the implementation under test, the
    testee.

    There are up to two tester components, both with only O_I and S ports:
    - The parent tester is connected to the F_INIT and O_F ports of the
      testee, and acts as its parent ("macro").
    - The sibling tester is connected to the O_I and S ports of the testee, and
      interacts with it as a peer on a matching timeline.

    Sends and receives are forwarded to the component that has a port with the given
    name. Every time the parent tester starts a new round of messages to the
    testee's F_INIT ports, it also sends a message to the sibling, so that
    the sibling's reuse loop runs in step with that of the testee.
    """

    def __init__(
        self,
        default_timeout: float,
        muscle_manager_address: str,
        test_ymmsl_config: Configuration,
    ) -> None:
        """
        Initialize the implementation tester.

        Args:
            default_timeout: Default timeout for receive operations in seconds.
            muscle_manager_address: Network location of the MUSCLE3 manager.
            test_ymmsl_config: The configuration containing the tester programs.
        """
        self._default_timeout = default_timeout
        self._is_shut_down = False

        programs = {
            name: test_ymmsl_config.programs[Reference(name)]
            for name in (PARENT_TESTER_NAME, SIBLING_TESTER_NAME)
            if Reference(name) in test_ymmsl_config.programs
        }

        instances = self._create_instances(programs, muscle_manager_address)

        self._parent = instances[PARENT_TESTER_NAME]
        self._sibling = instances.get(SIBLING_TESTER_NAME)

        self._parent_ports = {
            str(port)
            for port in programs[PARENT_TESTER_NAME].ports
            if port != SIBLING_SETTINGS_PORT_NAME
        }
        """Ports connected to the testee's F_INIT and O_F ports."""
        self._sibling_ports: set[str] = set()
        """Ports connected to the testee's O_I and S ports."""
        if SIBLING_TESTER_NAME in programs:
            self._sibling_ports = {str(p) for p in programs[SIBLING_TESTER_NAME].ports}

        self._round_sent: set[tuple[str, int | None]] = set()
        """F_INIT ports and slots sent to in the current round of messages."""

        for instance in instances.values():
            instance._communicator.set_receive_timeout(default_timeout)

        # The parent tester has no F_INIT ports, so we can start its reuse loop
        # straight away
        self._parent.reuse_instance()

        # Without F_INIT ports, the testee's reuse loop is driven through its
        # muscle_settings_in, so start its first round there
        if PARENT_SETTINGS_PORT_NAME in self._parent_ports:
            msg = Message(float("-inf"), data=Settings())
            self._send_f_init(PARENT_SETTINGS_PORT_NAME, msg, None)

    def send(self, port_name: str, message: Message, slot: int | None = None) -> None:
        """
        Send a message on the specified port.

        Args:
            port_name: Name of the port to send on.
            message: The message to send.
            slot: Optional slot number for vector ports.

        Raises:
            ValueError: If the testee has no port with this name.
            RuntimeError: If the message cannot be sent, e.g. because the previous
                round of messages is not finished.

        On an error, all tester instances are shut down.
        """
        if port_name == "muscle_settings_in":
            port_name = PARENT_SETTINGS_PORT_NAME

        try:
            if port_name in self._parent_ports:
                self._send_f_init(port_name, message, slot)
            elif self._sibling is not None and port_name in self._sibling_ports:
                self._check_round_started(port_name)
                self._sibling.send(port_name, message, slot)
            else:
                raise self._unknown_port_error(port_name)
        except (RuntimeError, ValueError) as exc:
            _logger.error(
                "ImplementationTester: error on port '%s'. Shutting down.", port_name
            )
            self._shut_down_all(str(exc))
            raise

    def receive(
        self,
        port_name: str,
        slot: int | None = None,
        *,
        timeout: float | None = None,
    ) -> Message:
        """
        Receive a message from the specified port.

        Args:
            port_name: Name of the port to receive from.
            slot: Optional slot number for vector ports.
            timeout: Timeout in seconds. If None, uses default_timeout.

        Raises:
            ValueError: If the testee has no port with this name.
            RuntimeError: If receiving is not allowed yet, a deadlock is detected, or
                the connection to the testee was lost.

        On an error, all tester instances are shut down.
        """
        if timeout is None:
            timeout = self._default_timeout

        try:
            if port_name in self._parent_ports:
                instance = self._parent
            elif self._sibling is not None and port_name in self._sibling_ports:
                self._check_round_started(port_name)
                instance = self._sibling
            else:
                raise self._unknown_port_error(port_name)

            instance._communicator.set_receive_timeout(timeout)
            return instance.receive(port_name, slot)
        except (RuntimeError, ValueError) as exc:
            _logger.error(
                "ImplementationTester: error on port '%s'. Shutting down.", port_name
            )
            self._shut_down_all(str(exc))
            raise

    def cleanup(self) -> None:
        """Clean up the tester instances.

        Safe to call even if the instances were already shut down after an error.

        Raises:
            RuntimeError: If the test did not finish its last round of messages.
        """
        if self._is_shut_down:
            return

        self._is_shut_down = True

        # A tester shuts down by sending the final milestone, and then waits for the
        # testee's final milestone, which it only sends once the other tester
        # has shut down too. So we finish both reuse loops concurrently. The parent's
        # loop ends right away, as it has no F_INIT ports, and its final milestone
        # ends the loops of the sibling and the testee.
        _, errors = _run_concurrently(
            {
                name: partial(self._finish, instance)
                for name, instance in self._instances().items()
            }
        )
        if errors:
            raise errors[0]

    @staticmethod
    def _finish(instance: Instance) -> None:
        """Run the reuse loop of a tester instance until it ends.

        On an error, the instance is shut down, so that others stop waiting for it.
        """
        try:
            while instance.reuse_instance():
                pass
        except RuntimeError as exc:
            instance.error_shutdown(str(exc))
            raise

    def _instances(self) -> dict[str, Instance]:
        """Return the tester instances by name."""
        instances = {PARENT_TESTER_NAME: self._parent}
        if self._sibling is not None:
            instances[SIBLING_TESTER_NAME] = self._sibling
        return instances

    def _create_instances(
        self, programs: dict[str, Program], muscle_manager_address: str
    ) -> dict[str, Instance]:
        """Create the Instances for the tester components.

        The constructor of an Instance waits until all its peers have registered, and
        the parent and sibling are peers, so they are created concurrently.

        Args:
            programs: The programs of the tester components, by name.
            muscle_manager_address: Network location of the MUSCLE3 manager.

        Returns:
            The Instances, by tester component name.
        """
        # The manager address is the same for all testers, so we can pass it through
        # the environment, which is shared by all threads
        with patch.dict(os.environ, {"MUSCLE_MANAGER": muscle_manager_address}):
            instances, errors = _run_concurrently(
                {
                    name: partial(self._create_instance, name, program)
                    for name, program in programs.items()
                }
            )

        if errors:
            # Don't leave the Instances that we did create waiting for their peers
            for instance in instances.values():
                instance.error_shutdown(str(errors[0]))
            raise errors[0]

        return instances

    @staticmethod
    def _create_instance(name: str, program: Program) -> Instance:
        """Create the Instance for a tester component.

        The instance name is passed through a thread-local variable, as the command
        line and the environment are shared by all threads.

        Args:
            name: Name of the tester component.
            program: The program of the tester component.

        Returns:
            The created Instance.
        """
        ports = {
            Operator.O_I: [str(p) for p in program.ports.sending_port_names()],
            Operator.S: [str(p) for p in program.ports.receiving_port_names()],
        }
        _thread_instance_name.value = name
        try:
            return Instance(ports)
        finally:
            _thread_instance_name.value = None

    def _send_f_init(self, port_name: str, message: Message, slot: int | None) -> None:
        """Send a message to an F_INIT port of the testee."""
        self._parent.send(port_name, message, slot)
        self._update_round(port_name, slot, message.timestamp)

    def _update_round(self, port_name: str, slot: int | None, timestamp: float) -> None:
        """Update the round after a message was sent to an F_INIT port of the testee.

        A round is one reuse loop iteration of the testee. Sending again on a port and
        slot that was already sent on in this round starts a new round. The sibling
        then starts its next reuse loop iteration too, so that it stays in step with
        the testee.

        Args:
            port_name: The F_INIT port that was sent on.
            slot: The slot that was sent on, if any.
            timestamp: Timestamp of the message that was sent.

        Raises:
            RuntimeError: If the sibling did not finish its previous iteration.
        """
        new_round = not self._round_sent or (port_name, slot) in self._round_sent
        if new_round:
            self._round_sent.clear()
            if self._sibling is not None:
                msg = Message(timestamp, data=Settings())
                self._parent.send(SIBLING_SETTINGS_PORT_NAME, msg)
                self._sibling.reuse_instance()
        self._round_sent.add((port_name, slot))

    def _check_round_started(self, port_name: str) -> None:
        """Check that the test may send or receive on the given port of the sibling.

        The testee first receives on its F_INIT ports and only then uses its O_I and S
        ports, so the test must send on the F_INIT ports before using the sibling's
        ports. libmuscle does not check this, because the F_INIT ports belong to the
        parent and the sibling is not in its reuse loop yet. Without this check, a
        send would fail on an internal assertion and a receive would time out.

        Raises:
            RuntimeError: If no message was sent on the testee's F_INIT ports yet.
        """
        if not self._round_sent:
            raise RuntimeError(
                f"Cannot use port '{port_name}' before sending a message on the"
                " implementation's F_INIT ports."
            )

    def _unknown_port_error(self, port_name: str) -> ValueError:
        """Return the error for a port that the testee does not have."""
        ports = sorted(
            (self._parent_ports | self._sibling_ports) - {PARENT_SETTINGS_PORT_NAME}
        )
        return ValueError(
            f"The implementation has no port named '{port_name}'. Available ports"
            f" are: {', '.join(ports)}"
        )

    def _shut_down_all(self, message: str) -> None:
        """Shut down all tester instances after an error.

        Like in cleanup(), each tester waits for the testee's final milestone,
        so they are shut down concurrently.
        """
        self._is_shut_down = True
        _, errors = _run_concurrently(
            {
                name: partial(instance.error_shutdown, message)
                for name, instance in self._instances().items()
            }
        )
        for error in errors:
            _logger.error("ImplementationTester: error while shutting down: %s", error)
