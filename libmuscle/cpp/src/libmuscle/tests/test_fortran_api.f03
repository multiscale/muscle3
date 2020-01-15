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

subroutine assert_eq_integer(x, y)
    use libmuscle
    implicit none
    integer :: x, y

    if (x .ne. y) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_eq_integer

subroutine assert_eq_int1(x, y)
    use libmuscle
    implicit none
    integer(kind=LIBMUSCLE_int1) :: x, y

    if (x .ne. y) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_eq_int1

subroutine assert_eq_int2(x, y)
    use libmuscle
    implicit none
    integer(kind=LIBMUSCLE_int2) :: x, y

    if (x .ne. y) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_eq_int2

subroutine assert_eq_int4(x, y)
    use libmuscle
    implicit none
    integer(kind=LIBMUSCLE_int4) :: x, y

    if (x .ne. y) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_eq_int4

subroutine assert_eq_int8(x, y)
    use libmuscle
    implicit none
    integer (LIBMUSCLE_int8) :: x, y

    if (x .ne. y) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_eq_int8

subroutine assert_eq_size(x, y)
    use libmuscle
    implicit none
    integer (LIBMUSCLE_size) :: x, y

    if (x .ne. y) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_eq_size

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

subroutine assert_eq_real4(x, y)
    use libmuscle
    implicit none
    real (LIBMUSCLE_real4) :: x, y

    if (x .ne. y) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_eq_real4

subroutine assert_eq_real8(x, y)
    use libmuscle
    implicit none
    real (LIBMUSCLE_real8) :: x, y

    if (x .ne. y) then
        print *, 'Assertion failed'
        stop
    end if
end subroutine assert_eq_real8

