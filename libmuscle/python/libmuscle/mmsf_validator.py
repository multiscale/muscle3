import logging
import sys
import types
from typing import List, Optional

from libmuscle.port_manager import PortManager
from ymmsl import Operator


_logger = logging.getLogger(__name__)


class MMSFValidator:
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
        self._check_send_receive(port_name, slot)

    def check_receive(self, port_name: str, slot: Optional[int]) -> None:
        self._check_send_receive(port_name, slot)

    def reuse_instance(self) -> None:
        if not self._enabled:
            return
        self._check_transition(Operator.NONE)

    def _check_send_receive(
            self, port_name: str, slot: Optional[int]) -> None:
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
        connected_ports = self._connected_ports.get(self._current_operator, [])
        expected: str = ""

        unused_ports = [
                port for port in connected_ports
                if port not in self._current_ports_used]
        if unused_ports:
            # We didn't complete the current phase
            if operator in (Operator.F_INIT, Operator.S):
                expected = "a receive"
            else:
                expected = "a send"
            expected += " on any of these ports: " + ", ".join(unused_ports)

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
            file_and_line = ""
            try:
                # Try to find the file:line where the user called
                # Instance.send/receive/reuse_instance
                frame: Optional[types.FrameType] = sys._getframe()
                while frame and frame.f_code.co_qualname.startswith("MMSFValidator."):
                    frame = frame.f_back
                while (frame
                       and frame.f_code.co_filename.endswith("libmuscle/instance.py")):
                    frame = frame.f_back
                if frame:
                    code = frame.f_code
                    file_and_line = f" ({code.co_filename}:{code.co_firstlineno})"
            except Exception:
                pass
            _logger.warning(
                "%s%s does not adhere to the MMSF: was expecting %s. "
                "Not adhering to the Multiscale Modelling and Simulation Framework "
                "may lead to deadlocks. You can disable this warning by "
                "setting the flag InstanceFlags.SKIP_MMSF_SEQUENCE_CHECKS "
                "when creating the libmuscle.Instance.",
                action, file_and_line, expected)

        self._current_operator = operator
        self._current_ports_used = []
