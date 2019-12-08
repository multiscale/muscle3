#!/usr/bin/env python3

from copy import copy
import textwrap
from typing import Dict, List, Optional, Tuple, Union


error_codes = {
        'runtime_error': 1,
        'domain_error': 2,
        'out_of_range': 3,
        'logic_error': 4
        }


def banner(comment_mark: str) -> str:
    """Generate a warning banner.
    """
    result = ('{} This is generated code. If it\'s broken, then you'
              ' should\n').format(comment_mark)
    result += ('{} fix the generation script, not this file.\n'
               ).format(comment_mark)
    result += '\n\n'
    return result


class Par:
    def __init__(self, name: str = 'ret_val') -> None:
        """Create a parameter description.

        Args:
            name: Name of the parameter.
        """
        self.name = name

    def set_ns_prefix(self, ns_for_name: Dict[str, str]) -> None:
        """Sets the namespace prefix correctly for all members.

        Args:
            ns_for_name: A map from type names to namespace names.
        """
        pass

    def fc_convert_input(self) -> str:
        return ''

    def f_aux_variables(self) -> List[Tuple[str, str]]:
        return list()

    def f_chain_arg(self) -> str:
        return self.name

    def f_call_c(self, result_name: str, call: str) -> str:
        return '    {} = {}\n'.format(result_name, call)

    def f_return_result(self, return_name: str, result_name: str) -> str:
        return '    {} = {}\n'.format(return_name, result_name)

    def _regular_type(self,
                      short_type: Union[str, List[Union[str, Tuple[str, str]]]]
                      ) -> List[Tuple[str, str]]:
        """Converts brief type description to more regular format.

        This is a helper function for derived classes. Output is a list
        of tuples (type, name_prefix).

        Input is either

        - a string with a type, or
        - a list containing items that are either
            - a string with a type, or
            - a (type, name_prefix) tuple.

        The name_prefix defaults to an empty string where not given.
        """
        if isinstance(short_type, str):
            return [(short_type, '')]
        elif isinstance(short_type, list):
            result = list() # type: List[Tuple[str, str]]
            for st in short_type:
                if isinstance(st, str):
                    result.append((st, ''))
                else:
                    result.append(st)
            return result
        raise ValueError('Invalid short type {}'.format(short_type))


class Void(Par):
    def tname(self) -> str:
        return 'void'

    def fc_cpp_type(self) -> str:
        return 'void'

    def fc_ret_type(self) -> str:
        return self._regular_type('void')

    def fi_ret_type(self) -> str:
        return ''

    def f_ret_type(self) -> str:
        return False, ''

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return cpp_chain_call

    def fc_return(self) -> str:
        return 'return;\n'

    def f_call_c(self, result_name: str, call: str) -> str:
        return '    call {}\n'.format(call)

    def f_return_result(self, result_name: str, call: str) -> str:
        return ''


class String(Par):
    """Represents a string-typed parameter.
    """
    def tname(self) -> str:
        return 'string'

    def fc_cpp_type(self) -> str:
        return 'std::string'

    def f_type(self) -> str:
        return self._regular_type('character (len=*)')

    def f_ret_type(self) -> str:
        return True, self._regular_type('character(:), allocatable')

    def f_aux_variables(self) -> List[Tuple[str, str]]:
        return [('character (c_char), dimension(:), pointer', 'f_ret_ptr'),
                ('integer', 'i')]

    def f_chain_arg(self) -> str:
        return '{}, int(len({}), c_size_t)'.format(self.name, self.name)

    def f_call_c(self, result_name: str, call: str) -> str:
        return '    call {}\n\n'.format(call)

    def f_return_result(self, return_name: str, result_name: str) -> str:
        return ('    call c_f_pointer(ret_val, f_ret_ptr, (/ret_val_size/))\n'
                '    allocate (character(ret_val_size) :: {0})\n'
                '    do i = 1, ret_val_size\n'
                '        {0}(i:i) = f_ret_ptr(i)\n'
                '    end do\n').format(return_name)

    def fi_type(self) -> str:
        return self._regular_type(
                ['character',
                 ('integer (c_size_t), value', '_size')])

    def fi_ret_type(self) -> str:
        return self._regular_type(
                ['type (c_ptr)',
                 ('integer (c_size_t)', '_size')])

    def fc_type(self) -> str:
        return self._regular_type(['char *', ('std::size_t', '_size')])

    def fc_ret_type(self) -> str:
        return self._regular_type(['char **', ('std::size_t *', '_size')])

    def fc_convert_input(self) -> str:
        return '    std::string {}_s({}, {}_size);\n'.format(
                self.name, self.name, self.name)

    def fc_cpp_arg(self) -> str:
        return self.name + '_s'

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'static std::string result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return ('    *{0} = const_cast<char*>(result.c_str());\n'
                '    *{0}_size = result.size();\n'
                '    return;\n').format(self.name)


class VecDbl(Par):
    """Represents a vector of double parameter.
    """
    def tname(self) -> str:
        return 'vecdbl'

    def fc_cpp_type(self) -> str:
        return 'std::vector<double>'

    def f_type(self) -> str:
        return self._regular_type(
                'real (selected_real_kind(15)), dimension(:)')

    def f_ret_type(self) -> str:
        return False, self._regular_type(
                [('real (selected_real_kind(15)), dimension(:)', self.name)])

    def f_aux_variables(self) -> List[Tuple[str, str]]:
        return [('real (selected_real_kind(15)), pointer, dimension(:)',
                 'f_ret_ptr')]

    def f_chain_arg(self) -> str:
        return '{}, int(size({}), c_size_t)'.format(self.name, self.name)

    def f_call_c(self, result_name: str, call: str) -> str:
        return '    call {}\n\n'.format(call)

    def f_return_result(self, return_name: str, result_name: str) -> str:
        return ('    call c_f_pointer(ret_val, f_ret_ptr, (/ret_val_size/))\n'
                '    {} = f_ret_ptr\n').format(return_name)

    def fi_type(self) -> str:
        return self._regular_type(
                ['real (selected_real_kind(15)), dimension(*)',
                 ('integer (c_size_t), value', '_size')])

    def fi_ret_type(self) -> str:
        return self._regular_type(
                ['type (c_ptr)',
                 ('integer (c_size_t)', '_size')])

    def fc_type(self) -> str:
        return self._regular_type(['double *', ('std::size_t', '_size')])

    def fc_ret_type(self) -> str:
        return self._regular_type(['double **', ('std::size_t *', '_size')])

    def fc_convert_input(self) -> str:
        return '    std::vector<double> {}_v({}, {} + {}_size);\n'.format(
                self.name, self.name, self.name, self.name)

    def fc_cpp_arg(self) -> str:
        return self.name + '_v'

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'static std::vector<double> result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return ('    *{0} = result.data();\n'
                '    *{0}_size = result.size();\n'
                '    return;\n').format(self.name)


