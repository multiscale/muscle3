module data_tests
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

    subroutine test_data_settings
        use ymmsl
        use libmuscle

        implicit none
        integer :: err_code
        type(YMMSL_Settings) :: s1, s2, s3
        type(LIBMUSCLE_Data) :: d1, d2

        print *, '[  RUN     ] data.settings'
        s1 = YMMSL_Settings_create()
        call YMMSL_Settings_set(s1, 'key', 'value')
        d1 = LIBMUSCLE_Data_create(s1)
        d2 = LIBMUSCLE_Data_create(1000)

        call assert_true(LIBMUSCLE_Data_is_a_settings(d1))
        call assert_false(LIBMUSCLE_Data_is_a_settings(d2))

        s2 = LIBMUSCLE_Data_as_settings(d1, err_code)
        call assert_eq_integer(err_code, LIBMUSCLE_success)
        call assert_eq_character(YMMSL_Settings_get_as_character(s2, 'key'), 'value')

        s3 = LIBMUSCLE_Data_as_settings(d2, err_code)
        call assert_eq_integer(err_code, LIBMUSCLE_runtime_error)

        call YMMSL_Settings_free(s1)
        call YMMSL_Settings_free(s2)
        call LIBMUSCLE_Data_free(d1)
        call LIBMUSCLE_Data_free(d2)
        print *, '[       OK ] data.settings'
    end subroutine test_data_settings

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

        print *, '[  RUN     ] data.create_grid'
        ad1 = (/.true., .false., .false./)
        d1 = LIBMUSCLE_DataConstRef_create_grid(ad1)
        call assert_true(LIBMUSCLE_DataConstRef_is_a_grid_of_logical(d1))
        call assert_false(LIBMUSCLE_DataConstRef_is_a_grid_of_int4(d1))
        call assert_eq_size(LIBMUSCLE_DataConstRef_num_dims(d1), 1_sz)
        call LIBMUSCLE_DataConstRef_shape(d1, shp)
        call assert_eq_size(shp(1), 3_sz)
        call assert_false(LIBMUSCLE_DataConstRef_has_indexes(d1))
        call LIBMUSCLE_DataConstRef_elements(d1, ad1_b)
        call assert_true(all(ad1_b .eqv. ad1))
        call LIBMUSCLE_DataConstRef_free(d1)

        ad7 = reshape(spread(.true., 1, 128), (/2, 2, 2, 2, 2, 2, 2/))
        d1 = LIBMUSCLE_DataConstRef_create_grid(ad7)
        call assert_true(LIBMUSCLE_DataConstRef_is_a_grid_of_logical(d1))
        call assert_false(LIBMUSCLE_DataConstRef_is_a_dict(d1))
        call assert_eq_size(LIBMUSCLE_DataConstRef_num_dims(d1), 7_sz)
        call LIBMUSCLE_DataConstRef_shape(d1, shp)
        call assert_true(all(shp .eq. (/2, 2, 2, 2, 2, 2, 2/)))
        call assert_false(LIBMUSCLE_DataConstRef_has_indexes(d1))
        call LIBMUSCLE_DataConstRef_elements(d1, ad7_b)
        call assert_true(all(ad7 .eqv. ad7_b))
        call LIBMUSCLE_DataConstRef_free(d1)

        ai45 = reshape((/13_int4, 42_int4/), (/1, 2, 1, 1, 1/))
        d1 = LIBMUSCLE_DataConstRef_create_grid(ai45)
        call assert_true(LIBMUSCLE_DataConstRef_is_a_grid_of_int4(d1))
        call assert_false(LIBMUSCLE_DataConstRef_is_a_int4(d1))
        call assert_eq_size(LIBMUSCLE_DataConstRef_num_dims(d1), 5_sz)
        call LIBMUSCLE_DataConstRef_shape(d1, shp)
        call assert_true(all(shp(1:5) .eq. (/1, 2, 1, 1, 1/)))
        call assert_false(LIBMUSCLE_DataConstRef_has_indexes(d1))
        call LIBMUSCLE_DataConstRef_elements(d1, ai45_b)
        call assert_true(all(ai45 .eq. ai45_b))
        call LIBMUSCLE_DataConstRef_free(d1)

        ai83 = reshape(spread((/7_int8, -3_int8/), 1, 12), (/2, 3, 4/))
        d1 = LIBMUSCLE_DataConstRef_create_grid(ai83)
        call assert_true(LIBMUSCLE_DataConstRef_is_a_grid_of_int8(d1))
        call assert_false(LIBMUSCLE_DataConstRef_is_a_character(d1))
        call assert_eq_size(LIBMUSCLE_DataConstRef_num_dims(d1), 3_sz)
        call LIBMUSCLE_DataConstRef_shape(d1, shp)
        call assert_true(all(shp(1:3) .eq. (/2, 3, 4/)))
        call assert_false(LIBMUSCLE_DataConstRef_has_indexes(d1))
        call LIBMUSCLE_DataConstRef_elements(d1, ai83_b)
        call assert_true(all(ai83 .eq. ai83_b))
        call LIBMUSCLE_DataConstRef_free(d1)

        ar42 = reshape(spread((/3.3_real4, -7.6_real4/), 1, 3), (/2, 3/))
        d1 = LIBMUSCLE_DataConstRef_create_grid(ar42)
        call assert_true(LIBMUSCLE_DataConstRef_is_a_grid_of_real4(d1))
        call assert_false(LIBMUSCLE_DataConstRef_is_a_logical(d1))
        call assert_eq_size(LIBMUSCLE_DataConstRef_num_dims(d1), 2_sz)
        call LIBMUSCLE_DataConstRef_shape(d1, shp)
        call assert_true(all(shp(1:2) .eq. (/2, 3/)))
        call assert_false(LIBMUSCLE_DataConstRef_has_indexes(d1))
        call LIBMUSCLE_DataConstRef_elements(d1, ar42_b)
        call assert_true(all(ar42 .eq. ar42_b))
        call LIBMUSCLE_DataConstRef_free(d1)

        ar86 = reshape(spread(3.14_real8, 1, 96), (/2, 2, 2, 2, 2, 3/))
        d1 = LIBMUSCLE_DataConstRef_create_grid(ar86)
        call assert_true(LIBMUSCLE_DataConstRef_is_a_grid_of_real8(d1))
        call assert_false(LIBMUSCLE_DataConstRef_is_a_byte_array(d1))
        call assert_eq_size(LIBMUSCLE_DataConstRef_num_dims(d1), 6_sz)
        call LIBMUSCLE_DataConstRef_shape(d1, shp)
        call assert_true(all(shp(1:6) .eq. (/2, 2, 2, 2, 2, 3/)))
        call assert_false(LIBMUSCLE_DataConstRef_has_indexes(d1))
        call LIBMUSCLE_DataConstRef_elements(d1, ar86_b)
        call assert_true(all(ar86 .eq. ar86_b))
        call LIBMUSCLE_DataConstRef_free(d1)

        ! Data instead of DataConstRef
        ai83 = reshape(spread((/7_int8, -3_int8/), 1, 12), (/2, 3, 4/))
        d2 = LIBMUSCLE_Data_create_grid(ai83)
        call assert_true(LIBMUSCLE_Data_is_a_grid_of_int8(d2))
        call assert_false(LIBMUSCLE_Data_is_a_character(d2))
        call assert_eq_size(LIBMUSCLE_Data_num_dims(d2), 3_sz)
        call LIBMUSCLE_Data_shape(d2, shp)
        call assert_true(all(shp(1:3) .eq. (/2, 3, 4/)))
        call assert_false(LIBMUSCLE_Data_has_indexes(d2))
        call LIBMUSCLE_Data_elements(d2, ai83_b)
        call assert_true(all(ai83 .eq. ai83_b))
        call LIBMUSCLE_Data_free(d2)

        ! Indexes
        ar42 = reshape(spread((/3.3_real4, -7.6_real4/), 1, 3), (/2, 3/))
        d1 = LIBMUSCLE_DataConstRef_create_grid(ar42, 'x', 'y')
        call assert_true(LIBMUSCLE_DataConstRef_is_a_grid_of_real4(d1))
        call assert_false(LIBMUSCLE_DataConstRef_is_a_logical(d1))
        call assert_eq_size(LIBMUSCLE_DataConstRef_num_dims(d1), 2_sz)
        call LIBMUSCLE_DataConstRef_shape(d1, shp)
        call assert_true(all(shp(1:2) .eq. (/2, 3/)))
        call assert_true(LIBMUSCLE_DataConstRef_has_indexes(d1))
        call assert_eq_character(LIBMUSCLE_DataConstRef_index(d1, 1_sz), 'x')
        call assert_eq_character(LIBMUSCLE_DataConstRef_index(d1, 2_sz), 'y')
        call LIBMUSCLE_DataConstRef_elements(d1, ar42_b)
        call assert_true(all(ar42 .eq. ar42_b))
        call LIBMUSCLE_DataConstRef_free(d1)

        print *, '[       OK ] data.create_grid'
    end subroutine test_data_grid

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
end module data_tests

program test_data
    use data_tests
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
end program test_data

