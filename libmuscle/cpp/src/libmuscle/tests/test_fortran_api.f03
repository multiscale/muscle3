subroutine assert_true(x)
    implicit none
    logical :: x

    if (.not. x) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_true

subroutine assert_false(x)
    implicit none
    logical :: x

    if (x) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_false

program test_fortran_api
    use libmuscle

    implicit none

    integer, parameter :: byte = selected_int_kind(2)
    integer, parameter :: short_int = selected_int_kind(4)
    integer, parameter :: long_int = selected_int_kind(18)
    type(LIBMUSCLE_Data) :: d1

    print *, ''
    print *, '[==========] Fortran API test'

    print *, '[  RUN     ] data.nil'
    d1 = LIBMUSCLE_Data_create()
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.nil'

    print *, '[  RUN     ] data.logical'
    d1 = LIBMUSCLE_Data_create(.true.)
    call assert_true(LIBMUSCLE_Data_is_a_bool(d1))
    call assert_false(LIBMUSCLE_Data_is_a_int(d1))
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.logical'

    print *, '[  RUN     ] data.string'
    d1 = LIBMUSCLE_Data_create('Testing')
    call assert_true(LIBMUSCLE_Data_is_a_string(d1))
    call assert_false(LIBMUSCLE_Data_is_a_bool(d1))
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.string'

    print *, '[  RUN     ] data.int8'
    d1 = LIBMUSCLE_Data_create(121_byte)
    call assert_true(LIBMUSCLE_Data_is_a_int(d1))
    call assert_false(LIBMUSCLE_Data_is_a_string(d1))
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.int8'

    print *, '[  RUN     ] data.int16'
    d1 = LIBMUSCLE_Data_create(1313_short_int)
    call assert_true(LIBMUSCLE_Data_is_a_int(d1))
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.int16'

    print *, '[  RUN     ] data.integer'
    d1 = LIBMUSCLE_Data_create(13)
    call assert_true(LIBMUSCLE_Data_is_a_int(d1))
    call assert_false(LIBMUSCLE_Data_is_a_bool(d1))
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.integer'

    print *, '[  RUN     ] data.integer64'
    d1 = LIBMUSCLE_Data_create(131313131313131313_long_int)
    call assert_true(LIBMUSCLE_Data_is_a_int64(d1))
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.integer64'

    print *, '[  RUN     ] data.single'
    d1 = LIBMUSCLE_Data_create(42.0)
    call assert_true(LIBMUSCLE_Data_is_a_float(d1))
    call assert_false(LIBMUSCLE_Data_is_a_int(d1))
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.single'

    print *, '[  RUN     ] data.double'
    d1 = LIBMUSCLE_Data_create(42.0d0)
    call assert_true(LIBMUSCLE_Data_is_a_double(d1))
    call assert_false(LIBMUSCLE_Data_is_a_float(d1))
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.double'

    print *, '[==========] Fortran API test'
    print *, '[  PASSED  ] Fortran API test'
    print *, ''

end program test_fortran_api

