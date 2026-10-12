import logging
from logging import Logger
from pathlib import Path
from random import uniform

import pytest
from ymmsl import Operator

from libmuscle import Instance, Message
from muscle3.actors.bridges.unidirectional_bridge import main as bridge
from muscle3.test.conftest import run_manager_with_actors


class Sender:
    """Implements a testing sender."""

    def __init__(
        self,
        instance: Instance,
        logger: Logger,
        t_start: float,
        t_end: float,
        strict: bool,
    ) -> None:
        self._instance = instance
        self._logger = logger
        self._t_end = t_end
        self._strict = strict

        self._first = True
        self._t_cur = t_start
        self._t_next: float | None = -30.0
        self.sent_msgs: list[Message] = []

    def send_until(self, until: float) -> None:
        """Run and send until the given time point, or just past if not strict.

        Always sends the first message, since it's based only on the initial state and
        therefore cannot cause a deadlock; the bridge always receives the first message
        to get an initial timestamp for the sender so we have to do it to avoid
        deadlock.
        """
        while self._first or (self._t_cur < until and self._t_next is not None):
            self._do_step()
            self._first = False

        if (
            not self._strict
            and (not self.sent_msgs or self.sent_msgs[-1].timestamp < until)
            and self._t_next is not None
        ):
            self._do_step()

        self._logger.debug("Sender done")

    def sent_in_window(self, begin: float, end: float) -> list[Message]:
        """Return all sent messages with a timestamp within the window.

        Ends are inclusive.
        """
        i = 0
        while i < len(self.sent_msgs) and self.sent_msgs[i].timestamp < begin:
            i += 1
        j = i
        while j < len(self.sent_msgs) and self.sent_msgs[j].timestamp <= end:
            j += 1
        return self.sent_msgs[i:j]

    def _do_step(self) -> None:
        """Move the sender one O_I/S step forward, sending on O_I."""
        # o_i
        self._t_next = self._t_cur + 10 ** uniform(-2.0, 0.0)
        if self._t_end < self._t_next:
            self._t_next = None
        self._logger.debug(
            "Sender sending at %s with next %s", self._t_cur, self._t_next
        )
        msg = Message(self._t_cur, self._t_next, self._t_cur)
        self._instance.send("data_out", msg)
        self.sent_msgs.append(msg)

        # s
        if self._t_next is not None:
            self._t_cur = self._t_next


def bridge_tester() -> None:
    logger = logging.getLogger("bridge_tester")
    instance = Instance(
        {Operator.O_I: ["data_out", "clock_out"], Operator.S: ["data_in"]}
    )

    while instance.reuse_instance():
        # f_init
        theta = instance.get_setting("theta", "float")
        strict = instance.get_setting("strict_causality", "bool")
        all_in_window = instance.get_setting("all_in_window", "bool")

        t_start_recv = uniform(-20.0, 20.0)
        t_start_snd = uniform(-20.0, 20.0)
        t_end = max(t_start_snd, t_start_recv) + uniform(10.0, 20.0)

        snd = Sender(instance, logger, t_start_snd, t_end, strict)

        recv_t_cur = t_start_recv
        while recv_t_cur < t_end:
            recv_t_next = recv_t_cur + 10 ** uniform(-2.0, 1.0)
            logger.debug("recv_t_cur = %s, recv_t_next = %s", recv_t_cur, recv_t_next)

            # receiver o_i
            instance.send("clock_out", Message(recv_t_cur, recv_t_next, None))

            # sender
            if all_in_window:
                snd_until = recv_t_next
            else:
                snd_until = (1.0 - theta) * recv_t_cur + theta * recv_t_next
            snd.send_until(snd_until)

            # receiver s
            msg = instance.receive("data_in")
            logger.debug("Received data %s at %s", msg.data, msg.timestamp)

            logger.debug(
                "Last sent: %s %s",
                snd.sent_msgs[-2].timestamp if len(snd.sent_msgs) > 1 else None,
                snd.sent_msgs[-1].timestamp if snd.sent_msgs else None,
            )
            if all_in_window:
                assert msg.timestamp == recv_t_cur
                assert msg.next_timestamp == recv_t_next
                exp_msgs = snd.sent_in_window(recv_t_cur, recv_t_next)
                for i, exp_msg in enumerate(exp_msgs):
                    assert msg.data[i] == [exp_msg.timestamp, exp_msg.data]
            else:
                if not snd.sent_msgs:
                    assert msg.data is None
                else:
                    if strict or len(snd.sent_msgs) < 2:
                        expected = snd.sent_msgs[-1]
                    else:
                        req_time = (1.0 - theta) * recv_t_cur + theta * recv_t_next
                        if abs(snd.sent_msgs[-2].timestamp - req_time) < abs(
                            snd.sent_msgs[-1].timestamp - req_time
                        ):
                            expected = snd.sent_msgs[-2]
                        else:
                            expected = snd.sent_msgs[-1]

                    assert msg.timestamp == expected.timestamp
                    assert msg.next_timestamp == recv_t_next
                    assert msg.data == expected.data

            recv_t_cur = recv_t_next


CONFIG = """
ymmsl_version: v0.2

imports:
- from muscle3.actors.bridges import implementation unidirectional_bridge

models:
  test_unidir_bridge:
    description: Test setup for the unidirectional bridge
    components:
      bridge_tester:
        ports:
          timeline sender:
            o_i: data_out
          timeline receiver:
            o_i: clock_out
            s: data_in
        description: Tester component
        implementation: bridge_tester
      bridge:
        ports:
          timeline sender:
            s: data_in
          timeline receiver:
            o_i: data_out
            s: clock_in
        description: Bridge component to be tested
        implementation: unidirectional_bridge

    matching_timelines:
      bridge_tester.sender: bridge.sender
      bridge_tester.receiver: bridge.receiver

    conduits:
      bridge_tester.data_out: bridge.data_in
      bridge_tester.clock_out: bridge.clock_in
      bridge.data_out: bridge_tester.data_in

settings:
  theta: {theta}
  strict_causality: {strict}
  all_in_window: {all_in_window}
"""


@pytest.mark.parametrize("theta", [0.0, 0.5, 1.0])
@pytest.mark.parametrize("strict", ["true", "false"])
def test_uni_bridge_single(tmp_path: Path, theta: float, strict: bool) -> None:
    run_manager_with_actors(
        CONFIG.format(theta=theta, strict=strict, all_in_window="false"),
        tmp_path,
        {"bridge_tester": ("python", bridge_tester), "bridge": ("python", bridge)},
    )


@pytest.mark.parametrize("strict", ["true", "false"])
def test_uni_bridge_all(tmp_path: Path, strict: bool) -> None:
    run_manager_with_actors(
        CONFIG.format(theta="0.0", strict=strict, all_in_window="true"),
        tmp_path,
        {"bridge_tester": ("python", bridge_tester), "bridge": ("python", bridge)},
    )
