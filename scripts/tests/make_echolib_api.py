#!/usr/bin/env python3

import argparse

from api_generator import (
        API, Bool, Bytes, Class, Constructor, Destructor, Double, Enum,
        EnumVal, Int, Int64t, MemFun, MemFunTmpl, Namespace, Obj, OverloadSet,
        String, T, VecDbl, Vec2Dbl, Void)


color_desc = Enum('Color', [('RED', 1), ('GREEN', 2), ('BLUE', 3)])


cmdlineargs_desc = Class('CmdLineArgs', None, [
        Constructor([Int('count')]),
        Destructor(),
        MemFun(Void(), 'set_arg', [Int('i'), String('arg')]),
        ])


echo_desc = Class('Echo', None, [
        Constructor([Obj('CmdLineArgs', 'cla')], fc_override=(
            'std::intptr_t ECHO_Echo_create_(std::intptr_t cla) {\n'
            '    CmdLineArgs * cla_p = reinterpret_cast<CmdLineArgs *>(\n'
            '            cla);\n'
            '    Echo * result = new Echo(cla_p->argc(), cla_p->argv());\n'
            '    return reinterpret_cast<std::intptr_t>(result);\n'
            '}\n\n'),
            f_override=(
                'type(ECHO_Echo) function ECHO_Echo_create()\n'
                '    implicit none\n'
                '\n'
                '    integer :: num_args, i, arg_len\n'
                '    integer (c_intptr_t) :: cla\n'
                '    character (kind=c_char, len=:), allocatable :: cur_arg\n'
                '\n'
                '    num_args = command_argument_count()\n'
                '    cla = ECHO_impl_CmdLineArgs_create_(num_args + 1)\n'
                '    do i = 0, num_args\n'
                '        call get_command_argument(i, length=arg_len)\n'
                '        allocate (character(arg_len+1) :: cur_arg)\n'
                '        call get_command_argument(i, value=cur_arg)\n'
                '        cur_arg(arg_len+1:arg_len+1) = c_null_char\n'
                '        call ECHO_impl_CmdLineArgs_set_arg_('
                        'cla, i, cur_arg, int(len(cur_arg), c_size_t))\n'  # noqa: E131
                '        deallocate(cur_arg)\n'
                '    end do\n'
                '    ECHO_Echo_create%ptr = ECHO_Echo_create_(cla)\n'
                '    call ECHO_impl_CmdLineArgs_free_(cla)\n'
                'end function ECHO_Echo_create\n'
                '\n'
                )),
        Destructor(),
        MemFun(Void(), 'echo_nothing'),
        MemFun(Int(), 'echo_int', [Int('value')]),
        MemFun(Int64t(), 'echo_int64_t', [Int64t('value')]),
        MemFun(Double(), 'echo_double', [Double('value')]),
        MemFun(Bool(), 'echo_bool', [Bool('value')]),
        MemFun(EnumVal('Color'), 'echo_enum', [EnumVal('Color', 'value')]),
        MemFun(String(), 'echo_string', [String('value')]),
        MemFun(VecDbl('echo'), 'echo_double_vec', [VecDbl('value')]),
        MemFun(Vec2Dbl('echo'), 'echo_double_vec2', [Vec2Dbl('value')]),
        MemFun(Obj('Echo'), 'echo_object', [Obj('Echo', 'value')]),
        MemFun(Bytes('echo'), 'echo_bytes', [Bytes('value')]),
        MemFun(String(), 'echo_error', [Double('value')], True),
        MemFunTmpl(
                [Int(), Double(), String()],
                T(), 'echo_template', [T('value')], True),
        OverloadSet('echo', ['echo_int', 'echo_bool', 'echo_double'], False),
        ])


test_api_description = API(
        'echolib',
        [
            'echolib.hpp',
            'cmdlineargs.hpp',
            'cstdint',
            'stdexcept',
            'string',
            'typeinfo',
            'vector'],
        [],
        [
            Namespace('echolib', True, 'ECHO', 'ECHO', [color_desc, echo_desc]),
            Namespace('echolib::impl', False, 'ECHO_impl', 'ECHO_impl',
                      [cmdlineargs_desc])
            ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test API Generator')
    parser.add_argument('--fortran-c-wrappers', action='store_true')
    parser.add_argument('--fortran-module', action='store_true')

    args = parser.parse_args()
    if args.fortran_c_wrappers:
        print(test_api_description.fortran_c_wrapper())
    elif args.fortran_module:
        print(test_api_description.fortran_module())
