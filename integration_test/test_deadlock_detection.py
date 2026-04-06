import functools
import sys

from ymmsl.v0_2 import Operator

from libmuscle import Instance, Message

from .conftest import skip_if_python_only, run_manager_with_actors


def suppress_deadlock_exception_output(func):
    @functools.wraps(func)
    def wrapper():
        try:
            func()
        except RuntimeError as exc:
            exc_str = str(exc).lower()
            if "deadlock" not in exc_str and "did the peer crash?" not in exc_str:
                raise
            sys.exit(1)
    return wrapper


@suppress_deadlock_exception_output
def deadlocking_micro():
    instance = Instance({Operator.F_INIT: ["in"], Operator.O_F: ["out"]})

    counter = 5  # Deadlock after 5 iterations
    while instance.reuse_instance():
        message = instance.receive("in")
        counter -= 1
        if counter > 0:
            instance.send("out", message)


@suppress_deadlock_exception_output
def micro():
    instance = Instance({Operator.F_INIT: ["in"], Operator.O_F: ["out"]})

    while instance.reuse_instance():
        message = instance.receive("in")
        instance.send("out", message)


@suppress_deadlock_exception_output
def deadlocking_macro():
    instance = Instance({Operator.O_I: ["out"], Operator.S: ["in"]})

    while instance.reuse_instance():
        for i in range(10):
            message = Message(float(i), data="testing")
            instance.send("out", message)
            instance.receive("in")
        # Deadlock:
        instance.receive("in")


@suppress_deadlock_exception_output
def macro():
    instance = Instance({Operator.O_I: ["out"], Operator.S: ["in"]})

    while instance.reuse_instance():
        for i in range(10):
            message = Message(float(i), data="testing")
            instance.send("out", message)
            instance.receive("in")


MACRO_MICRO_CONFIG = """
ymmsl_version: v0.2
description: Another simple macro-micro configuration
models:
- name: test_model
  description: The test model
  components:
    macro:
      ports:
        o_i: out
        s: in
      description: The macro model
      implementation: macro
    micro:
      ports:
        f_init: in
        o_f: out
      description: The micro model
      implementation: micro
  conduits:
    macro.out: micro.in
    micro.out: macro.in
settings:
  muscle_deadlock_receive_timeout: 0.1
"""


MACRO_MICRO_WITH_DISPATCH_CONFIG = """
ymmsl_version: v0.2
description: This one dispatches between three serial micros
models:
- name: test_model
  description: The test model
  components:
    macro:
      ports:
        o_i: out
        s: in
      description: The macro model
      implementation: macro
    micro1:
      ports:
        f_init: in
        o_f: out
      description: The first micro model
      implementation: micro
    micro2:
      ports:
        f_init: in
        o_f: out
      description: The second micro model
      implementation: micro
    micro3:
      ports:
        f_init: in
        o_f: out
      description: The third micro model
      implementation: micro
  conduits:
    macro.out: micro1.in
    micro1.out: micro2.in
    micro2.out: micro3.in
    micro3.out: macro.in
settings:
  muscle_deadlock_receive_timeout: 0.1
"""


def test_no_deadlock(tmp_path):
    run_manager_with_actors(
        MACRO_MICRO_CONFIG, tmp_path,
        {"macro": ("python", macro),
         "micro": ("python", micro)})


def test_deadlock1(tmp_path):
    run_manager_with_actors(
        MACRO_MICRO_CONFIG, tmp_path,
        {"macro": ("python", macro),
         "micro": ("python", deadlocking_micro)},
        expect_success=False)


def test_deadlock2(tmp_path):
    run_manager_with_actors(
        MACRO_MICRO_CONFIG, tmp_path,
        {"macro": ("python", deadlocking_macro),
         "micro": ("python", micro)},
        expect_success=False)


def test_no_deadlock_with_dispatch(tmp_path):
    run_manager_with_actors(
        MACRO_MICRO_WITH_DISPATCH_CONFIG, tmp_path,
        {"macro": ("python", macro),
         "micro1": ("python", micro),
         "micro2": ("python", micro),
         "micro3": ("python", micro)})


def test_deadlock1_with_dispatch(tmp_path):
    run_manager_with_actors(
        MACRO_MICRO_WITH_DISPATCH_CONFIG, tmp_path,
        {"macro": ("python", macro),
         "micro1": ("python", micro),
         "micro2": ("python", deadlocking_micro),
         "micro3": ("python", micro)},
        expect_success=False)


def test_deadlock2_with_dispatch(tmp_path):
    run_manager_with_actors(
        MACRO_MICRO_WITH_DISPATCH_CONFIG, tmp_path,
        {"macro": ("python", deadlocking_macro),
         "micro1": ("python", micro),
         "micro2": ("python", micro),
         "micro3": ("python", micro)},
        expect_success=False)


@skip_if_python_only
def test_no_deadlock_cpp(tmp_path):
    run_manager_with_actors(
        MACRO_MICRO_CONFIG, tmp_path,
        {"macro": ("cpp", "component_test"),
         "micro": ("python", micro)})


@skip_if_python_only
def test_deadlock1_cpp(tmp_path):
    run_manager_with_actors(
        MACRO_MICRO_CONFIG, tmp_path,
        {"macro": ("cpp", "component_test"),
         "micro": ("python", deadlocking_micro)},
        expect_success=False)


@skip_if_python_only
def test_deadlock2_cpp(tmp_path):
    run_manager_with_actors(
        MACRO_MICRO_WITH_DISPATCH_CONFIG, tmp_path,
        {"macro": ("cpp", "component_test"),
         "micro1": ("python", micro),
         "micro2": ("python", deadlocking_micro),
         "micro3": ("cpp", "component_test")},
        expect_success=False)
