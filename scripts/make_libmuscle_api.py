#!/usr/bin/env python3

import argparse
from copy import copy
from textwrap import indent
from typing import Dict, List, Optional

from api_generator import (
        API, Array, AssignmentOperator, Bool, Bytes, Char, Class, Constructor,
        Destructor, Double, Enum, EnumVal, Float, IndexAssignmentOperator, Int,
        Int16t, Int32t, Int64t, Member, MemFun, MemFunTmpl, MultiMemFun,
        NamedConstructor, Namespace, Obj, OverloadSet,
        ShiftedIndexAssignmentOperator, Sizet, String, T, VecDbl, Vec2Dbl,
        VecSizet, Void)


class GridConstructor(MultiMemFun):
    """Creates a constructor for grids.

    Grid constructors are a bit weird, with multidimensional array
    arguments, and a number of arguments that depends on the number of
    dimensions of that array. I don't have the time to implement that
    generically, so we're using this custom class. It's a hack, and
    nobody likes hacks, but it's what we can do. Also, this only runs
    once, and the output is verified by the test suite, so it's not
    very dangerous, just ugly.
    """

    def __init__(self, with_names: bool) -> None:
        """Create a grid constructor.

        This creates a set of named constructors, one for each
        combination of five element types and seven dimensions. If
        with_names is True, every instance has n additional string
        arguments for index names, where n is the number of dimensions
        of the array it accepts.

        Args:
            with_names: Whether to add index name arguments.
        """
        self.ns_prefix = None       # type: Optional[str]
        self.public = None          # type: Optional[bool]
        self.class_name = None      # type: Optional[str]
        self.with_names = with_names
        self.types = [Bool(), Int32t(), Int64t(), Float(), Double()]
        self.name = 'grid'
        self.instances = list()     # type: List[NamedConstructor]

        # generate flexible C functions
        for typ in self.types:
            # This is not set yet here, but f_type() needs it.
            # The dict is only used by Obj, which we don't have.
            typ.name = 'data_array'
            typ.set_ns_prefix({}, 'LIBMUSCLE')

            instance_params = [Array(1, copy(typ), 'data_array')]
            if not with_names:
                instance_name = 'grid_{}_a'.format(typ.tname())
                chain_call = lambda **kwargs: ('{}::grid(data_array_p,'
                        ' data_array_shape_v, {{}},'
                        ' libmuscle::StorageOrder::first_adjacent'
                        ')').format(kwargs['class_name'])
                self.instances.append(NamedConstructor(
                    instance_params, instance_name, cpp_func_name='grid',
                    cpp_chain_call=chain_call, f_override=''))
            else:
                for i in range(1, 8):
                    arg_name = 'index_name_{}'.format(i)
                    instance_params.append(String(arg_name))
                instance_name = 'grid_{}_n'.format(typ.tname())
                fc_override=(
                        'std::intptr_t LIBMUSCLE_$CLASSNAME$_create_grid_{0}_n_(\n'
                        '        {1} * data_array,\n'
                        '        std::size_t * data_array_shape,\n'
                        '        std::size_t data_array_ndims,\n'
                        '        char * index_name_1, std::size_t index_name_1_size,\n'
                        '        char * index_name_2, std::size_t index_name_2_size,\n'
                        '        char * index_name_3, std::size_t index_name_3_size,\n'
                        '        char * index_name_4, std::size_t index_name_4_size,\n'
                        '        char * index_name_5, std::size_t index_name_5_size,\n'
                        '        char * index_name_6, std::size_t index_name_6_size,\n'
                        '        char * index_name_7, std::size_t index_name_7_size\n'
                        ') {{\n'
                        '    std::vector<std::size_t> data_array_shape_v(\n'
                        '            data_array_shape, data_array_shape + data_array_ndims);\n'
                        '    auto data_array_p = const_cast<{1} const * const>(data_array);\n'
                        '\n'
                        '    std::vector<std::string> names_v;\n'
                        '    names_v.push_back(std::string(index_name_1, index_name_1_size));\n'
                        '    if (data_array_ndims >= 2u)\n'
                        '        names_v.push_back(std::string(index_name_2, index_name_2_size));\n'
                        '    if (data_array_ndims >= 3u)\n'
                        '        names_v.push_back(std::string(index_name_3, index_name_3_size));\n'
                        '    if (data_array_ndims >= 4u)\n'
                        '        names_v.push_back(std::string(index_name_4, index_name_4_size));\n'
                        '    if (data_array_ndims >= 5u)\n'
                        '        names_v.push_back(std::string(index_name_5, index_name_5_size));\n'
                        '    if (data_array_ndims >= 6u)\n'
                        '        names_v.push_back(std::string(index_name_6, index_name_6_size));\n'
                        '    if (data_array_ndims >= 7u)\n'
                        '        names_v.push_back(std::string(index_name_7, index_name_7_size));\n'
                        '\n'
                        '    Data * result = new Data(Data::grid(\n'
                        '            data_array_p, data_array_shape_v,\n'
                        '            names_v, libmuscle::StorageOrder::first_adjacent));\n'
                        '    return reinterpret_cast<std::intptr_t>(result);\n'
                        '}}\n\n').format(typ.tname(), typ.fc_cpp_type())
                self.instances.append(NamedConstructor(
                    instance_params, instance_name, fc_override=fc_override,
                    f_override=''))

        # generate instances
        for typ in self.types:
            for ndims in range(1, 8):
                instance_params = [Array(ndims, copy(typ), 'data_array')]
                if with_names:
                    for i in range(1, ndims+1):
                        arg_name = 'index_name_{}'.format(i)
                        instance_params.append(String(arg_name))

                instance_name = 'grid_{}_{}_{}'.format(
                        ndims, typ.tname(), 'n' if with_names else 'a')

                if with_names:
                    arg_list = [
                            'index_name_{}'.format(i)
                            for i in range(1, ndims+1)]
                    name_args = ', &\n        '.join(arg_list)
                    name_types = ''.join([
                            '    character (len=*), intent(in) :: {}\n'.format(arg)
                            for arg in arg_list])
                    name_params = ', &\n'.join([(
                        '            index_name_{0},'
                        ' int(len(index_name_{0}), c_size_t)').format(dim)
                        for dim in range(1, ndims+1)])
                    if ndims < 7:
                        name_params += ', &\n'
                    filler_params = ', &\n'.join([(
                        '            index_name_1,'
                        ' int(len(index_name_1), c_size_t)')
                        for dim in range(ndims+1, 8)])

                    dim_list = ', '.join([':'] * ndims)

                    f_override=(
                            'function LIBMUSCLE_$CLASSNAME$_create_grid_{0}_{1}_n( &\n'
                            '        data_array, &\n'
                            '        {2})\n'
                            '\n'
                            '    implicit none\n'
                            '    {6}, dimension({8}), intent(in) :: data_array\n'
                            '{3}'
                            '    type(LIBMUSCLE_$CLASSNAME$) :: LIBMUSCLE_$CLASSNAME$_create_grid_{0}_{1}_n\n'
                            '\n'
                            '    integer (c_intptr_t) :: ret_val\n'
                            '\n'
                            '    ret_val = LIBMUSCLE_$CLASSNAME$_create_grid_{1}_n_( &\n'
                            '            {7}, &\n'
                            '            int(shape(data_array), c_size_t), &\n'
                            '            {0}_LIBMUSCLE_size, &\n'
                            '{4}'
                            '{5} &\n'
                            '        )\n'
                            '\n'
                            '    LIBMUSCLE_$CLASSNAME$_create_grid_{0}_{1}_n%ptr = ret_val\n'
                            'end function LIBMUSCLE_$CLASSNAME$_create_grid_{0}_{1}_n\n'
                            '\n').format(
                                    ndims, typ.tname(), name_args, name_types,
                                    name_params, filler_params,
                                    typ.f_type()[0][0], typ.f_chain_arg(),
                                    dim_list)

                    self.instances.append(NamedConstructor(
                        instance_params, instance_name,
                        f_override=f_override, fc_override=''))
                else:
                    chain_call = lambda tname=typ.tname(), **a: (
                            '{}_{}_create_grid_{}_a_( &\n{})'.format(
                                a['ns_prefix'], a['class_name'], tname,
                                a['fc_args']))

                    self.instances.append(NamedConstructor(
                        instance_params, instance_name, cpp_func_name='grid',
                        fc_chain_call=chain_call, fc_override=''))

    def __copy__(self) -> 'GridConstructor':
        result = GridConstructor(self.with_names)
        result.ns_prefix = self.ns_prefix
        result.public = self.public
        if self.class_name is None:
            result.class_name = None
        else:
            result.set_class_name(self.class_name)
        result.instances = [copy(instance) for instance in self.instances]
        return result