class Vec2Dbl(Par):
    """Represents a vector of vector of double parameter.
    """
    def tname(self) -> str:
        return 'vec2dbl'

    def fc_cpp_type(self) -> str:
        return 'std::vector<std::vector<double>>'

    def f_type(self) -> str:
        return self._regular_type(
                'real (selected_real_kind(15)), dimension(:,:)')

    def f_ret_type(self) -> str:
        return False, self._regular_type(
                [('real (selected_real_kind(15)), dimension(:,:)', self.name)])

    def f_aux_variables(self) -> List[Tuple[str, str]]:
        return [('real (selected_real_kind(15)), pointer, dimension(:,:)',
                 'f_ret_ptr')]

    def f_chain_arg(self) -> str:
        return '{}, int(shape({}), c_size_t)'.format(self.name, self.name)

    def f_call_c(self, result_name: str, call: str) -> str:
        return '    call {}\n\n'.format(call)

    def f_return_result(self, return_name: str, result_name: str) -> str:
        return ('    call c_f_pointer(ret_val, f_ret_ptr, ret_val_shape)\n'
                '    {} = f_ret_ptr\n').format(return_name)

    def fi_type(self) -> str:
        return self._regular_type(
                ['real (selected_real_kind(15)), dimension(*)',
                 ('integer (c_size_t), dimension(2)', '_shape')])

    def fi_ret_type(self) -> str:
        return self._regular_type(
                ['type (c_ptr)',
                 ('integer (c_size_t), dimension(2)', '_shape')])

    def fc_type(self) -> str:
        return self._regular_type(['double *', ('std::size_t *', '_shape')])

    def fc_ret_type(self) -> str:
        return self._regular_type(['double **', ('std::size_t *', '_shape')])

    def fc_convert_input(self) -> str:
        result = (
                'std::vector<std::vector<double>> {0}_v(\n'
                '        {0}_shape[0], std::vector<double>({0}_shape[1]));\n'
                'for (std::size_t i = 0; i < {0}_shape[0]; ++i)\n'
                '    for (std::size_t j = 0; j < {0}_shape[1]; ++j)\n'
                '        {0}_v[i][j] = {0}[j * {0}_shape[0] + i];\n'
                )

        return textwrap.indent(result.format(self.name), '    ')

    def fc_cpp_arg(self) -> str:
        return self.name + '_v'

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'std::vector<std::vector<double>> result = {}'.format(
                cpp_chain_call)

    def fc_return(self) -> str:
        result = (
                'std::size_t max_len = 0u;\n'
                'for (auto const & v : result)\n'
                '    max_len = std::max(max_len, v.size());\n'
                '\n'
                'static std::vector<double> ret(result.size() * max_len);\n'
                'for (std::size_t i = 0; i < result.size(); ++i)\n'
                '    for (std::size_t j = 0; j < result[i].size(); ++j)\n'
                '        ret[j * result.size() + i] = result[i][j];\n'
                '\n'
                '*{0} = ret.data();\n'
                '{0}_shape[0] = result.size();\n'
                '{0}_shape[1] = max_len;\n'
                'return;\n'
                )

        return textwrap.indent(result.format(self.name), '    ')


class Bytes(Par):
    """Represents a vector of bytes.
    """
    def tname(self) -> str:
        return 'bytes'

    def fc_cpp_type(self) -> str:
        return 'std::vector<char>'

    def f_type(self) -> str:
        return self._regular_type(
                'character(len=1), dimension(:)')

    def f_ret_type(self) -> str:
        return False, self._regular_type(
                [('character(len=1), dimension(:)', self.name)])

    def f_aux_variables(self) -> List[Tuple[str, str]]:
        return [('character(len=1), pointer, dimension(:)',
                 'f_ret_ptr')]

    def f_chain_arg(self) -> str:
        return '{}, int(size({}), c_size_t)'.format(self.name, self.name)

    def f_call_c(self, result_name: str, call: str) -> str:
        return '    call {}\n\n'.format(call)

    def f_return_result(self, return_name: str, result_name: str) -> str:
        return ('    call c_f_pointer(ret_val, f_ret_ptr, (/ret_val_size/))\n'
                '    {} = f_ret_ptr\n').format(return_name)

    def fi_type(self) -> str:
        return self._regular_type(
                ['character(len=1), dimension(*)',
                 ('integer (c_size_t), value', '_size')])

    def fi_ret_type(self) -> str:
        return self._regular_type(
                ['type (c_ptr)',
                 ('integer (c_size_t)', '_size')])

    def fc_type(self) -> str:
        return self._regular_type(['char *', ('std::size_t', '_size')])

    def fc_ret_type(self) -> str:
        return self._regular_type(['char **', ('std::size_t *', '_size')])

    def fc_convert_input(self) -> str:
        return '    std::vector<char> {}_v({}, {} + {}_size);\n'.format(
                self.name, self.name, self.name, self.name)

    def fc_cpp_arg(self) -> str:
        return self.name + '_v'

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'static std::vector<char> result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return ('    *{0} = result.data();\n'
                '    *{0}_size = result.size();\n'
                '    return;\n').format(self.name)


