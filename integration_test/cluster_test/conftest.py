import logging
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import time

import cerulean
import pytest


logger_ = logging.getLogger(__name__)


REMOTE_SHARED = '/home/cerulean/shared'


# Shut down the containers after running the tests. Set to False to debug.
CLEAN_UP_CONTAINERS = True


skip_unless_cluster = pytest.mark.skipif(
        'MUSCLE_TEST_CLUSTER' not in os.environ,
        reason='Cluster tests were not explicitly enabled')


def run_cmd(term, timeout, command):
    exit_code, out, err = term.run(timeout, command, [])
    if exit_code != 0:
        logger_.error(err)
    assert exit_code == 0
    return out


@pytest.fixture(scope='session')
def local_term():
    return cerulean.LocalTerminal()


@pytest.fixture(scope='session')
def local_fs():
    return cerulean.LocalFileSystem()


@pytest.fixture(scope='session')
def fake_cluster_image(local_term):
    IMAGE_NAME = 'muscle3_test_cluster'
    run_cmd(local_term, 5400, (
        f'docker buildx build -t {IMAGE_NAME}'
        ' -f integration_test/fake_cluster/Dockerfile .'))
    return IMAGE_NAME


def ssh_term(timeout_msg):
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
def shared_dir():
    # Note that pytest's tmp_path is function-scoped, so cannot be used here
    with TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        path = Path(tmp_dir)
        path.chmod(0o1777)
        yield path


@pytest.fixture(scope='session')
def cleanup_docker(local_term):
    for i in range(5):
        node_name = f'node-{i}'
        run_cmd(local_term, 60, f'docker rm -f {node_name}')

    run_cmd(local_term, 60, 'docker rm -f headnode')
    run_cmd(local_term, 60, 'docker network rm -f muscle3-net')


@pytest.fixture(scope='session')
def fake_cluster_network(local_term, cleanup_docker):
    name = 'muscle3-net'
    run_cmd(local_term, 60, f'docker network create {name}')
    yield name

    if CLEAN_UP_CONTAINERS:
        run_cmd(local_term, 60, 'docker network rm -f muscle3-net')


@pytest.fixture(scope='session')
def fake_cluster_nodes(
        local_term, fake_cluster_image, fake_cluster_network, shared_dir):

    node_names = list()

    for i in range(5):
        node_name = f'node-{i}'
        ssh_port = 10030 + i

        run_cmd(local_term, 60, (
            f'docker run -d --name={node_name} --hostname={node_name}'
            f' --network={fake_cluster_network} -p {ssh_port}:22'
            f' --cap-add=CAP_SYS_NICE'
            f' --mount type=bind,source={shared_dir},target={REMOTE_SHARED}'
            f' {fake_cluster_image}'))

        node_names.append(node_name)

    yield None

    if CLEAN_UP_CONTAINERS:
        run_cmd(local_term, 60, f'docker rm -f {" ".join(node_names)}')


@pytest.fixture(scope='session')
def fake_cluster_headnode(
        local_term, fake_cluster_image, fake_cluster_network, fake_cluster_nodes,
        shared_dir):

    run_cmd(local_term, 60, (
        'docker run -d --name=headnode --hostname=headnode'
        f' --network={fake_cluster_network} -p 10022:22'
        f' --mount type=bind,source={shared_dir},target={REMOTE_SHARED}'
        f' {fake_cluster_image}'))

    ssh_term('Virtual cluster container start timed out')
    yield None

    if CLEAN_UP_CONTAINERS:
        run_cmd(local_term, 60, 'docker rm -f headnode')


@pytest.fixture(scope='session')
def setup_connection(fake_cluster_headnode):
    # Session-wide connection used for container setup actions only
    # Tests each have their own connection, see fake_cluster() below
    term = ssh_term('Connection to virtual cluster container timed out')
    with cerulean.SftpFileSystem(term, True) as fs:
        yield term, fs

    # We abuse this to clean up the contents of the shared directory.
    # Because it's been made inside of the container, it has a different owner
    # than what we're running with on the host, and the host user cannot remove
    # the files.
    if CLEAN_UP_CONTAINERS:
        run_cmd(term, 60, f'rm -rf {REMOTE_SHARED}/*')


@pytest.fixture(scope='session')
def repo_root(local_fs):
    root_dir = Path(__file__).parents[2]
    return local_fs / str(root_dir)


@pytest.fixture(scope='session')
def remote_source(repo_root, setup_connection):
    remote_term, remote_fs = setup_connection

    muscle3_tgt = remote_fs / 'home' / 'cerulean' / 'muscle3'
    muscle3_tgt.mkdir()
    (muscle3_tgt / 'libmuscle').mkdir()

    for f in (
            'muscle3', 'libmuscle', 'scripts', 'docs', 'setup.py', 'Makefile',
            'MANIFEST.in', 'LICENSE', 'NOTICE', 'VERSION', 'README.rst'):
        cerulean.copy(
                repo_root / f, muscle3_tgt / f, overwrite='always', copy_into=False)

    return muscle3_tgt


@pytest.fixture(scope='session')
def muscle3_venv(repo_root, remote_source, setup_connection):
    remote_term, remote_fs = setup_connection

    run_cmd(remote_term, 10, f'python3 -m venv {REMOTE_SHARED}/venv')
    in_venv = f'source {REMOTE_SHARED}/venv/bin/activate && '

    run_cmd(remote_term, 30, (
        f'/bin/bash -c "{in_venv} python3 -m pip install pip wheel setuptools"'))

    run_cmd(remote_term, 60, f'/bin/bash -c "{in_venv} pip install {remote_source}"')
    return in_venv


@pytest.fixture(scope='session')
def muscle3_native_openmpi(remote_source, setup_connection):
    remote_term, remote_fs = setup_connection

    prefix = remote_fs / REMOTE_SHARED / 'muscle3-openmpi'
    prefix.mkdir()

    run_cmd(remote_term, 600, (
        f'/bin/bash -l -c "'
        f'module load openmpi && '
        f'cd {remote_source} && '
        f'make distclean && '
        f'PREFIX={prefix} make install"'))

    return prefix


@pytest.fixture(scope='session')
def hwthread_to_core():
    """Translates hwthreads to core ids.

    In our tests, we use sched_getaffinity to check which cores we're bound to. This
    returns numbers identifying hwthreads, but our planner binds swthreads and processes
    to entire cores. So we get a comma-separated list of hwthread ids and want to
    compare that to a list of core ids.

    This reads /proc/cpuinfo to get the mapping between hwthreads and cores, and returns
    a function that takes a comma-separated list of hwthread ids and returns a list of
    corresponding core ids.
    """
    with open('/proc/cpuinfo', 'r') as f:
        cpuinfo = f.readlines()

    def get_values(cpuinfo, field):
        return [
                int(line.split(':')[1].strip())
                for line in cpuinfo if line.startswith(field)]

    hwthread_ids = get_values(cpuinfo, 'processor')
    core_ids = get_values(cpuinfo, 'core id')

    table = dict(zip(hwthread_ids, core_ids))

    def convert(aff_ids):
        cores = {table[i] for i in map(int, aff_ids.split(','))}
        return sorted(cores)

    return convert