class Elements(MultiMemFun):
    """Creates the elements() function.

    There are a lot of these, just like with the grid constructor, for
    different dimensions and types. So we do some extra work here too
    to reduce the size of the ABI.
    """

    def __init__(self) -> None:
        self.ns_prefix = None       # type: Optional[str]
        self.public = None          # type: Optional[bool]
        self.class_name = None      # type: Optional[str]
        self.types = [Bool(), Int32t(), Int64t(), Float(), Double()]
        self.name = 'elements'
        self.instances = list()     # type: List[Member]

        # Generate ABI
        for typ in self.types:
            # This is not set yet here, but f_type() needs it.
            # The dict is only used by Obj, which we don't have.
            typ.name = 'elements'
            typ.set_ns_prefix({}, 'LIBMUSCLE')
            func_name = 'elements_{}'.format(typ.tname())
            fc_override = (
                    'void LIBMUSCLE_$CLASSNAME$_elements_{0}_(\n'
                    '        std::intptr_t self,\n'
                    '        std::size_t ndims,\n'
                    '        {1} ** elements,\n'
                    '        std::size_t * elements_shape,\n'
                    '        int * elements_format,\n'
                    '        int * err_code, char ** err_msg, std::size_t * err_msg_len\n'
                    ') {{\n'
                    '    $CLASSNAME$ * self_p = reinterpret_cast<$CLASSNAME$ *>(self);\n'
                    '    try {{\n'
                    '        *err_code = 0;\n'
                    '        if (self_p->shape().size() != ndims)\n'
                    '            throw std::runtime_error("Grid does not have a matching number of dimensions.");\n'
                    '        {1} const * result = self_p->elements<{1}>();\n'
                    '        *elements = const_cast<{1} *>(result);\n'
                    '\n'
                    '        for (std::size_t i = 0u; i < ndims; ++i)\n'
                    '            elements_shape[i] = self_p->shape()[i];\n'
                    '\n'
                    '        *elements_format = (self_p->storage_order() == libmuscle::StorageOrder::last_adjacent);\n'
                    '        return;\n'
                    '    }}\n'
                    '    catch (std::runtime_error const & e) {{\n'
                    '        *err_code = 4;\n'
                    '        static std::string msg;\n'
                    '        msg = e.what();\n'
                    '        *err_msg = const_cast<char*>(msg.data());\n'
                    '        *err_msg_len = msg.size();\n'
                    '    }}\n'
                    '}}\n\n'
                    ).format(typ.tname(), typ.fc_cpp_type())

            self.instances.append(
                    MemFun(
                        Array(1, copy(typ), 'elements'), func_name, [Sizet('ndims')], True,
                        f_override='', fc_override=fc_override))

        # Generate API
        for typ in self.types:
            for ndims in range(1, 8):
                func_name = 'elements_{}_{}'.format(ndims, typ.tname())
                dims_list = ', '.join([':']*ndims)
                rev_dims = ', '.join(map(str, reversed(range(1, ndims+1))))
                f_override = (
                        'subroutine LIBMUSCLE_$CLASSNAME$_elements_{0}_{1}( &\n'
                        '        self, &\n'
                        '        elements, &\n'
                        '        err_code, &\n'
                        '        err_msg)\n'
                        '\n'
                        '    implicit none\n'
                        '    type(LIBMUSCLE_$CLASSNAME$), intent(in) :: self\n'
                        '    {2}, dimension({3}), intent(out) :: elements\n'
                        '    integer, optional, intent(out) :: err_code\n'
                        '    character(:), allocatable, optional, intent(out) :: err_msg\n'
                        '\n'
                        '    type (c_ptr) :: ret_val\n'
                        '    integer (c_size_t), dimension({0}) :: ret_val_shape\n'
                        '    integer (c_int) :: ret_val_format\n'
                        '    {4}, pointer, dimension({3}) :: f_ret_ptr\n'
                        '    {4}, pointer, dimension(:) :: f_ret_ptr_linear\n'
                        '    integer (c_int) :: err_code_v\n'
                        '    type (c_ptr) :: err_msg_v\n'
                        '    integer (c_size_t) :: err_msg_len_v\n'
                        '    character (c_char), dimension(:), pointer :: err_msg_f\n'
                        '    character(:), allocatable :: err_msg_p\n'
                        '    integer (c_size_t) :: err_msg_i\n'
                        '\n'
                        '    call LIBMUSCLE_$CLASSNAME$_elements_{1}_( &\n'
                        '        self%ptr, &\n'
                        '        {0}_LIBMUSCLE_size, &\n'
                        '        ret_val, &\n'
                        '        ret_val_shape, &\n'
                        '        ret_val_format, &\n'
                        '        err_code_v, &\n'
                        '        err_msg_v, &\n'
                        '        err_msg_len_v)\n'
                        '\n'
                        '    if (err_code_v .ne. 0) then\n'
                        '        if (present(err_code)) then\n'
                        '            err_code = err_code_v\n'
                        '            if (present(err_msg)) then\n'
                        '                call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))\n'
                        '                allocate (character(err_msg_len_v) :: err_msg)\n'
                        '                do err_msg_i = 1, err_msg_len_v\n'
                        '                    err_msg(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)\n'
                        '                end do\n'
                        '            end if\n'
                        '            return\n'
                        '        else\n'
                        '            call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))\n'
                        '            allocate (character(err_msg_len_v) :: err_msg_p)\n'
                        '            do err_msg_i = 1, err_msg_len_v\n'
                        '                err_msg_p(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)\n'
                        '            end do\n'
                        '            print *, err_msg_p\n'
                        '            stop\n'
                        '        end if\n'
                        '    else\n'
                        '        if (present(err_code)) then\n'
                        '            err_code = 0\n'
                        '        end if\n'
                        '    end if\n'
                        '\n'
                        '    if (ret_val_format .eq. 0) then\n'
                        '        call c_f_pointer(ret_val, f_ret_ptr, ret_val_shape)\n'
                        '        elements = f_ret_ptr\n'
                        '    else\n'
                        '        call c_f_pointer(ret_val, f_ret_ptr_linear, (/product(ret_val_shape)/))\n'
                        '        elements = reshape(f_ret_ptr_linear, ret_val_shape, (/ {4}:: /), (/{5}/))\n'
                        '    end if\n'
                        'end subroutine LIBMUSCLE_$CLASSNAME$_elements_{0}_{1}\n\n'
                        ).format(
                                ndims, typ.tname(), typ.f_ret_type()[1][0][0],
                                dims_list, typ.fi_ret_type()[0][0], rev_dims)

                self.instances.append(
                        MemFun(
                            Array(ndims, copy(typ), 'elements'),
                            func_name, [], True,
                            f_override=f_override, fc_override=''))

    def __copy__(self) -> 'Elements':
        result = Elements()
        result.ns_prefix = self.ns_prefix
        result.public = self.public
        if self.class_name is None:
            result.class_name = None
        else:
            result.set_class_name(self.class_name)
        result.instances = [copy(instance) for instance in self.instances]
        return result