class Obj(Par):
    """Represents an object of a type to pass.
    """
    def __init__(self, class_name: str, name: str = '') -> None:
        super().__init__(name)

        self.class_name = class_name
        self.ns_prefix = None

    def set_ns_prefix(self, ns_for_name: Dict[str, str]) -> None:
        self.ns_prefix = ns_for_name[self.class_name]

    def tname(self) -> str:
        return self.name.tolower()

    def fc_cpp_type(self) -> str:
        return self.class_name

    def f_type(self) -> str:
        return self._regular_type('type({}_{})'.format(
            self.ns_prefix, self.class_name))

    def f_ret_type(self) -> str:
        return True, self._regular_type('type({}_{})'.format(
            self.ns_prefix, self.class_name))

    def fi_type(self) -> str:
        return self._regular_type('integer (c_intptr_t), value')

    def fi_ret_type(self) -> str:
        return self._regular_type('integer (c_intptr_t)')

    def fc_type(self) -> str:
        return self._regular_type('std::intptr_t')

    def fc_ret_type(self) -> str:
        return self._regular_type('std::intptr_t')

    def fc_convert_input(self) -> str:
        return '    {} * {}_p = reinterpret_cast<{} *>({});\n'.format(
                self.class_name, self.name, self.class_name, self.name)

    def fc_cpp_arg(self) -> str:
        return '*{}_p'.format(self.name)

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return '{0} * result = new {0}({1})'.format(
                self.class_name, cpp_chain_call)

    def fc_return(self) -> str:
        return '    return reinterpret_cast<std::intptr_t>(result);\n'

    def f_chain_arg(self) -> str:
        return '{}%ptr'.format(self.name)

    def f_call_c(self, result_name: str, call: str) -> str:
        return '    {} = {}\n\n'.format(result_name, call)

    def f_return_result(self, return_name: str, result_name: str) -> str:
        return '    {}%ptr = {}\n'.format(return_name, result_name)


class Bool(Par):
    """Represents a bool-typed parameter.
    """
    def tname(self) -> str:
        return 'bool'

    def fc_cpp_type(self) -> str:
        return 'bool'

    def f_type(self) -> str:
        return self._regular_type('logical')

    def f_ret_type(self) -> str:
        return True, self._regular_type('logical')

    def fi_type(self) -> str:
        return self._regular_type('integer (c_int), value')

    def fi_ret_type(self) -> str:
        return self._regular_type('integer (c_int)')

    def fc_type(self) -> str:
        return self._regular_type('int')

    def fc_ret_type(self) -> str:
        return self._regular_type('int')

    def fc_cpp_arg(self) -> str:
        return '{} != 0'.format(self.name)

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'bool result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return '    return result ? 1 : 0;\n'

    def f_chain_arg(self) -> str:
        return 'merge(1, 0, {})'.format(self.name)

    def f_call_c(self, result_name: str, call: str) -> str:
        return '    {} = {}\n\n'.format(result_name, call)

    def f_return_result(self, return_name: str, result_name: str) -> str:
        return '    {} = {} .ne. 0\n'.format(return_name, result_name)


class EnumVal(Par):
    """Represents an enum-typed parameter.
    """
    def __init__(self, class_name: str, name: str = '') -> None:
        super().__init__(name)

        self.class_name = class_name
        self.ns_prefix = None

    def set_ns_prefix(self, ns_for_name: Dict[str, str]) -> None:
        self.ns_prefix = ns_for_name[self.class_name]

    def tname(self) -> str:
        return self.class_name.tolower()

    def fc_cpp_type(self) -> str:
        return self.class_name

    def f_type(self) -> str:
        return self._regular_type('integer({}_{})'.format(
            self.ns_prefix, self.class_name))

    def f_ret_type(self) -> str:
        return True, self._regular_type('integer({}_{})'.format(
            self.ns_prefix, self.class_name))

    def fi_type(self) -> str:
        return self._regular_type('integer (c_int), value')

    def fi_ret_type(self) -> str:
        return self._regular_type('integer (c_int)')

    def fc_type(self) -> str:
        return self._regular_type('int')

    def fc_ret_type(self) -> str:
        return self._regular_type('int')

    def fc_convert_input(self) -> str:
        return '    {} {}_e = static_cast<{}>({});\n'.format(
                self.class_name, self.name, self.class_name, self.name)

    def fc_cpp_arg(self) -> str:
        return self.name + '_e'

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return '{} result = {}'.format(self.class_name, cpp_chain_call)

    def fc_return(self) -> str:
        return '    return static_cast<int>(result);\n'


class Int(Par):
    """Represents an int-typed parameter.
    """
    def tname(self) -> str:
        return 'int'

    def fc_cpp_type(self) -> str:
        return 'int'

    def f_type(self) -> str:
        return self._regular_type('integer')

    def f_ret_type(self) -> str:
        return True, self._regular_type('integer')

    def fi_type(self) -> str:
        return self._regular_type('integer (c_int), value')

    def fi_ret_type(self) -> str:
        return self._regular_type('integer (c_int)')

    def fc_type(self) -> str:
        return self._regular_type('int')

    def fc_ret_type(self) -> str:
        return self._regular_type('int')

    def fc_cpp_arg(self) -> str:
        return self.name

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'int result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return '    return result;\n'


class Char(Par):
    """Represents an char-typed parameter.
    """
    def tname(self) -> str:
        return 'char'

    def fc_cpp_type(self) -> str:
        return 'char'

    def f_type(self) -> str:
        return self._regular_type('integer (selected_int_kind(2))')

    def f_ret_type(self) -> str:
        return True, self._regular_type('integer (selected_int_kind(2))')

    def fi_type(self) -> str:
        return self._regular_type('integer (c_int8_t), value')

    def fi_ret_type(self) -> str:
        return self._regular_type('integer (c_int8_t)')

    def fc_type(self) -> str:
        return self._regular_type('char')

    def fc_ret_type(self) -> str:
        return self._regular_type('char')

    def fc_cpp_arg(self) -> str:
        return self.name

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'char result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return '    return result;\n'


