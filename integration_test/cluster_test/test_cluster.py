import cerulean
import logging
import pytest

from integration_test.cluster_test.conftest import (
        REMOTE_SHARED, run_cmd, ssh_term, skip_unless_cluster)


logger_ = logging.getLogger(__name__)


@pytest.fixture(scope='session')
def copy_test_files(repo_root, setup_connection):
    remote_term, remote_fs = setup_connection
    remote_home = remote_fs / REMOTE_SHARED

    cerulean.copy(
            repo_root / 'integration_test' / 'cluster_test', remote_home,
            copy_permissions=True)

    return remote_home / 'cluster_test'


@pytest.fixture(scope='session')
def build_native_components(
        muscle3_native_openmpi, setup_connection, copy_test_files):
    remote_term, remote_fs = setup_connection
    remote_source = copy_test_files

    run_cmd(remote_term, 30, (
        f"/bin/bash -l -c '"
        f"module load openmpi && "
        f". {muscle3_native_openmpi}/bin/muscle3.env && "
        f"make -C {remote_source}'"))


@pytest.fixture
def fake_cluster(
        fake_cluster_headnode, muscle3_venv, build_native_components, copy_test_files):
    term = ssh_term('Connection to virtual cluster container timed out')
    with cerulean.SftpFileSystem(term, True) as fs:
        local_sched = cerulean.DirectGnuScheduler(term)
        slurm_sched = cerulean.SlurmScheduler(term)
        yield term, fs, local_sched, slurm_sched


@pytest.fixture
def remote_home(fake_cluster):
    remote_fs = fake_cluster[1]
    return remote_fs / REMOTE_SHARED


@pytest.fixture
def remote_test_files(remote_home):
    return remote_home / 'cluster_test'


@pytest.fixture
def remote_out_dir(remote_home):
    return remote_home / 'test_results'


def _make_job(name, mode, remote_test_files, remote_out_dir):
    job_dir = remote_out_dir / f'test_{name}_{mode}'
    job_dir.mkdir(0o755, True, True)

    job = cerulean.JobDescription()
    job.name = name
    job.working_directory = job_dir
    job.command = str(remote_test_files / f'{name}.sh')
    job.stdout_file = job_dir / 'stdout.txt'
    job.stderr_file = job_dir / 'stderr.txt'
    job.queue_name = 'debug'
    job.time_reserved = 60
    job.system_out_file = job_dir / 'sysout.txt'
    job.system_err_file = job_dir / 'syserr.txt'

    return job


def _sched(fake_cluster, mode):
    if mode == 'local':
        return fake_cluster[2]
    else:
        return fake_cluster[3]


def run_cmd_dir(remote_out_dir, testname, mode):
    results_name = f'test_{testname}_{mode}'

    for p in (remote_out_dir / results_name).iterdir():
        if p.name.startswith('run_'):
            return p


def _get_stdout(remote_out_dir, testname, mode, instance):
    run_dir = run_cmd_dir(remote_out_dir, testname, mode)
    stdout_file = run_dir / 'instances' / instance / 'stdout.txt'
    assert stdout_file.exists()     # test output redirection
    return stdout_file.read_text()


def _get_outfile(remote_out_dir, testname, mode, instance, rank):
    run_dir = run_cmd_dir(remote_out_dir, testname, mode)
    work_dir = run_dir / 'instances' / instance / 'workdir'
    out_file = work_dir / f'out_{rank}.txt'
    assert out_file.exists()        # test working directory
    return out_file.read_text()


_SCHED_OVERHEAD = 60


@skip_unless_cluster
@pytest.mark.parametrize('mode', ['local', 'slurm'])
def test_single(fake_cluster, remote_test_files, remote_out_dir, mode):
    sched = _sched(fake_cluster, mode)

    job = _make_job('single', mode, remote_test_files, remote_out_dir)
    if mode == 'slurm':
        job.num_nodes = 1
        job.mpi_processes_per_node = 1
        job.extra_scheduler_options = '--ntasks-per-core=1 --nodelist=muscle3-node-0'

    job_id = sched.submit(job)
    assert sched.wait(job_id, job.time_reserved + _SCHED_OVERHEAD) is not None
    assert sched.get_exit_code(job_id) == 0

    output = _get_stdout(remote_out_dir, 'single', mode, 'c1')

    if mode == 'local':
        assert output == 'muscle3-headnode\n'
    else:
        assert output == 'muscle3-node-0\n'


@skip_unless_cluster
@pytest.mark.parametrize('mode', ['local', 'slurm'])
def test_dispatch(fake_cluster, remote_test_files, remote_out_dir, mode):
    sched = _sched(fake_cluster, mode)

    job = _make_job('dispatch', mode, remote_test_files, remote_out_dir)
    if mode == 'slurm':
        job.num_nodes = 1
        job.mpi_processes_per_node = 1
        job.extra_scheduler_options = '--ntasks-per-core=1 --nodelist=muscle3-node-1'

    job_id = sched.submit(job)
    assert sched.wait(job_id, job.time_reserved + _SCHED_OVERHEAD) is not None
    assert sched.get_exit_code(job_id) == 0

    c1_out = _get_stdout(remote_out_dir, 'dispatch', mode, 'c1')
    c2_out = _get_stdout(remote_out_dir, 'dispatch', mode, 'c2')
    if mode == 'local':
        assert c1_out == 'muscle3-headnode\n'
        assert c2_out == 'muscle3-headnode\n'
    else:
        assert c1_out == 'muscle3-node-1\n'
        assert c2_out == 'muscle3-node-1\n'


@skip_unless_cluster
@pytest.mark.parametrize('mode', ['local'])
# SLURM mode is not implemented yet
def test_multiple(fake_cluster, remote_test_files, remote_out_dir, mode):
    sched = _sched(fake_cluster, mode)

    job = _make_job('multiple', mode, remote_test_files, remote_out_dir)
    if mode == 'slurm':
        job.num_nodes = 3
        job.extra_scheduler_options = '--nodelist=muscle3-node-[0-2]'

    job_id = sched.submit(job)
    assert sched.wait(job_id, job.time_reserved + _SCHED_OVERHEAD) is not None
    assert sched.get_exit_code(job_id) == 0

    for i in range(1, 7):
        if mode == 'local':
            assert _get_stdout(
                    remote_out_dir, 'multiple', mode, f'c{i}') == 'muscle3-headnode\n'
        else:
            out = _get_stdout(remote_out_dir, 'multiple', mode, f'c{i}')
            assert out == f'muscle3-node-{(i - 1) // 2}\n'


@skip_unless_cluster
@pytest.mark.parametrize('mode', ['local', 'slurm'])
def test_double_mpi(fake_cluster, remote_test_files, remote_out_dir, mode):
    sched = _sched(fake_cluster, mode)

    job = _make_job('double_mpi', mode, remote_test_files, remote_out_dir)
    if mode == 'slurm':
        job.num_nodes = 2
        job.extra_scheduler_options = '--nodelist=muscle3-node-[3-4]'

    job_id = sched.submit(job)
    assert sched.wait(job_id, job.time_reserved + _SCHED_OVERHEAD) is not None
    assert sched.get_exit_code(job_id) == 0

    for i in range(1, 3):
        for rank in range(2):
            output = _get_outfile(remote_out_dir, 'double_mpi', mode, f'c{i}', rank)
            if mode == 'local':
                assert output == 'muscle3-headnode\n'
            else:
                assert output == f'muscle3-node-{i + 2}\n'