create_grid_overloads = [
        'create_grid_{}_{}_{}'.format(ndims, typ, with_names_tag)
        for ndims in range(1, 8)
        for typ in ['logical', 'int4', 'int8', 'real4', 'real8']
        for with_names_tag in ['n', 'a']]


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
    GridConstructor(False),
    GridConstructor(True),
    OverloadSet('create_grid', create_grid_overloads),
    Destructor(),
    MemFunTmpl(
        [Bool(), String(), Int(), Char(), Int16t(), Int32t(), Int64t(),
            Float(), Double()],
        Bool(), 'is_a', [], False),
    MemFun(Bool(), 'is_a_dict'),
    MemFun(Bool(), 'is_a_list'),
    MemFunTmpl(
        [Bool(), Float(), Double(), Int32t(), Int64t()],
        Bool(), 'is_a_grid_of', [], False),
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
                'std::intptr_t LIBMUSCLE_$CLASSNAME$_get_item_by_key_(\n'
                '        std::intptr_t self,\n'
                '        char * key, std::size_t key_size,\n'
                '        int * err_code, char ** err_msg, std::size_t * err_msg_len\n'
                ') {\n'
                '    $CLASSNAME$ * self_p = reinterpret_cast<$CLASSNAME$ *>(self);\n'
                '    std::string key_s(key, key_size);\n'
                '    try {\n'
                '        *err_code = 0;\n'
                '        $CLASSNAME$ * result = new $CLASSNAME$((*self_p)[key_s]);\n'
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
                '    return 0;\n'
                '}\n\n')
            ),
    MemFun(Obj('DataConstRef', 'value'), 'get_item_by_index', [Sizet('i')], True,
            fc_override=(
                'std::intptr_t LIBMUSCLE_$CLASSNAME$_get_item_by_index_(\n'
                '        std::intptr_t self,\n'
                '        std::size_t i,\n'
                '        int * err_code, char ** err_msg, std::size_t * err_msg_len\n'
                ') {\n'
                '    $CLASSNAME$ * self_p = reinterpret_cast<$CLASSNAME$ *>(self);\n'
                '    try {\n'
                '        *err_code = 0;\n'
                '        $CLASSNAME$ * result = new $CLASSNAME$((*self_p)[i-1u]);\n'
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
                '    return 0;\n'
                '}\n\n')
            ),
    OverloadSet('get_item', [
        'get_item_by_key', 'get_item_by_index'
        ]),
    MemFun(Sizet(), 'num_dims', [], True,
            fc_override=(
                'std::size_t LIBMUSCLE_$CLASSNAME$_num_dims_(\n'
                '        std::intptr_t self,\n'
                '        int * err_code, char ** err_msg, std::size_t * err_msg_len\n'
                ') {\n'
                '    $CLASSNAME$ * self_p = reinterpret_cast<$CLASSNAME$ *>(self);\n'
                '    try {\n'
                '        *err_code = 0;\n'
                '        return self_p->shape().size();\n'
                '    }\n'
                '    catch (std::runtime_error const & e) {\n'
                '        *err_code = 1;\n'
                '        static std::string msg;\n'
                '        msg = e.what();\n'
                '        *err_msg = const_cast<char*>(msg.data());\n'
                '        *err_msg_len = msg.size();\n'
                '    }\n'
                '    return 0;\n'
                '}\n\n')
            ),
    MemFun(VecSizet('shp'), 'shape', [], True),
    Elements(),
    OverloadSet('elements', [
        'elements_1_logical', 'elements_1_real4', 'elements_1_real8',
        'elements_1_int4', 'elements_1_int8',
        'elements_2_logical', 'elements_2_real4', 'elements_2_real8',
        'elements_2_int4', 'elements_2_int8',
        'elements_3_logical', 'elements_3_real4', 'elements_3_real8',
        'elements_3_int4', 'elements_3_int8',
        'elements_4_logical', 'elements_4_real4', 'elements_4_real8',
        'elements_4_int4', 'elements_4_int8',
        'elements_5_logical', 'elements_5_real4', 'elements_5_real8',
        'elements_5_int4', 'elements_5_int8',
        'elements_6_logical', 'elements_6_real4', 'elements_6_real8',
        'elements_6_int4', 'elements_6_int8',
        'elements_7_logical', 'elements_7_real4', 'elements_7_real8',
        'elements_7_int4', 'elements_7_int8',
        ]),
    MemFun(Bool(), 'has_indexes', [], True),
    MemFun(String(), 'index', [Sizet('i')], True,
            cpp_chain_call=lambda **kwargs: 'self_p->indexes().at(i - 1)'),
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
                '    return 0;\n'
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
                '    return 0;\n'
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
                '    return 0;\n'
                '}\n\n')
            ),
    ])