subroutine test_data_basic_types
    use libmuscle

    implicit none

    integer, parameter :: int1 = LIBMUSCLE_int1
    integer, parameter :: int2 = LIBMUSCLE_int2
    integer, parameter :: int4 = LIBMUSCLE_int4
    integer, parameter :: int8 = LIBMUSCLE_int8
    type(LIBMUSCLE_Data) :: d1, d2
    integer :: xi, err_code
    logical :: l1
    character(len=:), allocatable :: c1, err_msg
    integer (int1) :: xi1
    integer (int2) :: xi2
    integer (int4) :: xi4
    integer (int8) :: xi8
    real (LIBMUSCLE_real4) :: xr4
    real (LIBMUSCLE_real8) :: xr8

    print *, '[  RUN     ] data.nil'
    d1 = LIBMUSCLE_Data_create()
    call assert_true(LIBMUSCLE_Data_is_nil(d1))
    call assert_false(LIBMUSCLE_Data_is_a_int4(d1))
    call LIBMUSCLE_Data_set(d1, 10)
    call assert_false(LIBMUSCLE_Data_is_nil(d1))
    call LIBMUSCLE_Data_set_nil(d1)
    call assert_true(LIBMUSCLE_Data_is_nil(d1))
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.nil'

    print *, '[  RUN     ] data.logical'
    d1 = LIBMUSCLE_Data_create(.true.)
    call assert_true(LIBMUSCLE_Data_is_a_logical(d1))
    call assert_false(LIBMUSCLE_Data_is_a_int4(d1))
    l1 = LIBMUSCLE_Data_as_logical(d1)
    call assert_eq_logical(l1, .true.)
    c1 = LIBMUSCLE_Data_as_character(d1, err_code, err_msg)
    call assert_eq_integer(err_code, LIBMUSCLE_runtime_error)
    deallocate(err_msg)
    call LIBMUSCLE_Data_set(d1, .false.)
    call assert_eq_logical(LIBMUSCLE_Data_as_logical(d1), .false.)
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.logical'

    print *, '[  RUN     ] data.character'
    d1 = LIBMUSCLE_Data_create('Testing')
    call assert_true(LIBMUSCLE_Data_is_a_character(d1))
    call assert_false(LIBMUSCLE_Data_is_a_logical(d1))
    c1 = LIBMUSCLE_Data_as_character(d1)
    call assert_eq_character(c1, 'Testing')
    deallocate(c1)
    xi4 = LIBMUSCLE_Data_as_int4(d1, err_code)
    call assert_eq_int4(err_code, LIBMUSCLE_runtime_error)
    call LIBMUSCLE_Data_set(d1, 'Something else')
    c1 = LIBMUSCLE_Data_as_character(d1)
    call assert_eq_character(LIBMUSCLE_Data_as_character(d1), 'Something else')
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.character'

    print *, '[  RUN     ] data.integer'
    d1 = LIBMUSCLE_Data_create(13)
    call assert_true(LIBMUSCLE_Data_is_a_int(d1))
    call assert_false(LIBMUSCLE_Data_is_a_logical(d1))
    xi = LIBMUSCLE_Data_as_int(d1)
    call assert_eq_integer(xi, 13)
    call LIBMUSCLE_Data_set(d1, 242424)
    call assert_eq_integer(LIBMUSCLE_Data_as_int(d1), 242424)
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.integer'

    print *, '[  RUN     ] data.int1'
    d1 = LIBMUSCLE_Data_create(121_int1)
    call assert_true(LIBMUSCLE_Data_is_a_int1(d1))
    call assert_true(LIBMUSCLE_Data_is_a_int4(d1))
    call assert_false(LIBMUSCLE_Data_is_a_character(d1))
    xi1 = LIBMUSCLE_Data_as_int1(d1)
    call assert_eq_int1(xi1, 121_int1)
    call LIBMUSCLE_Data_set(d1, 43_int1)
    call assert_eq_int1(LIBMUSCLE_Data_as_int1(d1), 43_int1)
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.int1'

    print *, '[  RUN     ] data.int2'
    d1 = LIBMUSCLE_Data_create(1313_int2)
    call assert_true(LIBMUSCLE_Data_is_a_int2(d1))
    xi2 = LIBMUSCLE_Data_as_int2(d1)
    call assert_eq_int2(xi2, 1313_int2)
    call LIBMUSCLE_Data_set(d1, 24242_int2)
    call assert_eq_int2(LIBMUSCLE_Data_as_int2(d1), 24242_int2)
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.int2'

    print *, '[  RUN     ] data.int8'
    d1 = LIBMUSCLE_Data_create(131313131313131313_int8)
    call assert_true(LIBMUSCLE_Data_is_a_int8(d1))
    call assert_false(LIBMUSCLE_Data_is_a_character(d1))
    xi8 = LIBMUSCLE_Data_as_int8(d1)
    call assert_eq_int8(xi8, 131313131313131313_int8)
    call LIBMUSCLE_Data_set(d1, 242424242424242424_int8)
    call assert_eq_int8(LIBMUSCLE_Data_as_int8(d1), 242424242424242424_int8)
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.int8'

    print *, '[  RUN     ] data.real4'
    d1 = LIBMUSCLE_Data_create(42.0)
    call assert_true(LIBMUSCLE_Data_is_a_real4(d1))
    call assert_false(LIBMUSCLE_Data_is_a_int(d1))
    xr4 = LIBMUSCLE_Data_as_real4(d1)
    call assert_eq_real4(xr4, 42.0)
    call LIBMUSCLE_Data_set(d1, 3.1415926536)
    call assert_eq_real4(LIBMUSCLE_Data_as_real4(d1), 3.1415926536)
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.real4'

    print *, '[  RUN     ] data.real8'
    d1 = LIBMUSCLE_Data_create(42.0d0)
    call assert_true(LIBMUSCLE_Data_is_a_real8(d1))
    call assert_false(LIBMUSCLE_Data_is_a_real4(d1))
    xr8 = LIBMUSCLE_Data_as_real8(d1)
    call assert_eq_real8(xr8, 42.0d0)
    call LIBMUSCLE_Data_set(d1, 3.1415926536d0)
    call assert_eq_real8(LIBMUSCLE_Data_as_real8(d1), 3.1415926536d0)
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.real8'

