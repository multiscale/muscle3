API Documentation for Fortran
=============================

This page provides full documentation for the Fortran API of MUSCLE 3.

.. f:module:: libmuscle
    :synopsis: Fortran module for libmuscle

.. f:currentmodule:: libmuscle

.. f:type:: LIBMUSCLE_Data

    Represents a libmuscle Data object. This is an opaque object that may be
    returned from and passed to libmuscle functions, but does not contain any
    directly accessible members.

    With respect to creation, assignment and copying, :f:type:`LIBMUSCLE_Data`
    objects act like Python objects: basic values (logicals, strings, integers
    and reals) get copied, while for lists, dictionaries, and byte arrays, the
    variable contains a reference which gets copied.

.. f:function:: LIBMUSCLE_Data_create()

    Creates a Data object representing nil.

    Nil is a special "no data" value, like nullptr in C++ or None in Python.

    :r obj: The new Data object
    :rtype obj: LIBMUSCLE_Data

.. f:function:: LIBMUSCLE_Data_create(value)

    Creates a Data object representing a logical value.

    :p logical value: The value to represent.
    :r obj: The new Data object
    :rtype obj: LIBMUSCLE_Data

.. f:function:: LIBMUSCLE_Data_create(value)

    Creates a Data object representing a character value.

    :p character value: The value to represent.
    :r obj: The new Data object
    :rtype obj: LIBMUSCLE_Data

.. f:function:: LIBMUSCLE_Data_create(value)

    Creates a Data object representing an integer value. Supported kinds are
    the default ``integer`` kind, and ``selected_int_kind(n)`` with ``n`` equal
    to 2, 4 or 18 (8, 16 and 64-bit signed integers respectively).

    Note that while libmuscle supports unsigned integers, these don't exist
    in Fortran. They will be mapped to the corresponding signed type, which
    may cause a silent overflow if the number is out of the signed type's
    range.

    :p integer value: The value to represent.
    :r obj: The new Data object
    :rtype obj: LIBMUSCLE_Data

.. f:function:: LIBMUSCLE_Data_create(value)

    Creates a Data object representing a real value. Supported kinds are
    ``selected_real_kind(6)`` and ``selected_int_kind(15)`` (32-bit single and
    64-bit double precision).

    :p real value: The value to represent.
    :r obj: The new Data object
    :rtype obj: LIBMUSCLE_Data

.. f:function:: LIBMUSCLE_Data_create_dict()

    Creates a Data object containing an empty dictionary.

    :r obj: The new Data object
    :rtype obj: LIBMUSCLE_Data

.. f:function:: LIBMUSCLE_Data_create_list()

    Creates a Data object containing an empty list.

    :r obj: The new Data object
    :rtype obj: LIBMUSCLE_Data

.. f:function:: LIBMUSCLE_Data_create_nils(size)

    Creates a Data object containing a list of ``size`` nil values.

    :p integer size: The number of nil values to put into the list.
    :r obj: The new Data object
    :rtype obj: LIBMUSCLE_Data

.. f:function:: LIBMUSCLE_Data_create_byte_array(size)

    Creates a Data object containing a byte array of the given number of bytes.

    :p integer size: The number of bytes to allocate for the array.
    :r obj: The new Data object
    :rtype obj: LIBMUSCLE_Data

.. f:function:: LIBMUSCLE_Data_create_byte_array(buf)

    Creates a Data object referring to the given data.

    The buffer passed will not be copied! This creates a Data object that refers
    to your buffer, and you need to make sure that that buffer exists for as
    long as the Data object (and/or any copies of it) is used.

    Example:

    .. code-block:: fortran

        type(LIBMUSCLE_Data) :: d1
        character(len=1), dimension(1024) :: bytes
        character(len=1), dimension(:), allocatable :: buf

        ! Create some data
        do i = 1, 1024
            bytes(i) = achar(mod(i, 256))
        end do

        ! Create a Data object referring to it
        d1 = LIBMUSCLE_Data_create_byte_array(bytes)
        ! Now d1 contains a byte array of size 1024

        ! Extract the data again, into a new buffer
        allocate(buf(LIBMUSCLE_Data_size(d1)))
        call LIBMUSCLE_Data_as_byte_array(d1, buf)
        ! Now, ichar(buf(i)) equals mod(i, 256)

        ! Clean up the buffer and the Data object
        deallocate(buf)
        call LIBMUSCLE_Data_free(d1)

    :p character buf: An array of characters to refer to.
    :r obj: The new Data object
    :rtype obj: LIBMUSCLE_Data