message_desc = Class('Message', None, [
    Constructor([Double('timestamp')], 'create_t'),
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
        'create_t', 'create_td', 'create_tnd', 'create_tds', 'create_tnds']),
    Destructor(),
    MemFun(Double(), 'timestamp'),
    MemFun(Void(), 'set_timestamp', [Double('timestamp')]),
    MemFun(Bool(), 'has_next_timestamp'),
    MemFun(Double(), 'next_timestamp'),
    MemFun(Void(), 'set_next_timestamp', [Double('next_timestamp')]),
    MemFun(Void(), 'unset_next_timestamp'),
    MemFun(Obj('DataConstRef', 'data'), 'get_data',
        cpp_chain_call=lambda **kwargs: 'self_p->data()'),
    MemFun(Void(), 'set_data_d', [Obj('Data', 'data')],
        cpp_chain_call=lambda **kwargs: 'self_p->set_data({})'.format(
            kwargs['cpp_args'])),
    MemFun(Void(), 'set_data_dcr', [Obj('DataConstRef', 'data')],
        cpp_chain_call=lambda **kwargs: 'self_p->set_data({})'.format(
            kwargs['cpp_args'])),
    OverloadSet('set_data', ['set_data_d', 'set_data_dcr']),
    MemFun(Bool(), 'has_settings'),
    MemFun(Obj('Settings'), 'get_settings',
        cpp_chain_call=lambda **kwargs: 'self_p->settings()'),
    MemFun(Void(), 'set_settings', [Obj('Settings', 'settings')]),
    MemFun(Void(), 'unset_settings'),
    ])


portsdescription_desc = Class('PortsDescription', None, [
    Constructor(),
    Destructor(),
    MemFun(Void(), 'add', [EnumVal('Operator', 'op'), String('port')],
        cpp_chain_call=lambda **kwargs: '(*self_p)[op_e].push_back(port_s)'),
    MemFun(Sizet(), 'num_ports', [EnumVal('Operator', 'op')],
        fc_override=(
            'std::size_t LIBMUSCLE_PortsDescription_num_ports_(std::intptr_t self, int op) {\n'
            '    PortsDescription * self_p = reinterpret_cast<PortsDescription *>(self);\n'
            '    Operator op_e = static_cast<Operator>(op);\n'
            '    std::size_t result = 0u;\n'
            '    if (self_p->count(op_e))\n'
            '        result = (*self_p)[op_e].size();\n'
            '    return result;\n'
            '}\n\n')
        ),
    MemFun(String(), 'get', [EnumVal('Operator', 'op'), Sizet('i')], True,
        cpp_chain_call=lambda **kwargs: '(*self_p)[op_e].at(i - 1)'),
    ])


