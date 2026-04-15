import sqlite3

import numpy as np

from libmuscle import Instance, Grid, Message
from ymmsl.v0_2 import Operator

from .conftest import (
        skip_if_python_only, skip_if_no_fortran, run_manager_with_actors)


def check_settings(instance):
    settings = instance.list_settings()

    assert len(settings) == 8   # test1-6, test_with_a_longer_name, python_compat
    setting_seen = [False] * 8
    for setting in settings:
        if setting == 'test1':
            setting_seen[0] = True
        elif setting == 'test2':
            setting_seen[1] = True
        elif setting == 'test3':
            setting_seen[2] = True
        elif setting == 'test4':
            setting_seen[3] = True
        elif setting == 'test5':
            setting_seen[4] = True
        elif setting == 'test6':
            setting_seen[5] = True
        elif setting == 'test_with_a_longer_name':
            setting_seen[6] = True
        elif setting == 'python_compat':
            setting_seen[7] = True
        else:
            raise RuntimeError('Unexpected setting name ' + setting)

    assert all(setting_seen)

    assert isinstance(instance.get_setting('test1'), int)
    assert not isinstance(instance.get_setting('test1'), bool)
    try:
        instance.get_setting('does_not_exist')
    except KeyError:
        pass

    assert instance.get_setting('test1', 'int') == 13
    assert instance.get_setting('test4', 'bool') is True

    # Test get_setting_as with default (scalar types only)
    assert instance.get_setting('test1', 'int', default=99) == 13
    assert instance.get_setting('does_not_exist', 'int', default=99) == 99

    assert instance.get_setting('test4', 'bool', default=False) is True
    assert instance.get_setting('does_not_exist', 'bool', default=False) is False

    assert instance.get_setting('test2', 'float', default=99.0) == 13.3
    assert instance.get_setting('does_not_exist', 'float', default=99.0) == 99.0

    assert instance.get_setting('test3', 'str', default='default') == 'testing'
    assert instance.get_setting('does_not_exist', 'str', default='default') == 'default'


def check_data(data, python_compat):
    assert data['bool'] is True
    assert data['char'] == 23
    assert data['short int'] == 4097
    assert data['int'] == 1234567
    assert data['long int'] == 1234568
    assert data['long long int'] == 6001002003
    if not python_compat:
        assert data['float'] == 1.23456
    assert data['double'] == 1.2345678901234
    assert data['message'] == 'testing'

    r_list = data['list']
    assert r_list[0] == 1
    assert r_list[1] == 'two'
    if not python_compat:
        assert data[2] == 3.0

    r_test_grid = data['test_grid']
    assert isinstance(r_test_grid, Grid)
    assert r_test_grid.array.dtype.type == np.float64
    assert r_test_grid.array.shape == (2, 3)
    assert r_test_grid.array.flat[3] == 4.0
    assert not r_test_grid.indexes


def make_data():
    test_array = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    assert test_array.shape == (2, 3)
    assert test_array.flags.c_contiguous
    return {
            'bool': True,
            'char': 23,
            'short int': 4097,
            'int': 1234567,
            'long int': 1234568,
            'long long int': 6001002003,
            'double': 1.2345678901234,
            'message': 'testing',
            'list': [1, 'two'],
            'test_grid': test_array}


def macro():
    instance = Instance({
            Operator.O_I: ['out'],
            Operator.S: ['in']})

    while instance.reuse_instance():
        # f_init
        python_compat = instance.get_setting('python_compat')
        assert instance.get_setting('test1') == 13

        for i in range(2):
            # o_i
            data = make_data()
            instance.send('out', Message(i * 10.0, (i + 1) * 10.0, data))

            # s/b
            msg = instance.receive('in')
            check_data(msg.data, python_compat)


def micro():
    instance = Instance({
        Operator.F_INIT: ['in'],
        Operator.O_F: ['out']})

    while instance.reuse_instance():
        # f_init
        check_settings(instance)
        python_compat = instance.get_setting('python_compat')

        msg = instance.receive('in')
        check_data(msg.data, python_compat)

        # o_f
        reply = make_data()
        instance.send('out', Message(msg.timestamp, None, reply))


def check_profile_output(tmp_path):
    conn = sqlite3.connect(tmp_path / 'performance.sqlite')
    cur = conn.cursor()

    def check(instance: str, typ: str, port: str, operator: str) -> None:
        cur.execute(
                "SELECT * FROM all_events"
                "    WHERE instance = ? AND type = ?"
                "    ORDER BY start_time", (instance, typ))
        res = cur.fetchall()
        assert len(res) == 2
        assert res[0][4:8] == (port, operator, None, None)
        assert res[0][8] == 0
        assert res[0][9] > 0
        assert res[0][10] == 0.0

        assert res[1][4:8] == (port, operator, None, None)
        assert res[1][8] == 1
        assert res[1][9] > 0
        assert res[1][10] == 10.0

    check('macro', 'SEND', 'out', 'O_I')
    check('micro', 'RECEIVE_TRANSFER', 'in', 'F_INIT')
    check('micro', 'SEND', 'out', 'O_F')
    check('macro', 'RECEIVE_DECODE', 'in', 'S')

    cur.close()
    conn.close()


def test_python_macro_micro(mmp_server_config_simple_python, tmp_path):
    run_manager_with_actors(
            mmp_server_config_simple_python,
            tmp_path,
            {'micro': ('python', micro),
             'macro': ('python', macro)})

    check_profile_output(tmp_path)


@skip_if_python_only
def test_python_cpp_macro_micro(mmp_server_config_simple_python, tmp_path):
    # create C++ micro model
    # see libmuscle/cpp/src/libmuscle/tests/micro_model_test.cpp
    run_manager_with_actors(
            mmp_server_config_simple_python,
            tmp_path,
            {'micro': ('cpp', 'micro_model_test'),
             'macro': ('python', macro)})

    check_profile_output(tmp_path)


@skip_if_python_only
def test_cpp_macro_micro(mmp_server_config_simple_nopython, tmp_path):
    # create C++ micro model
    # see libmuscle/cpp/src/libmuscle/tests/micro_model_test.cpp
    # and libmuscle/cpp/src/libmuscle/tests/macro_model_test.cpp
    run_manager_with_actors(
            mmp_server_config_simple_nopython,
            tmp_path,
            {'micro': ('cpp', 'micro_model_test'),
             'macro': ('cpp', 'macro_model_test')})

    check_profile_output(tmp_path)


@skip_if_python_only
@skip_if_no_fortran
def test_python_fortran_macro_micro(mmp_server_config_simple_python, tmp_path):
    # create Fortran micro model
    # see libmuscle/fortran/src/libmuscle/tests/fortran_micro_model_test.f90
    run_manager_with_actors(
            mmp_server_config_simple_python,
            tmp_path,
            {'micro': ('fortran', 'fortran_micro_model_test'),
             'macro': ('python', macro)})


@skip_if_python_only
@skip_if_no_fortran
def test_fortran_macro_micro(mmp_server_config_simple_nopython, tmp_path):
    # create Fortran micro model
    # see libmuscle/fortran/src/libmuscle/tests/fortran_micro_model_test.f90
    run_manager_with_actors(
            mmp_server_config_simple_nopython,
            tmp_path,
            {'micro': ('fortran', 'fortran_micro_model_test'),
             'macro': ('cpp', 'macro_model_test')})
