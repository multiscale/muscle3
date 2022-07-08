.. _api-docs-fortran:

API Documentation for Fortran
=============================

This page provides full documentation for the Fortran API of MUSCLE 3.

A note on types
---------------

Fortran variables have a type and a kind. The type specifies a broad category,
i.e. whether it is a logical value, text, or an integer or floating point
number. The kind further subdivides the numbers into kinds with different
precision or size. Traditional Fortran does not standardise which kinds are
available, and so this may vary from compiler to compiler and from machine to
machine. When Fortran was invented, number representations were much less
standardised than today, and so the language designers left it to the
implementation to avoid making the language impossible to implement on
particular hardware.

Sincle the libmuscle API uses integers and floating point numbers all over the
place, we need to be able to declare these kinds. Also, the type and/or kind
sometimes shows up in a function name, so we need some consistent naming to
avoid confusion.

This is complicated somewhat by the lack of guarantees on which types will be
available. However, these days, all hardware that is relevant to MUSCLE 3 uses
two's complement integers with sizes of 8, 16, 32 and 64 bits, and IEEE 754
floating point numbers using 32 and 64-bit precision. So we can standardise on
these without excluding anyone.

In many compilers, integer types of size n bytes can be written ``integer*n``.
This is not standard however, so it's not guaranteed to work. In Fortran 2003,
a standardised way of selecting a kind with at least a given precision became
available in the form of the ``selected_int_kind`` and ``selected_real_kind``
functions. These work, but they're a pain to write out all the time.

So, for each of the above mentioned integer and floating point types, libmuscle
has a unique name, which is used in function names, and a parameter using the
same name which defines the corresponding kind. You can use these to declare
variables which you use with the libmuscle API, or you can write the same
type/kind in another way that your compiler supports and it should work as well.
The names and types are as follows:

+---------+-----------------+----------------------------------------+
|  Name   | Kind parameter  | Description                            |
+=========+=================+========================================+
|  int1   | LIBMUSCLE_int1  | 8-bit signed 2's complement integer.   |
+---------+-----------------+----------------------------------------+
|  int2   | LIBMUSCLE_int2  | 16-bit signed 2's complement integer.  |
+---------+-----------------+----------------------------------------+
|  int4   | LIBMUSCLE_int4  | 32-bit signed 2's complement integer.  |
+---------+-----------------+----------------------------------------+
|  int8   | LIBMUSCLE_int8  | 64-bit signed 2's complement integer.  |
+---------+-----------------+----------------------------------------+
| integer |                 | Default integer.                       |
+---------+-----------------+----------------------------------------+
|  size   | LIBMUSCLE_size  | Used for array indiced and sizes.      |
+---------+-----------------+----------------------------------------+
|  real4  | LIBMUSCLE_real4 | 32-bit IEEE 754 floating point.        |
+---------+-----------------+----------------------------------------+
|  real8  | LIBMUSCLE_real8 | 64-bit IEEE 754 floating point.        |
+---------+-----------------+----------------------------------------+

As said above, if you are used to ``integer*n`` and ``real*n`` style types, then
you can use those, using e.g. ``integer*2`` where the API expects a
``LIBMUSCLE_int2``. For ``LIBMUSCLE_size``, ``integer*8`` will probably work,
otherwise try ``integer*4``.


Namespace LIBMUSCLE
-------------------

.. f:module:: libmuscle
    :synopsis: Fortran module for libmuscle

.. f:currentmodule:: libmuscle

LIBMUSCLE_Data
``````````````
.. f:type:: LIBMUSCLE_Data

    Represents a libmuscle Data object. This is an opaque object that may be
    returned from and passed to libmuscle functions, but does not contain any
    directly accessible members.

    With respect to creation, assignment and copying, :f:type:`LIBMUSCLE_Data`
    objects act like Python objects: basic values (logicals, strings, integers
    and reals) get copied, while for lists, dictionaries, and byte arrays, the
    variable contains a reference which gets copied.

.. f:type:: LIBMUSCLE_DataConstRef

    Represents a read-only reference to a libmuscle Data object. This is an
    opaque object like :f:type:`LIBMUSCLE_Data`. DataConstRef objects work
    exactly the same as Data objects, except that the names of the corresponding
    functions start with ``LIBMUSCLE_DataConstRef``, and that only creation,
    freeing, and non-modifying operations are supported. Since these functions
    are otherwise identical, they are not documented separately here. If you
    want to know how to use say ``LIBMUSCLE_DataConstRef_as_int8``, look
    up :f:func:`LIBMUSCLE_Data_as_int8`.

    This class is mainly used to represent received messages, which should not
    be modified.

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
    the default ``integer`` kind, and ``LIBMUSCLE_intN`` with N set to 1, 2, 4
    or 8. See the note at the top of this page for more on integer types in
    libmuscle.

    Note that while libmuscle supports unsigned integers, these don't exist
    in Fortran. They will be mapped to the corresponding signed type, which
    may cause a silent overflow if the number is out of the signed type's
    range.

    :p integer value: The value to represent (see above).
    :r obj: The new Data object
    :rtype obj: LIBMUSCLE_Data

.. f:function:: LIBMUSCLE_Data_create(value)

    Creates a Data object representing a real value. Supported kinds are
    ``LIBMUSCLE_real4`` and ``LIBMUSCLE_real8``. See the note at the top of this
    page for more on real types in libmuscle.

    :p real value: The value to represent.
    :r obj: The new Data object
    :rtype obj: LIBMUSCLE_Data

.. f:function:: LIBMUSCLE_Data_create(value)

    Creates a Data object containing a :f:type:`YMMSL_Settings` object.

    :p YMMSL_Settings value: The Settings value to represent.
    :r obj: The new Data object.
    :rtype obj: LIBMUSCLE_Data

.. f:function:: LIBMUSCLE_Data_create_grid(data_array)

    Creates a Data object containing a grid (array).

    The argument must be an array of type ``logical`` and default kind,
    an array of type ``integer`` and kind ``LIBMUSCLE_int4`` or
    ``LIBMUSCLE_int8``, or an array of type ``real`` and kind
    ``LIBMUSCLE_real4`` or kind ``LIBMUSCLE_real8``.

    Grids created with this function have no index names.

    :p array data_array: The array of data to represent.
    :r obj: The new Data object.
    :rtype obj: LIBMUSCLE_Data

.. f:function:: LIBMUSCLE_Data_create_grid(data_array, index_name, ...)

    Creates a Data object containing a grid (array).

    The ``data_array`` argument must be an array of type ``logical`` and
    default kind, an array of type ``integer`` and kind ``LIBMUSCLE_int4``
    or ``LIBMUSCLE_int8``, or an array of type ``real`` and kind
    ``LIBMUSCLE_real4`` or kind ``LIBMUSCLE_real8``.

    If an ``n``-dimensional array is passed as the first argument, then
    there must be ``n`` additional arguments of type ``character``, giving
    the names of the indexes in order. For instance, if your 2D array
    represents a table and you index it ``data_array(row, column)`` then
    ``"row"`` and ``"column"`` would be reasonable index names here. Note
    that MUSCLE 3 does not use these names, they are here to make it
    easier to understand the message on the receiver side, or if it is
    saved and analysed later.

    :p array data_array: The array of data to represent.
    :p character index_name: The names of the grid's indexes.
    :r obj: The new Data object.
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

    :p integer size: The number of nil values to put into the list
        (kind=LIBMUSCLE_size).
    :r obj: The new Data object
    :rtype obj: LIBMUSCLE_Data

.. f:function:: LIBMUSCLE_Data_create_byte_array(size)

    Creates a Data object containing a byte array of the given number of bytes.

    :p integer size: The number of bytes to allocate for the array
            (LIBMUSCLE_size).
    :r obj: The new Data object.
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

    This frees the resources associated with the given Data object. Do not use
    the object for anything after calling this, because it will be invalid.

    :p LIBMUSCLE_Data self: The Data object to free.

