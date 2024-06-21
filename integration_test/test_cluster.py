# This ensures that pytest can import this module in the non-cluster test env
# in which these dependencies don't exist, because these tests won' be run.
try:
    import cerulean
except ImportError:
    pass

import logging
from pathlib import Path
import pytest
import time

from .conftest import skip_unless_cluster


logger = logging.getLogger(__name__)


def _run(term, timeout, command):
    exit_code, out, err = term.run(timeout, command, [])
    if exit_code != 0:
        logger.error(err)
    assert exit_code == 0
    return out


@pytest.fixture(scope='session')
def local_term():
    return cerulean.LocalTerminal()


@pytest.fixture(scope='session')
def local_fs():
    return cerulean.LocalFileSystem()


@pytest.fixture(scope='session')
def virtual_cluster_image(local_term):
    IMAGE_NAME = 'muscle3_test_cluster'
    _run(local_term, 180, (
        f'docker buildx build -t {IMAGE_NAME}'
        ' -f integration_test/test_cluster.Dockerfile .'))
    return IMAGE_NAME


def _ssh_term(timeout_msg):
    cred = cerulean.PasswordCredential('cerulean', 'kingfisher')
    ready = False
    start = time.monotonic()
    while not ready:
        if (time.monotonic() - start) > 60.0:
            raise Exception(timeout_msg)

        try:
            term = cerulean.SshTerminal('localhost', 10022, cred)
            ready = True
        except Exception:
            time.sleep(3.0)

    return term


@pytest.fixture(scope='session')
def virtual_cluster_container(local_term, virtual_cluster_image):
    # clean up stray container from previous run, if any
    _run(local_term, 60, 'docker rm -f muscle3_test_slurm')

    _run(local_term, 60, (
        'docker run -d --name muscle3_test_slurm -p 10022:22'
        f' {virtual_cluster_image}'))

    _ssh_term('Virtual cluster container start timed out')
    yield None

    # _run(local_term, 60, 'docker rm -f muscle3_test_slurm')


@pytest.fixture(scope='session')
def setup_connection(virtual_cluster_container):
    # Session-wide connection used for container setup actions only
    # Tests each have their own connection, see virtual_cluster() below
    term = _ssh_term('Connection to virtual cluster container timed out')
    with cerulean.SftpFileSystem(term, True) as fs:
        yield term, fs


@pytest.fixture(scope='session')
def repo_root(local_fs):
    root_dir = Path(__file__).parents[1]
    return local_fs / str(root_dir)


@pytest.fixture(scope='session')
def muscle3_venv(repo_root, setup_connection):
    remote_term, remote_fs = setup_connection

    _run(remote_term, 10, 'python3 -m venv /home/cerulean/venv')
    in_venv = 'source /home/cerulean/venv/bin/activate && '
    _run(remote_term, 30, (
        f'/bin/bash -c "{in_venv} python3 -m pip install pip wheel setuptools"'))

    muscle3_tgt = remote_fs / 'home/cerulean/muscle3'
    muscle3_tgt.mkdir()
    (muscle3_tgt / 'libmuscle').mkdir()

    for f in (
            'muscle3', 'libmuscle/python', 'setup.py', 'MANIFEST.in', 'LICENSE',
            'NOTICE', 'VERSION', 'README.rst'):
        cerulean.copy(repo_root / f, muscle3_tgt / f)

    _run(remote_term, 60, f'/bin/bash -c "{in_venv} pip install ./muscle3"')
    return in_venv


@pytest.fixture(scope='session')
def create_remote_test_files(repo_root, setup_connection):
    remote_term, remote_fs = setup_connection

    remote_home = remote_fs / 'home' / 'cerulean'

    cerulean.copy(
            repo_root / 'integration_test' / 'cluster_test', remote_home,
            copy_permissions=True)


@pytest.fixture
def virtual_cluster(virtual_cluster_container, muscle3_venv, create_remote_test_files):
    term = _ssh_term('Connection to vitrual cluster container timed out')
    with cerulean.SftpFileSystem(term, True) as fs:
        sched = cerulean.SlurmScheduler(term)
        yield term, fs, sched


@pytest.fixture
def remote_home(virtual_cluster):
    _, remote_fs, _ = virtual_cluster
    return remote_fs / 'home' / 'cerulean'


@pytest.fixture
def remote_test_files(remote_home):
    return remote_home / 'cluster_test'


@pytest.fixture
def remote_out_dir(remote_home):
    return remote_home / 'test_results'


def _make_job(name, remote_test_files, remote_out_dir):
    job_dir = remote_out_dir / f'test_{name}'

    job = cerulean.JobDescription()
    job.name = name
    job.working_directory = job_dir
    job.command = remote_test_files / f'{name}.sh'
    job.stdout_file = job_dir / 'stdout.txt'
    job.stderr_file = job_dir / 'stderr.txt'
    job.queue_name = 'debug'
    job.time_reserved = 60
    job.system_out_file = job_dir / 'sysout.txt'
    job.system_err_file = job_dir / 'syserr.txt'

    return job


_SCHED_OVERHEAD = 60


@skip_unless_cluster
def test_single(virtual_cluster, remote_test_files, remote_out_dir):
    remote_term, remote_fs, sched = virtual_cluster

    job = _make_job('single', remote_test_files, remote_out_dir)
    job.num_nodes = 1
    job.mpi_processes_per_node = 1
    job.extra_scheduler_options = '--ntasks-per-core=1'

    job_id = sched.submit(job)
    assert sched.wait(job_id, job.time_reserved + _SCHED_OVERHEAD) is not None
    assert sched.get_exit_code(job_id) == 0


@skip_unless_cluster
def test_dispatch(virtual_cluster, remote_test_files, remote_out_dir):
    remote_term, remote_fs, sched = virtual_cluster

    job = _make_job('dispatch', remote_test_files, remote_out_dir)
    job.num_nodes = 2
    job.mpi_processes_per_node = 1
    job.extra_scheduler_options = '--ntasks-per-core=1'

    job_id = sched.submit(job)
    assert sched.wait(job_id, job.time_reserved + _SCHED_OVERHEAD) is not None
    assert sched.get_exit_code(job_id) == 0


@skip_unless_cluster
def test_multiple(virtual_cluster, remote_test_files, remote_out_dir):
    remote_term, remote_fs, sched = virtual_cluster

    job = _make_job('multiple', remote_test_files, remote_out_dir)
    job.num_nodes = 3

    job_id = sched.submit(job)
    assert sched.wait(job_id, job.time_reserved + _SCHED_OVERHEAD) is not None
    assert sched.get_exit_code(job_id) == 0