instance_constructors = [
    Constructor([Obj('CmdLineArgs', 'cla')], 'create_autoports', fc_override=(
        'std::intptr_t LIBMUSCLE_Instance_create_autoports_(std::intptr_t cla) {\n'
        '    CmdLineArgs * cla_p = reinterpret_cast<CmdLineArgs *>(cla);\n'
        '    Instance * result = new Instance(cla_p->argc(), cla_p->argv());\n'
        '    return reinterpret_cast<std::intptr_t>(result);\n'
        '}\n\n'),
        f_override=(
            'type(LIBMUSCLE_Instance) function LIBMUSCLE_Instance_create_autoports()\n'
            '    implicit none\n'
            '\n'
            '    integer :: num_args, i, arg_len\n'
            '    integer (c_intptr_t) :: cla\n'
            '    character (kind=c_char, len=:), allocatable :: cur_arg\n'
            '\n'
            '    num_args = command_argument_count()\n'
            '    cla = LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create_(num_args + 1)\n'
            '    do i = 0, num_args\n'
            '        call get_command_argument(i, length=arg_len)\n'
            '        allocate (character(arg_len+1) :: cur_arg)\n'
            '        call get_command_argument(i, value=cur_arg)\n'
            '        cur_arg(arg_len+1:arg_len+1) = c_null_char\n'
            '        call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_set_arg_( &\n'
            '               cla, i, cur_arg, int(len(cur_arg), c_size_t))\n'
            '        deallocate(cur_arg)\n'
            '    end do\n'
            '    LIBMUSCLE_Instance_create_autoports%ptr = &\n'
            '        LIBMUSCLE_Instance_create_autoports_(cla)\n'
            '    call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_free_(cla)\n'
            'end function LIBMUSCLE_Instance_create_autoports\n'
            '\n')),
    Constructor(
        [Obj('CmdLineArgs', 'cla'), Obj('PortsDescription', 'ports')],
        'create_with_ports',
        fc_override=(
            'std::intptr_t LIBMUSCLE_Instance_create_with_ports_(\n'
            '        std::intptr_t cla,\n'
            '        std::intptr_t ports\n'
            ') {\n'
            '    CmdLineArgs * cla_p = reinterpret_cast<CmdLineArgs *>(cla);\n'
            '    PortsDescription * ports_p = reinterpret_cast<PortsDescription *>(\n'
            '            ports);\n'
            '    Instance * result = new Instance(\n'
            '        cla_p->argc(), cla_p->argv(), *ports_p);\n'
            '    return reinterpret_cast<std::intptr_t>(result);\n'
            '}\n\n'),
        f_override=(
            'type(LIBMUSCLE_Instance) function LIBMUSCLE_Instance_create_with_ports(ports)\n'
            '    implicit none\n'
            '\n'
            '    type(LIBMUSCLE_PortsDescription) :: ports\n'
            '    integer :: num_args, i, arg_len\n'
            '    integer (c_intptr_t) :: cla\n'
            '    character (kind=c_char, len=:), allocatable :: cur_arg\n'
            '\n'
            '    num_args = command_argument_count()\n'
            '    cla = LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create_(num_args + 1)\n'
            '    do i = 0, num_args\n'
            '        call get_command_argument(i, length=arg_len)\n'
            '        allocate (character(arg_len+1) :: cur_arg)\n'
            '        call get_command_argument(i, value=cur_arg)\n'
            '        cur_arg(arg_len+1:arg_len+1) = c_null_char\n'
            '        call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_set_arg_( &\n'
            '               cla, i, cur_arg, int(len(cur_arg), c_size_t))\n'
            '        deallocate(cur_arg)\n'
            '    end do\n'
            '    LIBMUSCLE_Instance_create_with_ports%ptr = LIBMUSCLE_Instance_create_with_ports_(cla, ports%ptr)\n'
            '    call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_free_(cla)\n'
            'end function LIBMUSCLE_Instance_create_with_ports\n'
            '\n')),
    OverloadSet('create', ['create_autoports', 'create_with_ports']),
    ]


