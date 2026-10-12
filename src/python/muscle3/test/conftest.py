import logging
import multiprocessing as mp
import os
import subprocess
import sys
import time
from collections.abc import Callable
from contextlib import ExitStack
from pathlib import Path
from typing import Any

import ymmsl
from ymmsl.v0_2 import resolve_timelines

from libmuscle.pytest.muscle_tester import make_server_process


def _python_wrapper(
    tmpdir: Path,
    instance_name: str,
    muscle_manager: str,
    callable: Callable,
    *args: Any,
):
    sys.argv.append(f"--muscle-instance={instance_name}")
    sys.argv.append(f"--muscle-manager={muscle_manager}")

    with open(tmpdir / f"{instance_name}_stdout.txt", "w") as f_out:
        with open(tmpdir / f"{instance_name}_stderr.txt", "w") as f_err:
            sys.stdout = f_out
            sys.stderr = f_err

            root_logger = logging.getLogger()
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s"
                )
            )
            root_logger.addHandler(handler)
            root_logger.setLevel(logging.DEBUG)

            try:
                callable(*args)
            except Exception as e:
                root_logger.exception(e)
                raise


def mpi_is_intel() -> bool | None:
    if "MUSCLE_ENABLE_CPP_MPI" not in os.environ:
        return None

    result = subprocess.run(["mpirun", "--version"], capture_output=True, check=True)
    return "Intel" in result.stdout.decode("utf-8")


def mpirun_outfile_arg():
    if mpi_is_intel():
        return "-outfile-pattern"
    else:
        return "--output-filename"


def run_manager_with_actors(
    ymmsl_text: str, tmpdir: Path, actors: dict, expect_success: bool = True
) -> None:
    """Start muscle_manager along with C++ and Python actors.

    Args:
        ymmsl_text: YMMSL configuration for the simulation
        tmpdir: Temporary folder to use as runpath a
        actors: A dictionary of lists containing details for each actor:
            ``{"instance_name": ("language", "details", ...)}``.

            Language can be ``"python"``, ``"cpp"``, ``"mpi_cpp"`` or ``"fortran"``.
            Details differ per language.

            For python actors, details is a callable which is executed
            in a ``multiprocessing.Process``. Additional positional arguments can be
            supplied as well.

            For cpp actors, details is an executable path with optional arguments.
            The executable paths are assumed to be relative to
            ``../build/cpp/libmuscle/tests``.

            For mpi cpp actors, details is an executable path (see cpp), then number of
            processes and optionally arguments passed to the executable.

            For fortran actors, details is an executable path. Executable paths are
            assumed to be relative to ``../build/fortran/libmuscle/tests``.

            For both cpp and Fortran actors, LD_LIBRARY_PATH is automatically updated
            to include the msgpack library path.
        expect_success: Whether to assert a successful or unsuccessful run.
    """
    env = os.environ.copy()
    ymmsl_doc = ymmsl.load_as(ymmsl.v0_2.Configuration, ymmsl_text)
    for model in ymmsl_doc.models.values():
        resolve_timelines(model)
    build_dir = Path(__file__).parents[4] / "build"
    cpp_build_dir = build_dir / "cpp" / "libmuscle" / "tests"
    fortran_build_dir = build_dir / "fortran" / "libmuscle" / "tests"

    with ExitStack() as stack:
        # We need to convert from pytest Path to pathlib Path here
        ctx = make_server_process(ymmsl_doc, Path(tmpdir), False)
        env["MUSCLE_MANAGER"] = stack.enter_context(ctx)

        lib_paths = [cpp_build_dir / "msgpack" / "msgpack" / "lib"]
        if "LD_LIBRARY_PATH" in env:
            env["LD_LIBRARY_PATH"] += ":" + ":".join(map(str, lib_paths))
        else:
            env["LD_LIBRARY_PATH"] = ":".join(map(str, lib_paths))

        native_processes = []
        python_processes = []
        # start actors
        for instance_name, (language, actor, *args) in actors.items():
            if language == "python":
                # start python actor
                proc = mp.Process(
                    target=_python_wrapper,
                    args=(tmpdir, instance_name, env["MUSCLE_MANAGER"], actor, *args),
                    name=instance_name,
                )
                proc.start()
                python_processes.append(proc)
                continue
            elif language == "cpp":
                executable = cpp_build_dir / actor
            elif language == "mpicpp":
                assert len(args) > 0, "must provide at least number of mpi instances"
                executable = "mpirun"
                out_file = tmpdir / f"mpi_{instance_name}.log"
                args = (
                    "-np",
                    args[0],
                    mpirun_outfile_arg(),
                    str(out_file),
                    str(cpp_build_dir / actor),
                    *args[1:],
                )
            elif language == "fortran":
                executable = fortran_build_dir / actor
            else:
                raise ValueError(f"Unknown language: {language}")
            # start native code actor
            f_out = stack.enter_context(
                (tmpdir / f"{instance_name}_stdout.txt").open("w")
            )
            f_err = stack.enter_context(
                (tmpdir / f"{instance_name}_stderr.txt").open("w")
            )
            native_processes.append(
                subprocess.Popen(
                    [str(executable), *args, f"--muscle-instance={instance_name}"],
                    env=env,
                    stdout=f_out,
                    stderr=f_err,
                )
            )

        # check results
        remaining_processes = set(native_processes + python_processes)
        success = True
        while remaining_processes and success:
            time.sleep(0.1)
            for proc in list(remaining_processes):
                if isinstance(proc, subprocess.Popen):
                    returncode = proc.poll()
                else:
                    returncode = proc.exitcode
                if returncode is not None:
                    remaining_processes.discard(proc)
                    if returncode != 0:
                        success = False

        for proc in remaining_processes:
            proc.terminate()
        for proc in remaining_processes:
            if isinstance(proc, subprocess.Popen):
                proc.wait()
            else:
                proc.join()

        assert expect_success == success