.. f:subroutine:: LIBMUSCLE_Data_free(self)

    Frees a Data object.

    This frees the resources associated wit the given Data object. Do not use
    the object for anything after calling this, because it will be invalid.

    :p LIBMUSCLE_Data self: The Data object to free.

.. f:subroutine:: LIBMUSCLE_Data_set(self, value)

    Assigns the value of ``value`` to ``self``. Both ``value`` and ``self``
    must have a value (nil is okay, but an uninitialised
    :f:type:`LIBMUSCLE_Data` is not). If ``value`` holds a basic type, then the
    value will be copied into ``self``, overwriting any previous value in
    ``self``. If ``value`` holds a list, dict, or byte array, then ``self`` will
    end up referring to the same object as ``value``.

    If you haven't created ``self`` yet, then it's shorter to use
    :f:func:`LIBMUSCLE_Data_create`.

    This is the equivalent of ``self = value`` in C++ or Python.

    :p LIBMUSCLE_Data self: The Data object to assign to.
    :p LIBMUSCLE_Data value: The Data object to assign from.

.. f:subroutine:: LIBMUSCLE_Data_set(self, value)

    Assigns the value of ``value`` to ``self``. ``self`` must be an initialised
    :f:type:`LIBMUSCLE_Data` object. If your target :f:type:`LIBMUSCLE_Data`
    object does not exist yet, use :f:func:`LIBMUSCLE_Data_create` instead.

    This is the equivalent of ``self = value`` in C++ or Python.

    Value may be of types ``logical``, ``character``, ``integer`` or ``real``.
    Integer kinds may be those representing 8-bit, 16-bit, 32-bit and 64-bit
    values, real kinds may be 32-bit single and 64-bit double precision.

    :p LIBMUSCLE_Data self: The Data object to assign to.
    :p ``see_above`` value: The value to assign from.

.. f:function:: LIBMUSCLE_Data_is_a_bool(self)

    Determine whether the Data object contains a boolean (logical) value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a logical value.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_string(self)

    Determine whether the Data object contains a string (character) value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a character value.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_char(self)

    Determine whether the Data object contains an integer value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains an integer value.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_int(self)

    Determine whether the Data object contains an integer value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains an integer value.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_int16(self)

    Determine whether the Data object contains an integer value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains an integer value.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_int64(self)

    Determine whether the Data object contains an integer value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains an integer value.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_float(self)

    Determine whether the Data object contains a single precision floating
    point value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a single precision float value.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_double(self)

    Determine whether the Data object contains a double precision floating
    point value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a double precision float value.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_nil(self)

    Determine whether the Data object contains a nil value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a nil value.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_dict(self)

    Determine whether the Data object contains a dictionary value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a dictionary.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_list(self)

    Determine whether the Data object contains a list value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a list.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_byte_array(self)

    Determine whether the Data object contains a byte array value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a byte array.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_size(self)

    Returns the size of a list (number of items), dict (number of key/value
    pairs), or byte array (number of bytes).

    :p LIBMUSCLE_Data self: The Data object to get the size of.
    :r size: The size of the object.
    :rtype size: integer (selected_int_kind(18))

