! This is a part of the integration test suite, and is run from a Python
! test in /integration_test. It is not a unit test.

program micro_model
    use assert
    use ymmsl
    use libmuscle
    implicit none

    type(LIBMUSCLE_PortsDescription) :: ports
    type(LIBMUSCLE_Instance) :: instance
    type(LIBMUSCLE_Message) :: msg
    type(LIBMUSCLE_DataConstRef) :: rdata
    type(LIBMUSCLE_Message) :: message
    type(LIBMUSCLE_Data) :: sdata
    logical :: python_compat
    integer :: i

    ports = LIBMUSCLE_PortsDescription()
    call ports%add(YMMSL_Operator_F_INIT, 'in')
    call ports%add(YMMSL_Operator_O_F, 'out')
    instance = LIBMUSCLE_Instance(ports)
    call LIBMUSCLE_PortsDescription_free(ports)

    i = 0
    do while (instance%reuse_instance())
        ! F_INIT
        call check_settings(instance)

        python_compat = instance%get_setting_as_logical('python_compat')

        msg = instance%receive('in')
        rdata = msg%get_data()
        call check_data(rdata, python_compat)
        call LIBMUSCLE_DataConstRef_free(rdata)

        ! O_F
        sdata = make_data()
        message = LIBMUSCLE_Message(msg%timestamp(), sdata)
        call instance%send('out', message)
        call LIBMUSCLE_Message_free(message)
        call LIBMUSCLE_Data_free(sdata)
        call LIBMUSCLE_Message_free(msg)

        i = i + 1
    end do

    call LIBMUSCLE_Instance_free(instance)

