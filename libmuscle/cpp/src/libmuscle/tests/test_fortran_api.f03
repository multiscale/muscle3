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

subroutine assert_eq_byte(x, y)
    implicit none
    integer(kind=selected_int_kind(2)) :: x, y

    if (x .ne. y) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_eq_byte

subroutine assert_eq_int16(x, y)
    implicit none
    integer(kind=selected_int_kind(4)) :: x, y

    if (x .ne. y) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_eq_int16

subroutine assert_eq_integer(x, y)
    implicit none
    integer :: x, y

    if (x .ne. y) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_eq_integer

subroutine assert_eq_long_int(x, y)
    implicit none
    integer (selected_int_kind(18)) :: x, y

    if (x .ne. y) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_eq_long_int

subroutine assert_eq_logical(x, y)
    implicit none
    logical :: x, y

    if (x .neqv. y) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_eq_logical

subroutine assert_eq_character(x, y)
    implicit none
    character(len=*) :: x, y

    if (x .ne. y) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_eq_character

subroutine assert_eq_single(x, y)
    implicit none
    real (selected_real_kind(6)) :: x, y

    if (x .ne. y) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_eq_single

subroutine assert_eq_double(x, y)
    implicit none
    real (selected_real_kind(15)) :: x, y

    if (x .ne. y) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_eq_double