.. f:function:: LIBMUSCLE_Data_as_bool(self, err_code, err_msg)

    Access a bool value.

    You can use :f:func:`LIBMUSCLE_Data_is_a_bool` to ascertain that the Data
    object contains a bool value.

    If the Data object does not contain a bool (logical) value, then an error
    message will be printed and execution will be halted.

    Alternatively, you can pass an argument for ``err_code``, or for both
    ``err_code`` and ``err_msg``, to catch the error.

    If ``err_code`` equals ``LIBMUSCLE_success`` after the call, then the
    returned value is the logical value held in this Data object. If it equals
    ``LIBMUSCLE_runtime_error``, the Data value did not contain a boolean
    (logical) value. If you passed an ``err_msg`` argument as well, then the
    passed variable will contain an appropriate error message in case of error,
    and needs to be deallocated (using ``deallocate()``) when you're done with
    it.

    Example:

    .. code-block:: fortran

        type(LIBMUSCLE_Data) :: mydata
        integer :: err_code
        logical :: val
        character(len=:), allocatable :: str, err_msg

        ! Create data object containing a logical value
        mydata = LIBMUSCLE_Data_create(.true.)
        ! Retrieve the value
        val = LIBMUSCLE_Data_as_bool(mydata)
        ! val equals .true. here
        ! Attempt to (incorrectly) retrieve a string
        str = LIBMUSCLE_Data_as_string(mydata, err_code, err_msg)
        if (err_code .ne. LIBMUSCLE_success)
            print *, err_msg
            ! Need to free the memory if an error message was returned
            deallocate(err_msg)
        end if
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    :p LIBMUSCLE_Data self: The Data object to get a bool value out of.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: logical

.. f:function:: LIBMUSCLE_Data_as_string(self, err_code, err_msg)

    Access a string value.

    You can use :f:func:`LIBMUSCLE_Data_is_a_string` to ascertain that the Data
    object contains a string value.

    If the Data object does not contain a string (character) value, then an
    error message will be printed and execution will be halted.

    Alternatively, you can pass an argument for ``err_code``, or for both
    ``err_code`` and ``err_msg``, to catch the error.

    If ``err_code`` equals ``LIBMUSCLE_success`` after the call, then the
    returned value is the string value held in this Data object. If it equals
    ``LIBMUSCLE_runtime_error``, the Data value did not contain a string
    (character) value. If you passed an ``err_msg`` argument as well, then the
    passed variable will contain an appropriate error message in case of error,
    and needs to be deallocated (using ``deallocate()``) when you're done with
    it.

    Note that the result variable will be allocated (unless an error occurs),
    and must be deallocated when you're done with the resulting string, or
    you'll have a memory leak.

    Example:

    .. code-block:: fortran

        type(LIBMUSCLE_Data) :: mydata
        character(len=:), allocatable :: str

        ! Create a data object containing a string value
        mydata = LIBMUSCLE_Data_create('Example')
        ! Retrieve the value
        str = LIBMUSCLE_Data_as_string(mydata)
        ! Free the retrieved copy of the string
        deallocate(str)
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    See :f:func:`LIBMUSCLE_Data_as_bool` for an example of error handling.

    :p LIBMUSCLE_Data self The Data object to get a string out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: character(len=:), allocatable

.. f:function:: LIBMUSCLE_Data_as_char(self, err_code, err_msg)

    Access an int value that fits in 8 bits.

    You can use :f:func:`LIBMUSCLE_Data_is_a_char` to ascertain that the Data
    object contains a char value.

    If the Data object does not contain an char (integer with
    ``selected_int_kind(2)``) value, then an error message will be printed and
    execution will be halted.

    Alternatively, you can pass an argument for ``err_code``, or for both
    ``err_code`` and ``err_msg``, to catch the error.

    If ``err_code`` equals ``LIBMUSCLE_success`` after the call, then the
    returned value is the integer value held in this Data object. If it equals
    ``LIBMUSCLE_runtime_error``, the Data value did not contain an integer
    value. If you passed an ``err_msg`` argument as well, then the passed
    variable will contain an appropriate error message in case of error, and
    needs to be deallocated (using ``deallocate()``) when you're done with it.

    Example:

    .. code-block:: fortran

        type(LIBMUSCLE_Data) :: mydata
        integer(kind=selected_int_kind(2)) :: number

        ! Create a data object containing an integer value
        mydata = LIBMUSCLE_Data_create(42)
        ! Retrieve the value
        number = LIBMUSCLE_Data_as_char(mydata)
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    See :f:func:`LIBMUSCLE_Data_as_bool` for an example of error handling.

    :p LIBMUSCLE_Data self The Data object to get an integer value out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: integer(kind=selected_int_kind(2))

