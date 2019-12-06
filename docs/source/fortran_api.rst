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

.. f:subroutine:: LIBMUSCLE_DATA_free(self)

    Frees a Data object.

    This frees the resources associated wit the given Data object. Do not use
    the object for anything after calling this, because it will be invalid.

    :p LIBMUSCLE_Data self: The Data object to free.
