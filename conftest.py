import threading

import pytest


@pytest.fixture(autouse=True)
def assert_all_threads_closed():
    active_threads_before_test = len(threading.enumerate())
    yield
    assert active_threads_before_test == len(threading.enumerate())


@pytest.fixture(scope="session", autouse=True)
def assert_no_threads_left():
    # other than the main
    yield
    assert len(threading.enumerate()) == 1