class Int16t(Par):
    """Represents an int16_t-typed parameter.
    """
    def tname(self) -> str:
        return 'int16'

    def fc_cpp_type(self) -> str:
        return 'int16_t'

    def f_type(self) -> str:
        return self._regular_type('integer (selected_int_kind(4))')

    def f_ret_type(self) -> str:
        return True, self._regular_type('integer (selected_int_kind(4))')

    def fi_type(self) -> str:
        return self._regular_type('integer (c_short), value')

    def fi_ret_type(self) -> str:
        return self._regular_type('integer (c_short)')

    def fc_type(self) -> str:
        return self._regular_type('short int')

    def fc_ret_type(self) -> str:
        return self._regular_type('short int')

    def fc_cpp_arg(self) -> str:
        return self.name

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'short int result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return '    return result;\n'


class Int64t(Par):
    """Represents an int64_t-typed parameter.
    """
    def tname(self) -> str:
        return 'int64'

    def fc_cpp_type(self) -> str:
        return 'int64_t'

    def f_type(self) -> str:
        return self._regular_type('integer (selected_int_kind(18))')

    def f_ret_type(self) -> str:
        return True, self._regular_type('integer (selected_int_kind(18))')

    def fi_type(self) -> str:
        return self._regular_type('integer (c_int64_t), value')

    def fi_ret_type(self) -> str:
        return self._regular_type('integer (c_int64_t)')

    def fc_type(self) -> str:
        return self._regular_type('int64_t')

    def fc_ret_type(self) -> str:
        return self._regular_type('int64_t')

    def fc_cpp_arg(self) -> str:
        return self.name

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'int64_t result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return '    return result;\n'


class Float(Par):
    """Represents a single precision float parameter.
    """
    def tname(self) -> str:
        return 'float'

    def fc_cpp_type(self) -> str:
        return 'float'

    def f_type(self) -> str:
        return self._regular_type('real (selected_real_kind(6))')

    def f_ret_type(self) -> str:
        return True, self._regular_type('real (selected_real_kind(6))')

    def fi_type(self) -> str:
        return self._regular_type('real (selected_real_kind(6)), value')

    def fi_ret_type(self) -> str:
        return self._regular_type('real (selected_real_kind(6))')

    def fc_type(self) -> str:
        return self._regular_type('float')

    def fc_ret_type(self) -> str:
        return self._regular_type('float')

    def fc_cpp_arg(self) -> str:
        return self.name

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'float result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return '    return result;\n'


class Double(Par):
    """Represents a double precision float parameter.
    """
    def tname(self) -> str:
        return 'double'

    def fc_cpp_type(self) -> str:
        return 'double'

    def f_type(self) -> str:
        return self._regular_type('real (selected_real_kind(15))')

    def f_ret_type(self) -> str:
        return True, self._regular_type('real (selected_real_kind(15))')

    def fi_type(self) -> str:
        return self._regular_type('real (selected_real_kind(15)), value')

    def fi_ret_type(self) -> str:
        return self._regular_type('real (selected_real_kind(15))')

    def fc_type(self) -> str:
        return self._regular_type('double')

    def fc_ret_type(self) -> str:
        return self._regular_type('double')

    def fc_cpp_arg(self) -> str:
        return self.name

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'double result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return '    return result;\n'


class T(Par):
    """Represents a template dummy type.
    """
    pass


class Member:
    pass


