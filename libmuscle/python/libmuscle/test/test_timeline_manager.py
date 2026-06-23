import pytest
from ymmsl.v0_2 import Operator

from libmuscle.port_manager import PortManager
from libmuscle.timeline_manager import TimelineManager


@pytest.fixture
def port_manager() -> PortManager:
    declared_ports = {
            Operator.O_I: ['out'],
            Operator.S: ['in']}
    return PortManager([13], declared_ports)


@pytest.fixture
def timeline_manager(port_manager: PortManager) -> TimelineManager:
    return TimelineManager(port_manager)


def test_init(timeline_manager: TimelineManager) -> None:
    assert timeline_manager._iteration is None