subroutine test_data_basic_types
    use libmuscle

    implicit none

    integer, parameter :: byte = selected_int_kind(2)
    integer, parameter :: short_int = selected_int_kind(4)
    integer, parameter :: long_int = selected_int_kind(18)
    type(LIBMUSCLE_Data) :: d1, d2
    integer :: i1, err_code
    logical :: l1
    character(len=:), allocatable :: s1, err_msg
    integer (kind=byte) :: bi1
    integer (kind=short_int) :: si1
    integer (kind=long_int) :: li1
    real (selected_real_kind(6)) :: sr1
    real (selected_real_kind(15)) :: dr1

    print *, '[  RUN     ] data.nil'
    d1 = LIBMUSCLE_Data_create()
    call assert_true(LIBMUSCLE_Data_is_nil(d1))
    call assert_false(LIBMUSCLE_Data_is_a_int(d1))
    call LIBMUSCLE_Data_set(d1, 10)
    call assert_false(LIBMUSCLE_Data_is_nil(d1))
    call LIBMUSCLE_Data_set_nil(d1)
    call assert_true(LIBMUSCLE_Data_is_nil(d1))
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.nil'

    print *, '[  RUN     ] data.logical'
    d1 = LIBMUSCLE_Data_create(.true.)
    call assert_true(LIBMUSCLE_Data_is_a_bool(d1))
    call assert_false(LIBMUSCLE_Data_is_a_int(d1))
    l1 = LIBMUSCLE_Data_as_bool(d1)
    call assert_eq_logical(l1, .true.)
    s1 = LIBMUSCLE_Data_as_string(d1, err_code, err_msg)
    call assert_eq_integer(err_code, LIBMUSCLE_runtime_error)
    deallocate(err_msg)
    call LIBMUSCLE_Data_set(d1, .false.)
    call assert_eq_logical(LIBMUSCLE_Data_as_bool(d1), .false.)
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.logical'

    print *, '[  RUN     ] data.string'
    d1 = LIBMUSCLE_Data_create('Testing')
    call assert_true(LIBMUSCLE_Data_is_a_string(d1))
    call assert_false(LIBMUSCLE_Data_is_a_bool(d1))
    s1 = LIBMUSCLE_Data_as_string(d1)
    call assert_eq_character(s1, 'Testing')
    deallocate(s1)
    i1 = LIBMUSCLE_Data_as_int(d1, err_code)
    call assert_eq_integer(err_code, LIBMUSCLE_runtime_error)
    call LIBMUSCLE_Data_set(d1, 'Something else')
    s1 = LIBMUSCLE_Data_as_string(d1)
    call assert_eq_character(LIBMUSCLE_Data_as_string(d1), 'Something else')
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.string'

    print *, '[  RUN     ] data.int8'
    d1 = LIBMUSCLE_Data_create(121_byte)
    call assert_true(LIBMUSCLE_Data_is_a_char(d1))
    call assert_true(LIBMUSCLE_Data_is_a_int(d1))
    call assert_false(LIBMUSCLE_Data_is_a_string(d1))
    bi1 = LIBMUSCLE_Data_as_char(d1)
    call assert_eq_byte(bi1, 121_byte)
    call LIBMUSCLE_Data_set(d1, 43_byte)
    call assert_eq_byte(LIBMUSCLE_Data_as_char(d1), 43_byte)
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.int8'

    print *, '[  RUN     ] data.int16'
    d1 = LIBMUSCLE_Data_create(1313_short_int)
    call assert_true(LIBMUSCLE_Data_is_a_int16(d1))
    si1 = LIBMUSCLE_Data_as_int16(d1)
    call assert_eq_int16(si1, 1313_short_int)
    call LIBMUSCLE_Data_set(d1, 24242_short_int)
    call assert_eq_int16(LIBMUSCLE_Data_as_int16(d1), 24242_short_int)
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.int16'

    print *, '[  RUN     ] data.integer'
    d1 = LIBMUSCLE_Data_create(13)
    call assert_true(LIBMUSCLE_Data_is_a_int(d1))
    call assert_false(LIBMUSCLE_Data_is_a_bool(d1))
    i1 = LIBMUSCLE_Data_as_int(d1)
    call assert_eq_integer(i1, 13)
    call LIBMUSCLE_Data_set(d1, 242424)
    call assert_eq_integer(LIBMUSCLE_Data_as_int(d1), 242424)
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.integer'

    print *, '[  RUN     ] data.integer64'
    d1 = LIBMUSCLE_Data_create(131313131313131313_long_int)
    call assert_true(LIBMUSCLE_Data_is_a_int64(d1))
    call assert_false(LIBMUSCLE_Data_is_a_string(d1))
    li1 = LIBMUSCLE_Data_as_int64(d1)
    call assert_eq_long_int(li1, 131313131313131313_long_int)
    call LIBMUSCLE_Data_set(d1, 242424242424242424_long_int)
    call assert_eq_long_int(LIBMUSCLE_Data_as_int64(d1), 242424242424242424_long_int)
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.integer64'

    print *, '[  RUN     ] data.single'
    d1 = LIBMUSCLE_Data_create(42.0)
    call assert_true(LIBMUSCLE_Data_is_a_float(d1))
    call assert_false(LIBMUSCLE_Data_is_a_int(d1))
    sr1 = LIBMUSCLE_Data_as_float(d1)
    call assert_eq_single(sr1, 42.0)
    call LIBMUSCLE_Data_set(d1, 3.1415926536)
    call assert_eq_single(LIBMUSCLE_Data_as_float(d1), 3.1415926536)
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.single'

    print *, '[  RUN     ] data.double'
    d1 = LIBMUSCLE_Data_create(42.0d0)
    call assert_true(LIBMUSCLE_Data_is_a_double(d1))
    call assert_false(LIBMUSCLE_Data_is_a_float(d1))
    dr1 = LIBMUSCLE_Data_as_double(d1)
    call assert_eq_double(dr1, 42.0d0)
    call LIBMUSCLE_Data_set(d1, 3.1415926536d0)
    call assert_eq_double(LIBMUSCLE_Data_as_double(d1), 3.1415926536d0)
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
    call LIBMUSCLE_Data_set(d2, d1)
    call LIBMUSCLE_Data_free(d1)
    call assert_true(LIBMUSCLE_Data_is_a_double(d2))
    call assert_false(LIBMUSCLE_Data_is_a_float(d2))
    call LIBMUSCLE_Data_free(d2)
    print *, '[       OK ] data.assign'
end subroutine test_data_copy_assign


