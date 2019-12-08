#!/usr/bin/env python3

import argparse

import api_generator

from api_generator import (
        API, Bool, Bytes, Char, Class, Constructor, Destructor, Double, Enum,
        EnumVal, Float, Int, Int16t, Int64t, MemFun, MemFunTmpl, Namespace,
        Obj, OverloadSet, String, T, VecDbl, Vec2Dbl, Void)


data_desc = Class('Data', [
    Constructor([], 'create_nil'),
    Constructor([Bool('value')], 'create_bool'),
    Constructor([String('value')], 'create_string'),
    Constructor([Char('value')], 'create_char'),
    Constructor([Int('value')], 'create_int'),
    Constructor([Int16t('value')], 'create_int16t'),
    Constructor([Int64t('value')], 'create_int64t'),
    Constructor([Float('value')], 'create_float'),
    Constructor([Double('value')], 'create_double'),
    OverloadSet('create', [
        'create_nil', 'create_bool', 'create_string', 'create_char',
        'create_int', 'create_int16t', 'create_int64t', 'create_float',
        'create_double']),
    Destructor(),
    MemFunTmpl(
        [Bool(), String(), Char(), Int(), Int16t(), Int64t(), Float(),
            Double()],
        Bool(), 'is_a', [], True)
    ])


cmdlineargs_desc = Class('CmdLineArgs', [
        Constructor([Int('count')]),
        Destructor(),
        MemFun(Void(), 'set_arg', [Int('i'), String('arg')]),
        ])


libmuscle_api_description = API(
        'libmuscle',
        [
            'libmuscle/libmuscle.hpp',
            'libmuscle/bindings/cmdlineargs.hpp',
            'stdexcept'],
        [
            Namespace('libmuscle', True, 'LIBMUSCLE', [], [data_desc]),
            Namespace('libmuscle::impl::bindings', False,
                      'LIBMUSCLE_IMPL_BINDINGS', [], [cmdlineargs_desc])])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MUSCLE API Generator')
    parser.add_argument('--fortran-c-wrappers', action='store_true')
    parser.add_argument('--fortran-module', action='store_true')

    args = parser.parse_args()
    if args.fortran_c_wrappers:
        print(libmuscle_api_description.fortran_c_wrapper())
    elif args.fortran_module:
        print(libmuscle_api_description.fortran_module())
