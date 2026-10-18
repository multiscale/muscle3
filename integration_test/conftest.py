import logging
import os
from collections.abc import Generator
from pathlib import Path

import pytest
import yatiml
import ymmsl
from ymmsl.v0_2 import Configuration, Reference, resolve_timelines

from libmuscle.manager.manager import Manager
from libmuscle.manager.mmp_server import MMPServer
from libmuscle.manager.run_dir import RunDir
from libmuscle.pytest.muscle_tester import make_server_process
from muscle3.test.conftest import mpi_is_intel

skip_if_python_only = pytest.mark.skipif(
    "MUSCLE_TEST_PYTHON_ONLY" in os.environ, reason="Python-only tests requested"
)

skip_if_no_fortran = pytest.mark.skipif(
    "MUSCLE_DISABLE_FORTRAN" in os.environ, reason="No Fortran compiler available"
)

skip_if_no_mpi_cpp = pytest.mark.skipif(
    "MUSCLE_ENABLE_CPP_MPI" not in os.environ, reason="MPI support was not detected"
)


@pytest.fixture
def yatiml_log_warning() -> None:
    yatiml.logger.setLevel(logging.WARNING)


@pytest.fixture
def ymmsl_path() -> str:
    return str(Path(__file__).parent / "ymmsl")


@pytest.fixture
def codes_path() -> str:
    return str(Path(__file__).parent / "codes")


def ls_snapshots(run_dir: RunDir, instance: Reference | None = None) -> list[Path]:
    """List all snapshots of the instance or workflow"""
    n = str(instance).count("_") + 1 if instance is not None else 1
    return sorted(
        run_dir.snapshot_dir(instance).iterdir(),
        key=lambda path: tuple(map(int, path.stem.split("_")[n:])),
    )


@pytest.fixture
def mmp_server_config(yatiml_log_warning: None) -> str:
    return (
        "ymmsl_version: v0.2\n"
        "description: A less simple configuration for integration tests\n"
        "models:\n"
        "- name: test_model\n"
        "  description: A model for testing\n"
        "  components:\n"
        "    macro:\n"
        "      description: The macro model\n"
        "      ports:\n"
        "        o_i: out\n"
        "        s: in\n"
        "      implementation: macro_implementation\n"
        "    micro:\n"
        "      description: The micro model, many of them\n"
        "      ports:\n"
        "        f_init: in\n"
        "        o_f: out\n"
        "      implementation: micro_implementation\n"
        "      multiplicity: [10]\n"
        "  conduits:\n"
        "    macro.out: micro.in\n"
        "    micro.out: macro.in\n"
        "settings:\n"
        "  test1: 13\n"
        "  test2: 13.3\n"
        "  test3: testing\n"
        "  test4: True\n"
        "  test5: [2.3, 5.6]\n"
        "  test6:\n"
        "    - [1.0, 2.0]\n"
        "    - [3.0, 1.0]\n"
        "programs:\n"
        "  macro_implementation:\n"
        "    description: Program implementing macro\n"
        "    executable: macro.py\n"
        "  micro_implementation:\n"
        "    description: Program implementing micro\n"
        "    executable: micro.py\n"
    )


@pytest.fixture
def mmp_server_process(
    mmp_server_config: str, tmpdir: str
) -> Generator[str, None, None]:
    ymmsl_doc = ymmsl.load_as(ymmsl.v0_2.Configuration, mmp_server_config)
    for model in ymmsl_doc.models.values():
        resolve_timelines(model)

    with make_server_process(ymmsl_doc, Path(tmpdir), False) as addr:
        yield addr


@pytest.fixture
def mmp_server_config_simple(yatiml_log_warning: None) -> str:
    return (
        "ymmsl_version: v0.2\n"
        "description: A simple configuration for integration tests\n"
        "models:\n"
        "- name: test_model\n"
        "  description: A model for testing\n"
        "  components:\n"
        "    macro:\n"
        "      description: The macro model\n"
        "      ports:\n"
        "        o_i: out\n"
        "        s: in\n"
        "      implementation: macro_implementation\n"
        "    micro:\n"
        "      description: The micro model\n"
        "      ports:\n"
        "        f_init: in\n"
        "        o_f: out\n"
        "      implementation: micro_implementation\n"
        "  conduits:\n"
        "    macro.out: micro.in\n"
        "    micro.out: macro.in\n"
        "settings:\n"
        "  test1: 13\n"
        "  test2: 13.3\n"
        "  test3: testing\n"
        "  test4: True\n"
        "  test5: [2.3, 5.6]\n"
        "  test6:\n"
        "    - [1.0, 2.0]\n"
        "    - [3.0, 1.0]\n"
        "  test_with_a_longer_name: 1\n"
    )


@pytest.fixture
def mmp_server_config_simple_nopython(mmp_server_config_simple: str) -> str:
    return mmp_server_config_simple + "  python_compat: false\n"


@pytest.fixture
def mmp_server_config_simple_python(mmp_server_config_simple: str) -> str:
    return mmp_server_config_simple + "  python_compat: true\n"


@pytest.fixture
def mmp_server_process_simple(
    mmp_server_config_simple: str, tmpdir: str
) -> Generator[str, None, None]:
    ymmsl_doc = ymmsl.load_as(Configuration, mmp_server_config_simple)
    for model in ymmsl_doc.models.values():
        resolve_timelines(model)

    with make_server_process(ymmsl_doc, Path(tmpdir), False) as addr:
        yield addr


@pytest.fixture
def mmp_server(
    mmp_server_config_simple: str, yatiml_log_warning: None
) -> Generator[MMPServer, None, None]:
    ymmsl_doc = ymmsl.load_as(ymmsl.v0_2.Configuration, mmp_server_config_simple)
    for model in ymmsl_doc.models.values():
        resolve_timelines(model)

    manager = Manager(ymmsl_doc)
    yield manager._server
    manager.stop()


@pytest.fixture
def log_file_in_tmpdir(tmpdir: str) -> Generator[None, None, None]:
    old_workdir = os.getcwd()
    os.chdir(tmpdir)

    yield None

    os.chdir(old_workdir)


@pytest.fixture
def mpi_exec_model() -> str:
    if mpi_is_intel():
        return "intelmpi"
    else:
        return "openmpi"