instance_mpi_constructors = [
    Constructor(
        [Obj('CmdLineArgs', 'cla'), Int('communicator'), Int('root')],
        'create_autoports_cr',
        fc_override=(
            'std::intptr_t LIBMUSCLE_Instance_create_autoports_cr_(\n'
            '        std::intptr_t cla,\n'
            '        int communicator,\n'
            '        int root\n'
            ') {\n'
            '    CmdLineArgs * cla_p = reinterpret_cast<CmdLineArgs *>(cla);\n'
            '    MPI_Comm communicator_m = MPI_Comm_f2c(communicator);\n'
            '    Instance * result = new Instance(cla_p->argc(), cla_p->argv(), communicator_m, root);\n'
            '    return reinterpret_cast<std::intptr_t>(result);\n'
            '}\n\n'),
        f_override=(
            'type(LIBMUSCLE_Instance) function LIBMUSCLE_Instance_create_autoports_cr( &\n'
            '       communicator, root)\n'
            '    implicit none\n'
            '    integer :: communicator, root\n'
            '\n'
            '    integer :: num_args, i, arg_len\n'
            '    integer (c_intptr_t) :: cla\n'
            '    character (kind=c_char, len=:), allocatable :: cur_arg\n'
            '\n'
            '    num_args = command_argument_count()\n'
            '    cla = LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create_(num_args + 1)\n'
            '    do i = 0, num_args\n'
            '        call get_command_argument(i, length=arg_len)\n'
            '        allocate (character(arg_len+1) :: cur_arg)\n'
            '        call get_command_argument(i, value=cur_arg)\n'
            '        cur_arg(arg_len+1:arg_len+1) = c_null_char\n'
            '        call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_set_arg_( &\n'
            '               cla, i, cur_arg, int(len(cur_arg), c_size_t))\n'
            '        deallocate(cur_arg)\n'
            '    end do\n'
            '    LIBMUSCLE_Instance_create_autoports_cr%ptr = &\n'
            '        LIBMUSCLE_Instance_create_autoports_cr_(cla, communicator, root)\n'
            '    call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_free_(cla)\n'
            'end function LIBMUSCLE_Instance_create_autoports_cr\n'
            '\n')),
    Constructor(
        [Obj('CmdLineArgs', 'cla'), Int('communicator')],
        'create_autoports_c',
        fc_override='',
        f_override=(
            'type(LIBMUSCLE_Instance) function LIBMUSCLE_Instance_create_autoports_c( &\n'
            '       communicator)\n'
            '    implicit none\n'
            '    integer :: communicator\n'
            '\n'
            '    integer :: num_args, i, arg_len\n'
            '    integer (c_intptr_t) :: cla\n'
            '    character (kind=c_char, len=:), allocatable :: cur_arg\n'
            '\n'
            '    num_args = command_argument_count()\n'
            '    cla = LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create_(num_args + 1)\n'
            '    do i = 0, num_args\n'
            '        call get_command_argument(i, length=arg_len)\n'
            '        allocate (character(arg_len+1) :: cur_arg)\n'
            '        call get_command_argument(i, value=cur_arg)\n'
            '        cur_arg(arg_len+1:arg_len+1) = c_null_char\n'
            '        call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_set_arg_( &\n'
            '               cla, i, cur_arg, int(len(cur_arg), c_size_t))\n'
            '        deallocate(cur_arg)\n'
            '    end do\n'
            '    LIBMUSCLE_Instance_create_autoports_c%ptr = &\n'
            '        LIBMUSCLE_Instance_create_autoports_cr_(cla, communicator, 0)\n'
            '    call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_free_(cla)\n'
            'end function LIBMUSCLE_Instance_create_autoports_c\n'
            '\n')),
    Constructor(
        [Obj('CmdLineArgs', 'cla')],
        'create_autoports',
        fc_override='',
        f_override=(
            'type(LIBMUSCLE_Instance) function LIBMUSCLE_Instance_create_autoports()\n'
            '    implicit none\n'
            '\n'
            '    integer :: num_args, i, arg_len\n'
            '    integer (c_intptr_t) :: cla\n'
            '    character (kind=c_char, len=:), allocatable :: cur_arg\n'
            '\n'
            '    num_args = command_argument_count()\n'
            '    cla = LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create_(num_args + 1)\n'
            '    do i = 0, num_args\n'
            '        call get_command_argument(i, length=arg_len)\n'
            '        allocate (character(arg_len+1) :: cur_arg)\n'
            '        call get_command_argument(i, value=cur_arg)\n'
            '        cur_arg(arg_len+1:arg_len+1) = c_null_char\n'
            '        call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_set_arg_( &\n'
            '               cla, i, cur_arg, int(len(cur_arg), c_size_t))\n'
            '        deallocate(cur_arg)\n'
            '    end do\n'
            '    LIBMUSCLE_Instance_create_autoports%ptr = &\n'
            '        LIBMUSCLE_Instance_create_autoports_cr_(cla, MPI_COMM_WORLD, 0)\n'
            '    call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_free_(cla)\n'
            'end function LIBMUSCLE_Instance_create_autoports\n'
            '\n')),
    Constructor(
        [
            Obj('CmdLineArgs', 'cla'), Obj('PortsDescription', 'ports'),
            Int('communicator'), Int('root')],
        'create_with_ports_cr',
        fc_override=(
            'std::intptr_t LIBMUSCLE_Instance_create_with_ports_cr_(\n'
            '        std::intptr_t cla,\n'
            '        std::intptr_t ports,\n'
            '        int communicator, int root\n'
            ') {\n'
            '    CmdLineArgs * cla_p = reinterpret_cast<CmdLineArgs *>(cla);\n'
            '    PortsDescription * ports_p = reinterpret_cast<PortsDescription *>(\n'
            '            ports);\n'
            '    MPI_Comm communicator_m = MPI_Comm_f2c(communicator);\n'
            '    Instance * result = new Instance(\n'
            '        cla_p->argc(), cla_p->argv(), *ports_p, communicator_m, root);\n'
            '    return reinterpret_cast<std::intptr_t>(result);\n'
            '}\n\n'),
        f_override=(
            'type(LIBMUSCLE_Instance) function LIBMUSCLE_Instance_create_with_ports_cr( &\n'
            '        ports, communicator, root)\n'
            '    implicit none\n'
            '\n'
            '    type(LIBMUSCLE_PortsDescription) :: ports\n'
            '    integer :: communicator, root\n'
            '    integer :: num_args, i, arg_len\n'
            '    integer (c_intptr_t) :: cla\n'
            '    character (kind=c_char, len=:), allocatable :: cur_arg\n'
            '\n'
            '    num_args = command_argument_count()\n'
            '    cla = LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create_(num_args + 1)\n'
            '    do i = 0, num_args\n'
            '        call get_command_argument(i, length=arg_len)\n'
            '        allocate (character(arg_len+1) :: cur_arg)\n'
            '        call get_command_argument(i, value=cur_arg)\n'
            '        cur_arg(arg_len+1:arg_len+1) = c_null_char\n'
            '        call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_set_arg_( &\n'
            '               cla, i, cur_arg, int(len(cur_arg), c_size_t))\n'
            '        deallocate(cur_arg)\n'
            '    end do\n'
            '    LIBMUSCLE_Instance_create_with_ports_cr%ptr = &\n'
            '        LIBMUSCLE_Instance_create_with_ports_cr_( &\n'
            '            cla, ports%ptr, communicator, root)\n'
            '    call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_free_(cla)\n'
            'end function LIBMUSCLE_Instance_create_with_ports_cr\n'
            '\n')),
    Constructor(
        [
            Obj('CmdLineArgs', 'cla'), Obj('PortsDescription', 'ports'),
            Int('communicator')],
        'create_with_ports_c',
        fc_override='',
        f_override=(
            'type(LIBMUSCLE_Instance) function LIBMUSCLE_Instance_create_with_ports_c( &\n'
            '        ports, communicator)\n'
            '    implicit none\n'
            '\n'
            '    type(LIBMUSCLE_PortsDescription) :: ports\n'
            '    integer :: communicator\n'
            '    integer :: num_args, i, arg_len\n'
            '    integer (c_intptr_t) :: cla\n'
            '    character (kind=c_char, len=:), allocatable :: cur_arg\n'
            '\n'
            '    num_args = command_argument_count()\n'
            '    cla = LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create_(num_args + 1)\n'
            '    do i = 0, num_args\n'
            '        call get_command_argument(i, length=arg_len)\n'
            '        allocate (character(arg_len+1) :: cur_arg)\n'
            '        call get_command_argument(i, value=cur_arg)\n'
            '        cur_arg(arg_len+1:arg_len+1) = c_null_char\n'
            '        call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_set_arg_( &\n'
            '               cla, i, cur_arg, int(len(cur_arg), c_size_t))\n'
            '        deallocate(cur_arg)\n'
            '    end do\n'
            '    LIBMUSCLE_Instance_create_with_ports_c%ptr = &\n'
            '        LIBMUSCLE_Instance_create_with_ports_cr_( &\n'
            '            cla, ports%ptr, communicator, 0)\n'
            '    call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_free_(cla)\n'
            'end function LIBMUSCLE_Instance_create_with_ports_c\n'
            '\n')),
    Constructor(
        [
            Obj('CmdLineArgs', 'cla'), Obj('PortsDescription', 'ports')],
        'create_with_ports',
        fc_override='',
        f_override=(
            'type(LIBMUSCLE_Instance) function LIBMUSCLE_Instance_create_with_ports( &\n'
            '        ports)\n'
            '    implicit none\n'
            '\n'
            '    type(LIBMUSCLE_PortsDescription) :: ports\n'
            '    integer :: num_args, i, arg_len\n'
            '    integer (c_intptr_t) :: cla\n'
            '    character (kind=c_char, len=:), allocatable :: cur_arg\n'
            '\n'
            '    num_args = command_argument_count()\n'
            '    cla = LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create_(num_args + 1)\n'
            '    do i = 0, num_args\n'
            '        call get_command_argument(i, length=arg_len)\n'
            '        allocate (character(arg_len+1) :: cur_arg)\n'
            '        call get_command_argument(i, value=cur_arg)\n'
            '        cur_arg(arg_len+1:arg_len+1) = c_null_char\n'
            '        call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_set_arg_( &\n'
            '               cla, i, cur_arg, int(len(cur_arg), c_size_t))\n'
            '        deallocate(cur_arg)\n'
            '    end do\n'
            '    LIBMUSCLE_Instance_create_with_ports%ptr = &\n'
            '        LIBMUSCLE_Instance_create_with_ports_cr_( &\n'
            '            cla, ports%ptr, MPI_COMM_WORLD, 0)\n'
            '    call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_free_(cla)\n'
            'end function LIBMUSCLE_Instance_create_with_ports\n'
            '\n')),
    OverloadSet('create', [
        'create_autoports_cr', 'create_autoports_c', 'create_autoports',
        'create_with_ports_cr', 'create_with_ports_c', 'create_with_ports']),
    ]