class MemFun(Member):
    def __init__(self,
                 ret_type: Par,
                 name: str,
                 params: Optional[List[Par]] = None,
                 may_throw: bool = False,
                 **args
                 ) -> None:
        """Create a member function description.

        This can be a Constructor or a Destructor as well, see those
        classes.

        The _override arguments are for overriding the automatic code
        generation, which is sometimes needed for odd functions.

        Args:
            ret_type: Description of the return value.
            name: Name of the member.
            params: List of in/out parameters.
            may_throw: True iff this function can throw an exception.
            fc_override: Custom Fortran-C wrapper function.
            f_override: Custom Fortran function.
        """
        self.ns_prefix = None       # type: Optional[str]
        self.public = None          # type: Optional[bool]
        self.class_name = None      # type: Optional[str]
        self.ret_type = ret_type
        self.name = name
        self.params = params if params else list()  # type: List[Par]
        self.may_throw = may_throw
        self.fc_override = args.get('fc_override')
        self.f_override = args.get('f_override')

    def set_class_name(self, class_name: str) -> None:
        self.class_name = class_name
        self.params.insert(0, Obj(class_name, 'self'))

    def set_ns_prefix(self, ns_for_name: Dict[str, str]) -> None:
        """Sets the namespace prefix correctly for all members.

        Args:
            ns_for_name: A map from type names to namespace names.
        """
        self.ns_prefix = ns_for_name[self.class_name]
        self.ret_type.set_ns_prefix(ns_for_name)
        for param in self.params:
            param.set_ns_prefix(ns_for_name)

    def set_public(self, public: bool) -> None:
        self.public = public

    def fortran_c_wrapper(self) -> str:
        """Create a C wrapper for calling by Fortran.
        """
        if self.fc_override:
            return self.fc_override

        result = ''

        # declaration
        in_parameters = self._fc_in_parameters()
        return_type, out_parameters = self._fc_out_parameters()
        if self.may_throw:
            out_parameters.append('int * err_code')
            out_parameters.append('char ** err_msg')
            out_parameters.append('std::size_t * err_msg_len')

        func_name = '{}_{}_{}_'.format(
                self.ns_prefix, self.class_name, self.name)

        par_str = ', '.join(in_parameters + out_parameters)
        result += '{} {}({}) {{\n'.format(return_type, func_name, par_str)

        # convert input
        for par in self.params:
            result += '{}'.format(par.fc_convert_input())

        # call C++ function and return result
        if self.may_throw:
            result += '    try {\n'
            result += '        *err_code = 0;\n'
            result += textwrap.indent(self._fc_cpp_call(), 4*' ')
            result += textwrap.indent(self._fc_return(), 4*' ')
            result += '    }\n'
            for exception, code in error_codes.items():
                result += '    catch (std::{} const & e) {{\n'.format(exception)
                result += '        *err_code = {};\n'.format(code)
                result += '        static std::string msg(e.what());\n'
                result += '        *err_msg = const_cast<char*>(msg.data());\n'
                result += '        *err_msg_len = msg.size();\n'
                result += '    }\n'
        else:
            result += self._fc_cpp_call()
            result += self._fc_return()
        result += '}\n\n'
        return result

    def fortran_interface(self) -> str:
        """Create a Fortran interface declaration for the C wrapper.
        """
        result = ''
        func_name = '{}_{}_{}_'.format(
                self.ns_prefix, self.class_name, self.name)

        # declaration
        in_parameters = self._fi_in_parameters()
        return_type, out_parameters = self._fi_out_parameters()
        if self.may_throw:
            out_parameters.append(('integer (c_int)', 'err_code'))
            out_parameters.append(('type (c_ptr)', 'err_msg'))
            out_parameters.append(('integer (c_size_t)', 'err_msg_len'))

        arg_list = [par_name for _, par_name in in_parameters + out_parameters]
        if return_type != '':
            result += '{} function {}( &\n        {}) &\n'.format(
                    return_type, func_name, ', '.join(arg_list))
        else:
            result += 'subroutine {}( &\n        {}) &\n'.format(
                    func_name, ', '.join(arg_list))
        result += '        bind(C, name="{}")\n'.format(func_name)
        result += '\n'
        result += '    use iso_c_binding\n'

        # parameter declarations
        for par_type, par_name in in_parameters:
            result += '    {}, intent(in) :: {}\n'.format(
                    par_type, par_name)
        for par_type, par_name in out_parameters:
            result += '    {}, intent(out) :: {}\n'.format(par_type, par_name)

        # end
        if return_type != '':
            result += 'end function {}\n\n'.format(func_name)
        else:
            result += 'end subroutine {}\n\n'.format(func_name)
        return textwrap.indent(result, 8*' ')

    def fortran_function(self) -> str:
        """Create the Fortran function definition for this member.
        """
        if self.f_override:
            return textwrap.indent(self.f_override, 4*' ')

        result = ''

        # declaration
        func_name = '{}_{}_{}'.format(
                self.ns_prefix, self.class_name, self.name)
        in_parameters = self._f_in_parameters()
        return_type, out_parameters = self._f_out_parameters()
        if self.may_throw:
            out_parameters.append(('integer, optional', 'err_code'))
            out_parameters.append(('character(:), allocatable, optional',
                                   'err_msg'))

        all_parameters = in_parameters + out_parameters
        arg_list = ', '.join([par_name for _, par_name in all_parameters])
        if return_type != '':
            result += 'function {}({})\n'.format(func_name, arg_list)
        else:
            result += 'subroutine {}({})\n'.format(func_name, arg_list)

        # parameter declarations
        result += '    implicit none\n'
        for par_type, par_name in in_parameters:
            result += '    {}, intent(in) :: {}\n'.format(
                    par_type, par_name)
        for par_type, par_name in out_parameters:
            result += '    {}, intent(out) :: {}\n'.format(par_type, par_name)
        if return_type != '':
            result += '    {} :: {}\n'.format(return_type, func_name)
        result += '\n'

        # variable declarations
        c_return_type, fi_out_parameters = self._fi_out_parameters()
        if c_return_type:
            result += '    {} :: ret_val\n'.format(c_return_type)
        for par_type, par_name in fi_out_parameters:
            result += '    {} :: {}\n'.format(par_type, par_name)
        for par_type, par_name in self.ret_type.f_aux_variables():
            result += '    {} :: {}\n'.format(par_type, par_name)
        if self.may_throw:
            result += '    integer (c_int) :: err_code_v\n'
            result += '    type (c_ptr) :: err_msg_v\n'
            result += '    integer (c_size_t) :: err_msg_len_v\n'
            result += '    character (c_char), dimension(:), pointer :: err_msg_f\n'
            result += '    character(:), allocatable :: err_msg_p\n'
            result += '    integer (c_size_t) :: err_msg_i\n'
        if c_return_type or fi_out_parameters or self.may_throw:
            result += '\n'

        # convert input
        args = [param.f_chain_arg() for param in self.params]
        args += [par_name for _, par_name in fi_out_parameters]
        if self.may_throw:
            args += ['err_code_v', 'err_msg_v', 'err_msg_len_v']
        arg_str = ', &\n'.join([8*' ' + arg for arg in args])

        # call C function
        chain_call = '{}_( &\n{})'.format(func_name, arg_str)
        result_name = ''
        if return_type != '':
            result_name = func_name
        elif out_parameters:
            result_name = out_parameters[0][1]
        result += self.ret_type.f_call_c('ret_val', chain_call)

        # handle errors if necessary
        if self.may_throw:
            # Note: I tried to factor this out into a function, but Fortran
            # makes that near-impossible. Since we're generating anyway, it's
            # not really duplication, so leave it as is.
            result += '    if (err_code_v .ne. 0) then\n'
            result += '        if (present(err_code)) then\n'
            result += '            err_code = err_code_v\n'
            result += '            if (present(err_msg)) then\n'
            result += '                call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))\n'
            result += '                allocate (character(err_msg_len_v) :: err_msg)\n'
            result += '                do err_msg_i = 1, err_msg_len_v\n'
            result += '                    err_msg(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)\n'
            result += '                end do\n'
            result += '            end if\n'
            result += '            return\n'
            result += '        else\n'
            result += '            call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))\n'
            result += '            allocate (character(err_msg_len_v) :: err_msg_p)\n'
            result += '            do err_msg_i = 1, err_msg_len_v\n'
            result += '                err_msg_p(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)\n'
            result += '            end do\n'
            result += '            print *, err_msg_p\n'
            result += '            stop\n'
            result += '        end if\n'
            result += '    end if\n\n'

        # convert and return result
        result += self.ret_type.f_return_result(result_name, 'ret_val')

        # end
        if return_type != '':
            result += 'end function {}\n\n'.format(func_name)
        else:
            result += 'end subroutine {}\n\n'.format(func_name)
        return textwrap.indent(result, 4*' ')

    def fortran_public_declaration(self) -> str:
        """Create a Fortran statement declaring us public.
        """
        func_name = '{}_{}_{}'.format(
                self.ns_prefix, self.class_name, self.name)
        return '    public :: {}\n'.format(func_name)

    def _fc_cpp_call(self) -> str:
        cpp_args = ', '.join([par.fc_cpp_arg() for par in self.params[1:]])
        cpp_chain_call = 'self_p->{}({})'.format(self.name, cpp_args)
        result = self.ret_type.fc_get_result(cpp_chain_call)
        return '    {};\n'.format(result)

    def _fc_return(self) -> str:
        return self.ret_type.fc_return()

    def _fc_in_parameters(self) -> List[str]:
        """Create a list of input parameters.
        """
        result = list()     # type: List[str]

        for param in self.params:
            type_list = param.fc_type()
            for type_name, postfix in type_list:
                result.append('{} {}'.format(type_name, param.name + postfix))

        return result

    def _fc_out_parameters(self) -> Tuple[str, List[str]]:
        """Create return type and output parameters.

        Returns a tuple (ret_type, out_pars).
        """
        out_pars = self.ret_type.fc_ret_type()
        if len(out_pars) == 1:
            return (out_pars[0][0], [])

        out_par_strl = list()       # type: List[str]
        for type_name, postfix in out_pars:
            out_par_strl.append('{} {}'.format(
                type_name, self.ret_type.name + postfix))
        return ('void', out_par_strl)

    def _fi_in_parameters(self) -> List[Tuple[str, str]]:
        """Returns Fortran interface input parameters.

        The result is a list of (type, name) tuples.
        """
        result = list()     # type: List[Tuple[str, str]]
        for param in self.params:
            type_list = param.fi_type()
            for type_name, postfix in type_list:
                result.append((type_name, param.name + postfix))
        return result

    def _fi_out_parameters(self) -> Tuple[str, List[Tuple[str, str]]]:
        """Returns Fortran interface output parameters.

        The result is a tuple (ret_type, [(out_type, out_name)]).
        """
        out_pars = self.ret_type.fi_ret_type()
        if len(out_pars) == 1:
            return (out_pars[0][0], [])

        out_par_list = list()       # type: List[Tuple[str, str]]
        for par_type, par_name in out_pars:
            out_par_list.append((par_type, 'ret_val' + par_name))

        return ('', out_par_list)

    def _f_in_parameters(self) -> List[Tuple[str, str]]:
        """Returns Fortran input parameters.

        The result is a list of (type, name) tuples.
        """
        result = list()     # type: List[Tuple[str, str]]
        for param in self.params:
            type_list = param.f_type()
            for type_name, postfix in type_list:
                result.append((type_name, param.name + postfix))
        return result

    def _f_out_parameters(self) -> Tuple[str, List[Tuple[str, str]]]:
        """Returns Fortran output parameters.

        The result is a tuple (ret_type, [(out_type, out_name)]).
        """
        is_function, out_pars = self.ret_type.f_ret_type()
        if is_function:
            return (out_pars[0][0], [])

        out_par_list = list()       # type: List[Tuple[str, str]]
        for par_type, par_name in out_pars:
            out_par_list.append((par_type, par_name))

        return ('', out_par_list)


