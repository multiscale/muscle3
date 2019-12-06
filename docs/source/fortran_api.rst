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
    the default ``integer`` kind, and ``selected_int_kind(18)`` (a 64-bit
    signed integer).

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

.. f:subroutine:: LIBMUSCLE_DATA_free(self)

    Frees a Data object.

    This frees the resources associated wit the given Data object. Do not use
    the object for anything after calling this, because it will be invalid.

    :p LIBMUSCLE_Data self: The Data object to free.
