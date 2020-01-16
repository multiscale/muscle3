#!/usr/bin/env python3

import argparse

import api_generator

from api_generator import (
        API, AssignmentOperator, Bool, Bytes, Char, Class, Constructor,
        Destructor, Double, Enum, EnumVal, EqualsOperator, Float,
        IndexAssignmentOperator, Int, Int16t, Int32t, Int64t, MemFun,
        MemFunTmpl, NamedConstructor, Namespace, Obj, OverloadSet,
        ShiftedIndexAssignmentOperator, Sizet, String, T, VecDbl, Vec2Dbl,
        Void)


settings_desc = Class('Settings', [
    Constructor(),
    Destructor(),
    EqualsOperator(Obj('Settings', 'other')),
    MemFun(Sizet('size'), 'size'),
    MemFun(Bool('empty'), 'empty'),
    ])


ymmsl_api_description = API(
        'ymmsl',
        [
            'ymmsl/ymmsl.hpp',
            'stdexcept'],
        [
            Namespace('ymmsl', True, 'YMMSL', [], [settings_desc]),
        ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MUSCLE API Generator')
    parser.add_argument('--fortran-c-wrappers', action='store_true')
    parser.add_argument('--fortran-module', action='store_true')

    args = parser.parse_args()
    if args.fortran_c_wrappers:
        print(ymmsl_api_description.fortran_c_wrapper())
    elif args.fortran_module:
        print(ymmsl_api_description.fortran_module())