end subroutine test_data_basic_types

subroutine test_data_copy_assign
    use libmuscle

    implicit none
    type(LIBMUSCLE_Data) :: d1, d2

    print *, '[  RUN     ] data.copy_constructor'
    d1 = LIBMUSCLE_Data_create(42.0d0)
    d2 = LIBMUSCLE_Data_create(d1)
    call LIBMUSCLE_Data_free(d1)
    call assert_true(LIBMUSCLE_Data_is_a_real8(d2))
    call assert_false(LIBMUSCLE_Data_is_a_real4(d2))
    call LIBMUSCLE_Data_free(d2)
    print *, '[       OK ] data.copy_constructor'

    print *, '[  RUN     ] data.assign'
    d1 = LIBMUSCLE_Data_create(42.0d0)
    d2 = LIBMUSCLE_Data_create()
    call LIBMUSCLE_Data_set(d2, d1)
    call LIBMUSCLE_Data_free(d1)
    call assert_true(LIBMUSCLE_Data_is_a_real8(d2))
    call assert_false(LIBMUSCLE_Data_is_a_real4(d2))
    call LIBMUSCLE_Data_free(d2)
    print *, '[       OK ] data.assign'
end subroutine test_data_copy_assign


subroutine test_data_dict
    use libmuscle

    implicit none
    integer, parameter :: int1 = LIBMUSCLE_int1
    integer, parameter :: int2 = LIBMUSCLE_int2
    integer, parameter :: int4 = LIBMUSCLE_int4
    integer, parameter :: int8 = LIBMUSCLE_int8
    integer, parameter :: sz = LIBMUSCLE_size
    type(LIBMUSCLE_Data) :: d1, d2

    print *, '[  RUN     ] data.dict'
    d1 = LIBMUSCLE_Data_create_dict()
    call assert_true(LIBMUSCLE_Data_is_a_dict(d1))
    call LIBMUSCLE_Data_set_item(d1, 'key1', 1)
    call assert_eq_size(LIBMUSCLE_Data_size(d1), 1_sz)

    call LIBMUSCLE_Data_set_item(d1, 'key1', .true.)
    d2 = LIBMUSCLE_Data_get_item(d1, 'key1')
    call assert_true(LIBMUSCLE_Data_as_logical(d2))
    call LIBMUSCLE_Data_free(d2)

    call LIBMUSCLE_Data_set_item(d1, 'key2', 'test')
    d2 = LIBMUSCLE_Data_get_item(d1, 'key2')
    call assert_eq_character(LIBMUSCLE_Data_as_character(d2), 'test')
    call LIBMUSCLE_Data_free(d2)

    call LIBMUSCLE_Data_set_item(d1, 'key1', 63_int1)
    d2 = LIBMUSCLE_Data_get_item(d1, 'key1')
    call assert_eq_int1(LIBMUSCLE_Data_as_int1(d2), 63_int1)
    call LIBMUSCLE_Data_free(d2)

    call LIBMUSCLE_Data_set_item(d1, 'key1', 30000_int2)
    d2 = LIBMUSCLE_Data_get_item(d1, 'key1')
    call assert_eq_int2(LIBMUSCLE_Data_as_int2(d2), 30000_int2)
    call LIBMUSCLE_Data_free(d2)

    call LIBMUSCLE_Data_set_item(d1, 'key2', 1000030000_int4)
    d2 = LIBMUSCLE_Data_get_item(d1, 'key2')
    call assert_eq_int4(LIBMUSCLE_Data_as_int4(d2), 1000030000_int4)
    call LIBMUSCLE_Data_free(d2)

    call assert_eq_character(LIBMUSCLE_Data_key(d1, 1_sz), 'key1')
    d2 = LIBMUSCLE_Data_value(d1, 1_sz)
    call assert_eq_int2(LIBMUSCLE_Data_as_int2(d2), 30000_int2)
    call LIBMUSCLE_Data_free(d2)

    call assert_eq_character(LIBMUSCLE_Data_key(d1, 2_sz), 'key2')
    d2 = LIBMUSCLE_Data_value(d1, 2_sz)
    call assert_eq_int4(LIBMUSCLE_Data_as_int(d2), 1000030000_int4)
    call LIBMUSCLE_Data_free(d2)

    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.dict'
