import logging
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import time

import cerulean
import pytest


logger_ = logging.getLogger(__name__)


IMAGE_NAME = 'muscle3_test_cluster'

REMOTE_SHARED = '/home/cerulean/shared'

IDX_SLURM_VERSIONS = list(enumerate([
    '17-02', '17-11', '18-08', '19-05', '20-02', '20-11', '21-08', '22-05', '23-02',
    '23-11'
    ]))

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
def repo_root(local_fs):
    root_dir = Path(__file__).parents[2]
    return local_fs / str(root_dir)


@pytest.fixture(scope='session')
def fake_cluster_image(local_term):
    run_cmd(local_term, 5400, (
        f'docker buildx build -t {IMAGE_NAME}'
        ' -f integration_test/fake_cluster/Dockerfile .'))


@pytest.fixture(scope='session')
def fake_cluster_image_old(local_term):
    run_cmd(local_term, 5400, (
        f'docker buildx build -t {IMAGE_NAME}_old'
        ' -f integration_test/fake_cluster/old.Dockerfile .'))


def _image_name(slurm_version):
    if slurm_version <= '20-02':
        return IMAGE_NAME + '_old'
    return IMAGE_NAME


def _gcc_version(slurm_version):
    if slurm_version <= '20-02':
        return '7.5.0'
    return '11.4.0'


def ssh_term(port, timeout_msg):
    cred = cerulean.PasswordCredential('cerulean', 'kingfisher')
    ready = False
    start = time.monotonic()
    while not ready:
        if (time.monotonic() - start) > 60.0:
            raise Exception(timeout_msg)

        try:
            term = cerulean.SshTerminal('localhost', port, cred)
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
    for _, slurm_version in IDX_SLURM_VERSIONS:
        _clean_up_base_cluster(local_term, slurm_version)


def _create_network(local_term, slurm_version):
    name = f'muscle3-net-{slurm_version}'
    run_cmd(local_term, 60, f'docker network create {name}')
    return name


def _start_nodes(local_term, slurm_version, net_name, shared_dir):
    for i in range(5):
        node_name = f'node-{i}'

        image_name = _image_name(slurm_version)

        run_cmd(local_term, 60, (
            f'docker run -d --name={node_name}-{slurm_version} --hostname={node_name}'
            f' --network={net_name} --cap-add=CAP_SYS_NICE'
            f' --env SLURM_VERSION={slurm_version}'
            f' --mount type=bind,source={shared_dir},target={REMOTE_SHARED}'
            f' {image_name}'))


def _start_headnode(local_term, slurm_version, net_name, shared_dir, headnode_port):
    image_name = _image_name(slurm_version)

    run_cmd(local_term, 60, (
        f'docker run -d --name=headnode-{slurm_version} --hostname=headnode'
        f' --network={net_name} -p {headnode_port}:22'
        f' --env SLURM_VERSION={slurm_version}'
        f' --mount type=bind,source={shared_dir},target={REMOTE_SHARED}'
        f' {image_name}'))

    ssh_term(headnode_port, 'Virtual cluster container start timed out')


def _start_base_cluster(local_term, idx_slurm_version, shared_dir):
    slurm_index, slurm_version = idx_slurm_version

    headnode_port = 10022 + slurm_index

    net_name = _create_network(local_term, slurm_version)
    _start_nodes(local_term, slurm_version, net_name, shared_dir)
    _start_headnode(local_term, slurm_version, net_name, shared_dir, headnode_port)

    term = ssh_term(headnode_port, 'Connection to virtual cluster container timed out')
    fs = cerulean.SftpFileSystem(term, False)

    return term, fs, headnode_port


def _install_remote_source(repo_root, remote_term, remote_fs):
    muscle3_tgt = remote_fs / 'home' / 'cerulean' / 'muscle3'
    muscle3_tgt.mkdir()
    (muscle3_tgt / 'libmuscle').mkdir()

    for f in (
            'muscle3', 'libmuscle', 'scripts', 'docs', 'setup.py', 'Makefile',
            'MANIFEST.in', 'LICENSE', 'NOTICE', 'VERSION', 'README.rst'):
        cerulean.copy(
                repo_root / f, muscle3_tgt / f, overwrite='always', copy_into=False)

    return muscle3_tgt


def _create_muscle3_venv(remote_term, remote_source):
    run_cmd(remote_term, 10, f'python3 -m venv {REMOTE_SHARED}/venv')
    in_venv = f'source {REMOTE_SHARED}/venv/bin/activate && '

    run_cmd(remote_term, 30, (
        f'/bin/bash -c "{in_venv} python3 -m pip install pip wheel setuptools"'))

    run_cmd(remote_term, 60, f'/bin/bash -c "{in_venv} pip install {remote_source}"')


