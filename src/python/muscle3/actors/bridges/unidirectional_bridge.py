"""Unidirectional time bridge

This time bridge receives data from a sender, on whichever timeline it's sending, and
receives a clock signal from the receiver indicating the timeline on which it's
receiving. The bridge then sends data received from the sender to the receiver,
selecting messages according to its settings.

Ports:
    data_in (sender S): Data input from the sender
    *_data_in (sender S): Multiple or additional data inputs from the sender
    clock_in (receiver S): Timing input from the receiver
    data_out (receiver O_I): Data output to the receiver
    *_data_out (receiver O_I): Multiple or additional data outputs to the receiver
"""

import logging
from typing import Any, Generic, TypeVar

from ymmsl import Operator

from libmuscle import Instance, Message

logger = logging.getLogger()


class ConfigError(RuntimeError):
    pass


def get_data_channels(instance: Instance) -> list[str]:
    """Inspect and return data channels.

    For each string "abc_" in the returned list, there exists an S port "abc_in" and an
    O_I port "abc_out".

    This checks the configured ports, and raises an error if the user did not follow the
    naming convention.

    Raises:
        ConfigError: If the ``clock_in`` port is missing or not connected, or if there
            is a data input port without a corresponding data output port, or vice
            versa.
    """
    in_ports = instance.list_ports()[Operator.S]
    data_out_ports = instance.list_ports()[Operator.O_I]

    if "clock_in" not in in_ports:
        raise ConfigError(
            "This time bridge needs a clock_in input. Please declare an S port with"
            " that name on the receiver's timeline, and connect it to an O_I port"
            " on the receiver."
        )

    data_in_ports = [p for p in in_ports if p != "clock_in"]

    if not data_in_ports and not data_out_ports:
        raise ConfigError(
            "No data ports specified. Please add at least one matching pair,"
            " and ensure that they use O_I and S operators."
        )

    wrong_ports = [p for p in data_in_ports if not p.endswith("data_in")]
    if wrong_ports:
        port_list = ", ".join(wrong_ports)
        raise ConfigError(
            "Data input ports must have a name that ends with 'data_in', but the"
            f" following port(s) are named differently: {port_list}"
        )

    wrong_ports = [p for p in data_out_ports if not p.endswith("data_out")]
    if wrong_ports:
        port_list = ", ".join(wrong_ports)
        raise ConfigError(
            "Data output ports must have a name that ends with 'data_out', but the"
            f" following port(s) are named differently: {port_list}"
        )

    in_prefixes = {p[:-7] for p in data_in_ports}
    out_prefixes = {p[:-8] for p in data_out_ports}

    if in_prefixes != out_prefixes:
        missing_outputs = in_prefixes - out_prefixes
        missing_inputs = out_prefixes - in_prefixes
        msg = "The configured data ports do not match."
        if missing_outputs:
            msg += " The following input ports do not have a corresponding output: "
            msg += ", ".join(sorted([f"{o}_in" for o in missing_outputs])) + "."
        if missing_inputs:
            msg += " The following output ports do not have a corresponding input: "
            msg += ", ".join(sorted([f"{o}_out" for o in missing_outputs])) + "."
        raise ConfigError(msg)

    return sorted(in_prefixes)


class Buffer:
    """Keeps received data while it's needed."""

    def __init__(self, channels: list[str]) -> None:
        """Create a Buffer.

        This stores a list of recently received messages and corresponding t_cur
        timestamps for each channel. The timestamps of the i'th message on each channel
        are assumed to be the same.

        Args:
            channels: list of channels to buffer data for, must contain at least one
                item.
        """
        self._data: dict[str, list[tuple[float, Any]]] = {chn: [] for chn in channels}
        self._rdata = self._data[channels[0]]
        """Used whenever we need a reference list."""

    def get_messages_in_range(
        self, begin: float, end: float | None
    ) -> dict[str, tuple[float, list[tuple[float, Any]]]]:
        """Return all messages with a timestamp between (inclusive) begin and end.

        Returns a list of timestamp, message tuples for each channel. If end is None,
        returns all messages after begin.

        Returns:
            A list of timestamp, data pairs for each channel.
        """
        if end is None:
            end = float("inf")

        i = 0
        while i < len(self._rdata) and self._rdata[i][0] < begin:
            i += 1
        j = i
        while j < len(self._rdata) and self._rdata[j][0] <= end:
            j += 1

        return {chn: (end, data[i:j]) for chn, data in self._data.items()}

    def get_messages_near(self, timestamp: float) -> dict[str, tuple[float, Any]]:
        """Get messages nearest the given timestamp.

        Returns a single message for each channel.

        Returns:
            A dict mapping channel name to message data.
        """
        i = 0
        while i < len(self._rdata) and self._rdata[i][0] < timestamp:
            i += 1

        if i == len(self._rdata):
            result = {
                chn: data[-1] if data else (timestamp, None)
                for chn, data in self._data.items()
            }
        else:
            if abs(self._rdata[i - 1][0] - timestamp) < abs(
                self._rdata[i][0] - timestamp
            ):
                i -= 1
            result = {chn: data[i] for chn, data in self._data.items()}

        return result

    def add(self, channel: str, timestamp: float, data: Any) -> None:
        """Add a received message to the buffer."""
        self._data[channel].append((timestamp, data))

    def remove_before_almost(self, timestamp: float) -> None:
        """Remove messages with a timestamp before the given one, except one.

        This finds the most recent message with a timestamp smaller than the given one,
        and then deletes everything before it.
        """
        i = 0
        while i < len(self._rdata) and self._rdata[i][0] < timestamp:
            i += 1

        if i > 0:
            i -= 1

        for data in self._data.values():
            # edit in place keeps self._rdata correct
            num_kept = len(data) - i
            data[:num_kept] = data[i:]
            del data[num_kept:]