class Constructor(MemFun):
    """Represents a class constructor.

    This generates code suitable for a constructor, rather than
    the default code.
    """
    def __init__(self, params: List[Par] = list(), name: str = 'create', **args
            ) -> None:
        super().__init__(Obj('<deferred>'), name, params, **args)

    def set_class_name(self, class_name: str) -> None:
        # Don't add self parameter
        self.class_name = class_name
        self.ret_type.class_name = class_name

    def _fc_cpp_call(self) -> str:
        # Create object instead of calling something
        cpp_args = [par.fc_cpp_arg() for par in self.params]
        return '    {} * result = new {}({});\n'.format(
                self.class_name, self.class_name, ', '.join(cpp_args))

    def _fc_return(self) -> str:
        return '    return reinterpret_cast<std::intptr_t>(result);\n'


class Destructor(MemFun):
    def __init__(self, **args) -> None:
        super().__init__(Void(), 'free', **args)

    def _fc_cpp_call(self) -> str:
        # Destroy object instead of calling something
        return '    delete self_p;\n'


class MemFunTmplInstance(MemFun):
    def __init__(self,
                 ret_type: Par,
                 name: str,
                 targ: Par,
                 params: Optional[List[Par]] = None,
                 may_throw: bool = False,
                 **args
                 ) -> None:
        """Create a member function template instance.

        The _override arguments are for overriding the automatic code
        generation, which is sometimes needed for odd functions.

        Args:
            ret_type: Description of the return value.
            name: Name of the template.
            targ: Template argument type.
            params: List of parameters.
            fc_override: Custom Fortran-C wrapper function.
            f_override: Custom Fortran function.
        """
        instance_name = '{}_{}'.format(name, targ.tname())
        super().__init__(ret_type, instance_name, params, may_throw, **args)

        self.tpl_name = name
        self.targ = targ


    def _fc_cpp_call(self) -> str:
        cpp_args = ', '.join([par.fc_cpp_arg() for par in self.params[1:]])
        cpp_chain_call = 'self_p->{}<{}>({})'.format(
                self.tpl_name, self.targ.fc_cpp_type(), cpp_args)
        result = self.ret_type.fc_get_result(cpp_chain_call)
        return '    {};\n'.format(result)