subroutine test_data_dict
    use libmuscle

    implicit none
    integer, parameter :: byte = selected_int_kind(2)
    integer, parameter :: short_int = selected_int_kind(4)
    integer, parameter :: long_int = selected_int_kind(18)
    type(LIBMUSCLE_Data) :: d1, d2
    integer (kind=long_int) :: i

    print *, '[  RUN     ] data.dict'
    d1 = LIBMUSCLE_Data_create_dict()
    call assert_true(LIBMUSCLE_Data_is_a_dict(d1))
    call LIBMUSCLE_Data_set_item(d1, 'key1', 1)
    call assert_eq_long_int(LIBMUSCLE_Data_size(d1), 1_long_int)

    call LIBMUSCLE_Data_set_item(d1, 'key1', .true.)
    d2 = LIBMUSCLE_Data_get_item(d1, 'key1')
    call assert_true(LIBMUSCLE_Data_as_bool(d2))
    call LIBMUSCLE_Data_free(d2)

    call LIBMUSCLE_Data_set_item(d1, 'key2', 'test')
    d2 = LIBMUSCLE_Data_get_item(d1, 'key2')
    call assert_eq_character(LIBMUSCLE_Data_as_string(d2), 'test')
    call LIBMUSCLE_Data_free(d2)

    call LIBMUSCLE_Data_set_item(d1, 'key1', 63_byte)
    d2 = LIBMUSCLE_Data_get_item(d1, 'key1')
    call assert_eq_byte(LIBMUSCLE_Data_as_char(d2), 63_byte)
    call LIBMUSCLE_Data_free(d2)

    call LIBMUSCLE_Data_set_item(d1, 'key1', 30000_short_int)
    d2 = LIBMUSCLE_Data_get_item(d1, 'key1')
    call assert_eq_int16(LIBMUSCLE_Data_as_int16(d2), 30000_short_int)
    call LIBMUSCLE_Data_free(d2)

    call LIBMUSCLE_Data_set_item(d1, 'key2', 1000030000)
    d2 = LIBMUSCLE_Data_get_item(d1, 'key2')
    call assert_eq_integer(LIBMUSCLE_Data_as_int(d2), 1000030000)
    call LIBMUSCLE_Data_free(d2)

    call assert_eq_character(LIBMUSCLE_Data_key(d1, 1_long_int), 'key1')
    d2 = LIBMUSCLE_Data_value(d1, 1_long_int)
    call assert_eq_int16(LIBMUSCLE_Data_as_int16(d2), 30000_short_int)
    call LIBMUSCLE_Data_free(d2)

    call assert_eq_character(LIBMUSCLE_Data_key(d1, 2_long_int), 'key2')
    d2 = LIBMUSCLE_Data_value(d1, 2_long_int)
    call assert_eq_integer(LIBMUSCLE_Data_as_int(d2), 1000030000)
    call LIBMUSCLE_Data_free(d2)

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
    call assert_eq_long_int(LIBMUSCLE_Data_size(d1), 100_long_int)
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.nils'
end subroutine test_data_list

subroutine test_data_byte_array
    use libmuscle

    implicit none
    integer, parameter :: long_int = selected_int_kind(18)
    character(len=1), dimension(:), allocatable :: buf
    integer :: err_code
    type(LIBMUSCLE_Data) :: d1

    print *, '[  RUN     ] data.byte_array'
    d1 = LIBMUSCLE_Data_create_byte_array(1024_long_int)
    call assert_true(LIBMUSCLE_Data_is_a_byte_array(d1))
    call assert_false(LIBMUSCLE_Data_is_a_int(d1))
    call assert_eq_long_int(LIBMUSCLE_Data_size(d1), 1024_long_int)

    allocate(buf(LIBMUSCLE_Data_size(d1)))
    call LIBMUSCLE_Data_as_byte_array(d1, buf, err_code)
    call assert_eq_integer(err_code, LIBMUSCLE_success)
    call LIBMUSCLE_Data_free(d1)
    deallocate(buf)
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

