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

    With respect to creation, assignment and copying, ``LIBMUSCLE_Data`` objects
    act like Python objects: basic values (logicals, strings, integers and
    reals) get copied, while for lists, dictionaries, and byte arrays, the
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

.. f:subroutine:: LIBMUSCLE_Data_free(self)

    Frees a Data object.

    This frees the resources associated wit the given Data object. Do not use
    the object for anything after calling this, because it will be invalid.

    :p LIBMUSCLE_Data self: The Data object to free.

.. f:subroutine:: LIBMUSCLE_Data_assign(self, value)

    Assigns the value of ``value`` to ``self``. Both ``value`` and ``self``
    must have a value (nil is okay, but an uninitialised ``LIBMUSCLE_Data`` is
    not). If ``value`` holds a basic type, then the value will be copied into
    ``self``, overwriting any previous value in ``self``. If ``value`` holds a
    list, dict, or byte array, then ``self`` will end up referring to the same
    object as ``value``.

    If you haven't created ``self`` yet, then it's shorter to use
    ``LIBMUSCLE_Data_create(value)``.

    This is the equivalent of ``self = value`` in C++ or Python.

    :p LIBMUSCLE_Data self: The Data object to assign to.
    :p LIBMUSCLE_Data value: The Data object to assign from.

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

    You can use ``LIBMUSCLE_Data_is_a_bool()`` to ascertain that the Data object
    contains a bool value.

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

    You can use ``LIBMUSCLE_Data_is_a_string()`` to ascertain that the Data
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

    Example:

    .. code-block:: fortran

        type(LIBMUSCLE_Data) :: mydata
        character(len=:), allocatable :: str

        ! Create a data object containing a logical value
        mydata = LIBMUSCLE_Data_create('Example')
        ! Retrieve the value
        str = LIBMUSCLE_Data_as_string(mydata)
        ! Free the retrieved copy of the string
        deallocate(str)
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    See ``LIBMUSCLE_Data_is_a_bool()`` for an example of error handling.

    :p LIBMUSCLE_Data self The Data object to get a string out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: character(len=:), allocatable

.. f:function:: LIBMUSCLE_Data_as_char(self, err_code, err_msg)

    Access an int value that fits in 8 bits.

    You can use ``LIBMUSCLE_Data_is_a_char()`` to ascertain that the Data
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

    See ``LIBMUSCLE_Data_is_a_bool()`` for an example of error handling.

    :p LIBMUSCLE_Data self The Data object to get an integer value out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: integer(kind=selected_int_kind(2))

.. f:function:: LIBMUSCLE_Data_as_int16(self, err_code, err_msg)

    Access an int value that fits in 16 bits.

    You can use ``LIBMUSCLE_Data_is_a_int16()`` to ascertain that the Data
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

    See ``LIBMUSCLE_Data_is_a_bool()`` for an example of error handling.

    :p LIBMUSCLE_Data self The Data object to get an integer value out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: integer(kind=selected_int_kind(4))

.. f:function:: LIBMUSCLE_Data_as_int(self, err_code, err_msg)

    Access an integer value.

    You can use ``LIBMUSCLE_Data_is_a_int()`` to ascertain that the Data
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

    See ``LIBMUSCLE_Data_is_a_bool()`` for an example of error handling.

    :p LIBMUSCLE_Data self The Data object to get an integer value out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: integer

.. f:function:: LIBMUSCLE_Data_as_int64(self, err_code, err_msg)

    Access an integer value.

    You can use ``LIBMUSCLE_Data_is_a_int()`` to ascertain that the Data
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

    See ``LIBMUSCLE_Data_is_a_bool()`` for an example of error handling.

    :p LIBMUSCLE_Data self The Data object to get an integer value out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: integer(kind=selected_int_kind(18))

.. f:function:: LIBMUSCLE_Data_as_float(self, err_code, err_msg)

    Access a single-precision real value.

    You can use ``LIBMUSCLE_Data_is_a_float()`` to ascertain that the Data
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

        ! Create a data object containing an integer value
        mydata = LIBMUSCLE_Data_create(42.0)
        ! Retrieve the value
        number = LIBMUSCLE_Data_as_single(mydata)
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    See ``LIBMUSCLE_Data_is_a_bool()`` for an example of error handling.

    :p LIBMUSCLE_Data self The Data object to get a single-precision real value
            out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: real(kind=selected_real_kind(6))

.. f:function:: LIBMUSCLE_Data_as_double(self, err_code, err_msg)

    Access a double-precision real value.

    You can use ``LIBMUSCLE_Data_is_a_double()`` to ascertain that the Data
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

        ! Create a data object containing an integer value
        mydata = LIBMUSCLE_Data_create(42.0d0)
        ! Retrieve the value
        number = LIBMUSCLE_Data_as_double(mydata)
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    See ``LIBMUSCLE_Data_is_a_bool()`` for an example of error handling.

    :p LIBMUSCLE_Data self The Data object to get a double-precision real value
            out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: real(kind=selected_real_kind(15))