.. f:function:: LIBMUSCLE_Data_as_int16(self, err_code, err_msg)

    Access an int value that fits in 16 bits.

    You can use :f:func:`LIBMUSCLE_Data_is_a_int16` to ascertain that the Data
    object contains an integer value.

    If the Data object does not contain an int16 (integer with
    ``selected_int_kind(4)``) value, then an error message will be printed and
    execution will be halted.

    Alternatively, you can pass an argument for ``err_code``, or for both
    ``err_code`` and ``err_msg``, to catch the error.

    If ``err_code`` equals ``LIBMUSCLE_success`` after the call, then the
    returned value is the integer value held in this Data object. If it equals
    ``LIBMUSCLE_runtime_error``, the Data value did not contain an integer
    value. If you passed an ``err_msg`` argument as well, then the passed
    variable will contain an appropriate error message in case of error, and
    needs to be deallocated (using ``deallocate()``) when you're done with it.

    Example:

    .. code-block:: fortran

        type(LIBMUSCLE_Data) :: mydata
        integer(kind=selected_int_kind(4)) :: number

        ! Create a data object containing an integer value
        mydata = LIBMUSCLE_Data_create(4242)
        ! Retrieve the value
        number = LIBMUSCLE_Data_as_int16(mydata)
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    See :f:func:`LIBMUSCLE_Data_as_bool` for an example of error handling.

    :p LIBMUSCLE_Data self The Data object to get an integer value out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: integer(kind=selected_int_kind(4))

.. f:function:: LIBMUSCLE_Data_as_int(self, err_code, err_msg)

    Access an integer value.

    You can use :f:func:`LIBMUSCLE_Data_is_a_int` to ascertain that the Data
    object contains an integer value.

    If the Data object does not contain an int (integer) value, then an error
    message will be printed and execution will be halted.

    Alternatively, you can pass an argument for ``err_code``, or for both
    ``err_code`` and ``err_msg``, to catch the error.

    If ``err_code`` equals ``LIBMUSCLE_success`` after the call, then the
    returned value is the integer value held in this Data object. If it equals
    ``LIBMUSCLE_runtime_error``, the Data value did not contain an integer
    value. If you passed an ``err_msg`` argument as well, then the passed
    variable will contain an appropriate error message in case of error, and
    needs to be deallocated (using ``deallocate()``) when you're done with it.

    Example:

    .. code-block:: fortran

        type(LIBMUSCLE_Data) :: mydata
        integer :: number

        ! Create a data object containing an integer value
        mydata = LIBMUSCLE_Data_create(42424242)
        ! Retrieve the value
        number = LIBMUSCLE_Data_as_int(mydata)
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    See :f:func:`LIBMUSCLE_Data_as_bool` for an example of error handling.

    :p LIBMUSCLE_Data self The Data object to get an integer value out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: integer

.. f:function:: LIBMUSCLE_Data_as_int64(self, err_code, err_msg)

    Access an integer value.

    You can use :f:func:`LIBMUSCLE_Data_is_a_int` to ascertain that the Data
    object contains an integer value.

    If the Data object does not contain an int (integer with
    ``selected_int_kind(18)``) value, then an error message will be printed and
    execution will be halted.

    Alternatively, you can pass an argument for ``err_code``, or for both
    ``err_code`` and ``err_msg``, to catch the error.

    If ``err_code`` equals ``LIBMUSCLE_success`` after the call, then the
    returned value is the integer value held in this Data object. If it equals
    ``LIBMUSCLE_runtime_error``, the Data value did not contain an integer
    value. If you passed an ``err_msg`` argument as well, then the passed
    variable will contain an appropriate error message in case of error, and
    needs to be deallocated (using ``deallocate()``) when you're done with it.

    Example:

    .. code-block:: fortran

        type(LIBMUSCLE_Data) :: mydata
        integer(kind=selected_int_kind(18)) :: number

        ! Create a data object containing an integer value
        mydata = LIBMUSCLE_Data_create(123456789123456789)
        ! Retrieve the value
        number = LIBMUSCLE_Data_as_int64(mydata)
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    See :f:func:`LIBMUSCLE_Data_as_bool` for an example of error handling.

    :p LIBMUSCLE_Data self The Data object to get an integer value out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: integer(kind=selected_int_kind(18))