class MemFunTmpl(Member):
    def __init__(self,
                 types: List[Par],
                 ret_type: Par,
                 name: str,
                 params: Optional[List[Par]] = None,
                 may_throw: bool = False
                 ) -> None:
        """Create a member function template description.

        This class assumes that there is exactly one template
        parameter, designated by the special class T in the return
        value and/or parameters.

        Args:
            types: Types for which this template can be instantiated.
            ret_type: Description of the return value.
            name: Name of the member.
            params: List of in/out parameters.
        """
        self.ns_prefix = None       # type: Optional[str]
        self.public = None          # type: Optional[bool]
        self.class_name = None      # type: Optional[str]
        self.types = types
        self.ret_type = ret_type
        self.name = name
        self.params = params if params else list()  # type: List[Par]
        self.may_throw = may_throw
        self.instances = list()     # type: List[MemFun]

        # generate instances
        for typ in self.types:
            instance_ret_type = self.ret_type
            if isinstance(instance_ret_type, T):
                instance_ret_type = typ

            instance_params = list()    # type: List[Par]
            for param in self.params:
                if isinstance(param, T):
                    new_param = copy(typ)
                    new_param.name = param.name
                    instance_params.append(new_param)
                else:
                    instance_params.append(param)

            self.instances.append(MemFunTmplInstance(
                instance_ret_type, name, typ, instance_params, may_throw))


    def set_class_name(self, class_name: str) -> None:
        self.class_name = class_name
        self.params.insert(0, Obj(class_name, 'self'))
        for instance in self.instances:
            instance.set_class_name(class_name)

    def set_public(self, public: bool) -> None:
        self.public = public
        for instance in self.instances:
            instance.set_public(public)

    def set_ns_prefix(self, ns_for_name: Dict[str, str]) -> None:
        """Sets the namespace prefix correctly for all members.

        Args:
            ns_for_name: A map from type names to namespace names.
        """
        self.ns_prefix = ns_for_name[self.class_name]
        self.ret_type.set_ns_prefix(ns_for_name)
        for param in self.params:
            param.set_ns_prefix(ns_for_name)

        for instance in self.instances:
            instance.set_ns_prefix(ns_for_name)

    def fortran_c_wrapper(self) -> str:
        """Create a C wrapper for calling by Fortran.
        """
        result = ''
        for instance in self.instances:
            result += instance.fortran_c_wrapper()
        return result

    def fortran_interface(self) -> str:
        """Create a Fortran interface declaration for the C wrapper.
        """
        result = ''
        for instance in self.instances:
            result += instance.fortran_interface()
        return result

    def fortran_function(self) -> str:
        """Create the Fortran function definition for this member.
        """
        result = ''
        for instance in self.instances:
            result += instance.fortran_function()
        return result

    def fortran_public_declaration(self) -> str:
        """Create a Fortran statement declaring us public.
        """
        result = ''
        for instance in self.instances:
            result += instance.fortran_public_declaration()
        return result


class OverloadSet(Member):
    """Represents a set of overloaded functions.

    Since C does not support overloading (yes, C99, but that's too ugly
    to use), overloaded functions in the C++ API need to be represented
    here using different names. Fortran has a clean facility to tie
    these back together under a single name, which makes the Fortran
    API resemble the C++ one more closely, and is therefore a good
    idea. This class specifies a set of member functions to aggregate
    under a single name.
    """
    def __init__(self, name: str, names: List[str]) -> None:
        """Create an OverloadSet.

        Args:
            name: Name of the overloaded function to generate.
            names: List of function names to aggregate.
        """
        self.ns_prefix = None
        self.class_name = None
        self.public = None
        self.name = name
        self.names = names

    def set_class_name(self, class_name: str) -> None:
        self.class_name = class_name

    def set_ns_prefix(self, ns_for_name: Dict[str, str]) -> None:
        self.ns_prefix = ns_for_name[self.class_name]

    def set_public(self, public: bool) -> None:
        self.public = public

    def fortran_c_wrapper(self) -> str:
        return ''

    def fortran_interface(self) -> str:
        return ''

    def fortran_function(self) -> str:
        return ''

    def fortran_overload(self) -> str:
        prefix = '{}_{}'.format(self.ns_prefix, self.class_name)
        result = '    interface {}_{}\n'.format(prefix, self.name)
        result += '        module procedure &\n'

        names = ['{}{}_{}'.format(12*' ', prefix, name)
                 for name in self.names]
        result += '{}\n'.format(', &\n'.join(names))

        result += '    end interface\n\n'
        return result

    def fortran_public_declaration(self) -> str:
        """Create a Fortran statement declaring us public.
        """
        if self.public:
            return '    public :: {}_{}_{}\n'.format(
                    self.ns_prefix, self.class_name, self.name)
        return ''


class Class:
    def __init__(self, name: str, members: List[Member]) -> None:
        """Create a class description.

        Args:
            name: Name of the class.
            members: List of member functions.
        """
        self.ns_prefix = None       # type: Optional[str]
        self.public = None          # type: Optional[bool
        self.name = name
        self.members = members

        for member in members:
            member.set_class_name(name)

    def set_ns_prefix(self, ns_for_name: Dict[str, str]) -> None:
        """Sets the namespace prefix correctly for all members.

        Args:
            ns_for_name: A map from type names to namespace names.
        """
        self.ns_prefix = ns_for_name[self.name]
        for member in self.members:
            member.set_ns_prefix(ns_for_name)

    def set_public(self, public: bool) -> None:
        """Sets whether this class should be public.

        Public objects are usable by the Fortran program; this sets
        accessibility of the type and of all member functions.

        Args:
            public: True iff this is public.
        """
        self.public = public
        for member in self.members:
            member.set_public(public)

    def fortran_c_wrapper(self) -> str:
        """Create C functions for the members.
        """
        result = ''
        for member in self.members:
            result += member.fortran_c_wrapper()
        return result

    def fortran_interface(self) -> str:
        """Create a Fortran interface definition for the C ABI.
        """
        result = ''
        for member in self.members:
            result += member.fortran_interface()
        return result

    def fortran_overloads(self) -> str:
        """Create Fortran overload declarations for any OverloadSets.
        """
        result = ''
        for member in self.members:
            if isinstance(member, OverloadSet):
                result += member.fortran_overload()
        return result

    def fortran_type_definition(self) -> str:
        """Create a Fortran type/handle definition for this class.
        """
        result = 'type {}_{}\n'.format(self.ns_prefix, self.name)
        result += '    integer (c_intptr_t) :: ptr\n'
        result += 'end type {}_{}\n'.format(self.ns_prefix, self.name)
        if self.public:
            result += 'public :: {}_{}\n'.format(self.ns_prefix, self.name)
        result += '\n'
        return textwrap.indent(result, 4*' ')

    def fortran_public_declarations(self) -> str:
        """Creates Fortran declarations making functions public.
        """
        result = ''
        for member in self.members:
            result += member.fortran_public_declaration()
        return result

    def fortran_functions(self) -> str:
        """Create Fortran function definitions for this class.
        """
        result = ''
        for member in self.members:
            result += member.fortran_function()
        return result