.. f:subroutine:: LIBMUSCLE_Data_set(self, value)

    Assigns the value of Data object ``value`` to Data object ``self``. Both
    ``value`` and ``self`` must have a value (nil is okay, but an uninitialised
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

.. f:function:: LIBMUSCLE_Data_is_a_logical(self)

    Determine whether the Data object contains a logical (boolean) value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a logical value.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_character(self)

    Determine whether the Data object contains a character (string) value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a character value.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_int(self)

    Determine whether the Data object contains an integer value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains an integer value.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_int1(self)

    Determine whether the Data object contains an integer value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains an integer value.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_int2(self)

    Determine whether the Data object contains an integer value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains an integer value.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_int4(self)

    Determine whether the Data object contains an integer value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains an integer value.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_real4(self)

    Determine whether the Data object contains a single precision floating
    point value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a single precision float value.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_real8(self)

    Determine whether the Data object contains a double precision floating
    point value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a double precision float value.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_settings(self)

    Determine whether the Data object contains a Settings value.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a Settings value.
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

.. f:function:: LIBMUSCLE_Data_is_a_grid_of_logical(self)

    Determine whether the Data object contains a grid of logical values.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a grid of logical.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_grid_of_int4(self)

    Determine whether the Data object contains a grid of integer values
    of kind ``LIBMUSCLE_int4``.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a grid of int4.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_grid_of_int8(self)

    Determine whether the Data object contains a grid of integer values
    of kind ``LIBMUSCLE_int8``.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a grid of int8.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_grid_of_real4(self)

    Determine whether the Data object contains a grid of real values
    of kind ``LIBMUSCLE_real4``.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a grid of real4.
    :rtype is: logical

.. f:function:: LIBMUSCLE_Data_is_a_grid_of_real8(self)

    Determine whether the Data object contains a grid of real8 values
    of kind ``LIBMUSCLE_real8``.

    :p LIBMUSCLE_Data self: The Data object to inspect.
    :r is: True if the object contains a grid of real8.
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
    :rtype size: integer (kind=LIBMUSCLE_size)

.. f:function:: LIBMUSCLE_Data_as_logical(self, err_code, err_msg)

    Access a logical value.

    You can use :f:func:`LIBMUSCLE_Data_is_a_logical` to ascertain that the Data
    object contains a logical value.

    If the Data object does not contain a logical (boolean) value, then an error
    message will be printed and execution will be halted.

    Alternatively, you can pass an argument for ``err_code``, or for both
    ``err_code`` and ``err_msg``, to catch the error.

    If ``err_code`` equals ``LIBMUSCLE_success`` after the call, then the
    returned value is the logical value held in this Data object. If it equals
    ``LIBMUSCLE_runtime_error``, the Data value did not contain a logical
    (boolean) value. If you passed an ``err_msg`` argument as well, then the
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
        val = LIBMUSCLE_Data_as_logical(mydata)
        ! val equals .true. here
        ! Attempt to (incorrectly) retrieve a character value
        str = LIBMUSCLE_Data_as_character(mydata, err_code, err_msg)
        if (err_code .ne. LIBMUSCLE_success) then
            print *, err_msg
            ! Need to free the memory if an error message was returned
            deallocate(err_msg)
        end if
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    :p LIBMUSCLE_Data self: The Data object to get a logical value out of.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: logical

.. f:function:: LIBMUSCLE_Data_as_character(self, err_code, err_msg)

    Access a character (string) value.

    You can use :f:func:`LIBMUSCLE_Data_is_a_character` to ascertain that the
    Data object contains a character value.

    If the Data object does not contain a character (string) value, then an
    error message will be printed and execution will be halted.

    Alternatively, you can pass an argument for ``err_code``, or for both
    ``err_code`` and ``err_msg``, to catch the error.

    If ``err_code`` equals ``LIBMUSCLE_success`` after the call, then the
    returned value is the character value held in this Data object. If it equals
    ``LIBMUSCLE_runtime_error``, the Data value did not contain a character
    (string) value. If you passed an ``err_msg`` argument as well, then the
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

        ! Create a data object containing a character value
        mydata = LIBMUSCLE_Data_create('Example')
        ! Retrieve the value
        str = LIBMUSCLE_Data_as_character(mydata)
        ! Free the retrieved copy of the character
        deallocate(str)
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    See :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

    :p LIBMUSCLE_Data self The Data object to get a character out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: character(len=:), allocatable

.. f:function:: LIBMUSCLE_Data_as_int(self, err_code, err_msg)

    Access an integer value of default kind.

    You can use :f:func:`LIBMUSCLE_Data_is_a_int` to ascertain that the Data
    object contains a default integer value.

    If the Data object does not contain an integer value, then an error
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

    See :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

    :p LIBMUSCLE_Data self The Data object to get an integer value out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: integer

.. f:function:: LIBMUSCLE_Data_as_int1(self, err_code, err_msg)

    Access an int value that fits in 8 bits.

    You can use :f:func:`LIBMUSCLE_Data_is_a_int1` to ascertain that the Data
    object contains an ``int1`` value.

    If the Data object does not contain a ``LIBMUSCLE_int1`` (integer with
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
        integer(kind=LIBMUSCLE_int1) :: number

        ! Create a data object containing an integer value
        mydata = LIBMUSCLE_Data_create(42_LIBMUSCLE_int1)
        ! Retrieve the value
        number = LIBMUSCLE_Data_as_int1(mydata)
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    See :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

    :p LIBMUSCLE_Data self The Data object to get an integer value out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: integer(kind=LIBMUSCLE_int1)

.. f:function:: LIBMUSCLE_Data_as_int2(self, err_code, err_msg)

    Access an int value that fits in 16 bits.

    You can use :f:func:`LIBMUSCLE_Data_is_a_int2` to ascertain that the Data
    object contains an integer value.

    If the Data object does not contain a ``LIBMUSCLE_int2`` (integer with
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
        integer(kind=LIBMUSCLE_int2) :: number

        ! Create a data object containing an integer value
        mydata = LIBMUSCLE_Data_create(4242_LIBMUSCLE_int2)
        ! Retrieve the value
        number = LIBMUSCLE_Data_as_int2(mydata)
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    See :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

    :p LIBMUSCLE_Data self The Data object to get an integer value out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: integer(kind=LIBMUSCLE_int2)

.. f:function:: LIBMUSCLE_Data_as_int4(self, err_code, err_msg)

    Access an integer value.

    You can use :f:func:`LIBMUSCLE_Data_is_a_int4` to ascertain that the Data
    object contains an integer value of kind ``LIBMUSCLE_int4``.

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
        integer(LIBMUSCLE_int4) :: number

        ! Create a data object containing an integer value
        mydata = LIBMUSCLE_Data_create(42424242_LIBMUSCLE_int4)
        ! Retrieve the value
        number = LIBMUSCLE_Data_as_int4(mydata)
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    See :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

    :p LIBMUSCLE_Data self The Data object to get an integer value out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: integer(LIBMUSCLE_int4)

.. f:function:: LIBMUSCLE_Data_as_int8(self, err_code, err_msg)

    Access an integer value of kind ``LIBMUSCLE_int8``..

    You can use :f:func:`LIBMUSCLE_Data_is_a_int8` to ascertain that the Data
    object contains a 64-bit integer value.

    If the Data object does not contain a ``LIBMUSCLE_int8`` (integer with
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
        integer(kind=LIBMUSCLE_int8) :: number

        ! Create a data object containing an integer value
        mydata = LIBMUSCLE_Data_create(123456789123456789_LIBMUSCLE_int8)
        ! Retrieve the value
        number = LIBMUSCLE_Data_as_int8(mydata)
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    See :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

    :p LIBMUSCLE_Data self: The Data object to get an integer value out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: integer(kind=LIBMUSCLE_int8)

.. f:function:: LIBMUSCLE_Data_as_real4(self, err_code, err_msg)

    Access a single-precision (4 byte) real value.

    You can use :f:func:`LIBMUSCLE_Data_is_a_real4` to ascertain that the Data
    object contains a single-precision real value.

    If the Data object does not contain a ``LIBMUSCLE_real4`` (real with
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
        real(kind=LIBMUSCLE_real4) :: number

        ! Create a data object containing a real value
        mydata = LIBMUSCLE_Data_create(42.0)
        ! Retrieve the value
        number = LIBMUSCLE_Data_as_real4(mydata)
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    See :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

    :p LIBMUSCLE_Data self: The Data object to get a single-precision real
            value out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: real(kind=LIBMUSCLE_real4)

.. f:function:: LIBMUSCLE_Data_as_real8(self, err_code, err_msg)

    Access a double-precision (8 byte) real value.

    You can use :f:func:`LIBMUSCLE_Data_is_a_real8` to ascertain that the Data
    object contains a double-precision real value.

    If the Data object does not contain a ``LIBMUSCLE_real8`` (real with
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
        real(kind=LIBMUSCLE_real8) :: number

        ! Create a data object containing a real value
        mydata = LIBMUSCLE_Data_create(42.0d0)
        ! Retrieve the value
        number = LIBMUSCLE_Data_as_real8(mydata)
        ! Free the data object
        call LIBMUSCLE_Data_free(mydata)

    See :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

    :p LIBMUSCLE_Data self: The Data object to get a double-precision real value
            out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: real(kind=LIBMUSCLE_real8)

.. f:function:: LIBMUSCLE_Data_as_settings(self, err_code, err_msg)

    Access a :f:type:`YMMSL_Settings` value.

    You can use :f:func:`LIBMUSCLE_Data_is_a_settings` to ascertain that the
    Data object contains a Settings-type value.

    If the Data object does not contain a :f:type:`YMMSL_Settings` value, then
    an error message will be printed and execution will be halted.

    Alternatively, you can pass an argument for ``err_code``, or for both
    ``err_code`` and ``err_msg``, to catch the error.

    If ``err_code`` equals ``LIBMUSCLE_success`` after the call, then the
    returned value is the value held in this Data object. If it equals
    ``LIBMUSCLE_runtime_error``, the Data value did not contain a Settings
    value. If you passed an ``err_msg`` argument as well, then the passed
    variable will contain an appropriate error message in case of error, and
    needs to be deallocated (using ``deallocate()``) when you're done with it.

    Example:

    .. code-block:: fortran

        type(LIBMUSCLE_Data) :: mydata
        type(YMMSL_Settings) :: settings1, settings2

        ! Create a Settings object
        settings1 = YMMSL_Settings_create()
        ! Create a data object containing the Settings value
        mydata = LIBMUSCLE_Data_create(settings1)
        ! Retrieve the value
        settings2 = LIBMUSCLE_Data_as_settings(mydata)
        ! Free the data object and the settings objects
        call YMMSL_Settings_free(settings1)
        call YMMSL_Settings_free(settings2)
        call LIBMUSCLE_Data_free(mydata)

    See :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

    :p LIBMUSCLE_Data self: The Data object to get a Settings value out of.
    :p integer err_code: An error code output (optional)
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value.
    :rtype value: type(YMMSL_Settings)

.. f:subroutine:: LIBMUSCLE_Data_as_byte_array(self, buf, err_code, err_msg)

    Access a byte array value by copying it into ``buf``.

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
    :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

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

        type(LIBMUSCLE_Data) :: d1, d2

        d1 = LIBMUSCLE_Data_create_nils(10_LIBMUSCLE_size)
        d2 = LIBMUSCLE_Data_get_item(d1, 5_LIBMUSCLE_size)
        ! LIBMUSCLE_Data_is_nil(d2) returns .true. here
        call LIBMUSCLE_Data_free(d2)
        call LIBMUSCLE_Data_free(d1)

    See :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

    :p LIBMUSCLE_Data self: The Data object to get an item out of.
    :p integer i: The index to get the value at, in range [1..size]
            (kind=LIBMUSCLE_size)
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
        s1 = LIBMUSCLE_Data_as_character(d3)
        print *, s1     ! prints 'value1'
        deallocate(s1)
        call LIBMUSCLE_Data_free(d3)
        call LIBMUSCLE_Data_free(d2)
        call LIBMUSCLE_Data_free(d1)

    See :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

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
    :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

    :p LIBMUSCLE_Data self: The Data object to set an item value on.
    :p integer i: The position to set the value for, in range [1..size]
            (kind=LIBMUSCLE_size).
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
    :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

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
        integer (kind=LIBMUSCLE_size) :: i
        integer intval

        d1 = LIBMUSCLE_Data_create_dict()
        call LIBMUSCLE_Data_set_item(d1, 'key1', 'value1')
        call LIBMUSCLE_Data_set_item(d1, 'key2', 'value2')

        do i = 1, LIBMUSCLE_Data_size(d1)
            key = LIBMUSCLE_Data_key(d1, i)
            val = LIBMUSCLE_Data_value(d1, i)
            cval = LIBMUSCLE_Data_as_character(val)
            print '(a8, a8)', key, cval
            deallocate(key)
            deallocate(cval)
            LIBMUSCLE_Data_free(val)
        end do

        call LIBMUSCLE_Data_free(d1)

    :p LIBMUSCLE_Data self: The Data object to get a key for.
    :p integer i: The index of the key to retrieve (LIBMUSCLE_size)
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
    :p integer i: The index of the key to retrieve (LIBMUSCLE_size)
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value at the given index
    :rtype value: LIBMUSCLE_Data

.. f:function:: LIBMUSCLE_Data_num_dims(self, err_code, err_msg)

    Get the number of dimensions of a grid-valued Data object.

    This function is only valid for Data objects containing a grid. You
    can use :f:func:`LIBMUSCLE_Data_is_a_grid_of_logical` and similar
    functions to check that it is a grid. If the Data object does not
    contain a grid, ``err_code`` will be set to
    ``LIBMUSCLE_runtime_error``.

    :p LIBMUSCLE_Data self: The Data object to get the number of
            dimensions for.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r num_dims: The number of dimensions
    :rtype num_dims: integer (LIBMUSCLE_size)

.. f:subroutine:: LIBMUSCLE_Data_shape(self, shp, err_code, err_msg)

    Get the shape of the array of a grid-valued Data object.

    The array passed to receive the shape must be one-dimensional, and
    at least of length `n`, where `n` is the number of dimensions of
    the grid.

    This function is only valid for Data objects containing a grid. You
    can use :f:func:`LIBMUSCLE_Data_is_a_grid_of_logical` and similar
    functions to check that it is a grid. If the Data object does not
    contain a grid, ``err_code`` will be set to
    ``LIBMUSCLE_runtime_error``.

    :p LIBMUSCLE_Data self: The data object to get the shape of.
    :p integer shp: A 1D array of integer (LIBMUSCLE_size) to put the
            shape into (intent (out)).
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).

.. f:function:: LIBMUSCLE_Data_has_indexes(self, err_code, err_msg)

    Check whether a grid has index names.

    Returns ``.true.`` if the grid has index names, ``.false.`` otherwise.

    This function is only valid for Data objects containing a grid. You
    can use :f:func:`LIBMUSCLE_Data_is_a_grid_of_logical` and similar
    functions to check that it is a grid. If the Data object does not
    contain a grid, ``err_code`` will be set to
    ``LIBMUSCLE_runtime_error``.

    :p LIBMUSCLE_Data self: The data object to check for indexes.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r has_indexes: Whether there are indexes.
    :rtype has_indexes: logical

.. f:function:: LIBMUSCLE_Data_index(self, i, err_code, err_msg)

    Return the name of the i'th index.

    The value of ``i`` ranges from 1 to the number of dimensions.

    This function is only valid for Data objects containing a grid. You
    can use :f:func:`LIBMUSCLE_Data_is_a_grid_of_logical` and similar
    functions to check that it is a grid. If the Data object does not
    contain a grid, ``err_code`` will be set to
    ``LIBMUSCLE_runtime_error``. If the index is zero, negative, or
    larger than the number of dimensions, ``err_code`` will be set to
    ``LIBMUSCLE_out_of_range``.

    :p LIBMUSCLE_Data self: The data object to get the index of.
    :p integer i: The index of the index to get the name of (LIBMUSCLE_size).
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r index_name: The name of the index (allocatable)
    :rtype index_name: logical



LIBMUSCLE_Message
`````````````````
.. f:type:: LIBMUSCLE_Message

    Represents a message to be sent or that has been received.

    Messages have four attributes: A timestamp, an optional next timestamp,
    some data, and optional overlay settings.

    The timestamp holds the simulation time (not wallclock time) to which the
    data in this message corresponds. If a next timestamp is set, then that
    represents the simulation time of the next timestap of the model that
    generated the message. The data is the content of the message, and is
    model-specific. Overlay settings may be passed along with a message, and
    will be overlaid onto the receiving model's settings; this is normally only
    used by special simulation components.

.. f:function:: LIBMUSCLE_Message_create(timestamp, data)

    Create a new Message object.

    :p LIBMUSCLE_real8 timestamp: The simulated time to which the data in this
            message applies.
    :p LIBMUSCLE_Data data: An object to send or that was received

.. f:function:: LIBMUSCLE_Message_create(timestamp, next_timestamp, data)

    Create a new Message object.

    :p LIBMUSCLE_real8 timestamp: The simulated time to which the data in this
            message applies.
    :p LIBMUSCLE_real8 next_timestamp: Simulation time of the next message to
            be transmitted.
    :p LIBMUSCLE_Data data: An object to send or that was received

.. f:function:: LIBMUSCLE_Message_create(timestamp, data, settings)

    Create a new Message object.

    :p LIBMUSCLE_real8 timestamp: The simulated time to which the data in this
            message applies.
    :p LIBMUSCLE_Data data: An object to send or that was received
    :p YMMSL_Settings settings: Overlay settings to send or that were received.

.. f:function:: LIBMUSCLE_Message_create(timestamp, next_timestamp, data, settings)

    Create a new Message object.

    :p LIBMUSCLE_real8 timestamp: The simulated time to which the data in this
            message applies.
    :p LIBMUSCLE_real8 next_timestamp: Simulation time of the next message to
            be transmitted.
    :p LIBMUSCLE_Data data: An object to send or that was received
    :p YMMSL_Settings settings: Overlay settings to send or that were received.

.. f:function:: LIBMUSCLE_Message_timestamp(self)

    Returns the timestamp associated with the message.

    This is the simulated time to which the data in this message applies.

    :r timestamp: The timestamp.
    :rtype timestamp: LIBMUSCLE_real8

.. f:subroutine:: LIBMUSCLE_Message_set_timestamp(self, timestamp)

    Sets the timestamp associated with this message.

    This should be the simulated time to which the data in this message applies.

    :p LIBMUSCLE_Message self: The Message object to modify.
    :p timestamp: The timestamp to set.

.. f:function:: LIBMUSCLE_Message_has_next_timestamp(self)

    Returns whether the message has a next timestamp set.

    :p LIBMUSCLE_Message self: The Message object to inspect.
    :r has_next_timestamp: ``.true.`` if there's a next timestamp.
    :rtype has_next_timestamp: logical

.. f:function:: LIBMUSCLE_Message_next_timestamp(self)

    Returns the message's next timestamp.

    Only call if :f:func:`LIBMUSCLE_Message_has_next_timestamp` returns
    ``.true.``.

    :p LIBMUSCLE_Message self: The Message object to inspect.
    :r next_timestamp: The next timestamp for this message.
    :rtype next_timestamp: LIBMUSCLE_real8

.. f:subroutine:: LIBMUSCLE_Message_set_next_timestamp(self, timestamp)

    Sets the next timestamp associated with this message.

    This should be the simulated time of the next timestep of the model.

    :p LIBMUSCLE_Message self: The Message object to modify.
    :p timestamp: The timestamp to set.

.. f:subroutine:: LIBMUSCLE_Message_unset_next_timestamp(self)

    Unsets the next timestamp associated with this message.

    After calling this, :f:func:`LIBMUSCLE_Message_has_next_timestamp` will
    return ``.false.``.

    :p LIBMUSCLE_Message self: The Message object to modify.

.. f:function:: LIBMUSCLE_Message_get_data(self)

    Returns the data contained in the message.

    :p LIBMUSCLE_Message self: The Message object to inspect.
    :r data: The data contained in this message
    :rtype data: LIBMUSCLE_DataConstRef

.. f:subroutine:: LIBMUSCLE_Message_set_data(self, data)

    Sets the data contained by the message.

    Note that this will not transfer ownership of the data object, you still
    need to free it.

    :p LIBMUSCLE_Message self: The Message object to modify.
    :p LIBMUSCLE_Data data: The data object to take the value from.

.. f:subroutine:: LIBMUSCLE_Message_set_data(self, data)

    Sets the data contained by the message.

    Note that this will not transfer ownership of the data object, you still
    need to free it.

    :p LIBMUSCLE_Message self: The Message object to modify.
    :p LIBMUSCLE_DataConstRef data: The data object to take the value from.

.. f:function:: LIBMUSCLE_Message_has_settings(self)

    Returns whether the message has an associated Settings object.

    :p LIBMUSCLE_Message self: The Message object to inspect.
    :r has: ``.true.`` iff the message has settings.
    :rtype has: LIBMUSCLE_DataConstRef

.. f:function:: LIBMUSCLE_Message_get_settings(self)

    Returns the message's associated Settings object.

    Only call if :f:func:`LIBMUSCLE_Message_has_settings` returns ``.true.``.

    :p LIBMUSCLE_Message self: The Message object to inspect.
    :r settings: (A copy of) the associated settings object.
    :rtype settings: YMMSL_Settings

.. f:subroutine:: LIBMUSCLE_Message_set_settings(self, settings)

    Sets the message's associated Settings object.

    If the message has settings already, then they will be replaced by the new
    settings. After calling this, :f:func:`LIBMUSCLE_Message_has_settings` will
    return ``.true.``.

    :p LIBMUSCLE_Message self: The Message object to modify.
    :p YMMSL_Settings settings: The new settings.

.. f:subroutine:: LIBMUSCLE_Message_unset_settings(self)

    Removes any associated settings object from the message.

    This may be called whether the message currently has associated settings or
    not. After calling this function, :f:func:`LIBMUSCLE_Message_has_settings`
    will return ``.false.``.

    :p LIBMUSCLE_Message self: The Message object to modify.

LIBMUSCLE_PortsDescription
``````````````````````````
.. f:type:: LIBMUSCLE_PortsDescription

    Describes the ports of a component.

    This data structure is passed to libmuscle to describe how a
    component connects to the outside world, or it can be
    obtained from libmuscle in order to find out how a component
    with flexible ports was used.

    A PortsDescription contains a list of port names for each
    :f:type:`YMMSL_Operator`.

.. f:function:: LIBMUSCLE_PortsDescription_create()

    Create a PortsDescription containing no port names.

    :r ports_description: A new PortsDescription object.
    :rtype ports_description: LIBMUSCLE_PortsDescription

.. f:subroutine:: LIBMUSCLE_PortsDescription_free(self)

    Frees a PortsDescription object.

    This deallocates all resources associated with the object, and
    should be called for every PortsDescription object when you're
    done using it.

    :p LIBMUSCLE_PortsDescription self: The object to free.

.. f:subroutine:: LIBMUSCLE_PortsDescription_add(self, operator, port)

    Add a port name to a PortsDescription object.

    :p LIBMUSCLE_PortsDescription self: The object to modify.
    :p YMMSL_Operator operator: The operator under which to put the port.
    :p character port: The name of the port to add.

.. f:function:: LIBMUSCLE_PortsDescription_num_ports(self, operator)

    Get the number of ports in this object for the given operator.

    :p LIBMUSCLE_PortsDescription self: The object to inspect.
    :p YMMSL_Operator operator: A chosen operator.
    :r num_ports: The number of ports for this operator (of kind
            LIBMUSCLE_size).
    :rtype num_ports: integer

.. f:function:: LIBMUSCLE_PortsDescription_get(self, operator, i)

    Get the i'th port name for the given operator.

    Parameter ``i`` must be in the range 1..num_ports inclusive, where
    num_ports is the result of calling
    :f:func:`LIBMUSCLE_PortsDescription_num_ports` with the same
    object and operator.

    :p LIBMUSCLE_PortsDescription self: The object to inspect.
    :p YMMSL_Operator operator: A chosen operator.
    :r port_name: The name of the given port.
    :rtype port_name: character

LIBMUSCLE_Instance
``````````````````````````
.. f:type:: LIBMUSCLE_Instance

    The Instance class represents a component instance in a
    MUSCLE3 simulation. This class provides a low-level
    send/receive API for the instance to use.

.. f:function:: LIBMUSCLE_Instance_create()

    Create a new Instance object with ports from the configuration.

    For MPI-based components, this will have libmuscle_mpi use a duplicate of
    ``MPI_COMM_WORLD`` to communicate, and the designated root process will be
    that with rank 0.

    This object must be freed when you're done with it using
    :f:func:`LIBMUSCLE_Instance_free`.

    :r instance: The newly created instance object.
    :rtype instance: LIBMUSCLE_Instance

.. f:function:: LIBMUSCLE_Instance_create(ports)

    Create a new Instance object with the given ports.

    For MPI-based components, this will have libmuscle_mpi use a duplicate
    of ``MPI_COMM_WORLD`` to communicate, and the designated root process will
    be that with rank 0.

    This object must be freed when you're done with it using
    :f:func:`LIBMUSCLE_Instance_free`.

    :p LIBMUSCLE_PortsDescription ports: The ports of the new instance.
    :r instance: The newly created instance object.
    :rtype instance: LIBMUSCLE_Instance

.. f:function:: LIBMUSCLE_Instance_create(communicator, root)

    Create a new Instance object for MPI with ports from the configuration.

    For MPI-based components, an MPI communicator and a root rank may be
    passed. The communicator must contain all processes in this instance, and
    ``root`` must be the rank of one of them. MUSCLE will create a duplicate of
    this communicator for its own use. Creating a :f:type:`LIBMUSCLE_Instance`
    for an MPI component is a collective operation, so it must be done in
    all processes simultaneously, with the same communicator and the same root.

    This object must be freed when you're done with it using
    :f:func:`LIBMUSCLE_Instance_free`.

    :p integer communicator: MPI communicator to use (optional, default
            MPI_COMM_WORLD).
    :p integer root: Rank of the root process (optional, default 0).
    :r instance: The newly created instance object.
    :rtype instance: LIBMUSCLE_Instance

.. f:function:: LIBMUSCLE_Instance_create(ports, communicator, root)

    Create a new Instance object for MPI with the given ports.

    For MPI-based components, an MPI communicator and a root rank may be
    passed. The communicator must contain all processes in this instance, and
    ``root`` must be the rank of one of them. MUSCLE will create a duplicate of
    this communicator for its own use. Creating a :f:type:`LIBMUSCLE_Instance`
    for an MPI component is a collective operation, so it must be done in
    all processes simultaneously, with the same communicator and the same root.

    This object must be freed when you're done with it using
    :f:func:`LIBMUSCLE_Instance_free`.

    :p LIBMUSCLE_PortsDescription ports: The ports of the new instance.
    :p integer communicator: MPI communicator to use (optional, default
            MPI_COMM_WORLD).
    :p integer root: Rank of the root process (optional, default 0).
    :r instance: The newly created instance object.
    :rtype instance: LIBMUSCLE_Instance

.. f:subroutine:: LIBMUSCLE_Instance_free(self)

    Free resources associated with the given Instance object.

    :p LIBMUSCLE_Instance self: The object to free.

.. f:function:: LIBMUSCLE_Instance_reuse_instance(self)

    Checks whether to reuse this instance.

    This method must be called at the beginning of the reuse loop, i.e. before
    the F_INIT operator, and its return value should decide whether to enter
    that loop again.

    MPI-based components must execute the reuse loop in each process in
    parallel, and call this function at the top of the reuse loop in each
    process.

    :p LIBMUSCLE_Instance self: The object to check for reuse.
    :r reuse: Whether to enter the reuse loop another time.
    :rtype reuse: logical

.. f:function:: LIBMUSCLE_Instance_reuse_instance(self, apply_overlay)

    Checks whether to reuse this instance.

    This method must be called at the beginning of the reuse loop, i.e. before
    the F_INIT operator, and its return value should decide whether to enter
    that loop again.

    This version of this function lets you choose whether to apply the received
    settings overlay or to return it with the message. If you're going to use
    :f:func:`LIBMUSCLE_Instance_receive_with_settings` on your F_INIT ports, set
    this to ``.false.``. If you don't know what that means, just call
    ``LIBMUSCLE_Instance_reuse_instance()`` with no arguments and all will be
    fine. If it turns out that you did need to specify ``.false.`` here, MUSCLE
    3 will tell you in an error message, and you can add it.

    :p LIBMUSCLE_Instance self: The object to check for reuse.
    :p logical apply_overlay: Whether to apply the received settings overlay.
    :r reuse: Whether to enter the reuse loop another time.
    :rtype reuse: logical

.. f:subroutine:: LIBMUSCLE_Instance_error_shutdown(self, message)

    Logs an error and shuts down the Instance.

    If you detect that something is wrong and want to stop this instance, then
    you should call this function to shut down the instance before stopping the
    program. This makes debugging easier.

    MPI-based components may either call this function in all processes,
    or only in the root process (as passed to the constructor).

    :p LIBMUSCLE_Instance self: The instance to shut down.
    :p character message: An error message describing the problem encountered.

.. f:function:: LIBMUSCLE_Instance_is_setting_a_character(self, name, err_code, err_msg)

    Returns whether the setting is of type character.

    If no setting with the given name exists, ``err_code`` will be set to
    ``LIBMUSCLE_out_of_range``. See :f:func:`LIBMUSCLE_Data_as_logical` for an
    example of error handling.

    MPI-based components may call this function at any time within the reuse
    loop, in any or all processes, simultaneously or not.

    :p LIBMUSCLE_Instance self: The instance to get the setting from.
    :p character name: The name of the setting to inspect.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r is_character: .true. if the setting is of character type.
    :rtype is_character: logical

.. f:function:: LIBMUSCLE_Instance_is_setting_a_int8(self, name, err_code, err_msg)

    Returns whether the setting is of type integer.

    If no setting with the given name exists, ``err_code`` will be set to
    ``LIBMUSCLE_out_of_range``. See :f:func:`LIBMUSCLE_Data_as_logical` for an
    example of error handling.

    MPI-based components may call this function at any time within the
    reuse loop, in any or all processes, simultaneously or not.

    :p LIBMUSCLE_Instance self: The instance to get the setting from.
    :p character name: The name of the setting to inspect.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r is_int8: .true. if the setting is of integer type.
    :rtype is_int8: logical

.. f:function:: LIBMUSCLE_Instance_is_setting_a_real8(self, name, err_code, err_msg)

    Returns whether the setting is of type real.

    If no setting with the given name exists, ``err_code`` will be set to
    ``LIBMUSCLE_out_of_range``. See :f:func:`LIBMUSCLE_Data_as_logical` for an
    example of error handling.

    MPI-based components may call this function at any time within the
    reuse loop, in any or all processes, simultaneously or not.

    :p LIBMUSCLE_Instance self: The instance to get the setting from.
    :p character name: The name of the setting to inspect.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r is_real8: .true. if the setting is of real type.
    :rtype is_real8: logical

.. f:function:: LIBMUSCLE_Instance_is_setting_a_logical(self, name, err_code, err_msg)

    Returns whether the setting is of type logical.

    If no setting with the given name exists, ``err_code`` will be set to
    ``LIBMUSCLE_out_of_range``. See :f:func:`LIBMUSCLE_Data_as_logical` for an
    example of error handling.

    MPI-based components may call this function at any time within the
    reuse loop, in any or all processes, simultaneously or not.

    :p LIBMUSCLE_Instance self: The instance to get the setting from.
    :p character name: The name of the setting to inspect.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r is_logical: .true. if the setting is of logical type.
    :rtype is_logical: logical

.. f:function:: LIBMUSCLE_Instance_is_setting_a_real8array(self, name, err_code, err_msg)

    Returns whether the setting is a 1D array of real.

    If no setting with the given name exists, ``err_code`` will be set to
    ``LIBMUSCLE_out_of_range``. See :f:func:`LIBMUSCLE_Data_as_logical` for an
    example of error handling.

    MPI-based components may call this function at any time within the
    reuse loop, in any or all processes, simultaneously or not.

    :p LIBMUSCLE_Instance self: The instance to get the setting from.
    :p character name: The name of the setting to inspect.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r is_real8array: .true. if the setting is of real8array type.
    :rtype is_real8array: logical

.. f:function:: LIBMUSCLE_Instance_is_setting_a_real8array2(self, name, err_code, err_msg)

    Returns whether the setting is a 2D array of real.

    If no setting with the given name exists, ``err_code`` will be set to
    ``LIBMUSCLE_out_of_range``. See :f:func:`LIBMUSCLE_Data_as_logical` for an
    example of error handling.

    MPI-based components may call this function at any time within the
    reuse loop, in any or all processes, simultaneously or not.

    :p LIBMUSCLE_Instance self: The instance to get the setting from.
    :p character name: The name of the setting to inspect.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r is_real8array2: .true. if the setting is of real8array2 type.
    :rtype is_real8array2: logical

.. f:function:: LIBMUSCLE_Instance_get_setting_as_character(self, name, err_code, err_msg)

    Returns the value of a character-valued model setting.

    If no setting with the given name exists, ``err_code`` will be set to
    ``LIBMUSCLE_out_of_range``. If the value is not of type character, then
    ``err_code`` will be set to ``LIBMUSCLE_bad_cast``. See
    :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

    MPI-based components may call this function at any time within the
    reuse loop, in any or all processes, simultaneously or not.

    :p LIBMUSCLE_Instance self: The instance to get the setting from.
    :p character name: The name of the setting to retrieve.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The setting's value.
    :rtype value: character

.. f:function:: LIBMUSCLE_Instance_get_setting_as_int8(self, name, err_code, err_msg)

    Returns the value of an integer-valued model setting.

    If no setting with the given name exists, ``err_code`` will be set to
    ``LIBMUSCLE_out_of_range``. If the value is not of type integer, then
    ``err_code`` will be set to ``LIBMUSCLE_bad_cast``. See
    :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

    MPI-based components may call this function at any time within the
    reuse loop, in any or all processes, simultaneously or not.

    :p LIBMUSCLE_Instance self: The instance to get the setting from.
    :p character name: The name of the setting to retrieve.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The setting's value (kind=LIBMUSCLE_int8).
    :rtype value: integer

.. f:function:: LIBMUSCLE_Instance_get_setting_as_real8(self, name, err_code, err_msg)

    Returns the value of a real-valued model setting.

    If no setting with the given name exists, ``err_code`` will be set to
    ``LIBMUSCLE_out_of_range``. If the value is not of type integer, then
    ``err_code`` will be set to ``LIBMUSCLE_bad_cast``. See
    :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

    MPI-based components may call this function at any time within the
    reuse loop, in any or all processes, simultaneously or not.

    :p LIBMUSCLE_Instance self: The instance to get the setting from.
    :p character name: The name of the setting to retrieve.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The setting's value (kind=LIBMUSCLE_real8).
    :rtype value: real

.. f:function:: LIBMUSCLE_Instance_get_setting_as_logical(self, name, err_code, err_msg)

    Returns the value of a logical-valued model setting.

    If no setting with the given name exists, ``err_code`` will be set to
    ``LIBMUSCLE_out_of_range``. If the value is not of type integer, then
    ``err_code`` will be set to ``LIBMUSCLE_bad_cast``. See
    :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

    MPI-based components may call this function at any time within the
    reuse loop, in any or all processes, simultaneously or not.

    :p LIBMUSCLE_Instance self: The instance to get the setting from.
    :p character name: The name of the setting to retrieve.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The setting's value.
    :rtype value: logical

.. f:subroutine:: LIBMUSCLE_Instance_get_setting_as_real8array(self, name, value, err_code, err_msg)

    Returns the value of an array-of-real8-valued model setting.

    Note that there is currently no way to get the size of the array in advance.
    This feature is intended to be used for small fixed arrays, in which case
    the size will be known in advance to the programmer.

    If no setting with the given name exists, ``err_code`` will be set to
    ``LIBMUSCLE_out_of_range``. If the value is not a 1D array of real8, then
    ``err_code`` will be set to ``LIBMUSCLE_bad_cast``. See
    :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

    MPI-based components may call this function at any time within the
    reuse loop, in any or all processes, simultaneously or not.

    :p LIBMUSCLE_Instance self: The instance to get the setting from.
    :p character name: The name of the setting to retrieve.
    :p LIBMUSCLE_real8: The returned value (out, dimension(:))
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).

.. f:subroutine:: LIBMUSCLE_Instance_get_setting_as_real8array2(self, name, value, err_code, err_msg)

    Returns the value of a 2D-array-of-real8-valued model setting.

    Note that there is currently no way to get the size of the array in advance.
    This feature is intended to be used for small fixed arrays, in which case
    the size will be known in advance to the programmer.

    If no setting with the given name exists, ``err_code`` will be set to
    ``LIBMUSCLE_out_of_range``. If the value is not a 2D array of real8, then
    ``err_code`` will be set to ``LIBMUSCLE_bad_cast``. See
    :f:func:`LIBMUSCLE_Data_as_logical` for an example of error handling.

    MPI-based components may call this function at any time within the
    reuse loop, in any or all processes, simultaneously or not.

    :p LIBMUSCLE_Instance self: The instance to get the setting from.
    :p character name: The name of the setting to retrieve.
    :p LIBMUSCLE_real8: The returned value (out, dimension(:,:))
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).

.. f:function:: LIBMUSCLE_Instance_list_ports(self)

    Returns a description of the ports of this instance.

    MPI-based components may call this function only in the root process.

    :p LIBMUSCLE_Instance self: The instance whose ports to describe.
    :r ports: A description of the ports, organised by operator.
    :rtype ports: LIBMUSCLE_PortsDescription

.. f:function:: LIBMUSCLE_Instance_is_connected(self, port)

    Returns whether the given port is connected.

    MPI-based components may call this function only in the root process.

    :p LIBMUSCLE_Instance self: The instance to inspect.
    :p character port: The name of the port to inspect
    :r connected: ``.true.`` if the port is connected.
    :rtype connected: logical

.. f:function:: LIBMUSCLE_Instance_is_vector_port(self, port)

    Returns whether the given port is a vector port.

    MPI-based components may call this function only in the root process.

    :p LIBMUSCLE_Instance self: The instance to inspect.
    :p character port: The name of the port to inspect
    :r connected: ``.true.`` if the port is a vector port.
    :rtype connected: logical

.. f:function:: LIBMUSCLE_Instance_is_resizable(self, port, err_code, err_msg)

    Returns whether the port is resizable.

    This function must only be called on vector ports. If the port is a scalar
    port, ``err_code`` will be set to ``LIBMUSCLE_runtime_error`` and the return
    value will be invalid.

    MPI-based components may call this function only in the root process.

    :p LIBMUSCLE_Instance self: The instance to inspect.
    :p character port: The name of the port to inspect
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r connected: ``.true.`` if the port is a vector port.
    :rtype connected: logical

.. f:function:: LIBMUSCLE_Instance_get_port_length(self, port, err_code, err_msg)

    Returns the current length of a vector port.

    This function must only be called on vector ports. If the port is a scalar
    port, ``err_code`` will be set to ``LIBMUSCLE_runtime_error`` and the return
    value will be invalid.

    MPI-based components may call this function only in the root process.

    :p LIBMUSCLE_Instance self: The instance to inspect.
    :p character port: The name of the port to inspect
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r connected: ``.true.`` if the port is a vector port.
    :rtype connected: logical

.. f:subroutine:: LIBMUSCLE_Instance_set_port_length(self, port, length)

    Sets the current length of a vector port.

    This function must only be called on resizable vector ports. If the port is
    a scalar port or a non-resizable vector port, ``err_code`` will be set to
    ``LIBMUSCLE_runtime_error`` and the return value will be invalid.

    MPI-based components may call this function only in the root process.

    :p LIBMUSCLE_Instance self: The instance to change a port on.
    :p character port: The name of the port to modify.
    :p integer length: The new length of the port.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).

.. f:subroutine:: LIBMUSCLE_Instance_send(self, port_name, message)

    Send a message to the outside world via a port.

    Sending is non-blocking, a copy of the message will be made and stored until
    the receiver is ready to receive it.

    MPI-based components may call this function either in all processes,
    or only in the root process. In both cases, the message given by the root
    process will be sent, the others ignored. You may want to do a gather
    operation first to collect all the information that is to be sent in the
    root process.

    :p LIBMUSCLE_Instance self: The instance to send a message from.
    :p character port_name: The name of the port to send on.
    :p LIBMUSCLE_Message message: The message to send.

.. f:subroutine:: LIBMUSCLE_Instance_send(self, port_name, message, slot)

    Send a message to the outside world via a slot on a port.

    Sending is non-blocking, a copy of the message will be made and stored until
    the receiver is ready to receive it.

    MPI-based components may call this function either in all processes,
    or only in the root process. In both cases, the message given by the root
    process will be sent, the others ignored. You may want to do a gather
    operation first to collect all the information that is to be sent in the
    root process.

    :p LIBMUSCLE_Instance self: The instance to send a message from.
    :p character port_name: The name of the port to send on.
    :p int slot: The slot to send on.
    :p LIBMUSCLE_Message message: The message to send.

.. f:function:: LIBMUSCLE_Instance_receive(self, port_name, err_code, err_msg)

    Receive a message from the outside world via a port.

    Receiving is a blocking operation. This function will contact the sender,
    wait for a message to be available, and receive and return it. Note that you
    must free the returned :f:type:`LIBMUSCLE_Message` object when you're done
    with it.

    If the port you are receiving on is not connected, then err_code will be set
    to ``LIBMUSCLE_runtime_error``.

    MPI-based components must call this function in all processes
    simultaneously. The received message will be returned in the root process,
    all other processes will receive a dummy message. It is therefore up to the
    model code to scatter or broadcast the received message to the non-root
    processes, if necessary.

    :p LIBMUSCLE_Instance self: The instance to receive a message for.
    :p character port_name: The name of the port to receive on.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r message: The received message.
    :rtype message: LIBMUSCLE_Message

.. f:function:: LIBMUSCLE_Instance_receive(self, port_name, default_msg, err_code, err_msg)

    Receive a message from the outside world via a port.

    Receiving is a blocking operation. This function will contact the sender,
    wait for a message to be available, and receive and return it. Note that you
    must free the returned :f:type:`LIBMUSCLE_Message` object when you're done
    with it.

    If the port you are receiving on is not connected, then a copy of
    ``default_msg`` will be returned.

    MPI-based components must call this function in all processes
    simultaneously. The received message will be returned in the root process,
    all other processes will receive a dummy message. It is therefore up to the
    model code to scatter or broadcast the received message to the non-root
    processes, if necessary.

    :p LIBMUSCLE_Instance self: The instance to receive a message for.
    :p character port_name: The name of the port to receive on.
    :p LIBMUSCLE_Message default_msg: A default message in case the port is not
            connected.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r message: The received message.
    :rtype message: LIBMUSCLE_Message

.. f:function:: LIBMUSCLE_Instance_receive_on_slot(self, port_name, slot, err_code, err_msg)

    Receive a message from the outside world via a slot on a vector port.

    Receiving is a blocking operation. This function will contact the sender,
    wait for a message to be available, and receive and return it. Note that you
    must free the returned :f:type:`LIBMUSCLE_Message` object when you're done
    with it.

    If the port you are receiving on is not connected, then err_code will be set
    to ``LIBMUSCLE_runtime_error``.

    MPI-based components must call this function in all processes
    simultaneously. The received message will be returned in the root process,
    all other processes will receive a dummy message. It is therefore up to the
    model code to scatter or broadcast the received message to the non-root
    processes, if necessary.

    MPI-based components must call this function in all processes
    simultaneously. The received message will be returned in the root process,
    all other processes will receive a dummy message. It is therefore up to the
    model code to scatter or broadcast the received message to the non-root
    processes, if necessary.

    :p LIBMUSCLE_Instance self: The instance to receive a message for.
    :p character port_name: The name of the vector port to receive on.
    :p integer slot: The slot to receive on.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r message: The received message.
    :rtype message: LIBMUSCLE_Message

.. f:function:: LIBMUSCLE_Instance_receive_on_slot(self, port_name, slot, default_msg, err_code, err_msg)

    Receive a message from the outside world via a slot on a vector port.

    Receiving is a blocking operation. This function will contact the sender,
    wait for a message to be available, and receive and return it. Note that you
    must free the returned :f:type:`LIBMUSCLE_Message` object when you're done
    with it.

    If the port you are receiving on is not connected, then a copy of
    ``default_msg`` will be returned.

    MPI-based components must call this function in all processes
    simultaneously. The received message will be returned in the root process,
    all other processes will receive a dummy message. It is therefore up to the
    model code to scatter or broadcast the received message to the non-root
    processes, if necessary.

    :p LIBMUSCLE_Instance self: The instance to receive a message for.
    :p character port_name: The name of the port to receive on.
    :p integer slot: The slot to receive on.
    :p LIBMUSCLE_Message default_msg: A default message in case the port is not
            connected.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r message: The received message.
    :rtype message: LIBMUSCLE_Message

.. f:function:: LIBMUSCLE_Instance_receive_with_settings(self, port_name, err_code, err_msg)

    Receive a message with attached settings overlay.

    Receiving is a blocking operation. This function will contact the sender,
    wait for a message to be available, and receive and return it. Note that you
    must free the returned :f:type:`LIBMUSCLE_Message` object when you're done
    with it.

    If the port you are receiving on is not connected, then err_code will be set
    to ``LIBMUSCLE_runtime_error``.

    MPI-based components must call this function in all processes
    simultaneously. The received message will be returned in the root process,
    all other processes will receive a dummy message. It is therefore up to the
    model code to scatter or broadcast the received message to the non-root
    processes, if necessary.

    :p LIBMUSCLE_Instance self: The instance to receive a message for.
    :p character port_name: The name of the port to receive on.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r message: The received message.
    :rtype message: LIBMUSCLE_Message

.. f:function:: LIBMUSCLE_Instance_receive_with_settings(self, port_name, default_msg, err_code, err_msg)

    Receive a message with attached settings overlay.

    Receiving is a blocking operation. This function will contact the sender,
    wait for a message to be available, and receive and return it. Note that you
    must free the returned :f:type:`LIBMUSCLE_Message` object when you're done
    with it.

    If the port you are receiving on is not connected, then a copy of
    ``default_msg`` will be returned.

    MPI-based components must call this function in all processes
    simultaneously. The received message will be returned in the root process,
    all other processes will receive a dummy message. It is therefore up to the
    model code to scatter or broadcast the received message to the non-root
    processes, if necessary.

    :p LIBMUSCLE_Instance self: The instance to receive a message for.
    :p character port_name: The name of the port to receive on.
    :p LIBMUSCLE_Message default_msg: A default message in case the port is not
            connected.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r message: The received message.
    :rtype message: LIBMUSCLE_Message

.. f:function:: LIBMUSCLE_Instance_receive_with_settings_on_slot(self, port_name, slot, err_code, err_msg)

    Receive a message with attached settings overlay.

    Receiving is a blocking operation. This function will contact the sender,
    wait for a message to be available, and receive and return it. Note that you
    must free the returned :f:type:`LIBMUSCLE_Message` object when you're done
    with it.

    If the port you are receiving on is not connected, then err_code will be set
    to ``LIBMUSCLE_runtime_error``.

    MPI-based components must call this function in all processes
    simultaneously. The received message will be returned in the root process,
    all other processes will receive a dummy message. It is therefore up to the
    model code to scatter or broadcast the received message to the non-root
    processes, if necessary.

    :p LIBMUSCLE_Instance self: The instance to receive a message for.
    :p character port_name: The name of the vector port to receive on.
    :p integer slot: The slot to receive on.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r message: The received message.
    :rtype message: LIBMUSCLE_Message

.. f:function:: LIBMUSCLE_Instance_receive_with_settings_on_slot(self, port_name, slot, default_msg, err_code, err_msg)

    Receive a message with attached settings overlay.

    Receiving is a blocking operation. This function will contact the sender,
    wait for a message to be available, and receive and return it. Note that you
    must free the returned :f:type:`LIBMUSCLE_Message` object when you're done
    with it.

    If the port you are receiving on is not connected, then a copy of
    ``default_msg`` will be returned.

    MPI-based components must call this function in all processes
    simultaneously. The received message will be returned in the root process,
    all other processes will receive a dummy message. It is therefore up to the
    model code to scatter or broadcast the received message to the non-root
    processes, if necessary.

    :p LIBMUSCLE_Instance self: The instance to receive a message for.
    :p character port_name: The name of the port to receive on.
    :p integer slot: The slot to receive on.
    :p LIBMUSCLE_Message default_msg: A default message in case the port is not
            connected.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r message: The received message.
    :rtype message: LIBMUSCLE_Message

Namespace YMMSL
---------------

.. f:module:: ymmsl
    :synopsis: Fortran module for ymmsl

.. f:currentmodule:: ymmsl

YMMSL_Operator
``````````````

YMMSL operators are represented in Python by integer constants of kind
``YMMSL_Operator``. The following values are available:

+----------+-----------------------+
| Operator | Constant              |
+==========+=======================+
|   None   | YMMSL_Operator_NONE   |
+----------+-----------------------+
|  f_init  | YMMSL_Operator_F_INIT |
+----------+-----------------------+
|   O_i    | YMMSL_Operator_O_I    |
+----------+-----------------------+
|    S     | YMMSL_Operator_S      |
+----------+-----------------------+
|    B     | YMMSL_Operator_B      |
+----------+-----------------------+
|   O_f    | YMMSL_Operator_O_F    |
+----------+-----------------------+

YMMSL_Settings
``````````````
.. f:type:: YMMSL_Settings

    Represents a libmuscle Settings object. These are used to send and receive
    Settings objects to other components. This is an opaque object that
    may be returned from and passed to libmuscle functions, but does not contain
    any directly accessible members.

    A Settings object is a dictionary-like object which is indexed by a string,
    and whose values can be strings, logicals, 8-byte integers, 8-byte real
    numbers, and one- and two-dimensional arrays of 8-byte real numbers.

.. f:function:: YMMSL_Settings_create()

    Creates an empty Settings object.

    :r obj: The new Settings object
    :rtype obj: YMMSL_Settings

.. f:subroutine:: YMMSL_Settings_free(self)

    Frees a Settings object.

    This frees the resources associated with the given Settings object. Do not
    use the object for anything after calling this, because it will be invalid.

    :p YMMSL_Settings self: The Settings object to free.

.. f:function:: YMMSL_Settings_equals(self, other)

    Compares two Settings objects for equality.

    This returns ``.true.`` if and only if the two :f:type:`YMMSL_Settings`
    objects contain the same keys and values.

    :p YMMSL_Settings self: The object to compare.
    :p YMMSL_Settings other: The object to compare to.
    :r equal: ``.true.`` if the objects are equal.
    :rtype equal: logical

.. f:function:: YMMSL_Settings_size(self)

    Returns the number of settings in this object.

    :p YMMSL_Settings self: The object to inspect.
    :r count: The number of key-value pairs in this Settings object
            (kind=YMMSL_size).
    :rtype count: integer

.. f:function:: YMMSL_Settings_empty(self)

    Returns ``.true.`` if and only if the Settings object has no items.

    :p YMMSL_Settings self: The object to inspect.
    :r empty: Whether the object is empty.
    :rtype empty: logical

.. f:function:: YMMSL_Settings_contains(self, key)

    Returns ``.true.`` if the Settings object contains the given key.

    :p YMMSL_Settings self: The object to inspect.
    :r contains: Whether the given key exists in this Settings object.
    :rtype contains: logical

.. f:function:: YMMSL_Settings_is_a_character(self, key, err_code, err_msg)

    Return whether a value is of type character.

    If the given key does not exist, then ``err_code`` will be set to
    ``YMMSL_out_of_bounds`` and the result will be invalid.

    :p YMMSL_Settings self: The Settings object to inspect.
    :p character key: The name of the setting to check.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r is: ``.true.`` if the value is of type character.
    :rtype is: logical

.. f:function:: YMMSL_Settings_is_a_logical(self, key, err_code, err_msg)

    Return whether a value is of type logical.

    If the given key does not exist, then ``err_code`` will be set to
    ``YMMSL_out_of_bounds`` and the result will be invalid.

    :p YMMSL_Settings self: The Settings object to inspect.
    :p character key: The name of the setting to check.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r is: ``.true.`` if the value is of type logical.
    :rtype is: logical

.. f:function:: YMMSL_Settings_is_a_int4(self, key, err_code, err_msg)

    Return whether a value is of type ``YMMSL_int4``.

    This returns ``.true.`` if the value is an integer and fits in an int4.

    If the given key does not exist, then ``err_code`` will be set to
    ``YMMSL_out_of_bounds`` and the result will be invalid.

    :p YMMSL_Settings self: The Settings object to inspect.
    :p character key: The name of the setting to check.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r is: ``.true.`` if the value is of type ``YMMSL_int4``.
    :rtype is: logical

.. f:function:: YMMSL_Settings_is_a_int8(self, key, err_code, err_msg)

    Return whether a value is of type ``YMMSL_int8``.

    If the given key does not exist, then ``err_code`` will be set to
    ``YMMSL_out_of_bounds`` and the result will be invalid.

    :p YMMSL_Settings self: The Settings object to inspect.
    :p character key: The name of the setting to check.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r is: ``.true.`` if the value is of type ``YMMSL_int8``.
    :rtype is: logical

.. f:function:: YMMSL_Settings_is_a_real8(self, key, err_code, err_msg)

    Return whether a value is of type ``YMMSL_real8``.

    This will also return ``.true.`` if the value is an integer, even if
    converting it would lose precision.

    If the given key does not exist, then ``err_code`` will be set to
    ``YMMSL_out_of_bounds`` and the result will be invalid.

    :p YMMSL_Settings self: The Settings object to inspect.
    :p character key: The name of the setting to check.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r is: ``.true.`` if the value is of type ``YMMSL_real8``.
    :rtype is: logical

.. f:function:: YMMSL_Settings_is_a_real8array(self, key, err_code, err_msg)

    Return whether a value is a 1D array of type ``YMMSL_real8``.

    If the given key does not exist, then ``err_code`` will be set to
    ``YMMSL_out_of_bounds`` and the result will be invalid.

    :p YMMSL_Settings self: The Settings object to inspect.
    :p character key: The name of the setting to check.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r is: ``.true.`` if the value is a 1D array of type ``YMMSL_real8``.
    :rtype is: logical

.. f:function:: YMMSL_Settings_is_a_real8array2(self, key, err_code, err_msg)

    Return whether a value is a 2D array of type ``YMMSL_real8``.

    If the given key does not exist, then ``err_code`` will be set to
    ``YMMSL_out_of_bounds`` and the result will be invalid.

    :p YMMSL_Settings self: The Settings object to inspect.
    :p character key: The name of the setting to check.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r is: ``.true.`` if the value is a 2D array of type ``YMMSL_real8``.
    :rtype is: logical

.. f:subroutine:: YMMSL_Settings_set(self, key, value)

    Sets a setting to the given value.

    If no setting with the given key exists, one is added, if one does,
    it is overwritten.

    ``value`` may be a character (string), a logical, a 4-byte integer (e.g.
    ``YMMSL_int4``), an 8-byte integer (e.g.  ``YMMSL_int8``), an 8-byte real
    number (``YMMSL_real8``), or a one- or two-dimensional arrays of 8-byte real
    numbers.

    :p YMMSL_Settings self: The Settings object to modify.
    :p character key: The name of the setting.
    :p see_above value: The value to set the setting to.

.. f:function:: YMMSL_Settings_get_as_character(self, key, err_code, err_msg)

    Return the value of a character-typed setting.

    If this setting is not currently set to a character-typed value,
    then ``err_code`` will be set to ``YMMSL_bad_cast`` and the result
    will be invalid.

    :p character key: The name of the setting to get.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value at the given index
    :rtype value: character

.. f:function:: YMMSL_Settings_get_as_logical(self, key, err_code, err_msg)

    Return the value of a logical-typed setting.

    If this setting is not currently set to a logical-typed value,
    then ``err_code`` will be set to ``YMMSL_bad_cast`` and the result
    will be invalid.

    :p character key: The name of the setting to get.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value at the given index
    :rtype value: logical

.. f:function:: YMMSL_Settings_get_as_int4(self, key, err_code, err_msg)

    Return the value of an integer-typed setting.

    If this setting is not currently set to a integer-typed value, or the
    value is out of range for an int4, then ``err_code`` will be set to
    ``YMMSL_bad_cast`` and the result will be invalid.

    :p character key: The name of the setting to get.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value at the given index (YMMSL_int4)
    :rtype value: integer

.. f:function:: YMMSL_Settings_get_as_int8(self, key, err_code, err_msg)

    Return the value of an integer-typed setting.

    If this setting is not currently set to a integer-typed value,
    then ``err_code`` will be set to ``YMMSL_bad_cast`` and the result
    will be invalid.

    :p character key: The name of the setting to get.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value at the given index (YMMSL_int8)
    :rtype value: integer

.. f:function:: YMMSL_Settings_get_as_real8(self, key, err_code, err_msg)

    Return the value of a real-typed setting.

    This will also work if the setting is integer-typed in which case it
    will be converted, with possible loss of precision.

    If this setting is not currently set to a real- or integer-typed value,
    then ``err_code`` will be set to ``YMMSL_bad_cast`` and the result
    will be invalid.

    :p character key: The name of the setting to get.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value at the given index (YMMSL_real8)
    :rtype value: real

.. f:subroutine:: YMMSL_Settings_get_as_real8array(self, key, value, err_code, err_msg)

    Return the value of a setting that is a 1D array of reals.

    If this setting is not currently set to a 1D array of reals-typed value,
    then ``err_code`` will be set to ``YMMSL_bad_cast`` and ``value``
    will be invalid.

    :p character key: The name of the setting to get.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value at the given index (dimension(:))
    :rtype value: YMMSL_real8

.. f:subroutine:: YMMSL_Settings_get_as_real8array2(self, key, value, err_code, err_msg)

    Return the value of a setting that is a 2D array of reals.

    If this setting is not currently set to a 2D array of reals-typed value,
    then ``err_code`` will be set to ``YMMSL_bad_cast`` and ``value``
    will be invalid.

    :p character key: The name of the setting to get.
    :p integer err_code: An error code output (optional).
    :p character err_msg: An error message output (allocatable, optional).
    :r value: The value at the given index (dimension(:,:))
    :rtype value: YMMSL_real8

.. f:function:: YMMSL_Settings_erase(self, key)

    Remove a setting from the Settings object.

    :p YMMSL_Settings self: The Settings object to modify.
    :p character key: The name of the setting to remove.
    :r removed: The number of settings removed (0 or 1; YMMSL_size)
    :rtype removed: integer

.. f:subroutine:: YMMSL_Settings_clear(self)

    Remove all settings from the Settings object.

    After calling this subroutine, the Settings object will be empty.

    :p YMMSL_Settings self: The Settings object to modify.

.. f:function:: YMMSL_Settings_key(self, i, err_code, err_msg)

    Get the i'th key in this Settings object.

    Note that any changes to the Settings object may change the order of the
    keys, so this is only stable if the Settings object is not changed.

    Parameter ``i`` must be in the range [1..N], where N is the number of items
    in the Settings object (see :f:func:`YMMSL_Settings_size`).

    :p YMMSL_Settings self: The Settings object to get a key of.
    :p YMMSL_size i: The index of the key to retrieve.
    :r key: The name of the i'th key (allocatable)
    :rtype key: character
