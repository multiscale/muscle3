#!/usr/bin/env python3

import argparse

import api_generator

from api_generator import (
        API, AssignmentOperator, Bool, Bytes, Char, Class, Constructor,
        Destructor, Double, Enum, EnumVal, Float, IndexAssignmentOperator, Int,
        Int16t, Int64t, MemFun, MemFunTmpl, NamedConstructor, Namespace, Obj,
        OverloadSet, Sizet, String, T, VecDbl, Vec2Dbl, Void)


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
    AssignmentOperator('set_bool', Bool('value')),
    AssignmentOperator('set_string', String('value')),
    AssignmentOperator('set_char', Char('value')),
    AssignmentOperator('set_int16', Int16t('value')),
    AssignmentOperator('set_int', Int('value')),
    AssignmentOperator('set_int64', Int64t('value')),
    AssignmentOperator('set_float', Float('value')),
    AssignmentOperator('set_double', Double('value')),
    AssignmentOperator('set_data', Obj('Data', 'value')),
    OverloadSet('set', [
        'set_bool', 'set_string', 'set_char', 'set_int16', 'set_int',
        'set_int64', 'set_float', 'set_double', 'set_data']),
    MemFun(Void(), 'set_nil', [], False,
        fc_override=(
            'void LIBMUSCLE_Data_set_nil_(std::intptr_t self) {\n'
            '    Data * self_p = reinterpret_cast<Data *>(self);\n'
            '    *self_p = Data();\n'
            '}\n\n'
            )
        ),
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
    MemFun(Obj('Data', 'value'), 'get_item_by_key', [String('key')], True,
            fc_override=(
                'std::intptr_t LIBMUSCLE_Data_get_item_by_key_(\n'
                '        std::intptr_t self,\n'
                '        char * key, std::size_t key_size,\n'
                '        int * err_code, char ** err_msg, std::size_t * err_msg_len\n'
                ') {\n'
                '    Data * self_p = reinterpret_cast<Data *>(self);\n'
                '    std::string key_s(key, key_size);\n'
                '    try {\n'
                '        *err_code = 0;\n'
                '        Data * result = new Data((*self_p)[key_s]);\n'
                '        return reinterpret_cast<std::intptr_t>(result);\n'
                '    }\n'
                '    catch (std::runtime_error const & e) {\n'
                '        *err_code = 1;\n'
                '        static std::string msg;\n'
                '        msg = e.what();\n'
                '        *err_msg = const_cast<char*>(msg.data());\n'
                '        *err_msg_len = msg.size();\n'
                '    }\n'
                '    catch (std::out_of_range const & e) {\n'
                '        *err_code = 3;\n'
                '        static std::string msg;\n'
                '        msg = e.what();\n'
                '        *err_msg = const_cast<char*>(msg.data());\n'
                '        *err_msg_len = msg.size();\n'
                '    }\n'
                '}\n\n')
            ),
    MemFun(Obj('Data', 'value'), 'get_item_by_index', [Sizet('i')], True,
            fc_override=(
                'std::intptr_t LIBMUSCLE_Data_get_item_by_index_(\n'
                '        std::intptr_t self,\n'
                '        std::size_t i,\n'
                '        int * err_code, char ** err_msg, std::size_t * err_msg_len\n'
                ') {\n'
                '        Data * self_p = reinterpret_cast<Data *>(self);\n'
                '        try {\n'
                '            *err_code = 0;\n'
                '            Data * result = new Data((*self_p)[i-1u]);\n'
                '            return reinterpret_cast<std::intptr_t>(result);\n'
                '    }\n'
                '    catch (std::runtime_error const & e) {\n'
                '        *err_code = 1;\n'
                '        static std::string msg;\n'
                '        msg = e.what();\n'
                '        *err_msg = const_cast<char*>(msg.data());\n'
                '        *err_msg_len = msg.size();\n'
                '    }\n'
                '    catch (std::out_of_range const & e) {\n'
                '        *err_code = 3;\n'
                '        static std::string msg;\n'
                '        msg = e.what();\n'
                '        *err_msg = const_cast<char*>(msg.data());\n'
                '        *err_msg_len = msg.size();\n'
                '    }\n'
                '}\n\n')
            ),
    OverloadSet('get_item', [
        'get_item_by_key', 'get_item_by_index'
        ]),
    IndexAssignmentOperator('set_item_key_bool', [String('key'), Bool('value')], True),
    IndexAssignmentOperator('set_item_key_string', [String('key'), String('value')], True),
    IndexAssignmentOperator('set_item_key_char', [String('key'), Char('value')], True),
    IndexAssignmentOperator('set_item_key_int16', [String('key'), Int16t('value')], True),
    IndexAssignmentOperator('set_item_key_int', [String('key'), Int('value')], True),
    IndexAssignmentOperator('set_item_key_int64', [String('key'), Int64t('value')], True),
    IndexAssignmentOperator('set_item_key_float', [String('key'), Float('value')], True),
    IndexAssignmentOperator('set_item_key_double', [String('key'), Double('value')], True),
    IndexAssignmentOperator('set_item_key_data', [String('key'), Obj('Data', 'value')], True),
    OverloadSet('set_item', [
        'set_item_key_bool', 'set_item_key_string', 'set_item_key_char',
        'set_item_key_int16', 'set_item_key_int', 'set_item_key_int64',
        'set_item_key_float', 'set_item_key_double', 'set_item_key_data'
        ]),
    MemFun(String(), 'key', [Sizet('i')], True,
            fc_override=(
                'void LIBMUSCLE_Data_key_(\n'
                '        std::intptr_t self, std::size_t i,\n'
                '        char ** ret_val, std::size_t * ret_val_size,\n'
                '        int * err_code,\n'
                '        char ** err_msg, std::size_t * err_msg_len\n'
                ') {\n'
                '    try {\n'
                '        *err_code = 0;\n'
                '        Data * self_p = reinterpret_cast<Data *>(self);\n'
                '        static std::string result;\n'
                '        result = self_p->key(i - 1);\n'
                '        *ret_val = const_cast<char*>(result.c_str());\n'
                '        *ret_val_size = result.size();\n'
                '        return;\n'
                '    }\n'
                '    catch (std::runtime_error const & e) {\n'
                '        *err_code = 1;\n'
                '        static std::string msg;\n'
                '        msg = e.what();\n'
                '        *err_msg = const_cast<char*>(msg.data());\n'
                '        *err_msg_len = msg.size();\n'
                '    }\n'
                '    catch (std::out_of_range const & e) {\n'
                '        *err_code = 3;\n'
                '        static std::string msg;\n'
                '        msg = e.what();\n'
                '        *err_msg = const_cast<char*>(msg.data());\n'
                '        *err_msg_len = msg.size();\n'
                '    }\n'
                '}\n\n')
            ),
    MemFun(Obj('Data'), 'value', [Sizet('i')], True,
            fc_override=(
                'std::intptr_t LIBMUSCLE_Data_value_(\n'
                '        std::intptr_t self, std::size_t i,\n'
                '        int * err_code,\n'
                '        char ** err_msg, std::size_t * err_msg_len\n'
                ') {\n'
                '    try {\n'
                '        *err_code = 0;\n'
                '        Data * self_p = reinterpret_cast<Data *>(self);\n'
                '        Data * result = new Data(self_p->value(i - 1));\n'
                '        return reinterpret_cast<std::intptr_t>(result);\n'
                '    }\n'
                '    catch (std::runtime_error const & e) {\n'
                '        *err_code = 1;\n'
                '        static std::string msg;\n'
                '        msg = e.what();\n'
                '        *err_msg = const_cast<char*>(msg.data());\n'
                '        *err_msg_len = msg.size();\n'
                '    }\n'
                '    catch (std::out_of_range const & e) {\n'
                '        *err_code = 3;\n'
                '        static std::string msg;\n'
                '        msg = e.what();\n'
                '        *err_msg = const_cast<char*>(msg.data());\n'
                '        *err_msg_len = msg.size();\n'
                '    }\n'
                '}\n\n')
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
