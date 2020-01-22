#!/usr/bin/env python3

import argparse

import api_generator

from api_generator import (
        API, AssignmentOperator, Bool, Bytes, Char, Class, Constructor,
        Destructor, Double, Enum, EnumVal, Float, IndexAssignmentOperator, Int,
        Int16t, Int32t, Int64t, MemFun, MemFunTmpl, NamedConstructor, Namespace,
        Obj, OverloadSet, ShiftedIndexAssignmentOperator, Sizet, String, T,
        VecDbl, Vec2Dbl, Void)


dataconstref_desc = Class('DataConstRef', None, [
    Constructor([], 'create_nil'),
    Constructor([Bool('value')], 'create_logical'),
    Constructor([String('value')], 'create_character'),
    Constructor([Char('value')], 'create_int1'),
    Constructor([Int16t('value')], 'create_int2'),
    Constructor([Int32t('value')], 'create_int4'),
    Constructor([Int64t('value')], 'create_int8'),
    Constructor([Float('value')], 'create_real4'),
    Constructor([Double('value')], 'create_real8'),
    Constructor([Obj('Settings', 'value')], 'create_settings'),
    Constructor([Obj('DataConstRef', 'value')], 'create_copy'),
    OverloadSet('create', [
        'create_nil', 'create_logical', 'create_character', 'create_int1',
        'create_int2', 'create_int4', 'create_int8', 'create_real4',
        'create_real8', 'create_settings', 'create_copy']),
    Destructor(),
    MemFunTmpl(
        [Bool(), String(), Int(), Char(), Int16t(), Int32t(), Int64t(),
            Float(), Double()],
        Bool(), 'is_a', [], False),
    MemFun(Bool(), 'is_a_dict'),
    MemFun(Bool(), 'is_a_list'),
    MemFun(Bool(), 'is_a_byte_array'),
    MemFun(Bool(), 'is_nil'),
    MemFun(Bool(), 'is_a_settings', [], False,
            cpp_chain_call=lambda **kwargs: 'self_p->is_a<Settings>()'),
    MemFun(Sizet(), 'size'),
    MemFunTmpl(
        [Bool(), String(), Int(), Char(), Int16t(), Int32t(), Int64t(),
            Float(), Double()],
        T(), 'as', [], True),
    MemFun(Obj('Settings', 'value'), 'as_settings', [], True,
            cpp_chain_call=lambda **kwargs: 'self_p->as<Settings>()'),
    MemFun(Bytes('data'), 'as_byte_array', [], True,
        fc_override=(
            'void LIBMUSCLE_DataConstRef_as_byte_array_(\n'
            '        std::intptr_t self,\n'
            '        char ** data, std::size_t * data_size,\n'
            '        int * err_code, char ** err_msg, std::size_t * err_msg_len\n'
            ') {\n'
            '    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);\n'
            '    try {\n'
            '        *err_code = 0;\n'
            '        *data = const_cast<char*>(self_p->as_byte_array());\n'
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
    MemFun(Obj('DataConstRef', 'value'), 'get_item_by_key', [String('key')], True,
            fc_override=(
                'std::intptr_t LIBMUSCLE_DataConstRef_get_item_by_key_(\n'
                '        std::intptr_t self,\n'
                '        char * key, std::size_t key_size,\n'
                '        int * err_code, char ** err_msg, std::size_t * err_msg_len\n'
                ') {\n'
                '    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);\n'
                '    std::string key_s(key, key_size);\n'
                '    try {\n'
                '        *err_code = 0;\n'
                '        DataConstRef * result = new DataConstRef((*self_p)[key_s]);\n'
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
    MemFun(Obj('DataConstRef', 'value'), 'get_item_by_index', [Sizet('i')], True,
            fc_override=(
                'std::intptr_t LIBMUSCLE_DataConstRef_get_item_by_index_(\n'
                '        std::intptr_t self,\n'
                '        std::size_t i,\n'
                '        int * err_code, char ** err_msg, std::size_t * err_msg_len\n'
                ') {\n'
                '    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);\n'
                '    try {\n'
                '        *err_code = 0;\n'
                '        DataConstRef * result = new DataConstRef((*self_p)[i-1u]);\n'
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
    OverloadSet('get_item', [
        'get_item_by_key', 'get_item_by_index'
        ]),
    ])


data_desc = Class('Data', dataconstref_desc, [
    Constructor([Obj('Data', 'value')], 'create_copy'),
    NamedConstructor([], 'dict'),
    NamedConstructor([], 'list'),
    NamedConstructor([Sizet('size')], 'nils'),
    NamedConstructor([Sizet('size')], 'byte_array_empty',
        cpp_func_name='byte_array'),
    NamedConstructor([Bytes('buf')], 'byte_array_from_buf',
        cpp_func_name='byte_array',
        fc_override=(
            'std::intptr_t LIBMUSCLE_Data_create_byte_array_from_buf_(\n'
            '       char * buf, std::size_t buf_size\n'
            ') {\n'
            '   Data * result = new Data(Data::byte_array(buf, buf_size));\n'
            '   return reinterpret_cast<std::intptr_t>(result);\n'
            '}\n\n'
            )
        ),
    OverloadSet('create_byte_array', [
        'create_byte_array_empty', 'create_byte_array_from_buf']),

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
                '        Data * self_p = reinterpret_cast<DataConstRef *>(self);\n'
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

    AssignmentOperator('set_logical', Bool('value')),
    AssignmentOperator('set_character', String('value')),
    AssignmentOperator('set_int1', Char('value')),
    AssignmentOperator('set_int2', Int16t('value')),
    AssignmentOperator('set_int4', Int32t('value')),
    AssignmentOperator('set_int8', Int64t('value')),
    AssignmentOperator('set_real4', Float('value')),
    AssignmentOperator('set_real8', Double('value')),
    AssignmentOperator('set_data', Obj('Data', 'value')),
    OverloadSet('set', [
        'set_logical', 'set_character', 'set_int1', 'set_int2', 'set_int4',
        'set_int8', 'set_real4', 'set_real8', 'set_data']),
    MemFun(Void(), 'set_nil', [], False,
        fc_override=(
            'void LIBMUSCLE_Data_set_nil_(std::intptr_t self) {\n'
            '    Data * self_p = reinterpret_cast<Data *>(self);\n'
            '    *self_p = Data();\n'
            '}\n\n'
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
    IndexAssignmentOperator('set_item_key_logical', [String('key'), Bool('value')], True),
    IndexAssignmentOperator('set_item_key_character', [String('key'), String('value')], True),
    IndexAssignmentOperator('set_item_key_int1', [String('key'), Char('value')], True),
    IndexAssignmentOperator('set_item_key_int2', [String('key'), Int16t('value')], True),
    IndexAssignmentOperator('set_item_key_int4', [String('key'), Int('value')], True),
    IndexAssignmentOperator('set_item_key_int8', [String('key'), Int64t('value')], True),
    IndexAssignmentOperator('set_item_key_real4', [String('key'), Float('value')], True),
    IndexAssignmentOperator('set_item_key_real8', [String('key'), Double('value')], True),
    IndexAssignmentOperator('set_item_key_data', [String('key'), Obj('Data', 'value')], True),
    ShiftedIndexAssignmentOperator('set_item_index_logical', [Sizet('i'), Bool('value')], True),
    ShiftedIndexAssignmentOperator('set_item_index_character', [Sizet('i'), String('value')], True),
    ShiftedIndexAssignmentOperator('set_item_index_int1', [Sizet('i'), Char('value')], True),
    ShiftedIndexAssignmentOperator('set_item_index_int2', [Sizet('i'), Int16t('value')], True),
    ShiftedIndexAssignmentOperator('set_item_index_int4', [Sizet('i'), Int('value')], True),
    ShiftedIndexAssignmentOperator('set_item_index_int8', [Sizet('i'), Int64t('value')], True),
    ShiftedIndexAssignmentOperator('set_item_index_real4', [Sizet('i'), Float('value')], True),
    ShiftedIndexAssignmentOperator('set_item_index_real8', [Sizet('i'), Double('value')], True),
    ShiftedIndexAssignmentOperator('set_item_index_data', [Sizet('i'), Obj('Data', 'value')], True),
    OverloadSet('set_item', [
        'set_item_key_logical', 'set_item_key_character', 'set_item_key_int1',
        'set_item_key_int2', 'set_item_key_int4', 'set_item_key_int8',
        'set_item_key_real4', 'set_item_key_real8', 'set_item_key_data',
        'set_item_index_logical', 'set_item_index_character', 'set_item_index_int1',
        'set_item_index_int2', 'set_item_index_int4', 'set_item_index_int8',
        'set_item_index_real4', 'set_item_index_real8', 'set_item_index_data'
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


message_desc = Class('Message', None, [
    Constructor([Double('timestamp'), Obj('Data', 'data')], 'create_td'),
    Constructor(
        [Double('timestamp'), Double('next_timestamp'), Obj('Data', 'data')],
        'create_tnd'),
    Constructor(
        [Double('timestamp'), Obj('Data', 'data'), Obj('Settings', 'settings')],
        'create_tds'),
    Constructor(
        [Double('timestamp'), Double('next_timestamp'), Obj('Data', 'data'),
            Obj('Settings', 'settings')],
        'create_tnds'),
    OverloadSet('create', [
        'create_td', 'create_tnd', 'create_tds', 'create_tnds']),
    Destructor(),
    MemFun(Double(), 'timestamp'),
    MemFun(Void(), 'set_timestamp', [Double('timestamp')]),
    MemFun(Bool(), 'has_next_timestamp'),
    MemFun(Double(), 'next_timestamp'),
    MemFun(Void(), 'set_next_timestamp', [Double('next_timestamp')]),
    MemFun(Void(), 'unset_next_timestamp'),
    ])


cmdlineargs_desc = Class('CmdLineArgs', None, [
        Constructor([Int('count')]),
        Destructor(),
        MemFun(Void(), 'set_arg', [Int('i'), String('arg')]),
        ])


ymmsl_forward = [Class('Settings', None, [])]


libmuscle_api_description = API(
        'libmuscle',
        [
            'libmuscle/libmuscle.hpp',
            'libmuscle/bindings/cmdlineargs.hpp',
            'ymmsl/ymmsl.hpp',
            'stdexcept'],
        [
            'ymmsl'],
        [
            Namespace('libmuscle', True, 'LIBMUSCLE', [], [
                dataconstref_desc, data_desc, message_desc]),
            Namespace('libmuscle::impl::bindings', False,
                      'LIBMUSCLE_IMPL_BINDINGS', [], [cmdlineargs_desc]),
            Namespace('ymmsl', None, 'YMMSL', [], ymmsl_forward)
        ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MUSCLE API Generator')
    parser.add_argument('--fortran-c-wrappers', action='store_true')
    parser.add_argument('--fortran-module', action='store_true')

    args = parser.parse_args()
    if args.fortran_c_wrappers:
        print(libmuscle_api_description.fortran_c_wrapper())
    elif args.fortran_module:
        print(libmuscle_api_description.fortran_module())
