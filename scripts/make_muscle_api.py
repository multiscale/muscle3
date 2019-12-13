#!/usr/bin/env python3

import argparse

import api_generator

from api_generator import (
        API, AssignmentOperator, Bool, Bytes, Char, Class, Constructor,
        Destructor, Double, Enum, EnumVal, Float, Int, Int16t, Int64t, MemFun,
        MemFunTmpl, NamedConstructor, Namespace, Obj, OverloadSet, Sizet,
        String, T, VecDbl, Vec2Dbl, Void)


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
    Constructor([Obj('Data', 'value')], 'create_copy'),
    OverloadSet('create', [
        'create_nil', 'create_bool', 'create_string', 'create_char',
        'create_int', 'create_int16t', 'create_int64t', 'create_float',
        'create_double', 'create_copy']),
    Destructor(),
    NamedConstructor([], 'dict'),
    NamedConstructor([], 'list'),
    NamedConstructor([Sizet('size')], 'byte_array'),
    NamedConstructor([Sizet('size')], 'nils'),
    AssignmentOperator('set_data', Obj('Data', 'value')),
    MemFunTmpl(
        [Bool(), String(), Char(), Int(), Int16t(), Int64t(), Float(),
            Double()],
        Bool(), 'is_a', [], False),
    MemFun(Bool(), 'is_a_dict'),
    MemFun(Bool(), 'is_a_list'),
    MemFun(Bool(), 'is_a_byte_array'),
    MemFun(Bool(), 'is_nil'),
    MemFun(Int64t(), 'size'),
    MemFunTmpl(
        [Bool(), String(), Char(), Int16t(), Int(), Int64t(), Float(),
            Double()],
        T(), 'as', [], True),
    MemFun(Bytes('data'), 'as_byte_array', [], True,
        fc_override=(
            'void LIBMUSCLE_Data_as_byte_array_(\n'
            '        std::intptr_t self,\n'
            '        char ** data, std::size_t * data_size,\n'
            '        int * err_code, char ** err_msg, std::size_t * err_msg_len\n'
            ') {\n'
            '    Data * self_p = reinterpret_cast<Data *>(self);\n'
            '    try {\n'
            '        *err_code = 0;\n'
            '        *data = self_p->as_byte_array();\n'
            '        *data_size = self_p->size();\n'
            '        return;\n'
            '    }\n'
            '    catch (std::runtime_error const & e) {\n'
            '        *err_code = 1;\n'
            '        static std::string msg(e.what());\n'
            '        *err_msg = const_cast<char*>(msg.data());\n'
            '        *err_msg_len = msg.size();\n'
            '    }\n'
            '}\n'
            )
        ),
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
