#!/usr/bin/env python3

import abc
from copy import copy
from textwrap import indent, dedent
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union


error_codes = {
        'success': 0,
        'domain_error': 1,
        'out_of_range': 2,
        'logic_error': 3,
        'runtime_error': 4,
        'bad_cast': 5
        }


kinds = {
        'int1': 'selected_int_kind(2)',
        'int2': 'selected_int_kind(4)',
        'int4': 'selected_int_kind(9)',
        'int8': 'selected_int_kind(18)',
        'size': 'c_size_t',
        'real4': 'selected_real_kind(6)',
        'real8': 'selected_real_kind(15)'
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


class Par(abc.ABC):
    """Represent a parameter. Subclasses implement concrete types.

    This is used when generating:

    - The C wrapper function
    - The Fortran wrapper binding to the ISO C wrapper
    - The Fortran interface routine (public API) (Note, this is a function or
      subroutine, depending on return type)

    Parameters can be used as:

    - Return type of a method
    - Argument to a method

    The following member functions of this class are used to generate code when this
    parameter is used as return type:

    - fc_cpp_type: C-wrapper, the C++ type returned from the wrapped C++ API method
    - fc_ret_type: C-wrapper, the return type(s) of the C wrapper method
    - fc_get_result: C-wrapper, code for assigning the returned C++ value in C
    - fc_return: C-wrapper, code for returning the result
    - fc_return_default: C-wrapper, dummy result to return when an error occurred
    - fi_ret_type: Fortran wrapper, the output argument type(s) of the Fortran call to C
    - f_aux_variables: Fortran API, auxiliary variables needed by any of the below codes
    - f_call_c: Fortran API, the code for calling the C wrapper method
    - f_ret_type: Fortran API, the output argument type(s) of the public API procedure
    - f_return_result: Fortran API, how to convert from the output of the C wrapper to
        the public API output
    - f_return_dummy_result: Fortran API, dummy result to return when an error occurred

    The following member functions of this class are used to generate code when this
    parameter is used as a function argument:

    - fc_type: C-wrapper, the C-type(s) supplied as argument to the C wrapper function
    - fc_convert_input: C-wrapper, convert the arguments provided to the C wrapper
        function to the C++ type needed to call the C++ API
    - fc_cpp_arg: C-wrapper, return the argument name that is supplied to the C++
        API method
    - fi_type: Fortran wrapper, the input argument type(s) of the Fortran call to C
    - f_type: Fortran API, the input argument type(s) of the Fortran API
    - f_chain_arg: Fortran API, arguments to supply to the Fortran C call.
    """

    def __init__(self, name: str = 'ret_val') -> None:
        """Create a parameter description.

        Args:
            name: Name of the parameter.
        """
        self.name = name
        self.class_name = ""

    def set_ns_prefix(
            self, ns_for_name: Dict[str, Tuple[str, str]], c_ns: str, f_ns: str
            ) -> None:
        """Sets the namespace prefix correctly for all members.

        Args:
            ns_for_name: A map from type names to namespace names.
            c_ns: Name of the C namespace that this parameter's member function's
                    class is in.
            f_ns: Name of the Fortran namespace that this parameter's meember function's
                    class is in.
        """
        self.c_prefix = c_ns
        self.f_prefix = f_ns

    @abc.abstractmethod
    def tname(self) -> str:
        """Return the type name of this parameter class.

        Used when generating a name for instantiated templates."""

    @abc.abstractmethod
    def fc_cpp_type(self) -> str:
        ...

    @abc.abstractmethod
    def fc_cpp_arg(self) -> str:
        ...

    @abc.abstractmethod
    def fc_type(self) -> List[Tuple[str, str]]:
        """Format: [(C type, name_postfix), ...]
        """
        ...

    @abc.abstractmethod
    def fc_ret_type(self) -> List[Tuple[str, str]]:
        """Format: [(C type, name_postfix), ...]
        """
        ...

    @abc.abstractmethod
    def fi_ret_type(self) -> List[Tuple[str, str]]:
        """Format: [(F type, name_postfix), ...]
        """
        ...

    @abc.abstractmethod
    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        """Format: (is_function, [(F type, name_postfix), ...])

        When is_function is True, the wrapper generates a Fortran function, otherwise a
        subroutine.
        """

    @abc.abstractmethod
    def fi_type(self) -> List[Tuple[str, str]]:
        ...

    @abc.abstractmethod
    def f_type(self) -> List[Tuple[str, str]]:
        ...

    @abc.abstractmethod
    def fc_get_result(self, cpp_chain_call: str) -> str:
        ...

    @abc.abstractmethod
    def fc_return(self) -> str:
        ...

    def f_call_c(self, result_name: str, call: str) -> str:
        return '    {} = {}\n'.format(result_name, call)

    def f_return_result(self, return_name: str, result_name: str) -> str:
        return '    {} = {}\n'.format(return_name, result_name)

    def fc_return_default(self) -> str:
        return 'return {};'

    def fc_convert_input(self) -> str:
        return ''

    def f_aux_variables(self) -> List[Tuple[str, str]]:
        return list()

    def f_chain_arg(self) -> str:
        return self.name

    def f_return_dummy_result(self, return_name: str) -> str:
        return ''

    def _regular_type(self,
                      short_type: Union[str, List[Union[str, Tuple[str, str]]]]
                      ) -> List[Tuple[str, str]]:
        """Converts brief type description to more regular format.

        This is a helper function for derived classes. Output is a list
        of tuples (type, name_postfix), with one tuple for each
        variable. For simple types, this list will be of length 1, for
        variable-sized things however, there may be additional
        variables describing e.g. size or shape or format.

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
            result = list()  # type: List[Tuple[str, str]]
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

    def fc_type(self) -> List[Tuple[str, str]]:
        raise NotImplementedError("Cannot use void as argument")

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('void')

    def fi_type(self) -> List[Tuple[str, str]]:
        raise NotImplementedError("Cannot use void as argument")

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return []

    def f_type(self) -> List[Tuple[str, str]]:
        raise NotImplementedError("Cannot use void as argument")

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return False, []

    def fc_cpp_arg(self) -> str:
        raise NotImplementedError("Cannot use void as argument")

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return cpp_chain_call

    def fc_return(self) -> str:
        return '    return;\n'

    def f_call_c(self, result_name: str, call: str) -> str:
        return '    call {}\n'.format(call)

    def f_return_result(self, return_name: str, result_name: str) -> str:
        return ''

    def fc_return_default(self) -> str:
        return ''  # memfun has void signature


class String(Par):
    """Represents a string-typed parameter.
    """

    def tname(self) -> str:
        return 'character'

    def fc_cpp_type(self) -> str:
        return 'std::string'

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('character (len=*)')

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return True, self._regular_type('character(:), allocatable')

    def f_aux_variables(self) -> List[Tuple[str, str]]:
        return [('character (c_char), dimension(:), pointer', 'f_ret_ptr'),
                ('integer', 'i_loop')]

    def f_chain_arg(self) -> str:
        return '{}, int(len({}), c_size_t)'.format(self.name, self.name)

    def f_call_c(self, result_name: str, call: str) -> str:
        return '    call {}\n\n'.format(call)

    def f_return_result(self, return_name: str, result_name: str) -> str:
        return ('    call c_f_pointer(ret_val, f_ret_ptr, (/ret_val_size/))\n'
                '    allocate (character(ret_val_size) :: {0})\n'
                '    do i_loop = 1, ret_val_size\n'
                '        {0}(i_loop:i_loop) = f_ret_ptr(i_loop)\n'
                '    end do\n').format(return_name)

    def f_return_dummy_result(self, return_name: str) -> str:
        return '            allocate (character(0) :: {0})\n'.format(return_name)

    def fi_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                ['character',
                 ('integer (c_size_t), value', '_size')])

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                ['type (c_ptr)',
                 ('integer (c_size_t)', '_size')])

    def fc_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(['char *', ('std::size_t', '_size')])

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(['char **', ('std::size_t *', '_size')])

    def fc_convert_input(self) -> str:
        return '    std::string {}_s({}, {}_size);\n'.format(
                self.name, self.name, self.name)

    def fc_cpp_arg(self) -> str:
        return self.name + '_s'

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return ('static std::string result;\n'
                '    result = {}').format(cpp_chain_call)

    def fc_return(self) -> str:
        return ('    *{0} = const_cast<char*>(result.c_str());\n'
                '    *{0}_size = result.size();\n'
                '    return;\n').format(self.name)

    def fc_return_default(self) -> str:
        return ''  # memfun has void signature


class VecDbl(Par):
    """Represents a vector of double parameter.
    """
    def tname(self) -> str:
        return 'real8array'

    def fc_cpp_type(self) -> str:
        return 'std::vector<double>'

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                'real ({}_real8), dimension(:)'.format(self.f_prefix))

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return False, self._regular_type(
                [('real ({}_real8), dimension(:)'.format(self.f_prefix),
                  self.name)])

    def f_aux_variables(self) -> List[Tuple[str, str]]:
        return [(
            'real ({}_real8), pointer, dimension(:)'.format(self.f_prefix),
            'f_ret_ptr')]

    def f_chain_arg(self) -> str:
        return '{}, int(size({}), c_size_t)'.format(self.name, self.name)

    def f_call_c(self, result_name: str, call: str) -> str:
        return '    call {}\n\n'.format(call)

    def f_return_result(self, return_name: str, result_name: str) -> str:
        return ('    call c_f_pointer(ret_val, f_ret_ptr, (/ret_val_size/))\n'
                '    {} = f_ret_ptr\n').format(return_name)

    def fi_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                ['real (c_double), dimension(*)',
                 ('integer (c_size_t), value', '_size')])

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                ['type (c_ptr)',
                 ('integer (c_size_t)', '_size')])

    def fc_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(['double *', ('std::size_t', '_size')])

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(['double **', ('std::size_t *', '_size')])

    def fc_convert_input(self) -> str:
        return '    std::vector<double> {}_v({}, {} + {}_size);\n'.format(
                self.name, self.name, self.name, self.name)

    def fc_cpp_arg(self) -> str:
        return self.name + '_v'

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return ('static std::vector<double> result;\n'
                '    result = {}').format(cpp_chain_call)

    def fc_return(self) -> str:
        return ('    *{0} = result.data();\n'
                '    *{0}_size = result.size();\n'
                '    return;\n').format(self.name)

    def fc_return_default(self) -> str:
        return ''  # memfun has void signature


class Vec2Dbl(Par):
    """Represents a vector of vector of double parameter.
    """
    def tname(self) -> str:
        return 'real8array2'

    def fc_cpp_type(self) -> str:
        return 'std::vector<std::vector<double>>'

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                'real ({}_real8), dimension(:,:)'.format(self.f_prefix))

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return False, self._regular_type(
                [('real ({}_real8), dimension(:,:)'.format(self.f_prefix),
                  self.name)])

    def f_aux_variables(self) -> List[Tuple[str, str]]:
        return [('real ({}_real8), pointer, dimension(:,:)'.format(
                self.f_prefix), 'f_ret_ptr')]

    def f_chain_arg(self) -> str:
        return '{}, int(shape({}), c_size_t)'.format(self.name, self.name)

    def f_call_c(self, result_name: str, call: str) -> str:
        return '    call {}\n\n'.format(call)

    def f_return_result(self, return_name: str, result_name: str) -> str:
        return ('    call c_f_pointer(ret_val, f_ret_ptr, ret_val_shape)\n'
                '    {} = f_ret_ptr\n').format(return_name)

    def fi_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                ['real (c_double), dimension(*)',
                 ('integer (c_size_t), dimension(2)', '_shape')])

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                ['type (c_ptr)',
                 ('integer (c_size_t), dimension(2)', '_shape')])

    def fc_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(['double *', ('std::size_t *', '_shape')])

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(['double **', ('std::size_t *', '_shape')])

    def fc_convert_input(self) -> str:
        result = (
                'std::vector<std::vector<double>> {0}_v(\n'
                '        {0}_shape[0], std::vector<double>({0}_shape[1]));\n'
                'for (std::size_t i = 0; i < {0}_shape[0]; ++i)\n'
                '    for (std::size_t j = 0; j < {0}_shape[1]; ++j)\n'
                '        {0}_v[i][j] = {0}[j * {0}_shape[0] + i];\n'
                )

        return indent(result.format(self.name), '    ')

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
                'static std::vector<double> ret;\n'
                'ret.resize(result.size() * max_len);\n'
                'for (std::size_t i = 0; i < result.size(); ++i)\n'
                '    for (std::size_t j = 0; j < result[i].size(); ++j)\n'
                '        ret[j * result.size() + i] = result[i][j];\n'
                '\n'
                '*{0} = ret.data();\n'
                '{0}_shape[0] = result.size();\n'
                '{0}_shape[1] = max_len;\n'
                'return;\n'
                )

        return indent(result.format(self.name), '    ')

    def fc_return_default(self) -> str:
        return ''  # memfun has void signature


class VecSizet(Par):
    """Represents a vector of size_t parameter.
    """
    def tname(self) -> str:
        return 'sizearray'

    def fc_cpp_type(self) -> str:
        return 'std::vector<std::size_t>'

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                'integer ({}_size), dimension(:)'.format(self.f_prefix))

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return False, self._regular_type(
                [('integer ({}_size), dimension(:)'.format(self.f_prefix),
                  self.name)])

    def f_aux_variables(self) -> List[Tuple[str, str]]:
        return [(
            'integer ({}_size), pointer, dimension(:)'.format(self.f_prefix),
            'f_ret_ptr')]

    def f_chain_arg(self) -> str:
        return '{}, int(size({}), c_size_t)'.format(self.name, self.name)

    def f_call_c(self, result_name: str, call: str) -> str:
        return '    call {}\n\n'.format(call)

    def f_return_result(self, return_name: str, result_name: str) -> str:
        return ('    call c_f_pointer(ret_val, f_ret_ptr, (/ret_val_size/))\n'
                '    {}(1:ret_val_size) = f_ret_ptr\n').format(return_name)

    def fi_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                ['integer (c_size_t), dimension(*)',
                 ('integer (c_size_t), value', '_size')])

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                ['type (c_ptr)',
                 ('integer (c_size_t)', '_size')])

    def fc_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(['std::size_t *', ('std::size_t', '_size')])

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(['std::size_t **', ('std::size_t *', '_size')])

    def fc_convert_input(self) -> str:
        return '    std::vector<std::size_t> {}_v({}, {} + {}_size);\n'.format(
                self.name, self.name, self.name, self.name)

    def fc_cpp_arg(self) -> str:
        return self.name + '_v'

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return ('static std::vector<std::size_t> result;\n'
                '    result = {}').format(cpp_chain_call)

    def fc_return(self) -> str:
        return ('    *{0} = result.data();\n'
                '    *{0}_size = result.size();\n'
                '    return;\n').format(self.name)

    def fc_return_default(self) -> str:
        return ''  # memfun has void signature


class VecString(Par):
    """Represents a vector of string parameter.
    """
    def tname(self) -> str:
        return 'characterarray'

    def fc_cpp_type(self) -> str:
        return 'std::vector<std::string>'

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('character, dimension(:,:)')

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return True, self._regular_type(
                [('character(:), dimension(:), allocatable', self.name)])

    def f_aux_variables(self) -> List[Tuple[str, str]]:
        return [('character, pointer, dimension(:,:)', 'f_ret_ptr'),
                ('integer', 'i_loop, j_loop'),
                ('character(:), allocatable', 'tmp_s')]

    def f_chain_arg(self) -> str:
        return '{}, int(shape({}), c_size_t)'.format(self.name, self.name)

    def f_call_c(self, result_name: str, call: str) -> str:
        return '    call {}\n\n'.format(call)

    def f_return_result(self, return_name: str, result_name: str) -> str:
        return ('    call c_f_pointer(ret_val, f_ret_ptr, ret_val_shape)\n'
                '    allocate (character(ret_val_shape(2)) :: {0}(ret_val_shape(1)))\n'
                '    allocate (character(ret_val_shape(2)) :: tmp_s)\n'
                '    do i_loop = 1, ret_val_shape(1)\n'
                '        do j_loop = 1, ret_val_shape(2)\n'
                '            tmp_s(j_loop:j_loop) = f_ret_ptr(i_loop, j_loop)\n'
                '        end do\n'
                '        {0}(i_loop) = tmp_s\n'
                '    end do\n').format(return_name)

    def fi_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                ['character, dimension(*)',
                 ('integer (c_size_t), dimension(2)', '_shape')])

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                ['type (c_ptr)',
                 ('integer (c_size_t), dimension(2)', '_shape')])

    def fc_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(['char *', ('std::size_t *', '_shape')])

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(['char **', ('std::size_t *', '_shape')])

    def fc_convert_input(self) -> str:
        raise NotImplementedError()

    def fc_cpp_arg(self) -> str:
        return self.name + '_s'

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'std::vector<std::string> result = {}'.format(
                cpp_chain_call)

    def fc_return(self) -> str:
        result = (
                'std::size_t max_len = 0u;\n'
                'for (auto const & v : result)\n'
                '    max_len = std::max(max_len, v.size());\n'
                '\n'
                'static std::string ret;\n'
                # Note: "empty" spots in the array are a space, to work with Fortran
                'ret.resize(result.size() * max_len, \' \');\n'
                'for (std::size_t i = 0; i < result.size(); ++i)\n'
                '    for (std::size_t j = 0; j < result[i].size(); ++j)\n'
                '        ret[j * result.size() + i] = result[i][j];\n'
                '\n'
                '*{0} = const_cast<char*>(ret.c_str());\n'
                '{0}_shape[0] = result.size();\n'
                '{0}_shape[1] = max_len;\n'
                'return;\n'
                )

        return indent(result.format(self.name), '    ')

    def fc_return_default(self) -> str:
        return ''  # memfun has void signature


class Array(Par):
    def __init__(
            self, ndims: int, elem_type: Par, name: Optional[str] = None
            ) -> None:
        """Create an array parameter description.

        Args:
            ndims: Number of dimensions of the array.
            elem_type: Type of the array's elements.
            name: Name of the parameter.
        """
        if name is None:
            name = elem_type.name
            self.elem_type = elem_type
        else:
            self.elem_type = copy(elem_type)
            self.elem_type.name = name

        super().__init__(name)
        self.ndims = ndims

    def set_ns_prefix(
            self, ns_for_name: Dict[str, Tuple[str, str]], c_ns: str, f_ns: str
            ) -> None:
        self.c_prefix = c_ns
        self.f_prefix = f_ns
        self.elem_type.set_ns_prefix(ns_for_name, c_ns, f_ns)

    def tname(self) -> str:
        return '{}array{}'.format(self.elem_type.tname(), self.ndims)

    def fc_cpp_type(self) -> str:
        return '{} const *'.format(self.elem_type.fc_cpp_type())

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                '{}, dimension({})'.format(
                    self.elem_type.f_type()[0][0], self._f_dims()))

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return False, self._regular_type(
                [('{}, dimension({})'.format(self.elem_type.f_type()[0][0],
                                             self._f_dims()),
                  self.name)])

    def f_aux_variables(self) -> List[Tuple[str, str]]:
        return [('{}, pointer, dimension({})'.format(
                    self.elem_type.fi_ret_type()[0][0], self._f_dims()), 'f_ret_ptr'),
                ('{}, pointer, dimension(:)'.format(
                    self.elem_type.fi_ret_type()[0][0]), 'f_ret_ptr_linear')]

    def f_chain_arg(self) -> str:
        return '{0}, int(shape({0}), c_size_t), {1}_{2}_size'.format(
                self.elem_type.f_chain_arg(), self.ndims, self.f_prefix)

    def f_call_c(self, result_name: str, call: str) -> str:
        return '    call {}\n\n'.format(call)

    def f_return_result(self, return_name: str, result_name: str) -> str:
        c_order = '(/{}/)'.format(', '.join(
            map(str, reversed(range(1, self.ndims+1)))))
        return indent(dedent("""\
            if (ret_val_format .eq. 0) then
                call c_f_pointer(ret_val, f_ret_ptr, ret_val_shape)
                {0} = f_ret_ptr
            else
                call c_f_pointer(ret_val, f_ret_ptr_linear, (/product(ret_val_shape)/))
                {0} = reshape(f_ret_ptr_linear, ret_val_shape, (/ {2}:: /), {1})
            end if
            """), 4*' ').format(
                        return_name, c_order,
                        self.elem_type.fi_ret_type()[0][0])

    def fi_type(self) -> List[Tuple[str, str]]:
        base_type = self.elem_type.fi_type()[0][0].split(',')[0]
        return self._regular_type(
                ['{}, dimension(*)'.format(base_type),
                 ('integer (c_size_t), dimension({})'.format(self.ndims),
                     '_shape'),
                 ('integer (c_size_t), value', '_ndims')])

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                ['type (c_ptr)',
                 ('integer (c_size_t), dimension({})'.format(self.ndims),
                     '_shape'),
                 ('integer (c_int)', '_format')])

    def fc_type(self) -> List[Tuple[str, str]]:
        elem_fc_type = self.elem_type.fc_type()[0][0]
        return self._regular_type(
                ['{} *'.format(elem_fc_type),
                    ('std::size_t *', '_shape'),
                    ('std::size_t', '_ndims')])

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        # TODO: add ndims
        return self._regular_type(
            ['{} **'.format(self.elem_type.fc_cpp_type()),
             ('std::size_t *', '_shape'),
             ('int *', '_format')])

    def fc_convert_input(self) -> str:
        result = (
                'std::vector<std::size_t> {0}_shape_v(\n'
                '        {0}_shape, {0}_shape + {0}_ndims);\n'
                'auto {0}_p = const_cast<{1} const *>({0});\n'
                ).format(
                        self.name, self.elem_type.fc_cpp_type())

        return indent(result, '    ')

    def fc_cpp_arg(self) -> str:
        return '{0}_p, {0}_shape_v'.format(self.name)

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return '{} result = {}'.format(
                self.fc_cpp_type(), cpp_chain_call)

    def fc_return(self) -> str:
        result = dedent("""\
            if (self_p->shape().size() != {2}u)
                throw std::runtime_error(
                        "Grid does not have the expected {2} dimensions");
            *{0} = const_cast<{1} *>(result);
            for (std::size_t i = 0u; i < {2}u; ++i)
                {0}_shape[i] = self_p->shape()[i];

            *{0}_format = (
                    self_p->storage_order() == libmuscle::StorageOrder::last_adjacent);
            return;
            """)

        return indent(
                result.format(self.name, self.elem_type.fc_cpp_type(),
                              self.ndims),
                '    ')

    def fc_return_default(self) -> str:
        return ''  # memfun has void signature

    def _f_dims(self) -> str:
        return ', '.join([':'] * self.ndims)


class Bytes(Par):
    """Represents a vector of bytes.
    """
    def tname(self) -> str:
        return 'bytes'

    def fc_cpp_type(self) -> str:
        return 'std::vector<char>'

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                'character(len=1), dimension(:)')

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
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

    def fi_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                ['character(len=1), dimension(*)',
                 ('integer (c_size_t), value', '_size')])

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(
                ['type (c_ptr)',
                 ('integer (c_size_t)', '_size')])

    def fc_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(['char *', ('std::size_t', '_size')])

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type(['char **', ('std::size_t *', '_size')])

    def fc_convert_input(self) -> str:
        return '    std::vector<char> {}_v({}, {} + {}_size);\n'.format(
                self.name, self.name, self.name, self.name)

    def fc_cpp_arg(self) -> str:
        return self.name + '_v'

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return ('static std::vector<char> result;\n'
                'result = {}').format(cpp_chain_call)

    def fc_return(self) -> str:
        return ('    *{0} = result.data();\n'
                '    *{0}_size = result.size();\n'
                '    return;\n').format(self.name)

    def fc_return_default(self) -> str:
        return ''  # memfun has void signature


class Obj(Par):
    """Represents an object of a type to pass.
    """
    def __init__(self, class_name: str, name: str = '') -> None:
        super().__init__(name)

        self.class_name = class_name

    def set_ns_prefix(
            self, ns_for_name: Dict[str, Tuple[str, str]], c_ns: str, f_ns: str
            ) -> None:
        self.c_prefix, self.f_prefix = ns_for_name[self.class_name]

    def tname(self) -> str:
        return self.name.lower()

    def fc_cpp_type(self) -> str:
        return self.class_name

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('class({}_{})'.format(
            self.f_prefix, self.class_name))

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return True, self._regular_type('type({}_{})'.format(
            self.f_prefix, self.class_name))

    def fi_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (c_intptr_t), value')

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (c_intptr_t)')

    def fc_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('std::intptr_t')

    def fc_ret_type(self) -> List[Tuple[str, str]]:
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

    def fc_return_default(self) -> str:
        return '    return 0;\n'


class Bool(Par):
    """Represents a bool-typed parameter.
    """
    def tname(self) -> str:
        return 'logical'

    def fc_cpp_type(self) -> str:
        return 'bool'

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('logical')

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return True, self._regular_type('logical')

    def fi_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('logical (c_bool), value')

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('logical (c_bool)')

    def fc_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('bool')

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('bool')

    def fc_cpp_arg(self) -> str:
        return self.name

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'bool result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return '    return result;\n'

    def f_chain_arg(self) -> str:
        return 'logical({}, c_bool)'.format(self.name)

    def f_call_c(self, result_name: str, call: str) -> str:
        return '    {} = {}\n\n'.format(result_name, call)

    def f_return_result(self, return_name: str, result_name: str) -> str:
        return '    {} = {}\n'.format(return_name, result_name)

    def fc_return_default(self) -> str:
        return '    return false;\n'


class EnumVal(Par):
    """Represents an enum-typed parameter.
    """
    def __init__(self, class_name: str, name: str = '') -> None:
        super().__init__(name)

        self.class_name = class_name

    def set_ns_prefix(
            self, ns_for_name: Dict[str, Tuple[str, str]], c_ns: str, f_ns: str
            ) -> None:
        self.c_prefix, self.f_prefix = ns_for_name[self.class_name]

    def tname(self) -> str:
        return self.class_name.lower()

    def fc_cpp_type(self) -> str:
        return self.class_name

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer({}_{})'.format(
            self.f_prefix, self.class_name))

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return True, self._regular_type('integer({}_{})'.format(
            self.f_prefix, self.class_name))

    def fi_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (c_int), value')

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (c_int)')

    def fc_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('int')

    def fc_ret_type(self) -> List[Tuple[str, str]]:
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

    def fc_return_default(self) -> str:
        return '    return 0;\n'


class Int(Par):
    """Represents an int-typed parameter.
    """
    def tname(self) -> str:
        return 'int'

    def fc_cpp_type(self) -> str:
        return 'int'

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer')

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return True, self._regular_type('integer')

    def fi_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (c_int), value')

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (c_int)')

    def fc_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('int')

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('int')

    def fc_cpp_arg(self) -> str:
        return self.name

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'int result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return '    return result;\n'

    def fc_return_default(self) -> str:
        return '    return 0;\n'


class Char(Par):
    """Represents an char-typed parameter.
    """
    def tname(self) -> str:
        return 'int1'

    def fc_cpp_type(self) -> str:
        return 'char'

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer ({}_int1)'.format(self.f_prefix))

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return True, self._regular_type('integer ({}_int1)'.format(
                self.f_prefix))

    def fi_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (c_int8_t), value')

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (c_int8_t)')

    def fc_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('char')

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('char')

    def fc_cpp_arg(self) -> str:
        return self.name

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'char result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return '    return result;\n'

    def fc_return_default(self) -> str:
        return '    return 0;\n'


class Int16t(Par):
    """Represents an int16_t-typed parameter.
    """
    def tname(self) -> str:
        return 'int2'

    def fc_cpp_type(self) -> str:
        return 'int16_t'

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (selected_int_kind(4))')

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return True, self._regular_type('integer (selected_int_kind(4))')

    def fi_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (c_short), value')

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (c_short)')

    def fc_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('short int')

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('short int')

    def fc_cpp_arg(self) -> str:
        return self.name

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'short int result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return '    return result;\n'

    def fc_return_default(self) -> str:
        return '    return 0;\n'


class Int32t(Par):
    """Represents an int32_t-typed parameter.
    """
    def tname(self) -> str:
        return 'int4'

    def fc_cpp_type(self) -> str:
        return 'int32_t'

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer ({}_int4)'.format(self.f_prefix))

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return True, self._regular_type('integer ({}_int4)'.format(
                self.f_prefix))

    def fi_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (c_int32_t), value')

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (c_int32_t)')

    def fc_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('int32_t')

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('int32_t')

    def fc_cpp_arg(self) -> str:
        return self.name

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'int32_t result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return '    return result;\n'

    def fc_return_default(self) -> str:
        return '    return 0;\n'


class Int64t(Par):
    """Represents an int64_t-typed parameter.
    """
    def tname(self) -> str:
        return 'int8'

    def fc_cpp_type(self) -> str:
        return 'int64_t'

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (selected_int_kind(18))')

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return True, self._regular_type('integer (selected_int_kind(18))')

    def fi_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (c_int64_t), value')

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (c_int64_t)')

    def fc_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('int64_t')

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('int64_t')

    def fc_cpp_arg(self) -> str:
        return self.name

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'int64_t result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return '    return result;\n'

    def fc_return_default(self) -> str:
        return '    return 0;\n'


class Sizet(Par):
    """Represents an size_t-typed parameter.
    """
    def tname(self) -> str:
        return 'size'

    def fc_cpp_type(self) -> str:
        return 'std::size_t'

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer ({}_size)'.format(self.f_prefix))

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return True, self._regular_type('integer ({}_size)'.format(
                self.f_prefix))

    def fi_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (c_size_t), value')

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('integer (c_size_t)')

    def fc_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('std::size_t')

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('std::size_t')

    def fc_cpp_arg(self) -> str:
        return self.name

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'std::size_t result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return '    return result;\n'

    def fc_return_default(self) -> str:
        return '    return 0;\n'


class Float(Par):
    """Represents a single precision float parameter.
    """
    def tname(self) -> str:
        return 'real4'

    def fc_cpp_type(self) -> str:
        return 'float'

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('real ({}_real4)'.format(self.f_prefix))

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return True, self._regular_type('real ({}_real4)'.format(
                self.f_prefix))

    def fi_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('real (c_float), value')

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('real (c_float)')

    def fc_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('float')

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('float')

    def fc_cpp_arg(self) -> str:
        return self.name

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'float result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return '    return result;\n'

    def fc_return_default(self) -> str:
        return '    return 0.0;\n'


class Double(Par):
    """Represents a double precision float parameter.
    """
    def tname(self) -> str:
        return 'real8'

    def fc_cpp_type(self) -> str:
        return 'double'

    def f_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('real ({}_real8)'.format(self.f_prefix))

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        return True, self._regular_type('real ({}_real8)'.format(
                self.f_prefix))

    def fi_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('real (c_double), value')

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('real (c_double)')

    def fc_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('double')

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        return self._regular_type('double')

    def fc_cpp_arg(self) -> str:
        return self.name

    def fc_get_result(self, cpp_chain_call: str) -> str:
        return 'double result = {}'.format(cpp_chain_call)

    def fc_return(self) -> str:
        return '    return result;\n'

    def fc_return_default(self) -> str:
        return '    return 0.0;\n'


class T(Par):
    """Represents a template dummy type.
    """
    def tname(self) -> str:
        raise NotImplementedError("T is a dummy type")

    def fc_type(self) -> List[Tuple[str, str]]:
        raise NotImplementedError("T is a dummy type")

    def fc_cpp_type(self) -> str:
        raise NotImplementedError("T is a dummy type")

    def fc_ret_type(self) -> List[Tuple[str, str]]:
        raise NotImplementedError("T is a dummy type")

    def fi_type(self) -> List[Tuple[str, str]]:
        raise NotImplementedError("T is a dummy type")

    def fi_ret_type(self) -> List[Tuple[str, str]]:
        raise NotImplementedError("T is a dummy type")

    def f_type(self) -> List[Tuple[str, str]]:
        raise NotImplementedError("T is a dummy type")

    def f_ret_type(self) -> Tuple[bool, List[Tuple[str, str]]]:
        raise NotImplementedError("T is a dummy type")

    def fc_cpp_arg(self) -> str:
        raise NotImplementedError("T is a dummy type")

    def fc_get_result(self, cpp_chain_call: str) -> str:
        raise NotImplementedError("T is a dummy type")

    def fc_return(self) -> str:
        raise NotImplementedError("T is a dummy type")


class Member(abc.ABC):
    def __init__(self, name: str) -> None:
        self.c_prefix = self.f_prefix = ""
        self.name = name
        self.public: Optional[bool] = None
        self.class_name = ""

    def set_class_name(self, class_name: str) -> None:
        self.class_name = class_name

    def reset_class_name(self, class_name: str) -> None:
        self.class_name = class_name

    def set_ns_prefix(self, ns_for_name: Dict[str, Tuple[str, str]]) -> None:
        self.c_prefix, self.f_prefix = ns_for_name[self.class_name]

    def set_public(self, public: Optional[bool]) -> None:
        self.public = public

    @abc.abstractmethod
    def fortran_c_wrapper(self) -> str:
        ...

    @abc.abstractmethod
    def fortran_interface(self) -> str:
        ...

    @abc.abstractmethod
    def fortran_function(self) -> str:
        ...

    @abc.abstractmethod
    def fortran_public_declaration(self) -> str:
        ...

    @abc.abstractmethod
    def fortran_contains_definition(self) -> str:
        ...


class MemFun(Member):
    def __init__(self,
                 ret_type: Par,
                 name: str,
                 params: Optional[List[Par]] = None,
                 may_throw: bool = False,
                 *,
                 cpp_func_name: Optional[str] = None,
                 cpp_chain_call: Optional[Callable[..., str]] = None,
                 fc_override: Optional[str] = None,
                 fc_chain_call: Optional[Callable[..., str]] = None,
                 f_override: Optional[str] = None
                 ) -> None:
        """Create a member function description.

        This can be a Constructor or a Destructor as well, see those
        classes.

        The _override arguments are for overriding the automatic code
        generation, which is sometimes needed for odd functions.

        The ``cpp_chain_call`` argument takes a function. This function
        will be passed ``cpp_func_name`` and ``cpp_args`` parameters of
        type ``str``, containing the name of the C++ function to call
        and a comma-separated list of arguments to use. Note that
        ``cpp_func_name`` can be overridden using an argument of the
        same name. If ``cpp_chain_call`` is not specified, a plain
        member function call will be generated, so this is an override.

        Args:
            ret_type: Description of the return value.
            name: Name of the member.
            params: List of in/out parameters.
            may_throw: True iff this function can throw an exception.
            cpp_func_name: Name of C++ member function to call.
            cpp_chain_call: Function that produces the C++ chain call.
            fc_override: Custom Fortran-C wrapper function.
            fc_chain_call: Function that produces the C ABI call.
            f_override: Custom Fortran function.
        """
        super().__init__(name)
        self.ret_type = ret_type
        self.params: List[Par] = params if params else list()
        self.may_throw = may_throw
        self.cpp_chain_call = cpp_chain_call or self._default_cpp_chain_call
        self.fc_override = fc_override
        self.fc_chain_call = fc_chain_call or self._default_fc_chain_call
        self.f_override = f_override
        self.cpp_func_name = cpp_func_name or name

    def __copy__(self) -> 'MemFun':
        result = MemFun(
                self.ret_type, self.name, copy(self.params), self.may_throw)
        result.c_prefix = self.c_prefix
        result.f_prefix = self.f_prefix
        result.public = self.public
        result.class_name = self.class_name
        result.cpp_chain_call = self.cpp_chain_call
        result.fc_override = self.fc_override
        result.fc_chain_call = self.fc_chain_call
        result.f_override = self.f_override
        result.cpp_func_name = self.cpp_func_name
        return result

    def set_class_name(self, class_name: str) -> None:
        self.class_name = class_name
        self.params.insert(0, Obj(class_name, 'self'))

    def reset_class_name(self, class_name: str) -> None:
        self.class_name = class_name
        if len(self.params) > 0:
            if self.params[0].name == 'self':
                self.params[0] = Obj(class_name, 'self')

    def set_ns_prefix(self, ns_for_name: Dict[str, Tuple[str, str]]) -> None:
        """Sets the namespace prefix correctly for all members.

        Args:
            ns_for_name: A map from type names to namespace names.
        """
        self.c_prefix, self.f_prefix = ns_for_name[self.class_name]
        self.ret_type.set_ns_prefix(ns_for_name, self.c_prefix, self.f_prefix)
        for param in self.params:
            param.set_ns_prefix(ns_for_name, self.c_prefix, self.f_prefix)

    def fortran_c_wrapper(self) -> str:
        """Create a C wrapper for calling by Fortran.
        """
        if self.fc_override is not None:
            return self.fc_override.replace('$CLASSNAME$', self.class_name).replace(
                    "$C_PREFIX$", self.c_prefix).replace("$F_PREFIX$", self.f_prefix)

        result = ''

        # declaration
        in_parameters = self._fc_in_parameters()
        return_type, out_parameters = self._fc_out_parameters()
        if self.may_throw:
            out_parameters.append('int * err_code')
            out_parameters.append('char ** err_msg')
            out_parameters.append('std::size_t * err_msg_len')

        func_name = '{}_{}_{}_'.format(
                self.c_prefix, self.class_name, self.name)

        par_str = ', '.join(in_parameters + out_parameters)
        result += '{} {}({}) {{\n'.format(return_type, func_name, par_str)

        # convert input
        for par in self.params:
            result += '{}'.format(par.fc_convert_input())

        # call C++ function and return result
        if self.may_throw:
            result += '    try {\n'
            result += '        *err_code = 0;\n'
            result += indent(self._fc_cpp_call(), 4*' ')
            result += indent(self._fc_return(), 4*' ')
            result += '    }\n'
            for exception, code in error_codes.items():
                if code != 0:
                    catch = ''
                    catch += 'catch (std::{} const & e) {{\n'.format(exception)
                    catch += '    *err_code = {};\n'.format(code)
                    catch += '    static std::string msg;\n'
                    catch += '    msg = e.what();\n'
                    catch += '    *err_msg = const_cast<char*>(msg.data());\n'
                    catch += '    *err_msg_len = msg.size();\n'
                    catch += '}\n'
                    result += indent(catch, 4*' ')
            result += self._fc_return_default()
        else:
            result += self._fc_cpp_call()
            result += self._fc_return()
        result += '}\n\n'
        return result

    def fortran_interface(self) -> str:
        """Create a Fortran interface declaration for the C wrapper.
        """
        result = ''
        if self.fc_override == '':
            return result

        func_name = '{}_{}_{}_'.format(
                self.c_prefix, self.class_name, self.name)

        # declaration
        in_parameters = self._fi_in_parameters()
        return_type, out_parameters = self._fi_out_parameters()
        if self.may_throw:
            out_parameters.append(('integer (c_int)', 'err_code'))
            out_parameters.append(('type (c_ptr)', 'err_msg'))
            out_parameters.append(('integer (c_size_t)', 'err_msg_len'))

        arg_list = [par_name for _, par_name in in_parameters + out_parameters]
        if len(arg_list) > 1:
            arg_vlist = ' &\n' + indent(', &\n'.join(arg_list), 8*' ')
        else:
            arg_vlist = ', '.join(arg_list)

        if return_type != '':
            result += '{} function {}({}) &\n'.format(
                    return_type, func_name, arg_vlist)
        else:
            result += 'subroutine {}({}) &\n'.format(func_name, arg_vlist)
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
        return indent(result, 8*' ')

    def fortran_function(self) -> str:
        """Create the Fortran function definition for this member.
        """
        if self.f_override is not None:
            return indent(
                    self.f_override.replace('$CLASSNAME$', self.class_name).replace(
                            "$C_PREFIX$", self.c_prefix).replace(
                            "$F_PREFIX$", self.f_prefix),
                    4*' ')

        result = ''

        # declaration
        func_name = '{}_{}_{}'.format(
                self.f_prefix, self.class_name, self.name)
        in_parameters = self._f_in_parameters()
        return_type, out_parameters = self._f_out_parameters()
        if self.may_throw:
            out_parameters.append(('integer, optional', 'err_code'))
            out_parameters.append(('character(:), allocatable, optional',
                                   'err_msg'))

        all_parameters = in_parameters + out_parameters
        arg_list = ', &\n'.join([par_name for _, par_name in all_parameters])
        arg_ilist = indent(arg_list, 8*' ')
        if return_type != '':
            result += 'function {}( &\n{})\n'.format(func_name, arg_ilist)
        else:
            result += 'subroutine {}( &\n{})\n'.format(func_name, arg_ilist)

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
        fc_func_name = '{}_{}_{}_'.format(
                self.c_prefix, self.class_name, self.name)
        chain_call = self.fc_chain_call(
                ns_prefix=self.c_prefix, class_name=self.class_name,
                fc_func_name=fc_func_name, fc_args=arg_str)
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
            result += indent(dedent(f"""\
                if (err_code_v .ne. 0) then
                    if (present(err_code)) then
                        err_code = err_code_v
                        if (present(err_msg)) then
                            call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                            allocate (character(err_msg_len_v) :: err_msg)
                            do err_msg_i = 1, err_msg_len_v
                                err_msg(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                            end do
                        end if
                        {dedent(
                            self.ret_type.f_return_dummy_result(result_name))}
                        return
                    else
                        call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                        allocate (character(err_msg_len_v) :: err_msg_p)
                        do err_msg_i = 1, err_msg_len_v
                            err_msg_p(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                        end do
                        print *, err_msg_p
                        stop
                    end if
                else
                    if (present(err_code)) then
                        err_code = 0
                    end if
                end if

                """), 4*' ')

        # convert and return result
        result += self.ret_type.f_return_result(result_name, 'ret_val')

        # end
        if return_type != '':
            result += 'end function {}\n\n'.format(func_name)
        else:
            result += 'end subroutine {}\n\n'.format(func_name)
        return indent(result, 4*' ')

    def fortran_public_declaration(self) -> str:
        """Create a Fortran statement declaring us public.
        """
        if self.f_override == '':
            return ''

        func_name = '{}_{}_{}'.format(
                self.f_prefix, self.class_name, self.name)
        return '    public :: {}\n'.format(func_name)

    def fortran_contains_definition(self) -> str:
        if self.f_override == '':
            return ''
        full_name = f'{self.f_prefix}_{self.class_name}_{self.name}'
        return f'    procedure :: {self.name} => {full_name}\n'

    @staticmethod
    def _default_fc_chain_call(**kwargs: str) -> str:
        return '{fc_func_name}( &\n{fc_args})'.format(**kwargs)

    @staticmethod
    def _default_cpp_chain_call(**kwargs: str) -> str:
        return 'self_p->{cpp_func_name}({cpp_args})'.format(**kwargs)

    def _fc_cpp_call(self) -> str:
        cpp_args = ', '.join([par.fc_cpp_arg() for par in self.params[1:]])
        chain_args = {
                'cpp_func_name': self.cpp_func_name,
                'cpp_args': cpp_args
                }
        cpp_chain_call = self.cpp_chain_call(**chain_args)
        result = self.ret_type.fc_get_result(cpp_chain_call)
        return '    {};\n'.format(result)

    def _fc_return(self) -> str:
        return self.ret_type.fc_return()

    def _fc_return_default(self) -> str:
        return self.ret_type.fc_return_default()

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
    def __init__(
            self, params: Optional[List[Par]] = None, name: str = 'create',
            **args: Any) -> None:
        if params is None:
            params = list()
        super().__init__(Obj('<deferred>'), name, params, **args)

    def __copy__(self) -> 'Constructor':
        result = Constructor(copy(self.params), self.name)
        result.c_prefix = self.c_prefix
        result.f_prefix = self.f_prefix
        result.public = self.public
        result.class_name = self.class_name
        result.ret_type = self.ret_type
        result.may_throw = self.may_throw
        result.cpp_chain_call = self.cpp_chain_call
        result.fc_override = self.fc_override
        result.f_override = self.f_override
        result.cpp_func_name = self.cpp_func_name
        return result

    def set_class_name(self, class_name: str) -> None:
        # Don't add self parameter
        self.class_name = class_name
        self.ret_type.class_name = class_name

    def reset_class_name(self, class_name: str) -> None:
        self.class_name = class_name
        self.ret_type = Obj(class_name)

    def fortran_overload(self) -> str:
        if self.name != "create":
            return ''
        return indent(dedent(f"""\
            interface {self.f_prefix}_{self.class_name}
                module procedure {self.f_prefix}_{self.class_name}_{self.name}
            end interface

            """), 4*' ')

    def fortran_contains_definition(self) -> str:
        return ''

    def _fc_cpp_call(self) -> str:
        # Create object instead of calling something
        cpp_args = [par.fc_cpp_arg() for par in self.params]
        return '    {} * result = new {}({});\n'.format(
                self.class_name, self.class_name, ', '.join(cpp_args))

    def _fc_return(self) -> str:
        return '    return reinterpret_cast<std::intptr_t>(result);\n'


class EqualsOperator(MemFun):
    """Represents an equality operator.

    This generates code suitable for an equality comparison operator, rather
    than the default code.
    """
    def __init__(self, param: Par, name: str = 'equals', **args: Any) -> None:
        super().__init__(Bool(), name, [param], False, **args)

    def __copy__(self) -> 'EqualsOperator':
        result = EqualsOperator(copy(self.params[0]), self.name)
        result.c_prefix = self.c_prefix
        result.f_prefix = self.f_prefix
        result.public = self.public
        result.class_name = self.class_name
        result.ret_type = self.ret_type
        result.may_throw = self.may_throw
        result.cpp_chain_call = self.cpp_chain_call
        result.fc_override = self.fc_override
        result.f_override = self.f_override
        result.cpp_func_name = self.cpp_func_name
        return result

    def _fc_cpp_call(self) -> str:
        # Call operator instead of function
        rhs = self.params[1].fc_cpp_arg()
        cpp_chain_call = '((*self_p) == {})'.format(rhs)
        result = self.ret_type.fc_get_result(cpp_chain_call)
        return '    {};\n'.format(result)


class AssignmentOperator(MemFun):
    """Represents an assignment operator.

    This generates code suitable for an assignment operator, rather than
    the default code.
    """
    def __init__(self,
                 name: str,
                 param: Par,
                 **args: Any
                 ) -> None:
        super().__init__(Void(), name, [param], False, **args)

    def __copy__(self) -> 'AssignmentOperator':
        result = AssignmentOperator(self.name, copy(self.params[0]))
        result.c_prefix = self.c_prefix
        result.f_prefix = self.f_prefix
        result.public = self.public
        result.class_name = self.class_name
        result.ret_type = self.ret_type
        result.may_throw = self.may_throw
        result.cpp_chain_call = self.cpp_chain_call
        result.fc_override = self.fc_override
        result.f_override = self.f_override
        result.cpp_func_name = self.cpp_func_name
        return result

    def _fc_cpp_call(self) -> str:
        # Create object instead of calling something
        cpp_args = [par.fc_cpp_arg() for par in self.params]
        return '    *self_p = {};\n'.format(cpp_args[1])


class IndexAssignmentOperator(MemFun):
    """Assigns to an indexed item

    This generates code suitable for assigning to a subobject accessed
    via the square brackets operator, i.e. self[key] = value.
    """
    def __init__(self, name: str, params: List[Par], may_throw: bool = False
                 ) -> None:
        super().__init__(Void(), name, params, may_throw)

    def __copy__(self) -> 'IndexAssignmentOperator':
        result = IndexAssignmentOperator(
                self.name, copy(self.params), self.may_throw)
        result.c_prefix = self.c_prefix
        result.f_prefix = self.f_prefix
        result.public = self.public
        result.class_name = self.class_name
        result.ret_type = self.ret_type
        result.cpp_chain_call = self.cpp_chain_call
        result.fc_override = self.fc_override
        result.f_override = self.f_override
        result.cpp_func_name = self.cpp_func_name
        return result

    def _fc_cpp_call(self) -> str:
        # Call operator[] instead of a function
        cpp_args = [par.fc_cpp_arg() for par in self.params]
        return '    (*self_p)[{}] = {};\n'.format(cpp_args[1], cpp_args[2])


class ShiftedIndexAssignmentOperator(IndexAssignmentOperator):
    """Assigns to an indexed item, shifting the index by 1.

    This generates code suitable for assigning to a subobject accessed
    via the square brackets operator, i.e. self[i] / value.

    The index is shifted as necessary, e.g. to make it 1-based in
    Fortran and 0-based in C++.
    """
    def __copy__(self) -> 'ShiftedIndexAssignmentOperator':
        result = ShiftedIndexAssignmentOperator(
                self.name, copy(self.params), self.may_throw)
        result.c_prefix = self.c_prefix
        result.f_prefix = self.f_prefix
        result.public = self.public
        result.class_name = self.class_name
        result.ret_type = self.ret_type
        result.cpp_chain_call = self.cpp_chain_call
        result.fc_override = self.fc_override
        result.f_override = self.f_override
        result.cpp_func_name = self.cpp_func_name
        return result

    def _fc_cpp_call(self) -> str:
        # Call operator[] instead of a function
        cpp_args = [par.fc_cpp_arg() for par in self.params]
        return '    (*self_p)[{} - 1u] = {};\n'.format(
                cpp_args[1], cpp_args[2])


class NamedConstructor(Constructor):
    """Represents a named class constructor.

    This generates code suitable for a named constructor, which is a
    static function, rather than the default code.

    For name, pass the name of the static function, the Fortran name
    will then be create_<name>.
    """
    def __init__(self, params: List[Par], name: str, **args: Any) -> None:
        if 'cpp_func_name' not in args:
            args['cpp_func_name'] = name
        super().__init__(params, 'create_' + name, **args)
        self.cpp_chain_call = args.get(
                'cpp_chain_call', self._default_cpp_chain_call)

    def __copy__(self) -> 'NamedConstructor':
        result = NamedConstructor(copy(self.params), self.name)
        result.c_prefix = self.c_prefix
        result.f_prefix = self.f_prefix
        result.public = self.public
        result.class_name = self.class_name
        result.name = self.name
        result.ret_type = self.ret_type
        result.may_throw = self.may_throw
        result.cpp_chain_call = self.cpp_chain_call
        result.fc_chain_call = self.fc_chain_call
        result.fc_override = self.fc_override
        result.f_override = self.f_override
        result.cpp_func_name = self.cpp_func_name
        return result

    @staticmethod
    def _default_cpp_chain_call(**kwargs: Any) -> str:
        return '{0}::{1}({2})'.format(
                kwargs['class_name'], kwargs['cpp_func_name'],
                kwargs['cpp_args'])

    def _fc_cpp_call(self) -> str:
        # Create object instead of calling something
        cpp_args = ', '.join([par.fc_cpp_arg() for par in self.params])
        chain_args = {
                'class_name': self.class_name,
                'cpp_func_name': self.cpp_func_name,
                'cpp_args': cpp_args
                }
        cpp_chain_call = self.cpp_chain_call(**chain_args)
        result = self.ret_type.fc_get_result(cpp_chain_call)
        return '    {};\n'.format(result)

    def _fc_return(self) -> str:
        return '    return reinterpret_cast<std::intptr_t>(result);\n'


class Destructor(MemFun):
    def __init__(self, **args: Any) -> None:
        super().__init__(Void(), 'free', **args)

    def __copy__(self) -> 'MemFun':
        result = Destructor()
        result.c_prefix = self.c_prefix
        result.f_prefix = self.f_prefix
        result.public = self.public
        result.class_name = self.class_name
        result.ret_type = self.ret_type
        result.name = self.name
        result.params = copy(self.params)
        result.may_throw = self.may_throw
        result.cpp_chain_call = self.cpp_chain_call
        result.fc_override = self.fc_override
        result.f_override = self.f_override
        result.cpp_func_name = self.cpp_func_name
        return result

    def _fc_cpp_call(self) -> str:
        # Destroy object instead of calling something
        return '    delete self_p;\n'

    def fortran_function(self) -> str:
        return indent(dedent(f"""\
            subroutine {self.f_prefix}_{self.class_name}_{self.name}(self)
                implicit none
                type({self.f_prefix}_{self.class_name}), intent(inout) :: self

                call {self.c_prefix}_{self.class_name}_{self.name}_(self%ptr)
                self%ptr = 0
            end subroutine {self.f_prefix}_{self.class_name}_{self.name}

            """), 4*' ')

    def fortran_contains_definition(self) -> str:
        # Disabled until compilers stop giving errors and/or producing crashing
        # code whenever they see a finalizer.

        # full_name = f'{self.f_prefix}_{self.class_name}_{self.name}'
        # return f'    final :: {full_name}\n'
        return ''


class MultiMemFun(Member):
    """A base class for classes that generate many functions.

    This class represents a set of member functions, for example
    a set of template instantiations or functions taking array
    arguments of different number of dimensions. It forwards all
    functions to the individual instances contained in it.

    Attributes:
        instances: A list of the instances in this MultiMemFun.
    """
    def __init__(self) -> None:
        """Create a MultiMemFun."""
        super().__init__("")
        self.instances: List[Member] = list()

    def __copy__(self) -> 'MultiMemFun':
        result = MultiMemFun()
        result.instances = [copy(instance) for instance in self.instances]
        return result

    def set_class_name(self, class_name: str) -> None:
        for instance in self.instances:
            instance.set_class_name(class_name)

    def reset_class_name(self, class_name: str) -> None:
        for instance in self.instances:
            instance.reset_class_name(class_name)

    def set_public(self, public: Optional[bool]) -> None:
        for instance in self.instances:
            instance.set_public(public)

    def set_ns_prefix(self, ns_for_name: Dict[str, Tuple[str, str]]) -> None:
        """Sets the namespace prefix correctly for all members.

        Args:
            ns_for_name: A map from type names to namespace names.
        """
        for instance in self.instances:
            instance.set_ns_prefix(ns_for_name)

    def fortran_c_wrapper(self) -> str:
        """Create a C wrapper for calling by Fortran.
        """
        return ''.join([i.fortran_c_wrapper() for i in self.instances])

    def fortran_interface(self) -> str:
        """Create a Fortran interface declaration for the C wrapper.
        """
        return ''.join([i.fortran_interface() for i in self.instances])

    def fortran_function(self) -> str:
        """Create the Fortran function definition for this member.
        """
        return ''.join([i.fortran_function() for i in self.instances])

    def fortran_public_declaration(self) -> str:
        """Create a Fortran statement declaring us public.
        """
        return ''.join(
                [i.fortran_public_declaration() for i in self.instances])

    def fortran_contains_definition(self) -> str:
        return ''.join(i.fortran_contains_definition() for i in self.instances)


class MemFunTmplInstance(MemFun):
    def __init__(self,
                 ret_type: Par,
                 name: str,
                 targ: Par,
                 params: Optional[List[Par]] = None,
                 may_throw: bool = False,
                 **args: Any
                 ) -> None:
        """Create a member function template instance.

        The _override arguments are for overriding the automatic code
        generation, which is sometimes needed for odd functions.

        The ``cpp_chain_call`` argument takes a function. This function
        will be passed ``cpp_func_name``, ``tpl_type``, ``cpp_args``
        parameters of type ``str``, containing the name of the C++
        function to call and a comma-separated list of arguments to use.
        Note that ``cpp_func_name`` can be overridden using the
        argument of the same name. If ``cpp_chain_call`` is not
        specified, a plain member function template call will be
        generated, so this is an override.

        Args:
            ret_type: Description of the return value.
            name: Name of the template.
            targ: Template argument type.
            params: List of parameters.
            cpp_func_name: Name of C++ member function to call.
            cpp_chain_call: Function that produces the C++ chain call.
            fc_override: Custom Fortran-C wrapper function.
            f_override: Custom Fortran function.
        """
        instance_name = '{}_{}'.format(name, targ.tname())
        super().__init__(ret_type, instance_name, params, may_throw, **args)

        self.tpl_name = name
        self.targ = targ

    def __copy__(self) -> 'MemFunTmplInstance':
        result = MemFunTmplInstance(
                self.ret_type, self.tpl_name, self.targ, copy(self.params),
                self.may_throw)

        result.c_prefix = self.c_prefix
        result.f_prefix = self.f_prefix
        result.public = self.public
        result.name = self.name
        result.class_name = self.class_name
        result.cpp_chain_call = self.cpp_chain_call
        result.fc_override = self.fc_override
        result.f_override = self.f_override
        result.cpp_func_name = self.cpp_func_name
        return result

    @staticmethod
    def _default_cpp_chain_call(**kwargs: Any) -> str:
        return 'self_p->{cpp_func_name}<{tpl_type}>({cpp_args})'.format(
                **kwargs)

    def _fc_cpp_call(self) -> str:
        cpp_args = ', '.join([par.fc_cpp_arg() for par in self.params[1:]])
        chain_args = {
                'cpp_func_name': self.tpl_name,
                'cpp_args': cpp_args,
                'tpl_type': self.targ.fc_cpp_type()
                }
        cpp_chain_call = self.cpp_chain_call(**chain_args)
        result = self.ret_type.fc_get_result(cpp_chain_call)
        return '    {};\n'.format(result)


class MemFunTmpl(MultiMemFun):
    def __init__(self,
                 types: List[Par],
                 ret_type: Par,
                 name: str,
                 params: Optional[List[Par]] = None,
                 may_throw: bool = False,
                 **args: Any
                 ) -> None:
        """Create a member function template description.

        This class assumes that there is exactly one template
        parameter, designated by the special class T in the return
        value and/or parameters.

        The ``cpp_chain_call`` argument takes a function. This function
        will be passed ``cpp_func_name``, ``tpl_type``, ``cpp_args``
        parameters of type ``str``, containing the name of the C++
        function to call and a comma-separated list of arguments to use.
        Note that ``cpp_func_name`` can be overridden using the
        argument of the same name. If ``cpp_chain_call`` is not
        specified, a plain member function template call will be
        generated, so this is an override.

        Args:
            types: Types for which this template can be instantiated.
            ret_type: Description of the return value.
            name: Name of the member.
            params: List of in/out parameters.
            cpp_func_name: Name of C++ member function to call.
            cpp_chain_call: Function that produces the C++ chain call.
        """
        super().__init__()
        self.types = types
        self.ret_type = ret_type
        self.name = name
        self.params = params if params else list()  # type: List[Par]
        self.may_throw = may_throw

        # generate instances
        for typ in self.types:
            instance_ret_type = self.ret_type
            if isinstance(instance_ret_type, T):
                instance_ret_type = typ
            if isinstance(instance_ret_type, Array):
                if isinstance(instance_ret_type.elem_type, T):
                    instance_ret_type = copy(instance_ret_type)
                    instance_ret_type.elem_type = typ

            instance_params = list()    # type: List[Par]
            for param in self.params:
                if isinstance(param, T):
                    new_param = copy(typ)
                    new_param.name = param.name
                    instance_params.append(new_param)
                else:
                    instance_params.append(param)

            self.instances.append(MemFunTmplInstance(
                instance_ret_type, name, typ, instance_params, may_throw,
                **args))

    def __copy__(self) -> 'MemFunTmpl':
        result = MemFunTmpl(
                self.types, self.ret_type, self.name, copy(self.params),
                self.may_throw)
        result.c_prefix = self.c_prefix
        result.f_prefix = self.f_prefix
        result.public = self.public
        if self.class_name is None:
            result.class_name = None
        else:
            result.set_class_name(self.class_name)
        result.instances = [copy(instance) for instance in self.instances]
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
    def __init__(self, name: str, names: List[str], is_constructor: bool) -> None:
        """Create an OverloadSet.

        Args:
            name: Name of the overloaded function to generate.
            names: List of function names to aggregate.
            is_constructor: Whether this overload set is for a constructor.
        """
        super().__init__(name)
        self.names = names
        self.is_constructor = is_constructor

    def __copy__(self) -> 'OverloadSet':
        result = OverloadSet(self.name, self.names, self.is_constructor)
        result.c_prefix = self.c_prefix
        result.f_prefix = self.f_prefix
        result.class_name = self.class_name
        result.public = self.public
        return result

    def fortran_c_wrapper(self) -> str:
        return ''

    def fortran_interface(self) -> str:
        return ''

    def fortran_function(self) -> str:
        return ''

    def fortran_overload(self) -> str:
        prefix = '{}_{}'.format(self.f_prefix, self.class_name)
        interfaces = [f'{prefix}_{self.name}']
        # do not generate a fortran constructor for named constructors like create_grid
        if self.is_constructor and self.name == 'create':
            interfaces.append(f"{prefix}")

        result = ''
        for interface in interfaces:
            result += '    interface {}\n'.format(interface)
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
                    self.f_prefix, self.class_name, self.name)
        return ''

    def fortran_contains_definition(self) -> str:
        if self.is_constructor:
            return ''
        mem_fun_names = ', &\n        '.join(self.names)
        return f'    generic :: {self.name} => {mem_fun_names}\n'


class NamespaceMember(abc.ABC):
    def __init__(self, name: str):
        self.c_prefix: Optional[str] = None
        self.f_prefix: Optional[str] = None
        self.public: Optional[bool] = None
        self.name = name

    def set_ns_prefix(self, ns_for_name: Dict[str, Tuple[str, str]]) -> None:
        """Sets the namespace prefix correctly for all members.

        Args:
            ns_for_name: A map from type names to namespace names.
        """
        self.c_prefix, self.f_prefix = ns_for_name[self.name]

    def set_public(self, public: Optional[bool]) -> None:
        """Sets whether this class should be public.

        Public objects are usable by the Fortran program; this sets
        accessibility of the type and of all member functions.

        Args:
            public: True iff this is public.
        """
        self.public = public

    @abc.abstractmethod
    def fortran_type_definition(self) -> str:
        ...

    def fortran_public_declarations(self) -> str:
        """Creates Fortran declarations making functions public.
        """
        return ''

    def fortran_interface(self) -> str:
        """Create a Fortran interface definition for the C ABI.
        """
        return ''

    def fortran_overloads(self) -> str:
        """Create Fortran overload declarations for any OverloadSets.
        """
        return ''

    def fortran_functions(self) -> str:
        """Create Fortran function definitions for this class.
        """
        return ''

    def fortran_c_wrapper(self) -> str:
        """Create C functions for the members.
        """
        return ''


class Class(NamespaceMember):
    def __init__(
            self,
            name: str, parent: Optional['Class'],
            members: List[Member]
            ) -> None:
        """Create a class description.

        Args:
            name: Name of the class.
            members: List of member functions.
        """
        super().__init__(name)

        if parent is None:
            self.members = members
            for member in self.members:
                member.set_class_name(name)
        else:
            self.members = [copy(member) for member in parent.members]
            for member in self.members:
                member.reset_class_name(name)

            for member in members:
                member.set_class_name(name)
                for i in range(len(self.members)):
                    if self.members[i].name == member.name:
                        self.members[i] = member
                        break
                else:
                    self.members.append(member)

    def set_ns_prefix(self, ns_for_name: Dict[str, Tuple[str, str]]) -> None:
        super().set_ns_prefix(ns_for_name)
        for member in self.members:
            member.set_ns_prefix(ns_for_name)

    def set_public(self, public: Optional[bool]) -> None:
        super().set_public(public)
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
            if isinstance(member, (OverloadSet, Constructor)):
                result += member.fortran_overload()
        return result

    def fortran_type_definition(self) -> str:
        """Create a Fortran type/handle definition for this class.
        """
        result = 'type {}_{}\n'.format(self.f_prefix, self.name)
        result += '    integer (c_intptr_t) :: ptr = 0\n'
        ctn = ''.join(member.fortran_contains_definition() for member in self.members)
        if ctn:
            result += 'contains\n' + ctn
        result += 'end type {}_{}\n'.format(self.f_prefix, self.name)
        if self.public:
            result += 'public :: {}_{}\n'.format(self.f_prefix, self.name)
        result += '\n'
        return indent(result, 4*' ')

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


class Enum(NamespaceMember):
    def __init__(self, name: str, values: List[Tuple[str, int]]) -> None:
        """Create an enumeration description.

        Args:
            name: Name of the enum.
            values: List of name, value pairs.
        """
        super().__init__(name)
        self.values = values

    def fortran_type_definition(self) -> str:
        """Create a Fortran type definition for this enum.
        """
        result = ''
        public = ''
        if self.public:
            public = ', public'
        for val_name, val_value in self.values:
            result += 'integer, parameter{} :: {}_{}_{} = {}\n'.format(
                    public, self.f_prefix, self.name, val_name, val_value)
        result += ('integer, parameter{0} :: {1}_{2} = selected_int_kind(9)\n\n'
                   ).format(public, self.f_prefix, self.name)
        return indent(result, 4*' ')


class Flags(NamespaceMember):
    def __init__(self, name: str, values: List[str]):
        """Create a Flags description.

        Flags are an enum class in C++, but a custom derived type with boolean
        attributes in Fortran.

        Args:
            name: name of the flags
            values: list of option names
        """
        super().__init__(name)
        self.values = values

    def fortran_type_definition(self) -> str:
        """Create a Fortran type definition for this enum.
        """
        result = ''
        if self.public:
            result += f'public :: {self.f_prefix}_{self.name}\n'

        result += f'type {self.f_prefix}_{self.name}\n'
        for value in self.values:
            result += f'    logical :: {value} = .false.\n'
        result += '\n'
        result += 'contains\n'
        result += f'    procedure :: to_int => {self.f_prefix}_{self.name}_to_int_\n'
        result += 'end type\n'
        return indent(result, 4*' ')

    def fortran_functions(self) -> str:
        """Create Fortran function definitions for this class.
        """
        fun_name = f'{self.f_prefix}_{self.name}_to_int_'
        result = f'integer function {fun_name}(flags)\n'
        result += '    implicit none\n'
        result += '\n'
        result += f'    class({self.f_prefix}_{self.name}), intent(in) :: flags\n'
        result += '    integer :: ret_val\n'
        result += '\n'
        result += '    ret_val = 0\n'
        for i, value in enumerate(self.values):
            result += f"    if (flags%{value}) ret_val = ret_val + {1 << i}\n"
        result += f'    {fun_name} = ret_val\n'
        result += f'end function {fun_name}\n'
        return indent(result, 4*' ')


class Namespace:
    def __init__(self, name: str, public: Optional[bool], c_prefix: str, f_prefix: str,
                 members: Sequence[NamespaceMember]
                 ) -> None:
        """Create a namespace description.

        Args:
            name: Name of the namespace, full C++ name if nested.
            public: Whether to put the symbols in this namespace in the
                    generated public API. If None, do not generate at
                    all (used for forward declarations).
            c_prefix: Short prefix to use in C function names.
            f_prefix: Short prefix to use in Fortran function names.
            enums: List of enums in this namespace.
            classes: List of classes in this namespace.
        """
        self.name = name
        self.public = public
        self.c_prefix = c_prefix
        self.f_prefix = f_prefix
        self.members = members

        for member in self.members:
            member.set_public(public)

    def set_ns_prefix(self, ns_for_name: Dict[str, Tuple[str, str]]) -> None:
        """Sets the namespace prefix correctly for all members.

        Args:
            ns_for_name: A map from type names to namespace names.
        """
        for member in self.members:
            member.set_ns_prefix(ns_for_name)

    def fortran_typedefs(self) -> str:
        """Generates Fortran type definitions for public types.
        """
        result = ''
        public = ''
        if self.public is None:
            return result
        if self.public:
            public = ', public'
        for err_name, err_code in error_codes.items():
            result += '    integer, parameter{} :: {}_{} = {}\n'.format(
                    public, self.f_prefix, err_name, err_code)
        result += '\n'

        for kind_name, kind_def in kinds.items():
            result += '    integer, parameter{} :: {}_{} = {}\n'.format(
                    public, self.f_prefix, kind_name, kind_def)
        result += '\n'

        for member in self.members:
            result += member.fortran_type_definition()
            if self.public:
                result += member.fortran_public_declarations()

        return result

    def fortran_interface(self) -> str:
        """Generates a Fortran interface block for this API.

        The interface block declares the C functions created by
        fortran_c_wrapper() so that Fortran can call them.
        """
        if self.public is None:
            return ''

        result = '    interface\n\n'
        result += "".join(member.fortran_interface() for member in self.members)
        result += '    end interface\n\n'

        for member in self.members:
            result += member.fortran_overloads()
        return result

    def fortran_functions(self) -> str:
        """Generates the public Fortran functions for the module.
        """
        result = ''
        if self.public is None:
            return result

        result += "".join(member.fortran_functions() for member in self.members)
        return result


class API:
    def __init__(
            self, name: str, headers: List[str], uses: List[str],
            namespaces: List[Namespace]) -> None:
        """Create an API description.

        The API name will be used as module name in Fortran.

        Args:
            name: Name of the API.
            headers: Headers to include in the Fortran C wrapper file.
            uses: List of Fortran modules used by this module.
            namespaces: Namespaces making up the API.
        """
        self.name = name
        self.headers = headers
        self.uses = uses
        self.namespaces = namespaces

        # set ns_prefix throughout the description
        ns_for_name: Dict[str, Tuple[str, str]] = dict()
        for namespace in self.namespaces:
            for member in namespace.members:
                ns_for_name[member.name] = (namespace.c_prefix, namespace.f_prefix)

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
        for dep in self.uses:
            result += '    use {}\n'.format(dep)
        result += '\n'
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
            for member in namespace.members:
                result += 'using {}::{};\n'.format(namespace.name, member.name)
        result += '\n\n'
        return result

    def _fc_function_definitions(self) -> str:
        """Generate a function for each wrapped member.
        """
        result = 'extern "C" {\n\n'
        for namespace in self.namespaces:
            for member in namespace.members:
                result += member.fortran_c_wrapper()

        result += '}\n\n'
        return result
