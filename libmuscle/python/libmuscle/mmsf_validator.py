import logging
import sys
import types
from typing import List, Optional

from libmuscle.port_manager import PortManager
from ymmsl import Operator


_logger = logging.getLogger(__name__)


class MMSFValidator:
    """The MMSF Validator checks whether Instances are following the Multiscale
    Modelling and Simulation Framework when sending and receiving messages.

    In particular it checks that in order:

    1. reuse_instance() is called
    2. Messages are received on all F_INIT ports
    3. The following sub-items happen in order, 0 or more times:

        a. Messages are sent on all O_I ports
        b. Messages are received on all S ports

    4. Messages are sent on all O_F ports

    If any message is sent or received out of order, a warning is logged to indicate
    that the instance is not following the MMSF pattern. In some cases (for example the
    time bridge in ``examples/python/interact_coupling.py``) this is expected and the
    warnings can be disabled by setting the
    :attr:`~libmuscle.instance.InstanceFlags.SKIP_MMSF_SEQUENCE_CHECKS` flag.

    Note:
        Checks on vector ports are not implemented. When the instance uses vector ports,
        the MMSF Validator will be disabled.
    """
    def __init__(self, port_manager: PortManager) -> None:
        self._port_manager = port_manager

        port_names = port_manager.list_ports()
        port_objects = {
                operator: [port_manager.get_port(name) for name in names]
                for operator, names in port_names.items()}
        self._connected_ports = {
                operator: [str(port.name) for port in ports if port.is_connected()]
                for operator, ports in port_objects.items()}
        self._port_operators = {
                port: operator
                for operator, ports in port_names.items()
                for port in ports}

        # Allowed operator transitions, the following are unconditionally allowed:
        self._allowed_transitions = {
                (Operator.NONE, Operator.NONE),
                (Operator.NONE, Operator.F_INIT),
                (Operator.F_INIT, Operator.O_I),
                (Operator.F_INIT, Operator.O_F),
                (Operator.O_I, Operator.S),
                (Operator.S, Operator.O_I),
                (Operator.S, Operator.O_F),
                (Operator.O_F, Operator.NONE),
                }
        # If there are operators without connected ports, we can skip over those
        for operator in [Operator.F_INIT, Operator.O_I, Operator.S, Operator.O_F]:
            if not self._connected_ports.get(operator, []):
                # Find all transitions A -> operator -> B and allow transition A -> B:
                skip_from = []
                skip_to = []
                for from_op, to_op in self._allowed_transitions:
                    if from_op is operator:
                        skip_to.append(to_op)
                    if to_op is operator:
                        skip_from.append(from_op)
                for from_op in skip_from:
                    for to_op in skip_to:
                        self._allowed_transitions.add((from_op, to_op))

        # Disable this validator when the instance uses vector ports to keep this class
        # simpler. Support for vector ports may be added in the future.
        self._enabled = not any(
                port.is_vector() for ports in port_objects.values() for port in ports)
        _logger.debug(
                "MMSF Validator is %s", "enabled" if self._enabled else "disabled")

        # State tracking
        self._current_ports_used: List[str] = []
        self._current_operator: Operator = Operator.NONE

    def check_send(self, port_name: str, slot: Optional[int]) -> None:
        """Check that sending on the provided port adheres to the MMSF."""
        self._check_send_receive(port_name, slot)

    def check_receive(self, port_name: str, slot: Optional[int]) -> None:
        """Check that receiving on the provided port adheres to the MMSF."""
        self._check_send_receive(port_name, slot)

    def reuse_instance(self) -> None:
        """Check that a reuse_instance() adheres to the MMSF."""
        if not self._enabled:
            return
        self._check_transition(Operator.NONE)

    def skip_f_init(self) -> None:
        """Call when resuming from an intermediate snapshot: F_INIT is skipped."""
        # Pretend we're now in F_INIT and we have already received on all F_INIT ports:
        self._current_operator = Operator.F_INIT
        self._current_ports_used = self._connected_ports.get(Operator.F_INIT, [])

    def _check_send_receive(
            self, port_name: str, slot: Optional[int]) -> None:
        """Actual implementation of check_send/check_receive."""
        if not self._enabled:
            return

        operator = self._port_operators[port_name]
        if self._current_operator != operator:
            # Operator changed, check that all ports were used in the previous operator
            self._check_transition(operator, port_name)

        if port_name in self._current_ports_used:
            # We're using the same port for a second time, this is fine when we're
            # allowed to do this operator immediately again:
            self._check_transition(operator, port_name)

        self._current_ports_used.append(port_name)

    def _check_transition(self, operator: Operator, port_name: str = "") -> None:
        """Check that a transition to the provided operator is allowed.

        Log a warning when the transition does not adhere to the MMSF.

        Args:
            operator: Operator to transition to.
            port_name: The name of the port that was sent/receveived on. This is only
                used for constructing the warning message.
        """
        connected_ports = self._connected_ports.get(self._current_operator, [])
        expected: str = ""

        unused_ports = [
                port for port in connected_ports
                if port not in self._current_ports_used]
        if unused_ports:
            # We didn't complete the current phase
            if self._current_operator in (Operator.F_INIT, Operator.S):
                expected = "a receive"
            else:
                expected = "a send"
            expected += (
                    f" on any of these {self._current_operator.name} ports: "
                    + ", ".join(unused_ports))

        elif (self._current_operator, operator) not in self._allowed_transitions:
            # Transition to the operator is not allowed, now figure out what we were
            # actually expecting.
            # First find the allowed transitions from self._current_operator, that are
            # also 'valid' (i.e. have connected ports):
            allowed = [
                    to_op for from_op, to_op in self._allowed_transitions
                    if from_op is self._current_operator and
                    (to_op in self._connected_ports or to_op is Operator.NONE)]
            # Build the message we want to display to users:
            expected_lst = []
            for to_op in sorted(allowed, key=lambda op: op.value):
                ports = ', '.join(map(repr, self._connected_ports.get(to_op, [])))
                if to_op is Operator.NONE:
                    expected_lst.append("a call to reuse_instance()")
                elif to_op in (Operator.F_INIT, Operator.S):
                    expected_lst.append(f"a receive on an {to_op.name} port ({ports})")
                else:
                    expected_lst.append(f"a send on an {to_op.name} port ({ports})")
            assert expected_lst
            expected = " or ".join(expected_lst)

        if expected:
            # We expected something else, log a warning:
            if operator is Operator.NONE:
                action = "reuse_instance()"
            elif operator in (Operator.F_INIT, Operator.S):
                action = f"Receive on port '{port_name}'"
            else:
                action = f"Send on port '{port_name}'"

            # Find the file:line where the user called send/receive/reuse_instance
            try:
                frame: Optional[types.FrameType] = sys._getframe()
            except Exception:
                frame = None  # sys._getframe() is not guaranteed available
            while (frame
                    and frame.f_globals.get("__name__", "").startswith("libmuscle.")):
                # This frame is still part of a libmuscle module, step up:
                frame = frame.f_back
            loc = f" ({frame.f_code.co_filename}:{frame.f_lineno})" if frame else ""

            _logger.warning(
                "%s%s does not adhere to the MMSF: was expecting %s.\n"
                "Not adhering to the Multiscale Modelling and Simulation Framework "
                "may lead to deadlocks. You can disable this warning by "
                "setting the flag InstanceFlags.SKIP_MMSF_SEQUENCE_CHECKS "
                "when creating the libmuscle.Instance.",
                action, loc, expected)

        self._current_operator = operator
        self._current_ports_used = []