end subroutine test_data_dict


subroutine test_data_list
    use libmuscle

    implicit none
    integer, parameter :: int1 = LIBMUSCLE_int1
    integer, parameter :: int2 = LIBMUSCLE_int2
    integer, parameter :: int4 = LIBMUSCLE_int4
    integer, parameter :: int8 = LIBMUSCLE_int8
    integer, parameter :: sz = LIBMUSCLE_size
    integer, parameter :: real4 = selected_real_kind(6)
    integer, parameter :: real8 = selected_real_kind(15)
    type(LIBMUSCLE_Data) :: d1, d2

    print *, '[  RUN     ] data.list'
    d1 = LIBMUSCLE_Data_create_list()
    call assert_true(LIBMUSCLE_Data_is_a_list(d1))
    call assert_false(LIBMUSCLE_Data_is_a_real4(d1))
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.list'

    print *, '[  RUN     ] data.nils'
    d1 = LIBMUSCLE_Data_create_nils(100_sz)
    call assert_true(LIBMUSCLE_Data_is_a_list(d1))
    call assert_false(LIBMUSCLE_Data_is_a_real4(d1))
    call assert_eq_size(LIBMUSCLE_Data_size(d1), 100_sz)
    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.nils'

    print *, '[  RUN     ] data.list_get_item'
    d1 = LIBMUSCLE_Data_create_nils(10_sz)
    d2 = LIBMUSCLE_Data_get_item(d1, 1_sz)
    call assert_true(LIBMUSCLE_Data_is_nil(d2))
    call LIBMUSCLE_Data_free(d1)
    call LIBMUSCLE_Data_free(d2)
    print *, '[       OK ] data.list_get_item'

    print *, '[  RUN     ] data.list_set_item'
    d1 = LIBMUSCLE_Data_create_nils(9_sz)
    call LIBMUSCLE_Data_set_item(d1, 1_sz, .true.)
    call LIBMUSCLE_Data_set_item(d1, 2_sz, 'Testing')
    call LIBMUSCLE_Data_set_item(d1, 3_sz, 42_int1)
    call LIBMUSCLE_Data_set_item(d1, 4_sz, 6565_int2)
    call LIBMUSCLE_Data_set_item(d1, 5_sz, 1313131313_int4)
    call LIBMUSCLE_Data_set_item(d1, 6_sz, 100100100100100_int8)
    call LIBMUSCLE_Data_set_item(d1, 7_sz, 12.34_real4)
    call LIBMUSCLE_Data_set_item(d1, 8_sz, 56.78901234_real8)
    d2 = LIBMUSCLE_Data_create_dict()
    call LIBMUSCLE_Data_set_item(d1, 9_sz, d2)
    call LIBMUSCLE_Data_free(d2)

    d2 = LIBMUSCLE_Data_get_item(d1, 1_sz)
    call assert_true(LIBMUSCLE_Data_as_logical(d2))
    call LIBMUSCLE_Data_free(d2)

    d2 = LIBMUSCLE_Data_get_item(d1, 2_sz)
    call assert_eq_character(LIBMUSCLE_Data_as_character(d2), 'Testing')
    call LIBMUSCLE_Data_free(d2)

    d2 = LIBMUSCLE_Data_get_item(d1, 3_sz)
    call assert_eq_int1(LIBMUSCLE_Data_as_int1(d2), 42_int1)
    call LIBMUSCLE_Data_free(d2)

    d2 = LIBMUSCLE_Data_get_item(d1, 4_sz)
    call assert_eq_int2(LIBMUSCLE_Data_as_int2(d2), 6565_int2)
    call LIBMUSCLE_Data_free(d2)

    d2 = LIBMUSCLE_Data_get_item(d1, 5_sz)
    call assert_eq_int4(LIBMUSCLE_Data_as_int4(d2), 1313131313_int4)
    call LIBMUSCLE_Data_free(d2)

    d2 = LIBMUSCLE_Data_get_item(d1, 6_sz)
    call assert_eq_int8(LIBMUSCLE_Data_as_int8(d2), 100100100100100_int8)
    call LIBMUSCLE_Data_free(d2)

    d2 = LIBMUSCLE_Data_get_item(d1, 7_sz)
    call assert_eq_real4(LIBMUSCLE_Data_as_real4(d2), 12.34_real4)
    call LIBMUSCLE_Data_free(d2)

    d2 = LIBMUSCLE_Data_get_item(d1, 8_sz)
    call assert_eq_real8(LIBMUSCLE_Data_as_real8(d2), 56.78901234_real8)
    call LIBMUSCLE_Data_free(d2)

    d2 = LIBMUSCLE_Data_get_item(d1, 9_sz)
    call assert_true(LIBMUSCLE_Data_is_a_dict(d2))
    call assert_eq_int8(LIBMUSCLE_Data_size(d2), 0_sz)
    call LIBMUSCLE_Data_free(d2)

    call LIBMUSCLE_Data_free(d1)
    print *, '[       OK ] data.list_set_item'