contains

    subroutine check_settings(instance)
        implicit none

        type(LIBMUSCLE_Instance) :: instance
        character(:), dimension(:), allocatable :: settings
        character(:), allocatable :: setting
        logical, dimension(8) :: setting_seen
        integer :: i, err_code
        logical :: is_int

        settings = instance%list_settings()
        ! test1-6, test_with_a_longer_name, python_compat
        call assert_eq_integer(size(settings, 1), 8)
        do i = 1, size(settings, 1)
            setting = settings(i)
            if (trim(setting) .eq. 'test1') then
                setting_seen(1) = .true.
            elseif (trim(setting) .eq. 'test2') then
                setting_seen(2) = .true.
            elseif (trim(setting) .eq. 'test3') then
                setting_seen(3) = .true.
            elseif (trim(setting) .eq. 'test4') then
                setting_seen(4) = .true.
            elseif (trim(setting) .eq. 'test5') then
                setting_seen(5) = .true.
            elseif (trim(setting) .eq. 'test6') then
                setting_seen(6) = .true.
            elseif (trim(setting) .eq. 'test_with_a_longer_name') then
                setting_seen(7) = .true.
            elseif (trim(setting) .eq. 'python_compat') then
                setting_seen(8) = .true.
            else
                print *, 'Unexpected setting name: ', trim(setting)
                stop 1
            endif
        end do
        call assert_true(all(setting_seen))

        call assert_true(instance%is_setting_a_int8('test1'))
        call assert_false(instance%is_setting_a_logical('test1'))
        is_int = instance%is_setting_a_int8('does_not_exist', err_code)
        call assert_eq_integer(err_code, LIBMUSCLE_out_of_range)

        call assert_eq_int8(instance%get_setting_as_int8('test1'), 13_LIBMUSCLE_int8)
        call assert_true(instance%get_setting_as_logical('test4'))

        ! Test get_setting_with_default_as functions (scalar types only)
        call assert_eq_int8( &
                instance%get_setting_as_int8('test1', 99_LIBMUSCLE_int8), &
                13_LIBMUSCLE_int8)
        call assert_eq_int8( &
                instance%get_setting_as_int8('does_not_exist', 99_LIBMUSCLE_int8), &
                99_LIBMUSCLE_int8)
        call assert_true(instance%get_setting_as_logical('test4', .false.))
        call assert_false(instance%get_setting_as_logical('does_not_exist', .false.))
        call assert_eq_real8(instance%get_setting_as_real8('test2', 99.0d0), 13.3d0)
        call assert_eq_real8( &
                instance%get_setting_as_real8('does_not_exist', 99.0d0), 99.0d0)
        call assert_eq_character( &
                instance%get_setting_as_character('test3', 'default'), 'testing')
        call assert_eq_character( &
                instance%get_setting_as_character('does_not_exist', 'default'), &
                'default')
    end subroutine check_settings

    subroutine check_data(rdata, python_compat)
        implicit none

        type(LIBMUSCLE_DataConstRef) :: rdata, rdata2, rlist, rgrid
        logical :: python_compat
        integer (LIBMUSCLE_size), dimension(2) :: rshape
        real (LIBMUSCLE_real8), dimension(:, :), allocatable :: test_grid

        rdata2 = rdata%get_item('bool')
        call assert_true(rdata2%as_logical())
        call LIBMUSCLE_DataConstRef_free(rdata2)

        rdata2 = rdata%get_item('char')
        call assert_eq_int1(rdata2%as_int1(), 23_LIBMUSCLE_int1)
        call LIBMUSCLE_DataConstRef_free(rdata2)

        rdata2 = rdata%get_item('short int')
        call assert_eq_int2(rdata2%as_int2(), 4097_LIBMUSCLE_int2)
        call LIBMUSCLE_DataConstRef_free(rdata2)

        rdata2 = rdata%get_item('int')
        call assert_eq_int4(rdata2%as_int4(), 1234567_LIBMUSCLE_int4)
        call LIBMUSCLE_DataConstRef_free(rdata2)

        rdata2 = rdata%get_item('long int')
        call assert_eq_int4(rdata2%as_int4(), 1234568_LIBMUSCLE_int4)
        call LIBMUSCLE_DataConstRef_free(rdata2)

        rdata2 = rdata%get_item('long long int')
        call assert_eq_int8(rdata2%as_int8(), 6001002003_LIBMUSCLE_int8)
        call LIBMUSCLE_DataConstRef_free(rdata2)

        if (.not. python_compat) then
            rdata2 = rdata%get_item('float')
            call assert_eq_real4(rdata2%as_real4(), 1.23456_LIBMUSCLE_real4)
            call LIBMUSCLE_DataConstRef_free(rdata2)
        end if

        rdata2 = rdata%get_item('double')
        call assert_eq_real8(rdata2%as_real8(), 1.2345678901234_LIBMUSCLE_real8)
        call LIBMUSCLE_DataConstRef_free(rdata2)

        rdata2 = rdata%get_item('message')
        call assert_eq_character(rdata2%as_character(), 'testing')
        call LIBMUSCLE_DataConstRef_free(rdata2)

        rlist = rdata%get_item('list')

        rdata2 = rlist%get_item(1_LIBMUSCLE_size)
        call assert_eq_int4(rdata2%as_int4(), 1)
        call LIBMUSCLE_DataConstRef_free(rdata2)

        rdata2 = rlist%get_item(2_LIBMUSCLE_size)
        call assert_eq_character(rdata2%as_character(), 'two')
        call LIBMUSCLE_DataConstRef_free(rdata2)

        if (.not. python_compat) then
            rdata2 = rlist%get_item(3_LIBMUSCLE_size)
            call assert_eq_real4(rdata2%as_real4(), 3.0_LIBMUSCLE_real4)
            call LIBMUSCLE_DataConstRef_free(rdata2)
        end if

        call LIBMUSCLE_DataConstRef_free(rlist)

        rgrid = rdata%get_item('test_grid')
        call assert_true(LIBMUSCLE_DataConstref_is_a_grid_of_real8(rgrid))
        call assert_eq_size(rgrid%num_dims(), 2_LIBMUSCLE_size)
        call rgrid%shape(rshape)
        call assert_eq_size(rshape(1), 2_LIBMUSCLE_size)
        call assert_eq_size(rshape(2), 3_LIBMUSCLE_size)

        allocate (test_grid(rshape(1), rshape(2)))
        call rgrid%elements(test_grid)
        call assert_eq_real8(test_grid(1, 2), 2.0d0)

        deallocate (test_grid)
        call LIBMUSCLE_DataConstRef_free(rgrid)
    end subroutine check_data

    function make_data()
        implicit none

        real (LIBMUSCLE_real8), dimension(2, 3) :: test_grid_data
        type(LIBMUSCLE_Data) :: make_data, sgrid, slist

        make_data = LIBMUSCLE_Data_create_dict()
        call make_data%set_item('bool', .true.)
        call make_data%set_item('char', 23_LIBMUSCLE_int1)
        call make_data%set_item('short int', 4097_LIBMUSCLE_int2)
        call make_data%set_item('int', 1234567_LIBMUSCLE_int4)
        call make_data%set_item('long int', 1234568_LIBMUSCLE_int4)
        call make_data%set_item('long long int', 6001002003_LIBMUSCLE_int8)
        call make_data%set_item('float', 1.23456_LIBMUSCLE_real4)
        call make_data%set_item('double', 1.2345678901234_LIBMUSCLE_real8)
        call make_data%set_item('message', 'testing')

        slist = LIBMUSCLE_DATA_create_nils(3_LIBMUSCLE_size)
        call slist%set_item(1_LIBMUSCLE_size, 1)
        call slist%set_item(2_LIBMUSCLE_size, 'two')
        call slist%set_item(3_LIBMUSCLE_size, 3.0_LIBMUSCLE_real4)

        call make_data%set_item('list', slist)
        call LIBMUSCLE_Data_free(slist)

        test_grid_data = reshape((/1., 4., 2., 5., 3., 6./), (/2, 3/))
        sgrid = LIBMUSCLE_Data_create_grid(test_grid_data)
        call make_data%set_item('test_grid', sgrid)

        call LIBMUSCLE_Data_free(sgrid)
    end function make_data

end program micro_model