.. f:function:: LIBMUSCLE_Data_as_float(self, err_code, err_msg)

    Access a single-precision real value.

    You can use :f:func:`LIBMUSCLE_Data_is_a_float` to ascertain that the Data
    object contains a single-precision real value.

    If the Data object does not contain a float (real with
    ``selected_real_kind(6)``) value, then an error message will be printed and
    execution will be halted.

    Alternatively, you can pass an argument for ``err_code``, or for both
    ``err_code`` and ``err_msg``, to catch the error.

    If ``err_code`` equals ``LIBMUSCLE_success`` after the call, then the
    returned value is the real value held in this Data object. If it equals
    ``LIBMUSCLE_runtime_error``, the Data value did not contain a real
    value. If you passed an ``err_msg`` argument as well, then the passed
    variable will contain an appropriate error message in case of error, and
    needs to be deallocated (using ``deallocate()``) when you're done with it.

    Example:

    .. code-block:: fortran

        type(LIBMUSCLE_Data) :: mydata
        real(kind=selected_real_kind(6)) :: number

        ! Create a data object containing a real value
        mydata = LIBMUSCLE_Data_create(42.0)
        ! Retrieve the value
        number = LIBMUSCLE_Data_as_single(mydata)
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    See :f:func:`LIBMUSCLE_Data_as_bool` for an example of error handling.

    :p LIBMUSCLE_Data self: The Data object to get a single-precision real value out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: real(kind=selected_real_kind(6))

.. f:function:: LIBMUSCLE_Data_as_double(self, err_code, err_msg)

    Access a double-precision real value.

    You can use :f:func:`LIBMUSCLE_Data_is_a_double` to ascertain that the Data
    object contains a double-precision real value.

    If the Data object does not contain a double (real with
    ``selected_real_kind(15)``) value, then an error message will be printed and
    execution will be halted.

    Alternatively, you can pass an argument for ``err_code``, or for both
    ``err_code`` and ``err_msg``, to catch the error.

    If ``err_code`` equals ``LIBMUSCLE_success`` after the call, then the
    returned value is the real value held in this Data object. If it equals
    ``LIBMUSCLE_runtime_error``, the Data value did not contain a real
    value. If you passed an ``err_msg`` argument as well, then the passed
    variable will contain an appropriate error message in case of error, and
    needs to be deallocated (using ``deallocate()``) when you're done with it.

    Example:

    .. code-block:: fortran

        type(LIBMUSCLE_Data) :: mydata
        real(kind=selected_real_kind(15)) :: number

        ! Create a data object containing a real value
        mydata = LIBMUSCLE_Data_create(42.0d0)
        ! Retrieve the value
        number = LIBMUSCLE_Data_as_double(mydata)
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    See :f:func:`LIBMUSCLE_Data_as_bool` for an example of error handling.

    :p LIBMUSCLE_Data self: The Data object to get a double-precision real value out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: real(kind=selected_real_kind(15))

.. f:subroutine:: LIBMUSCLE_Data_as_byte_array(self, buf, err_code, err_msg)

    Access a byte array value.

    You can use :f:func:`LIBMUSCLE_Data_is_a_byte_array` to ascertain that the
    Data object contains a byte array value. You can use
    :f:func:`LIBMUSCLE_Data_size` to get the number of bytes stored.

    If the Data object does not contain a byte array (character array) value,
    then an error message will be printed and execution will be halted.

    Alternatively, you can pass an argument for ``err_code``, or for both
    ``err_code`` and ``err_msg``, to catch the error.

    If ``err_code`` equals ``LIBMUSCLE_success`` after the call, then the
    contents of this variable will have been copied into ``buf``. If it equals
    ``LIBMUSCLE_runtime_error``, the Data value did not contain a byte array
    value. If you passed an ``err_msg`` argument as well, then the passed
    variable will contain an appropriate error message in case of error, and
    needs to be deallocated (using ``deallocate()``) when you're done with it.

    See :f:func:`LIBMUSCLE_Data_create_byte_array` for an example of
    creating and extracting byte array values. See
    :f:func:`LIBMUSCLE_Data_as_bool` for an example of error handling.

    :p LIBMUSCLE_Data self: The Data object to get a byte array out of.
    :p character buf: A buffer large enough to hold the contents of the data
            object.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).

