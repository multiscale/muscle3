from .conftest import skip_if_python_only, run_manager_with_actors


CONFIG = """
ymmsl_version: v0.1
model:
  name: test_cpp_tcp_reconnect
  components:
    macro:
      implementation: component
    micro:
      implementation: component
  conduits:
    macro.out: micro.init
    micro.result: macro.in
settings:
  muscle_local_log_level: debug
  muscle_remote_log_level: debug
"""


@skip_if_python_only
def test_cpp_tcp_reconnect(tmp_path):
    # create C++ macro/micro model
    # see libmuscle/cpp/src/libmuscle/tests/tcp_reconnect_test.cpp
    run_manager_with_actors(
            CONFIG,
            tmp_path,
            {'macro': ('cpp', 'tcp_reconnect_test'),
             'micro': ('cpp', 'tcp_reconnect_test')})
