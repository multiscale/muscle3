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
    type(LIBMUSCLE_DataConstRef) :: rdata, rdata2, rgrid
    type(LIBMUSCLE_Message) :: message
    type(LIBMUSCLE_Data) :: sdata, sgrid
    integer :: i, err_code
    integer (LIBMUSCLE_size), dimension(2) :: rshape
    real (LIBMUSCLE_real8), dimension(:, :), allocatable :: test_grid
    integer (LIBMUSCLE_int8), dimension(2, 3) :: test_grid_data

    character(len=14) :: reply
    logical :: is_int

    ports = LIBMUSCLE_PortsDescription_create()
    call ports%add(YMMSL_Operator_F_INIT, 'in')
    call ports%add(YMMSL_Operator_O_F, 'out')
    instance = LIBMUSCLE_Instance_create(ports)

    i = 0
    do while (instance%reuse_instance())
        ! F_INIT
        call assert_true(instance%is_setting_a_int8('test1'))
        call assert_false(instance%is_setting_a_logical('test1'))
        is_int = instance%is_setting_a_int8('does_not_exist', err_code)
        call assert_eq_integer(err_code, LIBMUSCLE_out_of_range)

        call assert_eq_int8(instance%get_setting_as_int8('test1'), 13_LIBMUSCLE_int8)
        call assert_true(instance%get_setting_as_logical('test4'))

        msg = instance%receive('in')

        rdata = msg%get_data()
        rdata2 = rdata%get_item('message')
        call assert_eq_character(rdata2%as_character(), 'testing')

        rgrid = rdata%get_item('test_grid')
        call assert_true(rgrid%is_a_grid_of_real8())
        call assert_eq_size(rgrid%num_dims(), 2_LIBMUSCLE_size)
        call rgrid%shape(rshape)
        call assert_eq_size(rshape(1), 2_LIBMUSCLE_size)
        call assert_eq_size(rshape(2), 3_LIBMUSCLE_size)

        allocate (test_grid(rshape(1), rshape(2)))
        call rgrid%elements(test_grid)
        call assert_eq_real8(test_grid(1, 2), 2.0d0)

        deallocate (test_grid)

        ! O_F
        write (reply, '(A12, " ", I0)') 'testing back', i
        test_grid_data = int(reshape((/1, 4, 2, 5, 3, 6/), (/2, 3/)), LIBMUSCLE_int8)
        sgrid = LIBMUSCLE_Data_create_grid(test_grid_data)
        sdata = LIBMUSCLE_Data_create_dict()
        call sdata%set_item('reply', reply)
        call sdata%set_item('test_grid', sgrid)
        message = LIBMUSCLE_Message_create(msg%timestamp(), sdata)
        call instance%send('out', message)

        i = i + 1
    end do

end program micro_model