.. f:function:: LIBMUSCLE_Data_get_item(self, i, err_code, err_msg)

    Access an item in a list.

    This function is only valid for Data objects containing a list. You
    can use :f:func:`LIBMUSCLE_Data_is_a_list` to check whether that is the
    case.

    This returns a :f:type:`LIBMUSCLE_Data` object containing the value at the
    given index in the list object. If ``self`` does not contain a list, the
    result will be invalid, and ``err_code`` will be set to
    ``LIBMUSCLE_runtime_error``. If ``i`` is negative, zero, or larger than the
    number of items in the list (see :f:func:`LIBMUSCLE_Data_size`),
    ``err_code`` will be set to ``LIBMUSCLE_out_of_range``, and the result will
    be invalid.

    As with any returned :f:type:`LIBMUSCLE_Data` object, the result needs to be
    freed via :f:func:`LIBMUSCLE_Data_free` once you're done with it. Setting
    the value of the returned object will update the list, but it's easier and
    safer to use :f:func:`LIBMUSCLE_Data_set_item` instead.

    Example:

    .. code-block:: fortran

        integer, parameter :: size_kind = selected_int_kind(18)
        type(LIBMUSCLE_Data) :: d1, d2
        character(len=:), allocatable :: s1

        d1 = LIBMUSCLE_Data_create_nils(10_size_kind)
        d2 = LIBMUSCLE_Data_get_item(d1, 5_size_kind)
        ! LIBMUSCLE_Data_is_nil(d2) returns .true. here
        call LIBMUSCLE_Data_free(d2)
        call LIBMUSCLE_Data_free(d1)

    See :f:func:`LIBMUSCLE_Data_as_bool` for an example of error handling.

    :p LIBMUSCLE_Data self: The Data object to get an item out of.
    :p integer i: The index to get the value at, in range [1..size]
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value at the corresponding index.
    :rtype value: LIBMUSCLE_Data

.. f:function:: LIBMUSCLE_Data_get_item(self, key, err_code, err_msg)

    Access an item in a dictionary.

    This function is only valid for Data objects containing a dictionary. You
    can use :f:func:`LIBMUSCLE_Data_is_a_dict` to check whether that is the
    case.

    This returns a :f:type:`LIBMUSCLE_Data` object containing the value
    associated with the given key in the dictionary object. If ``self`` does not
    contain a dictionary, the result will be invalid, and ``err_code`` will be
    set to ``LIBMUSCLE_runtime_error``. If ``key`` does not exist in this
    dictionary, ``err_code`` will be set to ``LIBMUSCLE_out_of_range``, and the
    result will be invalid.

    As with any returned :f:type:`LIBMUSCLE_Data` object, the result needs to be
    freed via :f:func:`LIBMUSCLE_Data_free` once you're done with it. Note that
    the returned object will be invalidated if a new key is added to the
    dictionary.  Assigning to the returned object will update the dictionary,
    but it's easier and safer to use :f:func:`LIBMUSCLE_Data_set_item` instead.

    Example:

    .. code-block:: fortran

        type(LIBMUSCLE_Data) :: d1, d2, d3
        character(len=:), allocatable :: s1

        d1 = LIBMUSCLE_Data_create_dict()
        call LIBMUSCLE_Data_set_item(d1, 'key1', 'value1')
        d3 = LIBMUSCLE_Data_get_item(d1, 'key1')
        s1 = LIBMUSCLE_Data_as_string(d3)
        print *, s1     ! prints 'value1'
        call LIBMUSCLE_Data_free(s1)
        call LIBMUSCLE_Data_free(d3)
        call LIBMUSCLE_Data_free(d2)
        call LIBMUSCLE_Data_free(d1)

    See :f:func:`LIBMUSCLE_Data_as_bool` for an example of error handling.

    :p LIBMUSCLE_Data self: The Data object to get an item out of.
    :p character key: The key to get the value for.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value corresponding to the selected key.
    :rtype value: LIBMUSCLE_Data

.. f:subroutine:: LIBMUSCLE_Data_set_item(self, i, value, err_code, err_msg)

    Set an item in a list.

    This function is only valid for Data objects containing a list. You can
    use :f:func:`LIBMUSCLE_Data_is_a_list` to check whether that is the case.

    This subroutine sets the ``i``'th value in the list to ``value``. If a value
    is already stored at this position, then it will be replaced. If the Data
    object does not contain a list, ``err_code`` will be set to
    ``LIBMUSCLE_runtime_error``. If the position ``i`` is zero, negative, or
    larger than the size of the list, ``err_code`` will be set to
    ``LIBMUSCLE_out_of_range``.

    ``value`` may be of type logical, character, integer, real, or Data. See
    :f:func:`LIBMUSCLE_Data_get_item` for an example. See
    :f:func:`LIBMUSCLE_Data_as_bool` for an example of error handling.

    :p LIBMUSCLE_Data self: The Data object to set an item value on.
    :p integer i: The position to set the value for, in range [1..size].
    :p see_above value: The value to set.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional)