_T = TypeVar("_T")


class ConsensusTimestamp(Generic[_T]):
    """Checks that received timestamps are consistent with others.

    Attributes:
        value: The consensus timestamp value
    """

    def __init__(self, name: str) -> None:
        """Create a checker.

        Args:
            name: Name of the timestamp we're checking, "current" or "next".
        """
        self._name = name
        self._first = True
        self._ref_chn: str
        self.value: _T

    def record(self, channel: str, val: _T) -> None:
        """Check that the received timestamp is consistent with others.

        Args:
            channel: Channel we received on
            val: Timestamp value that was received

        Raises:
            RuntimeError: if a mismatch is detected
        """
        if self._first:
            self._ref_chn = channel
            self.value = val
            self._first = False
        else:
            if self.value != val:
                raise RuntimeError(
                    f"Received {self._name} timestamp {val} on {channel}data_in,"
                    f" which is inconsistent with {self.value} received"
                    f" previously on {self._ref_chn}data_in"
                )


def receive_data(
    instance: Instance,
    buffer: Buffer,
    data_channels: list[str],
) -> tuple[float, float | None]:
    """Receive data on all channels and put it into the buffer."""
    cur_ts = ConsensusTimestamp[float]("current")
    next_ts = ConsensusTimestamp[float | None]("next")
    for chn in data_channels:
        data_msg = instance.receive(chn + "data_in")
        cur_ts.record(chn, data_msg.timestamp)
        next_ts.record(chn, data_msg.next_timestamp)
        buffer.add(chn, data_msg.timestamp, data_msg.data)

    return cur_ts.value, next_ts.value


def main() -> None:
    instance = Instance()

    try:
        data_channels = get_data_channels(instance)
        buffer = Buffer(data_channels)

        while instance.reuse_instance():
            theta = instance.get_setting("theta", "float", default=0.0)
            strict = instance.get_setting("strict_causality", "bool", default=True)
            all_in_window = instance.get_setting("all_in_window", "bool", default=False)

            recv_next: float | None = float("-inf")
            snd_cur: float = float("-inf")
            snd_next: float | None = float("-inf")
            while recv_next is not None:
                # Receive clock data from receiver
                clock_msg = instance.receive("clock_in")
                recv_cur = clock_msg.timestamp
                recv_next = clock_msg.next_timestamp

                # Receive any additional data we need from sender
                if recv_next is None:
                    recv_until = recv_cur
                else:
                    if all_in_window:
                        recv_until = recv_next
                    else:
                        recv_until = (1.0 - theta) * recv_cur + theta * recv_next

                while snd_next is not None and (
                    (snd_next if strict else snd_cur) < recv_until
                ):
                    snd_cur, snd_next = receive_data(instance, buffer, data_channels)

                buffer.remove_before_almost(recv_cur)

                # Send selected data to the receiver
                if all_in_window:
                    data = buffer.get_messages_in_range(recv_cur, recv_next)
                else:
                    data = buffer.get_messages_near(recv_until)

                for chn in data_channels:
                    instance.send(
                        chn + "data_out", Message(data[chn][0], recv_next, data[chn][1])
                    )

            # Get unused sent messages, so any next pass doesn't get them
            while snd_next is not None:
                snd_cur, snd_next = receive_data(instance, buffer, data_channels)

    except RuntimeError as e:
        instance.error_shutdown(str(e))


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