class Enum:
    def __init__(self, name: str, values: List[Tuple[str, int]]) -> None:
        """Create an enumeration description.

        Args:
            name: Name of the enum.
            values: List of name, value pairs.
        """
        self.ns_prefix = None       # type: Optional[str]
        self.public = None          # type: Optional[bool]
        self.name = name
        self.values = values

    def set_ns_prefix(self, ns_for_name: Dict[str, str]) -> None:
        """Sets the namespace prefix correctly for all members.

        Args:
            ns_for_name: A map from type names to namespace names.
        """
        self.ns_prefix = ns_for_name[self.name]

    def set_public(self, public: bool) -> None:
        """Sets whether this enum should be public.

        Public objects are usable by the Fortran program.

        Args:
            public: True iff this is public.
        """
        self.public = public

    def fortran_type_definition(self) -> str:
        """Create a Fortran type definition for this enum.
        """
        result = ''
        public = ''
        if self.public:
            public = ', public'
        for val_name, val_value in self.values:
            result += 'integer, parameter{} :: {}_{}_{} = {}\n'.format(
                    public, self.ns_prefix, self.name, val_name, val_value)
        result += ('integer, parameter{0} :: {1}_{2} = kind(2)\n\n'
                ).format(public, self.ns_prefix, self.name)
        return textwrap.indent(result, 4*' ')


class Namespace:
    def __init__(self, name: str, public: bool, prefix: str, enums: List[Enum],
                 classes: List[Class]) -> None:
        """Create a namespace description.

        Args:
            name: Name of the namespace, full C++ name if nested.
            public: Whether to put the symbols in this namespace in the
                    generated public API.
            prefix: Short prefix to use in C/Fortran function names.
            enums: List of enums in this namespace.
            classes: List of classes in this namespace.
        """
        self.name = name
        self.public = public
        self.prefix = prefix
        self.enums = enums
        self.classes = classes

        for enum in self.enums:
            enum.set_public(public)
        for cls in self.classes:
            cls.set_public(public)

    def set_ns_prefix(self, ns_for_name: Dict[str, str]) -> None:
        """Sets the namespace prefix correctly for all members.

        Args:
            ns_for_name: A map from type names to namespace names.
        """
        for cls in self.classes:
            cls.set_ns_prefix(ns_for_name)
        for enum in self.enums:
            enum.set_ns_prefix(ns_for_name)

    def fortran_typedefs(self) -> str:
        """Generates Fortran type definitions for public types.
        """
        result = ''
        public = ''
        if self.public:
            public = ', public'
        for err_name, err_code in error_codes.items():
            result += '    integer, parameter{} :: {}_{} = {}\n'.format(
                    public, self.prefix, err_name, err_code)
        result += '\n'

        for enum in self.enums:
            result += enum.fortran_type_definition()

        for cls in self.classes:
            result += cls.fortran_type_definition()
            if self.public:
                result += cls.fortran_public_declarations()
        return result

    def fortran_interface(self) -> str:
        """Generates a Fortran interface block for this API.

        The interface block declares the C functions created by
        fortran_c_wrapper() so that Fortran can call them.
        """
        result = '    interface\n\n'
        for cls in self.classes:
            result += cls.fortran_interface()

        result += '    end interface\n\n'

        for cls in self.classes:
            result += cls.fortran_overloads()
        return result

    def fortran_functions(self) -> str:
        """Generates the public Fortran functions for the module.
        """
        result = ''
        for cls in self.classes:
            result += cls.fortran_functions()
        return result


class API:
    def __init__(self, name: str, headers: List[str], namespaces: List[Namespace]) -> None:
        """Create an API description.

        The API name will be used as module name in Fortran.

        Args:
            name: Name of the API.
            headers: Headers to include in the Fortran C wrapper file.
            namespaces: Namespaces making up the API.
        """
        self.name = name
        self.headers = headers
        self.namespaces = namespaces

        # set ns_prefix throughout the description
        ns_for_name = dict()  # type: Dict[str, str]
        for namespace in self.namespaces:
            for enum in namespace.enums:
                ns_for_name[enum.name] = namespace.prefix
            for cls in namespace.classes:
                ns_for_name[cls.name] = namespace.prefix

        for namespace in namespaces:
            namespace.set_ns_prefix(ns_for_name)


    def fortran_c_wrapper(self) -> str:
        """Generate a Fortran C-wrapper for this API.

        This wrapper wraps the C++ code in extern C functions that are
        suitable for calling by Fortran.
        """
        result = banner('//')
        result += self._fc_includes()
        result += self._fc_using_statements()
        result += self._fc_function_definitions()
        return result

    def fortran_module(self) -> str:
        """Generates a Fortran module for this API.

        The module contains an interface block for calling the C ABI
        created by fortran_c_wrapper(), and the public Fortran API.
        """
        result = banner('!')
        result += 'module {}\n'.format(self.name)
        result += '    use iso_c_binding\n'
        result += '    private\n\n'

        for ns in self.namespaces:
            result += ns.fortran_typedefs()
            result += '\n'

        for ns in self.namespaces:
            result += ns.fortran_interface()
            result += '\n'

        result += 'contains\n\n'
        for ns in self.namespaces:
            result += ns.fortran_functions()
            result += '\n'
        result += 'end module {}\n'.format(self.name)
        return result

    def _fc_includes(self) -> str:
        """Generate header includes.
        """
        result = ''
        for header in self.headers:
            result += '#include <{}>\n'.format(header)
        result += '\n\n'
        return result

    def _fc_using_statements(self) -> str:
        """Generate using statements for all enums and classes.

        This makes the rest of the code more readable and compact.
        """
        result = ''
        for namespace in self.namespaces:
            for enum in namespace.enums:
                result += 'using {}::{};\n'.format(namespace.name, enum.name)

            for cls in namespace.classes:
                result += 'using {}::{};\n'.format(namespace.name, cls.name)
        result += '\n\n'
        return result

    def _fc_function_definitions(self) -> str:
        """Generate a function for each wrapped member.
        """
        result = 'extern "C" {\n\n'
        for namespace in self.namespaces:
            for cls in namespace.classes:
                result += cls.fortran_c_wrapper()

        result += '}\n\n'
        return result
