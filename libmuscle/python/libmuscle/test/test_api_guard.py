from typing import Callable, Set

import pytest

from libmuscle.api_guard import APIGuard


def test_no_checkpointing_support():
    guard = APIGuard(False)
    for _ in range(3):
        guard.verify_reuse_instance()
        guard.reuse_instance_done(True)

    guard.verify_reuse_instance()
    guard.reuse_instance_done(False)


def test_final_snapshot_only(guard: APIGuard):
    for i in range(4):
        guard.verify_reuse_instance()
        guard.reuse_instance_done(True)

        guard.verify_resuming()
        if i == 0:
            guard.resuming_done(True)

            guard.verify_load_snapshot()
            guard.load_snapshot_done()
        else:
            guard.resuming_done(False)

        guard.verify_should_init()
        guard.should_init_done()

        guard.verify_should_save_final_snapshot()
        if i == 2:
            guard.should_save_final_snapshot_done(True)

            guard.verify_save_final_snapshot()
            guard.save_final_snapshot_done()
        else:
            guard.should_save_final_snapshot_done(False)

    guard.verify_reuse_instance()
    guard.reuse_instance_done(False)


def test_full_checkpointing(guard: APIGuard):
    for i in range(4):
        guard.verify_reuse_instance()
        guard.reuse_instance_done(True)

        guard.verify_resuming()
        if i == 0:
            guard.resuming_done(True)

            guard.verify_load_snapshot()
            guard.load_snapshot_done()
        else:
            guard.resuming_done(False)

        guard.verify_should_init()
        guard.should_init_done()

        for j in range(3):
            guard.verify_should_save_snapshot()
            if j != 2:
                guard.should_save_snapshot_done(True)

                guard.verify_save_snapshot()
                guard.save_snapshot_done()
            else:
                guard.should_save_snapshot_done(False)

        guard.verify_should_save_final_snapshot()
        if i == 2:
            guard.should_save_final_snapshot_done(True)

            guard.verify_save_final_snapshot()
            guard.save_final_snapshot_done()
        else:
            guard.should_save_final_snapshot_done(False)

    guard.verify_reuse_instance()
    guard.reuse_instance_done(False)


_api_guard_funs = (
    (APIGuard.verify_reuse_instance, ()),
    (APIGuard.reuse_instance_done, (True,)),
    (APIGuard.verify_resuming, ()),
    (APIGuard.resuming_done, (True,)),
    (APIGuard.verify_load_snapshot, ()),
    (APIGuard.load_snapshot_done, ()),
    (APIGuard.verify_should_init, ()),
    (APIGuard.should_init_done, ()),
    (APIGuard.verify_should_save_snapshot, ()),
    (APIGuard.should_save_snapshot_done, (True,)),
    (APIGuard.verify_save_snapshot, ()),
    (APIGuard.save_snapshot_done, ()),
    (APIGuard.verify_should_save_final_snapshot, ()),
    (APIGuard.should_save_final_snapshot_done, (True,)),
    (APIGuard.verify_save_final_snapshot, ())
)


def run_until_before(guard: APIGuard, excluded: Callable) -> None:
    for fun, args in _api_guard_funs:
        if fun is excluded:
            break
        fun(guard, *args)


def check_all_raise_except(guard: APIGuard, excluded: Set[Callable]) -> None:
    for fun, args in _api_guard_funs:
        if fun.__name__.startswith('verify_'):
            if fun not in excluded:
                with pytest.raises(RuntimeError):
                    fun(guard, *args)
            else:
                fun(guard, *args)


@pytest.mark.parametrize('fun', [
        APIGuard.verify_load_snapshot,
        APIGuard.verify_should_init, APIGuard.verify_save_snapshot,
        APIGuard.verify_save_final_snapshot])
def test_missing_step(guard, fun):
    run_until_before(guard, fun)
    check_all_raise_except(guard, {fun})


def test_missing_resuming(guard: APIGuard):
    run_until_before(guard, APIGuard.verify_resuming)
    check_all_raise_except(guard, {APIGuard.verify_resuming})


def test_missing_should_save_final(guard: APIGuard):
    run_until_before(guard, APIGuard.verify_should_save_final_snapshot)
    check_all_raise_except(guard, {
        APIGuard.verify_should_save_snapshot,
        APIGuard.verify_should_save_final_snapshot})


def test_double_should_save(guard: APIGuard):
    run_until_before(guard, APIGuard.verify_should_save_snapshot)
    guard.verify_should_save_snapshot()
    guard.should_save_snapshot_done(True)
    with pytest.raises(RuntimeError):
        guard.verify_should_save_snapshot()
