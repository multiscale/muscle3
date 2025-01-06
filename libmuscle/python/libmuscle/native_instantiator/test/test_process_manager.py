from time import monotonic, sleep

import pytest

from libmuscle.native_instantiator.process_manager import ProcessManager


@pytest.fixture
def lpm():
    return ProcessManager()


def _poll_completion(lpm, num_jobs):
    completed_jobs = list()
    while len(completed_jobs) < num_jobs:
        done = lpm.get_finished()
        while not done:
            sleep(0.1)
            done = lpm.get_finished()
        completed_jobs.extend(done)

    return completed_jobs


def test_run_process(lpm, tmp_path):
    lpm.start(
            'test', tmp_path, ['bash', '-c', 'exit 0'], {},
            tmp_path / 'out', tmp_path / 'err')
    completed_jobs = _poll_completion(lpm, 1)
    assert completed_jobs[0] == ('test', 0)


def test_existing_process(lpm, tmp_path):
    lpm.start(
            'test', tmp_path, ['bash', '-c', 'exit 0'], {},
            tmp_path / 'out', tmp_path / 'err')
    with pytest.raises(RuntimeError):
        lpm.start(
                'test', tmp_path, ['bash', '-c', 'exit 0'], {},
                tmp_path / 'out', tmp_path / 'err')

    completed_jobs = _poll_completion(lpm, 1)

    assert completed_jobs[0] == ('test', 0)


def test_env(lpm, tmp_path):
    env = {'ENVVAR': 'TESTING123'}
    lpm.start(
            'test', tmp_path, ['bash', '-c', 'echo ${ENVVAR}'], env,
            tmp_path / 'out', tmp_path / 'err')
    _poll_completion(lpm, 1)

    with (tmp_path / 'out').open('r') as f:
        lines = f.readlines()

    assert lines[0] == 'TESTING123\n'


def test_exit_code(lpm, tmp_path):
    lpm.start(
            'test_exit_code', tmp_path, ['bash', '-c', 'exit 3'], {},
            tmp_path / 'out', tmp_path / 'err')
    done = lpm.get_finished()
    while not done:
        sleep(0.02)
        done = lpm.get_finished()

    assert done[0] == ('test_exit_code', 3)


def test_multiple(lpm, tmp_path):
    for i in range(3):
        lpm.start(
                f'test_{i}', tmp_path, ['bash', '-c', 'sleep 1'], {},
                tmp_path / f'out{i}', tmp_path / f'err{i}')

    completed_jobs = _poll_completion(lpm, 3)

    assert sorted(completed_jobs) == [('test_0', 0), ('test_1', 0), ('test_2', 0)]


def test_cancel_all(lpm, tmp_path):
    begin_time = monotonic()

    for i in range(2):
        lpm.start(
                f'test_{i}', tmp_path, ['bash', '-c', 'sleep 1'], {},
                tmp_path / f'out{i}', tmp_path / f'err{i}')

    lpm.cancel_all()

    completed_jobs = _poll_completion(lpm, 2)

    end_time = monotonic()

    assert sorted(completed_jobs) == [('test_0', -9), ('test_1', -9)]
    assert end_time - begin_time < 1.0


def test_output_redirect(lpm, tmp_path):
    lpm.start(
            'test', tmp_path, ['bash', '-c', 'ls'], {},
            tmp_path / 'out', tmp_path / 'err')
    _poll_completion(lpm, 1)
    with (tmp_path / 'out').open('r') as f:
        assert f.readlines()
    with (tmp_path / 'err').open('r') as f:
        assert f.readlines() == []


def test_error_redirect(lpm, tmp_path):
    lpm.start(
            'test', tmp_path, ['bash', '-c', 'ls 1>&2'], {},
            tmp_path / 'out', tmp_path / 'err')
    _poll_completion(lpm, 1)
    with (tmp_path / 'out').open('r') as f:
        assert f.readlines() == []
    with (tmp_path / 'err').open('r') as f:
        assert f.readlines()