end subroutine test_data_list

subroutine test_data_byte_array
    use libmuscle

    implicit none
    integer, parameter :: sz = LIBMUSCLE_size
    character(len=1), dimension(1024) :: bytes
    character(len=1), dimension(:), allocatable :: buf
    integer :: i, err_code
    type(LIBMUSCLE_Data) :: d1

    print *, '[  RUN     ] data.byte_array'
    d1 = LIBMUSCLE_Data_create_byte_array(1024_sz)
    call assert_true(LIBMUSCLE_Data_is_a_byte_array(d1))
    call assert_false(LIBMUSCLE_Data_is_a_int(d1))
    call assert_eq_size(LIBMUSCLE_Data_size(d1), 1024_sz)

    allocate(buf(LIBMUSCLE_Data_size(d1)))
    call LIBMUSCLE_Data_as_byte_array(d1, buf, err_code)
    call assert_eq_integer(err_code, LIBMUSCLE_success)
    deallocate(buf)

    call LIBMUSCLE_Data_free(d1)

    do i = 1, 1024
        bytes(i) = achar(mod(i, 256))
    end do

    d1 = LIBMUSCLE_Data_create_byte_array(bytes)
    call assert_true(LIBMUSCLE_Data_is_a_byte_array(d1))
    call assert_false(LIBMUSCLE_Data_is_a_int(d1))
    call assert_eq_size(LIBMUSCLE_Data_size(d1), 1024_sz)

    allocate(buf(LIBMUSCLE_Data_size(d1)))
    call LIBMUSCLE_Data_as_byte_array(d1, buf, err_code)
    call assert_eq_integer(err_code, LIBMUSCLE_success)

    do i = 1, 1024
        call assert_eq_integer(mod(i, 256), ichar(buf(i)))
    end do
    deallocate(buf)

    call LIBMUSCLE_Data_free(d1)

    print *, '[       OK ] data.byte_array'
end subroutine test_data_byte_array


subroutine test_data
    call test_data_basic_types
    call test_data_copy_assign
    call test_data_dict
    call test_data_list
    call test_data_byte_array
end subroutine test_data


subroutine test_settings
    use ymmsl
    implicit none

    type(YMMSL_Settings) :: s1

    print *, '[  RUN     ] ymmsl.settings'
    s1 = YMMSL_Settings_create()
    call YMMSL_Settings_free(s1)
    print *, '[       OK ] ymmsl.settings'
end subroutine test_settings


program test_fortran_api
    implicit none

    print *, ''
    print *, '[==========] Fortran API test'

    call test_data

    print *, '[==========] Fortran API test'
    print *, '[  PASSED  ] Fortran API test'
    print *, ''
end program test_fortran_api

