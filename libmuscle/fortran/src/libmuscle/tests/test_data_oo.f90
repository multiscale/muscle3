module data_oo_tests
    use assert
    implicit none
contains
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

        print *, '[  RUN     ] data_oo.nil'
        d1 = LIBMUSCLE_Data()
        call assert_true(d1%is_nil())
        call assert_false(d1%is_a_int4())
        call d1%set(10)
        call assert_false(d1%is_nil())
        call d1%set_nil()
        call assert_true(d1%is_nil())
        call LIBMUSCLE_Data_free(d1)
        print *, '[       OK ] data_oo.nil'

        print *, '[  RUN     ] data_oo.logical'
        d1 = LIBMUSCLE_Data(.true.)
        call assert_true(d1%is_a_logical())
        call assert_false(d1%is_a_int4())
        l1 = d1%as_logical()
        call assert_eq_logical(l1, .true.)
        c1 = d1%as_character(err_code, err_msg)
        call assert_eq_integer(err_code, LIBMUSCLE_runtime_error)
        deallocate(err_msg)
        call d1%set(.false.)
        call assert_eq_logical(d1%as_logical(), .false.)
        call LIBMUSCLE_Data_free(d1)
        print *, '[       OK ] data_oo.logical'

        print *, '[  RUN     ] data_oo.character'
        d1 = LIBMUSCLE_Data('Testing')
        call assert_true(d1%is_a_character())
        call assert_false(d1%is_a_logical())
        c1 = d1%as_character()
        call assert_eq_character(c1, 'Testing')
        deallocate(c1)
        xi4 = d1%as_int4(err_code)
        call assert_eq_int4(err_code, LIBMUSCLE_runtime_error)
        call d1%set('Something else')
        c1 = d1%as_character()
        call assert_eq_character(d1%as_character(), 'Something else')
        call LIBMUSCLE_Data_free(d1)
        print *, '[       OK ] data_oo.character'

        print *, '[  RUN     ] data_oo.integer'
        d1 = LIBMUSCLE_Data(13)
        call assert_true(d1%is_a_int())
        call assert_false(d1%is_a_logical())
        xi = d1%as_int()
        call assert_eq_integer(xi, 13)
        call d1%set(242424)
        call assert_eq_integer(d1%as_int(), 242424)
        call LIBMUSCLE_Data_free(d1)
        print *, '[       OK ] data_oo.integer'

        print *, '[  RUN     ] data_oo.int1'
        d1 = LIBMUSCLE_Data(121_int1)
        call assert_true(d1%is_a_int1())
        call assert_true(d1%is_a_int4())
        call assert_false(d1%is_a_character())
        xi1 = d1%as_int1()
        call assert_eq_int1(xi1, 121_int1)
        call d1%set(43_int1)
        call assert_eq_int1(d1%as_int1(), 43_int1)
        call LIBMUSCLE_Data_free(d1)
        print *, '[       OK ] data_oo.int1'

        print *, '[  RUN     ] data_oo.int2'
        d1 = LIBMUSCLE_Data(1313_int2)
        call assert_true(d1%is_a_int2())
        xi2 = d1%as_int2()
        call assert_eq_int2(xi2, 1313_int2)
        call d1%set(24242_int2)
        call assert_eq_int2(d1%as_int2(), 24242_int2)
        call LIBMUSCLE_Data_free(d1)
        print *, '[       OK ] data_oo.int2'

        print *, '[  RUN     ] data_oo.int8'
        d1 = LIBMUSCLE_Data(131313131313131313_int8)
        call assert_true(d1%is_a_int8())
        call assert_false(d1%is_a_character())
        xi8 = d1%as_int8()
        call assert_eq_int8(xi8, 131313131313131313_int8)
        call d1%set(242424242424242424_int8)
        call assert_eq_int8(d1%as_int8(), 242424242424242424_int8)
        call LIBMUSCLE_Data_free(d1)
        print *, '[       OK ] data_oo.int8'

        print *, '[  RUN     ] data_oo.real4'
        d1 = LIBMUSCLE_Data(42.0)
        call assert_true(d1%is_a_real4())
        call assert_false(d1%is_a_int())
        xr4 = d1%as_real4()
        call assert_eq_real4(xr4, 42.0)
        call d1%set(3.1415926536)
        call assert_eq_real4(d1%as_real4(), 3.1415926536)
        call LIBMUSCLE_Data_free(d1)
        print *, '[       OK ] data_oo.real4'

        print *, '[  RUN     ] data_oo.real8'
        d1 = LIBMUSCLE_Data(42.0d0)
        call assert_true(d1%is_a_real8())
        call assert_false(d1%is_a_real4())
        xr8 = d1%as_real8()
        call assert_eq_real8(xr8, 42.0d0)
        call d1%set(3.1415926536d0)
        call assert_eq_real8(d1%as_real8(), 3.1415926536d0)
        call LIBMUSCLE_Data_free(d1)
        print *, '[       OK ] data_oo.real8'
    end subroutine test_data_basic_types

    subroutine test_data_settings
        use ymmsl
        use libmuscle

        implicit none
        integer :: err_code
        type(YMMSL_Settings) :: s1, s2, s3
        type(LIBMUSCLE_Data) :: d1, d2

        print *, '[  RUN     ] data_oo.settings'
        s1 = YMMSL_Settings_create()
        call YMMSL_Settings_set(s1, 'key', 'value')
        d1 = LIBMUSCLE_Data(s1)
        d2 = LIBMUSCLE_Data(1000)

        call assert_true(d1%is_a_settings())
        call assert_false(d2%is_a_settings())

        s2 = d1%as_settings(err_code)
        call assert_eq_integer(err_code, LIBMUSCLE_success)
        call assert_eq_character(YMMSL_Settings_get_as_character(s2, 'key'), 'value')

        s3 = d2%as_settings(err_code)
        call assert_eq_integer(err_code, LIBMUSCLE_runtime_error)

        call YMMSL_Settings_free(s1)
        call YMMSL_Settings_free(s2)
        call LIBMUSCLE_Data_free(d1)
        call LIBMUSCLE_Data_free(d2)
        print *, '[       OK ] data_oo.settings'
    end subroutine test_data_settings

    subroutine test_data_copy_assign
        use libmuscle

        implicit none
        type(LIBMUSCLE_Data) :: d1, d2

        print *, '[  RUN     ] data_oo.copy_constructor'
        d1 = LIBMUSCLE_Data(42.0d0)
        d2 = LIBMUSCLE_Data(d1)
        call LIBMUSCLE_Data_free(d1)
        call assert_true(d2%is_a_real8())
        call assert_false(d2%is_a_real4())
        call LIBMUSCLE_Data_free(d2)
        print *, '[       OK ] data_oo.copy_constructor'

        print *, '[  RUN     ] data_oo.assign'
        d1 = LIBMUSCLE_Data(42.0d0)
        d2 = LIBMUSCLE_Data()
        call d2%set(d1)
        call LIBMUSCLE_Data_free(d1)
        call assert_true(d2%is_a_real8())
        call assert_false(d2%is_a_real4())
        call LIBMUSCLE_Data_free(d2)
        print *, '[       OK ] data_oo.assign'
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

        print *, '[  RUN     ] data_oo.dict'
        d1 = LIBMUSCLE_Data_create_dict()
        call assert_true(d1%is_a_dict())
        call d1%set_item('key1', 1)
        call assert_eq_size(d1%size(), 1_sz)

        call d1%set_item('key1', .true.)
        d2 = d1%get_item('key1')
        call assert_true(d2%as_logical())
        call LIBMUSCLE_Data_free(d2)

        call d1%set_item('key2', 'test')
        d2 = d1%get_item('key2')
        call assert_eq_character(d2%as_character(), 'test')
        call LIBMUSCLE_Data_free(d2)

        call d1%set_item('key1', 63_int1)
        d2 = d1%get_item('key1')
        call assert_eq_int1(d2%as_int1(), 63_int1)
        call LIBMUSCLE_Data_free(d2)

        call d1%set_item('key1', 30000_int2)
        d2 = d1%get_item('key1')
        call assert_eq_int2(d2%as_int2(), 30000_int2)
        call LIBMUSCLE_Data_free(d2)

        call d1%set_item('key2', 1000030000_int4)
        d2 = d1%get_item('key2')
        call assert_eq_int4(d2%as_int4(), 1000030000_int4)
        call LIBMUSCLE_Data_free(d2)

        call assert_eq_character(d1%key(1_sz), 'key1')
        d2 = d1%value(1_sz)
        call assert_eq_int2(d2%as_int2(), 30000_int2)
        call LIBMUSCLE_Data_free(d2)

        call assert_eq_character(d1%key(2_sz), 'key2')
        d2 = d1%value(2_sz)
        call assert_eq_int4(d2%as_int(), 1000030000_int4)
        call LIBMUSCLE_Data_free(d2)

        call LIBMUSCLE_Data_free(d1)
        print *, '[       OK ] data_oo.dict'
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

        print *, '[  RUN     ] data_oo.list'
        d1 = LIBMUSCLE_Data_create_list()
        call assert_true(d1%is_a_list())
        call assert_false(d1%is_a_real4())
        call LIBMUSCLE_Data_free(d1)
        print *, '[       OK ] data_oo.list'

        print *, '[  RUN     ] data_oo.nils'
        d1 = LIBMUSCLE_Data_create_nils(100_sz)
        call assert_true(d1%is_a_list())
        call assert_false(d1%is_a_real4())
        call assert_eq_size(d1%size(), 100_sz)
        call LIBMUSCLE_Data_free(d1)
        print *, '[       OK ] data_oo.nils'

        print *, '[  RUN     ] data_oo.list_get_item'
        d1 = LIBMUSCLE_Data_create_nils(10_sz)
        d2 = d1%get_item(1_sz)
        call assert_true(d2%is_nil())
        call LIBMUSCLE_Data_free(d1)
        call LIBMUSCLE_Data_free(d2)
        print *, '[       OK ] data_oo.list_get_item'

        print *, '[  RUN     ] data_oo.list_set_item'
        d1 = LIBMUSCLE_Data_create_nils(9_sz)
        call d1%set_item(1_sz, .true.)
        call d1%set_item(2_sz, 'Testing')
        call d1%set_item(3_sz, 42_int1)
        call d1%set_item(4_sz, 6565_int2)
        call d1%set_item(5_sz, 1313131313_int4)
        call d1%set_item(6_sz, 100100100100100_int8)
        call d1%set_item(7_sz, 12.34_real4)
        call d1%set_item(8_sz, 56.78901234_real8)
        d2 = LIBMUSCLE_Data_create_dict()
        call d1%set_item(9_sz, d2)
        call LIBMUSCLE_Data_free(d2)

        d2 = d1%get_item(1_sz)
        call assert_true(d2%as_logical())
        call LIBMUSCLE_Data_free(d2)

        d2 = d1%get_item(2_sz)
        call assert_eq_character(d2%as_character(), 'Testing')
        call LIBMUSCLE_Data_free(d2)

        d2 = d1%get_item(3_sz)
        call assert_eq_int1(d2%as_int1(), 42_int1)
        call LIBMUSCLE_Data_free(d2)

        d2 = d1%get_item(4_sz)
        call assert_eq_int2(d2%as_int2(), 6565_int2)
        call LIBMUSCLE_Data_free(d2)

        d2 = d1%get_item(5_sz)
        call assert_eq_int4(d2%as_int4(), 1313131313_int4)
        call LIBMUSCLE_Data_free(d2)

        d2 = d1%get_item(6_sz)
        call assert_eq_int8(d2%as_int8(), 100100100100100_int8)
        call LIBMUSCLE_Data_free(d2)

        d2 = d1%get_item(7_sz)
        call assert_eq_real4(d2%as_real4(), 12.34_real4)
        call LIBMUSCLE_Data_free(d2)

        d2 = d1%get_item(8_sz)
        call assert_eq_real8(d2%as_real8(), 56.78901234_real8)
        call LIBMUSCLE_Data_free(d2)

        d2 = d1%get_item(9_sz)
        call assert_true(d2%is_a_dict())
        call assert_eq_int8(d2%size(), 0_sz)
        call LIBMUSCLE_Data_free(d2)

        call LIBMUSCLE_Data_free(d1)
        print *, '[       OK ] data_oo.list_set_item'
    end subroutine test_data_list

    subroutine test_data_grid
        use libmuscle

        implicit none
        integer, parameter :: int4 = LIBMUSCLE_int4
        integer, parameter :: int8 = LIBMUSCLE_int8
        integer, parameter :: sz = LIBMUSCLE_size
        integer, parameter :: real4 = LIBMUSCLE_real4
        integer, parameter :: real8 = LIBMUSCLE_real8

        logical, dimension(3) :: ad1, ad1_b
        logical, dimension(2, 2, 2, 2, 2, 2, 2) :: ad7, ad7_b
        integer (int4), dimension(1, 2, 1, 1, 1) :: ai45, ai45_b
        integer (int8), dimension(2, 3, 4) :: ai83, ai83_b
        real (real4), dimension(2, 3) :: ar42, ar42_b
        real (real8), dimension(2, 2, 2, 2, 2, 3) :: ar86, ar86_b

        integer (sz), dimension(7) :: shp

        type(LIBMUSCLE_DataConstRef) :: d1
        type(LIBMUSCLE_Data) :: d2

        print *, '[  RUN     ] data_oo.create_grid'
        ad1 = (/.true., .false., .false./)
        d1 = LIBMUSCLE_DataConstRef_create_grid(ad1)
        call assert_true(d1%is_a_grid_of_logical())
        call assert_false(d1%is_a_grid_of_int4())
        call assert_eq_size(d1%num_dims(), 1_sz)
        call d1%shape(shp)
        call assert_eq_size(shp(1), 3_sz)
        call assert_false(d1%has_indexes())
        call d1%elements(ad1_b)
        call assert_true(all(ad1_b .eqv. ad1))
        call LIBMUSCLE_DataConstRef_free(d1)

        ad7 = reshape(spread(.true., 1, 128), (/2, 2, 2, 2, 2, 2, 2/))
        d1 = LIBMUSCLE_DataConstRef_create_grid(ad7)
        call assert_true(d1%is_a_grid_of_logical())
        call assert_false(d1%is_a_dict())
        call assert_eq_size(d1%num_dims(), 7_sz)
        call d1%shape(shp)
        call assert_true(all(shp .eq. (/2, 2, 2, 2, 2, 2, 2/)))
        call assert_false(d1%has_indexes())
        call d1%elements(ad7_b)
        call assert_true(all(ad7 .eqv. ad7_b))
        call LIBMUSCLE_DataConstRef_free(d1)

        ai45 = reshape((/13_int4, 42_int4/), (/1, 2, 1, 1, 1/))
        d1 = LIBMUSCLE_DataConstRef_create_grid(ai45)
        call assert_true(d1%is_a_grid_of_int4())
        call assert_false(d1%is_a_int4())
        call assert_eq_size(d1%num_dims(), 5_sz)
        call d1%shape(shp)
        call assert_true(all(shp(1:5) .eq. (/1, 2, 1, 1, 1/)))
        call assert_false(d1%has_indexes())
        call d1%elements(ai45_b)
        call assert_true(all(ai45 .eq. ai45_b))
        call LIBMUSCLE_DataConstRef_free(d1)

        ai83 = reshape(spread((/7_int8, -3_int8/), 1, 12), (/2, 3, 4/))
        d1 = LIBMUSCLE_DataConstRef_create_grid(ai83)
        call assert_true(d1%is_a_grid_of_int8())
        call assert_false(d1%is_a_character())
        call assert_eq_size(d1%num_dims(), 3_sz)
        call d1%shape(shp)
        call assert_true(all(shp(1:3) .eq. (/2, 3, 4/)))
        call assert_false(d1%has_indexes())
        call d1%elements(ai83_b)
        call assert_true(all(ai83 .eq. ai83_b))
        call LIBMUSCLE_DataConstRef_free(d1)

        ar42 = reshape(spread((/3.3_real4, -7.6_real4/), 1, 3), (/2, 3/))
        d1 = LIBMUSCLE_DataConstRef_create_grid(ar42)
        call assert_true(d1%is_a_grid_of_real4())
        call assert_false(d1%is_a_logical())
        call assert_eq_size(d1%num_dims(), 2_sz)
        call d1%shape(shp)
        call assert_true(all(shp(1:2) .eq. (/2, 3/)))
        call assert_false(d1%has_indexes())
        call d1%elements(ar42_b)
        call assert_true(all(ar42 .eq. ar42_b))
        call LIBMUSCLE_DataConstRef_free(d1)

        ar86 = reshape(spread(3.14_real8, 1, 96), (/2, 2, 2, 2, 2, 3/))
        d1 = LIBMUSCLE_DataConstRef_create_grid(ar86)
        call assert_true(d1%is_a_grid_of_real8())
        call assert_false(d1%is_a_byte_array())
        call assert_eq_size(d1%num_dims(), 6_sz)
        call d1%shape(shp)
        call assert_true(all(shp(1:6) .eq. (/2, 2, 2, 2, 2, 3/)))
        call assert_false(d1%has_indexes())
        call d1%elements(ar86_b)
        call assert_true(all(ar86 .eq. ar86_b))
        call LIBMUSCLE_DataConstRef_free(d1)

        ! Data instead of DataConstRef
        ai83 = reshape(spread((/7_int8, -3_int8/), 1, 12), (/2, 3, 4/))
        d2 = LIBMUSCLE_Data_create_grid(ai83)
        call assert_true(d2%is_a_grid_of_int8())
        call assert_false(d2%is_a_character())
        call assert_eq_size(d2%num_dims(), 3_sz)
        call d2%shape(shp)
        call assert_true(all(shp(1:3) .eq. (/2, 3, 4/)))
        call assert_false(d2%has_indexes())
        call d2%elements(ai83_b)
        call assert_true(all(ai83 .eq. ai83_b))
        call LIBMUSCLE_Data_free(d2)

        ! Indexes
        ar42 = reshape(spread((/3.3_real4, -7.6_real4/), 1, 3), (/2, 3/))
        d1 = LIBMUSCLE_DataConstRef_create_grid(ar42, 'x', 'y')
        call assert_true(d1%is_a_grid_of_real4())
        call assert_false(d1%is_a_logical())
        call assert_eq_size(d1%num_dims(), 2_sz)
        call d1%shape(shp)
        call assert_true(all(shp(1:2) .eq. (/2, 3/)))
        call assert_true(d1%has_indexes())
        call assert_eq_character(d1%index(1_sz), 'x')
        call assert_eq_character(d1%index(2_sz), 'y')
        call d1%elements(ar42_b)
        call assert_true(all(ar42 .eq. ar42_b))
        call LIBMUSCLE_DataConstRef_free(d1)

        print *, '[       OK ] data_oo.create_grid'
    end subroutine test_data_grid

    subroutine test_data_byte_array
        use libmuscle

        implicit none
        integer, parameter :: sz = LIBMUSCLE_size
        character(len=1), dimension(1024) :: bytes
        character(len=1), dimension(:), allocatable :: buf
        integer :: i, err_code
        type(LIBMUSCLE_Data) :: d1

        print *, '[  RUN     ] data_oo.byte_array'
        d1 = LIBMUSCLE_Data_create_byte_array(1024_sz)
        call assert_true(d1%is_a_byte_array())
        call assert_false(d1%is_a_int())
        call assert_eq_size(d1%size(), 1024_sz)

        allocate(buf(d1%size()))
        call d1%as_byte_array(buf, err_code)
        call assert_eq_integer(err_code, LIBMUSCLE_success)
        deallocate(buf)

        call LIBMUSCLE_Data_free(d1)

        do i = 1, 1024
            bytes(i) = achar(mod(i, 256))
        end do

        d1 = LIBMUSCLE_Data_create_byte_array(bytes)
        call assert_true(d1%is_a_byte_array())
        call assert_false(d1%is_a_int())
        call assert_eq_size(d1%size(), 1024_sz)

        allocate(buf(d1%size()))
        call d1%as_byte_array(buf, err_code)
        call assert_eq_integer(err_code, LIBMUSCLE_success)

        do i = 1, 1024
            call assert_eq_integer(mod(i, 256), ichar(buf(i)))
        end do
        deallocate(buf)

        call LIBMUSCLE_Data_free(d1)

        print *, '[       OK ] data_oo.byte_array'
    end subroutine test_data_byte_array
end module data_oo_tests

program test_data_oo
    use data_oo_tests
    implicit none

    print *, ''
    print *, '[==========] Fortran API Data'

    call test_data_basic_types
    call test_data_copy_assign
    call test_data_dict
    call test_data_list
    call test_data_grid
    call test_data_byte_array
    call test_data_settings

    print *, '[==========] Fortran API Data'
    print *, '[  PASSED  ] Fortran API Data'
    print *, ''
end program test_data_oo

