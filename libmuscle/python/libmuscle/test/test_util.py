from typing import List

import pytest
from ymmsl import Conduit, Reference

from libmuscle.util import (conduit_to_grpc, instance_indices,
                            instance_to_kernel)


def test_conduit_to_grpc() -> None:
    conduit = Conduit(Reference('kernel1.out'), Reference('kernel2.in'))
    mmp_conduit = conduit_to_grpc(conduit)
    assert mmp_conduit.sender == 'kernel1.out'
    assert mmp_conduit.receiver == 'kernel2.in'


@pytest.fixture
def instances() -> List[Reference]:
    return [
        Reference('test'),
        Reference('test.test'),
        Reference('test[4]'),
        Reference('test[3][2]'),
        Reference('test.test[3]'),
        Reference('test.test[1][2]')]


def test_instance_to_kernel(instances: List[Reference]) -> None:
    assert instance_to_kernel(instances[0]) == 'test'
    assert instance_to_kernel(instances[1]) == 'test.test'
    assert instance_to_kernel(instances[2]) == 'test'
    assert instance_to_kernel(instances[3]) == 'test'
    assert instance_to_kernel(instances[4]) == 'test.test'
    assert instance_to_kernel(instances[5]) == 'test.test'


def test_instance_indices(instances: List[Reference]) -> None:
    assert instance_indices(instances[0]) == []
    assert instance_indices(instances[1]) == []
    assert instance_indices(instances[2]) == [4]
    assert instance_indices(instances[3]) == [3, 2]
    assert instance_indices(instances[4]) == [3]
    assert instance_indices(instances[5]) == [1, 2]
