import threading

import pytest


@pytest.fixture(autouse=True)
def assert_no_threads_left():
    assert len(threading.enumerate()) == 1
    yield
    assert len(threading.enumerate()) == 1
