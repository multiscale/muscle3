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
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_F_INIT, 'in')
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_O_F, 'out')
    instance = LIBMUSCLE_Instance_create(ports)
    call LIBMUSCLE_PortsDescription_free(ports)

    i = 0
    do while (LIBMUSCLE_Instance_reuse_instance(instance))
        ! F_INIT
        call assert_true(LIBMUSCLE_Instance_is_setting_a_int8(instance, 'test1'))
        call assert_false(LIBMUSCLE_Instance_is_setting_a_logical(instance, 'test1'))
        is_int = LIBMUSCLE_Instance_is_setting_a_int8(instance, 'does_not_exist', err_code)
        call assert_eq_integer(err_code, LIBMUSCLE_out_of_range)

        call assert_eq_int8(LIBMUSCLE_Instance_get_setting_as_int8(instance, 'test1'), 13_LIBMUSCLE_int8)
        call assert_true(LIBMUSCLE_Instance_get_setting_as_logical(instance, 'test4'))

        msg = LIBMUSCLE_Instance_receive(instance, 'in')

        rdata = LIBMUSCLE_Message_get_data(msg)
        rdata2 = LIBMUSCLE_DataConstRef_get_item(rdata, 'message')
        call assert_eq_character(LIBMUSCLE_DataConstRef_as_character(rdata2), 'testing')
        call LIBMUSCLE_DataConstRef_free(rdata2)

        rgrid = LIBMUSCLE_DataConstRef_get_item(rdata, 'test_grid')
        call assert_true(LIBMUSCLE_DataConstref_is_a_grid_of_real8(rgrid))
        call assert_eq_size(LIBMUSCLE_DataConstRef_num_dims(rgrid), 2_LIBMUSCLE_size)
        call LIBMUSCLE_DataConstRef_shape(rgrid, rshape)
        call assert_eq_size(rshape(1), 2_LIBMUSCLE_size)
        call assert_eq_size(rshape(2), 3_LIBMUSCLE_size)

        allocate (test_grid(rshape(1), rshape(2)))
        call LIBMUSCLE_DataConstRef_elements(rgrid, test_grid)
        call assert_eq_real8(test_grid(1, 2), 2.0d0)

        deallocate (test_grid)
        call LIBMUSCLE_DataConstRef_free(rgrid)
        call LIBMUSCLE_DataConstRef_free(rdata)

        ! O_F
        write (reply, '(A12, " ", I0)') 'testing back', i
        test_grid_data = int(reshape((/1, 4, 2, 5, 3, 6/), (/2, 3/)), LIBMUSCLE_int8)
        sgrid = LIBMUSCLE_Data_create_grid(test_grid_data)
        sdata = LIBMUSCLE_Data_create_dict()
        call LIBMUSCLE_Data_set_item(sdata, 'reply', reply)
        call LIBMUSCLE_Data_set_item(sdata, 'test_grid', sgrid)
        message = LIBMUSCLE_Message_create(LIBMUSCLE_Message_timestamp(msg), sdata)
        call LIBMUSCLE_Instance_send(instance, 'out', message)
        call LIBMUSCLE_Message_free(message)
        call LIBMUSCLE_Data_free(sdata)
        call LIBMUSCLE_Data_free(sgrid)

        call LIBMUSCLE_Message_free(msg)
        i = i + 1
    end do

    call LIBMUSCLE_Instance_free(instance)

end program micro_model

