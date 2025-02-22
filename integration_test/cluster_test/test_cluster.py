import cerulean
import logging
import pytest

from integration_test.cluster_test.conftest import (
        REMOTE_SHARED, ssh_term, skip_unless_cluster)


_logger = logging.getLogger(__name__)


@pytest.fixture
def fake_cluster(installed_cluster):
    headnode_port = installed_cluster
    term = ssh_term(headnode_port, 'Connection to virtual cluster container timed out')
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


def _make_base_job(name, remote_out_dir, dir_name):
    job_dir = remote_out_dir / dir_name
    job_dir.mkdir(0o755, True, True)

    job = cerulean.JobDescription()
    job.name = name
    job.working_directory = job_dir
    job.stdout_file = job_dir / 'stdout.txt'
    job.stderr_file = job_dir / 'stderr.txt'
    job.queue_name = 'debug'
    job.time_reserved = 60
    job.system_out_file = job_dir / 'sysout.txt'
    job.system_err_file = job_dir / 'syserr.txt'
    job.extra_scheduler_options = '--ntasks-per-node=4'

    return job


def _make_job(name, mode, remote_test_files, remote_out_dir):
    job = _make_base_job(name, remote_out_dir, f'test_{name}_{mode}')
    job.command = str(remote_test_files / f'{name}.sh')
    return job


def _make_mpi_job(name, mode, execution_model, remote_test_files, remote_out_dir):
    job = _make_base_job(name, remote_out_dir, f'test_{name}_{mode}_{execution_model}')
    job.command = str(remote_test_files / f'{name}_{execution_model}.sh')
    return job


def _sched(fake_cluster, mode):
    if mode == 'local':
        return fake_cluster[2]
    else:
        return fake_cluster[3]


def _run_cmd_dir(remote_out_dir, testname, mode, execution_model=None):
    results_name = f'test_{testname}_{mode}'
    if execution_model is not None:
        results_name += f'_{execution_model}'

    for p in (remote_out_dir / results_name).iterdir():
        if p.name.startswith('run_'):
            return p


def _get_stdout(remote_out_dir, testname, mode, instance):
    run_dir = _run_cmd_dir(remote_out_dir, testname, mode)
    stdout_file = run_dir / 'instances' / instance / 'stdout.txt'
    assert stdout_file.exists()     # test output redirection
    return stdout_file.read_text()


def _get_outfile(remote_out_dir, testname, mode, execution_model, instance, rank):
    run_dir = _run_cmd_dir(remote_out_dir, testname, mode, execution_model)
    work_dir = run_dir / 'instances' / instance / 'workdir'
    out_file = work_dir / f'out_{rank}.txt'
    assert out_file.exists()        # test working directory
    return out_file.read_text()


_SCHED_OVERHEAD = 60


@skip_unless_cluster
@pytest.mark.parametrize('mode', ['local', 'slurm'])
def test_single(
        fake_cluster, remote_test_files, remote_out_dir, mode, hwthread_to_core):
    sched = _sched(fake_cluster, mode)

    job = _make_job('single', mode, remote_test_files, remote_out_dir)
    if mode == 'slurm':
        job.num_nodes = 1
        job.mpi_processes_per_node = 1
        job.extra_scheduler_options += ' --nodelist=node-0'

    job_id = sched.submit(job)
    assert sched.wait(job_id, job.time_reserved + _SCHED_OVERHEAD) is not None
    assert sched.get_exit_code(job_id) == 0

    output = _get_stdout(remote_out_dir, 'single', mode, 'c1')

    if mode == 'local':
        assert output.split('\n')[0] == 'headnode'
    else:
        node, hwthreads, _ = output.split('\n')
        assert node == 'node-0.example.org'
        assert hwthread_to_core(hwthreads) == [0]


@skip_unless_cluster
@pytest.mark.parametrize('mode', ['local', 'slurm'])
def test_dispatch(
        fake_cluster, remote_test_files, remote_out_dir, mode, hwthread_to_core):
    sched = _sched(fake_cluster, mode)

    job = _make_job('dispatch', mode, remote_test_files, remote_out_dir)
    if mode == 'slurm':
        job.num_nodes = 1
        job.mpi_processes_per_node = 1
        job.extra_scheduler_options += ' --nodelist=node-1'

    job_id = sched.submit(job)
    assert sched.wait(job_id, job.time_reserved + _SCHED_OVERHEAD) is not None
    assert sched.get_exit_code(job_id) == 0

    c1_out = _get_stdout(remote_out_dir, 'dispatch', mode, 'c1')
    c2_out = _get_stdout(remote_out_dir, 'dispatch', mode, 'c2')
    if mode == 'local':
        assert c1_out.split('\n')[0] == 'headnode'
        assert c2_out.split('\n')[0] == 'headnode'
    else:
        node, hwthreads, _ = c1_out.split('\n')
        assert node == 'node-1.example.org'
        assert hwthread_to_core(hwthreads) == [0]

        node, hwthreads, _ = c2_out.split('\n')
        assert node == 'node-1.example.org'
        assert hwthread_to_core(hwthreads) == [0]


