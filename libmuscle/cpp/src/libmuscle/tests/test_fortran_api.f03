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

subroutine assert_eq(x, y)
    implicit none
    integer (selected_int_kind(18)) :: x, y

    if (x .ne. y) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_eq

subroutine test_data_basic_types
    use libmuscle

    implicit none

    integer, parameter :: byte = selected_int_kind(2)
    integer, parameter :: short_int = selected_int_kind(4)
    integer, parameter :: long_int = selected_int_kind(18)
    type(LIBMUSCLE_Data) :: d1, d2

    print *, '[  RUN     ] data.nil'
    d1 = LIBMUSCLE_Data_create()
    call assert_true(LIBMUSCLE_Data_is_nil(d1))
    call assert_false(LIBMUSCLE_Data_is_a_int(d1))
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
    call assert_true(LIBMUSCLE_Data_is_a_char(d1))
    call assert_true(LIBMUSCLE_Data_is_a_int(d1))
    call assert_false(LIBMUSCLE_Data_is_a_string(d1))
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.int8'

    print *, '[  RUN     ] data.int16'
    d1 = LIBMUSCLE_Data_create(1313_short_int)
    call assert_true(LIBMUSCLE_Data_is_a_int16(d1))
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
    call assert_false(LIBMUSCLE_Data_is_a_string(d1))
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

end subroutine test_data_basic_types

subroutine test_data_copy_assign
    use libmuscle

    implicit none
    type(LIBMUSCLE_Data) :: d1, d2

    print *, '[  RUN     ] data.copy_constructor'
    d1 = LIBMUSCLE_Data_create(42.0d0)
    d2 = LIBMUSCLE_Data_create(d1)
    call LIBMUSCLE_Data_free(d1)
    call assert_true(LIBMUSCLE_Data_is_a_double(d2))
    call assert_false(LIBMUSCLE_Data_is_a_float(d2))
    call LIBMUSCLE_Data_free(d2)
    print *, '[       OK ] data.copy_constructor'

    print *, '[  RUN     ] data.assign'
    d1 = LIBMUSCLE_Data_create(42.0d0)
    d2 = LIBMUSCLE_Data_create()
    call LIBMUSCLE_Data_assign(d2, d1)
    call LIBMUSCLE_Data_free(d1)
    call assert_true(LIBMUSCLE_Data_is_a_double(d2))
    call assert_false(LIBMUSCLE_Data_is_a_float(d2))
    call LIBMUSCLE_Data_free(d2)
    print *, '[       OK ] data.assign'
end subroutine test_data_copy_assign


subroutine test_data_dict
    use libmuscle

    implicit none
    type(LIBMUSCLE_Data) :: d1, d2

    print *, '[  RUN     ] data.dict'
    d1 = LIBMUSCLE_Data_create_dict()
    call assert_true(LIBMUSCLE_Data_is_a_dict(d1))
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.dict'
end subroutine test_data_dict


subroutine test_data_list
    use libmuscle

    implicit none
    integer, parameter :: long_int = selected_int_kind(18)
    type(LIBMUSCLE_Data) :: d1, d2

    print *, '[  RUN     ] data.list'
    d1 = LIBMUSCLE_Data_create_list()
    call assert_true(LIBMUSCLE_Data_is_a_list(d1))
    call assert_false(LIBMUSCLE_Data_is_a_float(d1))
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.list'

    print *, '[  RUN     ] data.nils'
    d1 = LIBMUSCLE_Data_create_nils(100_long_int)
    call assert_true(LIBMUSCLE_Data_is_a_list(d1))
    call assert_false(LIBMUSCLE_Data_is_a_float(d1))
    call assert_eq(LIBMUSCLE_Data_size(d1), 100_long_int)
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.nils'
end subroutine test_data_list

subroutine test_data_byte_array
    use libmuscle

    implicit none
    integer, parameter :: long_int = selected_int_kind(18)
    type(LIBMUSCLE_Data) :: d1

    print *, '[  RUN     ] data.byte_array'
    d1 = LIBMUSCLE_Data_create_byte_array(1024_long_int)
    call assert_true(LIBMUSCLE_Data_is_a_byte_array(d1))
    call assert_false(LIBMUSCLE_Data_is_a_int(d1))
    call assert_eq(LIBMUSCLE_Data_size(d1), 1024_long_int)
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.byte_array'
end subroutine test_data_byte_array


subroutine test_data
    call test_data_basic_types
    call test_data_copy_assign
    call test_data_dict
    call test_data_list
    call test_data_byte_array
end subroutine


program test_fortran_api
    implicit none

    print *, ''
    print *, '[==========] Fortran API test'

    call test_data

    print *, '[==========] Fortran API test'
    print *, '[  PASSED  ] Fortran API test'
    print *, ''
end program test_fortran_api