def _install_muscle3_native_openmpi(
        remote_source, remote_term, remote_fs, slurm_version):
    prefix = remote_fs / REMOTE_SHARED / 'muscle3-openmpi'
    prefix.mkdir()

    openmpi_hash = run_cmd(remote_term, 600, (
        '/bin/bash -c "'
        'for phash in $(/opt/spack/bin/spack find --format \\"{hash}\\" openmpi'
        '        | tr \'\\n\' \' \') ; do'
        '    if /opt/spack/bin/spack find --deps /\\${phash} |'
        f'                grep -q slurm@{slurm_version} ; then'
        '        echo \\${phash} ;'
        '     fi ;'
        'done'
        '"'))

    openmpi_version = run_cmd(remote_term, 600, (
        '/bin/bash -c "'
        f'/opt/spack/bin/spack find --format \\"{{version}}\\" /{openmpi_hash}'
        '"')).strip()

    gcc_version = _gcc_version(slurm_version)

    module_name = f'openmpi/{openmpi_version}-gcc-{gcc_version}-{openmpi_hash[:7]}'

    logger_.info(f'Slurm {slurm_version} and module {module_name}')

    run_cmd(remote_term, 600, (
        f'/bin/bash -l -c "'
        f'module load {module_name} && '
        f'cd {remote_source} && '
        f'make distclean && '
        f'PREFIX={prefix} make install"'))

    return prefix, module_name


def _install_muscle3(repo_root, remote_term, remote_fs, slurm_version):
    remote_source = _install_remote_source(repo_root, remote_term, remote_fs)
    _create_muscle3_venv(remote_term, remote_source)
    return _install_muscle3_native_openmpi(
            remote_source, remote_term, remote_fs, slurm_version)


def _install_tests(repo_root, remote_term, remote_fs, remote_m3_openmpi):
    remote_home = remote_fs / REMOTE_SHARED
    remote_m3, openmpi_module = remote_m3_openmpi

    cerulean.copy(
            repo_root / 'integration_test' / 'cluster_test', remote_home,
            copy_permissions=True)

    remote_source = remote_home / 'cluster_test'

    run_cmd(remote_term, 30, (
        '/bin/bash -c "'
        f'sed -i \\"s^modules: openmpi^modules: {openmpi_module}^\\"'
        f' {remote_source}/implementations_openmpi.ymmsl'
        '"'))

    run_cmd(remote_term, 30, (
        '/bin/bash -c "'
        f'sed -i \\"s^modules: openmpi^modules: {openmpi_module}^\\"'
        f' {remote_source}/implementations_srunmpi.ymmsl'
        '"'))

    run_cmd(remote_term, 30, (
        f'/bin/bash -l -c "'
        f'module load {openmpi_module} && '
        f'. {remote_m3}/bin/muscle3.env && '
        f'make -C {remote_source}"'))


def _clean_up_base_cluster(local_term, slurm_version):
    node_names = [f'node-{i}-{slurm_version}' for i in range(5)]
    run_cmd(local_term, 60, f'docker rm -f {" ".join(node_names)}')

    run_cmd(local_term, 60, f'docker rm -f headnode-{slurm_version}')

    net_name = f'muscle3-net-{slurm_version}'
    run_cmd(local_term, 60, f'docker network rm -f {net_name}')


@pytest.fixture(scope='session', params=IDX_SLURM_VERSIONS)
def installed_cluster(
        request, cleanup_docker, fake_cluster_image, fake_cluster_image_old, shared_dir,
        repo_root, local_term):

    slurm_version = request.param[1]
    local_shared_dir = shared_dir / slurm_version
    local_shared_dir.mkdir()
    local_shared_dir.chmod(0o1777)

    remote_term, remote_fs, headnode_port = _start_base_cluster(
            local_term, request.param, local_shared_dir)
    remote_m3_openmpi = _install_muscle3(
            repo_root, remote_term, remote_fs, slurm_version)
    _install_tests(repo_root, remote_term, remote_fs, remote_m3_openmpi)

    yield headnode_port

    # Because it's been made inside of the container, the shared directory has a
    # different owner than what we're running with on the host, and the host user cannot
    # remove the files. So we do it here from inside the container
    if CLEAN_UP_CONTAINERS:
        run_cmd(remote_term, 60, f'rm -rf {REMOTE_SHARED}/*')

    remote_fs.close()
    remote_term.close()

    if CLEAN_UP_CONTAINERS:
        _clean_up_base_cluster(local_term, slurm_version)


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