@skip_unless_cluster
@pytest.mark.parametrize('mode', ['local', 'slurm'])
def test_multiple(
        fake_cluster, remote_test_files, remote_out_dir, mode, hwthread_to_core):
    sched = _sched(fake_cluster, mode)

    job = _make_job('multiple', mode, remote_test_files, remote_out_dir)
    if mode == 'slurm':
        job.num_nodes = 3
        job.extra_scheduler_options += ' --nodelist=node-[0-2]'

    job_id = sched.submit(job)
    assert sched.wait(job_id, job.time_reserved + _SCHED_OVERHEAD) is not None
    assert sched.get_exit_code(job_id) == 0

    for i in range(1, 7):
        instance = f'c{i}'
        out = _get_stdout(remote_out_dir, 'multiple', mode, instance)
        if mode == 'local':
            assert out.split('\n')[0] == 'headnode'
        else:
            node, hwthreads, _ = out.split('\n')
            assert (instance, node) == (instance, f'node-{(i - 1) // 2}.example.org')
            assert (instance, hwthread_to_core(hwthreads)) == (instance, [(i - 1) % 2])


@skip_unless_cluster
@pytest.mark.parametrize('mode', ['local', 'slurm'])
@pytest.mark.parametrize('execution_model', ['openmpi', 'intelmpi', 'srunmpi'])
def test_double(
        fake_cluster, remote_test_files, remote_out_dir, hwthread_to_core,
        mode, execution_model):

    if mode == 'local' and execution_model == 'srunmpi':
        pytest.skip('srun does not work without slurm')

    sched = _sched(fake_cluster, mode)

    job = _make_mpi_job(
            'double', mode, execution_model, remote_test_files, remote_out_dir)
    if mode == 'slurm':
        job.num_nodes = 2
        job.extra_scheduler_options += ' --nodelist=node-[3-4]'

    job_id = sched.submit(job)
    assert sched.wait(job_id, job.time_reserved + _SCHED_OVERHEAD) is not None
    assert sched.get_exit_code(job_id) == 0

    for i in range(1, 3):
        for rank in range(2):
            out = _get_outfile(
                    remote_out_dir, 'double', mode, execution_model, f'c{i}', rank)
            if mode == 'local':
                assert out.split('\n')[0] == 'headnode'
            else:
                node, hwthreads, _ = out.split('\n')
                assert node == f'node-{i + 2}.example.org'
                assert hwthread_to_core(hwthreads) == [rank]


@skip_unless_cluster
@pytest.mark.parametrize('mode', ['local', 'slurm'])
@pytest.mark.parametrize('execution_model', ['openmpi', 'intelmpi', 'srunmpi'])
def test_macro_micro(
        fake_cluster, remote_test_files, remote_out_dir, hwthread_to_core,
        mode, execution_model):

    if mode == 'local' and execution_model == 'srunmpi':
        pytest.skip('srun does not work without slurm')

    sched = _sched(fake_cluster, mode)

    job = _make_mpi_job(
            'macro_micro', mode, execution_model, remote_test_files, remote_out_dir)
    if mode == 'slurm':
        job.num_nodes = 1
        job.extra_scheduler_options += ' --nodelist=node-4'

    job_id = sched.submit(job)
    assert sched.wait(job_id, job.time_reserved + _SCHED_OVERHEAD) is not None
    assert sched.get_exit_code(job_id) == 0

    for i in range(1, 3):
        for rank in range(2):
            out = _get_outfile(
                    remote_out_dir, 'macro_micro', mode, execution_model, f'c{i}', rank)
            if mode == 'local':
                assert out.split('\n')[0] == 'headnode'
            else:
                node, hwthreads, _ = out.split('\n')
                assert node == 'node-4.example.org'
                assert hwthread_to_core(hwthreads) == [rank]


@skip_unless_cluster
@pytest.mark.parametrize('mode', ['local', 'slurm'])
def test_base_env(
        fake_cluster, remote_test_files, remote_out_dir, mode):
    sched = _sched(fake_cluster, mode)

    job = _make_job('base_env', mode, remote_test_files, remote_out_dir)
    if mode == 'slurm':
        job.num_nodes = 2
        job.mpi_processes_per_node = 2

    job_id = sched.submit(job)
    assert sched.wait(job_id, job.time_reserved + _SCHED_OVERHEAD) is not None
    assert sched.get_exit_code(job_id) == 0

    login_out = _get_stdout(remote_out_dir, 'base_env', mode, 'login')
    clean_out = _get_stdout(remote_out_dir, 'base_env', mode, 'clean')
    manager_out = _get_stdout(remote_out_dir, 'base_env', mode, 'manager')

    assert login_out.split('\n')[0] == '1'     # .profile loaded
    assert login_out.split('\n')[1] == '0'     # .bashrc loaded
    assert login_out.split('\n')[2] == '0'     # manager shell
    assert login_out.split('\n')[3] == '1'     # modules loaded
    assert login_out.split('\n')[4] == ''      # venv active

    assert clean_out.split('\n')[0] == '0'     # .profile loaded
    assert clean_out.split('\n')[1] == '0'     # .bashrc loaded
    assert clean_out.split('\n')[2] == '1'     # manager shell
    assert clean_out.split('\n')[3] == '0'     # modules loaded
    assert clean_out.split('\n')[4] == ''      # venv active

    assert manager_out.split('\n')[0] == '0'   # .profile loaded
    assert manager_out.split('\n')[1] == '0'   # .bashrc loaded
    assert manager_out.split('\n')[2] == '1'   # manager shell
    assert manager_out.split('\n')[3] == '1'   # modules loaded
    assert manager_out.split('\n')[4] == '/home/cerulean/shared/venv'