.. f:subroutine:: LIBMUSCLE_Data_set_item(self, key, value, err_code, err_msg)

    Set an item in a dictionary.

    This function is only valid for Data objects containing a dictionary. You
    can use :f:func:`LIBMUSCLE_Data_is_a_dict` to check whether that is the
    case.

    This subroutine sets the value stored under ``key`` to ``value``. If a value
    is already stored under this key, then it will be replaced. If the Data
    object does not contain a dictionary, ``err_code`` will be set to
    ``LIBMUSCLE_runtime_error``.

    ``value`` may be of type logical, character, integer, real, or Data. See
    :f:func:`LIBMUSCLE_Data_get_item` for an example. See
    :f:func:`LIBMUSCLE_Data_as_bool` for an example of error handling.

    :p LIBMUSCLE_Data self: The Data object to set an item value on.
    :p character key: The key to set the value for.
    :p see_above value: The value to set.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional)

.. f:function:: LIBMUSCLE_Data_key(self, i, err_code, err_msg)

    Get the i'th key in the dictionary.

    This function is only valid for Data objects containing a dictionary. You
    can use :f:func:`LIBMUSCLE_Data_is_a_dict` to check whether that is the
    case.

    The indices range from 1 to the number of items in the dictionary
    (inclusive), as usual in Fortran. Use :f:func:`LIBMUSCLE_Data_size` to get
    the number of items. Note that changes to the dictionary (e.g. inserting a
    new key) may change the order in which the key-value pairs are retrieved by
    this function. It's best to not change the dictionary while iterating
    through it.

    As always when a character value is returned by MUSCLE, the variable it ends
    up in must be allocatable, and must be deallocated after use.

    The corresponding value may be obtained via
    :f:func:`LIBMUSCLE_Data_value(i)`.

    .. code-block:: fortran

        type(LIBMUSCLE_Data) :: d1, val
        character(len=:), allocatable :: key, cval
        integer (kind=selected_int_kind(18)) :: i
        integer intval

        d1 = LIBMUSCLE_Data_create_dict()
        call LIBMUSCLE_Data_set_item(d1, 'key1', 'value1')
        call LIBMUSCLE_Data_set_item(d1, 'key2', 'value2')

        do i = 1, LIBMUSCLE_Data_size(d1)
            key = LIBMUSCLE_Data_key(d1, i)
            val = LIBMUSCLE_Data_value(d1, i)
            cval = LIBMUSCLE_Data_as_string(val)
            print '(a8, a8)', key, cval
            deallocate(key)
            deallocate(cval)
            LIBMUSCLE_Data_free(val)
        end do

        call LIBMUSCLE_Data_free(d1)

    :p LIBMUSCLE_Data self: The Data object to get a key for.
    :p integer i: The index of the key to retrieve (``selected_int_kind(18)``)
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r key: The key at the given index.
    :rtype key: character (allocatable)

.. f:function:: LIBMUSCLE_Data_value(self, i, err_code, err_msg)

    Get the i'th value in the dictionary.

    This function is only valid for Data objects containing a dictionary. You
    can use :f:func:`LIBMUSCLE_Data_is_a_dict` to check whether that is the
    case.

    The indices range from 1 to the number of items in the dictionary
    (inclusive), as usual in Fortran. Use :f:func:`LIBMUSCLE_Data_size` to get
    the number of items. Note that changes to the dictionary (e.g. inserting a
    new key) may change the order in which the key-value pairs are retrieved by
    this function. It's best to not change the dictionary while iterating
    through it.

    The corresponding key may be obtained via :f:func:`LIBMUSCLE_Data_key`. See
    there for an example as well.

    :p LIBMUSCLE_Data self: The Data object to get a value for.
    :p integer i: The index of the key to retrieve (``selected_int_kind(18)``)
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value at the given index
    :rtype value: LIBMUSCLE_Data