instance_members = [
    Destructor(),
    MemFun(
            Bool(), 'reuse_instance_default',
            cpp_chain_call=lambda **kwargs: 'self_p->reuse_instance()'),
    MemFun(
            Bool(), 'reuse_instance_apply', [Bool('apply_overlay')],
            cpp_chain_call=lambda **kwargs: (
                'self_p->reuse_instance({})'.format(kwargs['cpp_args']))
            ),
    OverloadSet(
            'reuse_instance',
            ['reuse_instance_default', 'reuse_instance_apply']),
    MemFun(Void(), 'error_shutdown', [String('message')]),
    MemFunTmpl(
        [String(), Int64t(), Double(), Bool(), VecDbl('value'),
            Vec2Dbl('value')],
        Bool(), 'is_setting_a', [String('name')], True,
            cpp_chain_call=lambda **kwargs: 'self_p->get_setting({}).is_a<{}>()'.format(
                    kwargs['cpp_args'], kwargs['tpl_type'])
        ),

    MemFunTmpl(
        [String(), Int64t(), Double(), Bool(), VecDbl('value'),
            Vec2Dbl('value')],
        T(), 'get_setting_as', [String('name')], True),
    MemFun(Obj('PortsDescription'), 'list_ports'),
    MemFun(Bool(), 'is_connected', [String('port')]),
    MemFun(Bool(), 'is_vector_port', [String('port')]),
    MemFun(Bool(), 'is_resizable', [String('port')]),
    MemFun(Int(), 'get_port_length', [String('port')]),
    MemFun(Void(), 'set_port_length', [String('port'), Int('length')]),

    MemFun(Void(), 'send_pm',
           [String('port_name'), Obj('Message', 'message')],
           cpp_chain_call=lambda **kwargs: 'self_p->send({})'.format(
               kwargs['cpp_args'])),
    MemFun(Void(), 'send_pms',
           [String('port_name'), Obj('Message', 'message'), Int('slot')],
           cpp_chain_call=lambda **kwargs: 'self_p->send({})'.format(
               kwargs['cpp_args'])),
    OverloadSet('send', ['send_pm', 'send_pms']),

    MemFun(Obj('Message'), 'receive_p', [String('port_name')], True,
           cpp_chain_call=lambda **kwargs: 'self_p->receive({})'.format(
               kwargs['cpp_args'])),
    MemFun(Obj('Message'), 'receive_pd',
           [String('port_name'), Obj('Message', 'default_msg')], True,
           cpp_chain_call=lambda **kwargs: 'self_p->receive({})'.format(
               kwargs['cpp_args'])),
    OverloadSet('receive', ['receive_p', 'receive_pd']),

    MemFun(Obj('Message'), 'receive_ps', [String('port_name'), Int('slot')],
           True,
           cpp_chain_call=lambda **kwargs: 'self_p->receive({})'.format(
               kwargs['cpp_args'])),
    MemFun(Obj('Message'), 'receive_psd',
           [String('port_name'), Int('slot'), Obj('Message', 'default_message')],
           True,
           cpp_chain_call=lambda **kwargs: 'self_p->receive({})'.format(
               kwargs['cpp_args'])),
    OverloadSet('receive_on_slot', ['receive_ps', 'receive_psd']),

    MemFun(Obj('Message'), 'receive_with_settings_p',
           [String('port_name')], True,
           cpp_chain_call=lambda **kwargs: (
               'self_p->receive_with_settings({})'.format(
               kwargs['cpp_args']))),
    MemFun(Obj('Message'), 'receive_with_settings_pd',
           [String('port_name'), Obj('Message', 'default_msg')], True,
           cpp_chain_call=lambda **kwargs: (
               'self_p->receive_with_settings({})'.format(
               kwargs['cpp_args']))),
    OverloadSet('receive_with_settings',
                ['receive_with_settings_p', 'receive_with_settings_pd']),

    MemFun(Obj('Message'), 'receive_with_settings_ps',
           [String('port_name'), Int('slot')], True,
           cpp_chain_call=lambda **kwargs: (
               'self_p->receive_with_settings({})'.format(
               kwargs['cpp_args']))),
    MemFun(Obj('Message'), 'receive_with_settings_psd',
           [String('port_name'), Int('slot'), Obj('Message', 'default_msg')],
           True,
           cpp_chain_call=lambda **kwargs: (
               'self_p->receive_with_settings({})'.format(
               kwargs['cpp_args']))),
    OverloadSet('receive_with_settings_on_slot',
                ['receive_with_settings_ps', 'receive_with_settings_psd'])
    ]


