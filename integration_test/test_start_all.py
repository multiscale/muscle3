import logging
import os
from pathlib import Path

from qcg.pilotjob.api.manager import LocalManager
import ymmsl
from ymmsl import Implementation

from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir

from .conftest import skip_if_python_only


@skip_if_python_only
def test_start_all(tmpdir, caplog):
    caplog.set_level(logging.DEBUG)

    tmppath = Path(str(tmpdir))

    # find our test component and its requirements
    cpp_build_dir = Path(__file__).parents[1] / 'libmuscle' / 'cpp' / 'build'
    lib_paths = [
            cpp_build_dir / 'grpc' / 'c-ares' / 'c-ares' / 'lib',
            cpp_build_dir / 'grpc' / 'zlib' / 'zlib' / 'lib',
            cpp_build_dir / 'grpc' / 'openssl' / 'openssl' / 'lib',
            cpp_build_dir / 'protobuf' / 'protobuf' / 'lib',
            cpp_build_dir / 'grpc' / 'grpc' / 'lib',
            cpp_build_dir / 'msgpack' / 'msgpack' / 'lib']
    ld_lib_path = ':'.join(map(str, lib_paths))

    cpp_test_dir = cpp_build_dir / 'libmuscle' / 'tests'
    test_component = cpp_test_dir / 'component_test'

    component_script = ((
            '#!/bin/bash\n\n'
            'export LD_LIBRARY_PATH={}\n'
            '{} $*\n').format(ld_lib_path, test_component))

    # make config
    ymmsl_text = (
            'ymmsl_version: v0.1\n'
            'model:\n'
            '  name: test_model\n'
            '  components:\n'
            '    macro: component\n'
            '    micro: component\n'
            '  conduits:\n'
            '    macro.out: micro.init\n'
            '    micro.result: macro.in\n'
            'resources:\n'
            '  macro: 1\n'
            '  micro: 1\n'
            )

    config = ymmsl.load(ymmsl_text)
    config.implementations['component'] = Implementation(
            'component', component_script)

    # set up
    run_dir = RunDir(tmppath / 'run')

    # start QCG (with output in tmppath)
    cwd = Path.cwd()
    os.chdir(tmppath)
    qcg_manager = LocalManager(['--net-port', '5555'])
    os.chdir(cwd)

    # launch MUSCLE Manager with simulation
    manager = Manager(config, run_dir)
    manager.start_instances()
    success = manager.wait()

    # shut down QCG so we don't hang
    qcg_manager.finish()

    # check that all went well
    assert success
