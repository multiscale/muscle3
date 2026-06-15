from .conftest import run_manager_with_actors, skip_if_python_only

CONFIG = """
ymmsl_version: v0.2
description: Reconnect test config for C++
models:
- name: test_cpp_tcp_reconnect
  description: A simple macro-micro model
  components:
    macro:
      ports:
        o_i: out
        s: in
      description: The macro model
      implementation: component
    micro:
      ports:
        f_init: init
        o_f: result
      description: The micro model
      implementation: component
  conduits:
    macro.out: micro.init
    micro.result: macro.in
settings:
  muscle_local_log_level: debug
  muscle_remote_log_level: warning
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
