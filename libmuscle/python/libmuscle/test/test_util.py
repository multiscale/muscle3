from typing import List

import pytest
from ymmsl import Reference

from libmuscle.util import instance_indices, instance_to_kernel


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