instance_desc = Class(
        'Instance', None, instance_constructors + [
            copy(mem) for mem in instance_members])


instance_mpi_desc = Class(
        'Instance', None, instance_mpi_constructors + [
            copy(mem) for mem in instance_members])


cmdlineargs_desc = Class('CmdLineArgs', None, [
        Constructor([Int('count')]),
        Destructor(),
        MemFun(Void(), 'set_arg', [Int('i'), String('arg')]),
        ])


ymmsl_forward_enums = [Enum('Operator', [])]


ymmsl_forward_classes = [Class('Settings', None, [])]


libmuscle_api_description = API(
        'libmuscle',
        [
            'libmuscle/libmuscle.hpp',
            'libmuscle/bindings/cmdlineargs.hpp',
            'ymmsl/ymmsl.hpp',
            'stdexcept',
            'typeinfo'],
        [
            'ymmsl'],
        [
            Namespace('libmuscle', True, 'LIBMUSCLE', [], [
                dataconstref_desc, data_desc, portsdescription_desc,
                message_desc, instance_desc]),
            Namespace('libmuscle::impl::bindings', False,
                      'LIBMUSCLE_IMPL_BINDINGS', [], [cmdlineargs_desc]),
            Namespace('ymmsl', None, 'YMMSL',
                      ymmsl_forward_enums, ymmsl_forward_classes)
        ])


libmuscle_mpi_api_description = API(
        'libmuscle_mpi',
        #define LIBMUSCLE_ENABLE_MPI
        [
            'libmuscle/libmuscle.hpp',
            'libmuscle/bindings/cmdlineargs.hpp',
            'ymmsl/ymmsl.hpp',
            'stdexcept',
            'typeinfo'],
        [
            'mpi', 'ymmsl'],
        [
            Namespace('libmuscle', True, 'LIBMUSCLE', [], [
                dataconstref_desc, data_desc, portsdescription_desc,
                message_desc, instance_mpi_desc]),
            Namespace('libmuscle::impl::bindings', False,
                      'LIBMUSCLE_IMPL_BINDINGS', [], [cmdlineargs_desc]),
            Namespace('ymmsl', None, 'YMMSL',
                      ymmsl_forward_enums, ymmsl_forward_classes)
        ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MUSCLE API Generator')
    parser.add_argument('--fortran-c-wrappers', action='store_true')
    parser.add_argument('--fortran-module', action='store_true')
    parser.add_argument('--fortran-exports', nargs=2)
    parser.add_argument('--fortran-mpi-c-wrappers', action='store_true')
    parser.add_argument('--fortran-mpi-module', action='store_true')
    parser.add_argument('--fortran-mpi-exports', nargs=2)

    args = parser.parse_args()
    if args.fortran_c_wrappers:
        print(libmuscle_api_description.fortran_c_wrapper())
    elif args.fortran_module:
        print(libmuscle_api_description.fortran_module())
    elif args.fortran_exports:
        exports = libmuscle_api_description.fortran_exports()
        exports_txt = indent('\n'.join(exports), 8*' ') + '\n'

        in_name = args.fortran_exports[0]
        out_name = args.fortran_exports[1]
        with open(in_name, 'r') as in_file:
            with open(out_name, 'w') as out_file:
                for line in in_file:
                    if 'FORTRAN ABI' in line:
                        out_file.write(exports_txt)
                    else:
                        out_file.write(line)
    elif args.fortran_mpi_c_wrappers:
        print(libmuscle_mpi_api_description.fortran_c_wrapper())
    elif args.fortran_mpi_module:
        print(libmuscle_mpi_api_description.fortran_module())
    elif args.fortran_mpi_exports:
        exports = libmuscle_mpi_api_description.fortran_exports()
        exports_txt = indent('\n'.join(exports), 8*' ') + '\n'

        in_name = args.fortran_mpi_exports[0]
        out_name = args.fortran_mpi_exports[1]
        with open(in_name, 'r') as in_file:
            with open(out_name, 'w') as out_file:
                for line in in_file:
                    if 'FORTRAN ABI' in line:
                        out_file.write(exports_txt)
                    else:
                        out_file.write(line)
