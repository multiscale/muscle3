#!/usr/bin/env python3

import argparse

import api_generator

from api_generator import (
        API, Bool, Bytes, Class, Constructor, Destructor, Double, Enum,
        EnumVal, Int, Int64t, MemFun, MemFunTmpl, Namespace, Obj, OverloadSet,
        String, T, VecDbl, Vec2Dbl, Void)


data_desc = Class('Data', [
    Constructor(),
    Destructor()
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
