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
    integer :: i
    character(len=14) :: reply

    ports = LIBMUSCLE_PortsDescription_create()
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_F_INIT, 'in')
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_O_F, 'out')
    instance = LIBMUSCLE_Instance_create(ports)
    call LIBMUSCLE_PortsDescription_free(ports)

    i = 0
    do while (LIBMUSCLE_Instance_reuse_instance(instance))
        ! F_INIT
        call assert_eq_int8(LIBMUSCLE_Instance_get_setting_as_int8(instance, 'test1'), 13_LIBMUSCLE_int8)
        call assert_true(LIBMUSCLE_Instance_get_setting_as_logical(instance, 'test4'))

        msg = LIBMUSCLE_Instance_receive(instance, 'in')

        rdata = LIBMUSCLE_Message_get_data(msg)
        call assert_eq_character(LIBMUSCLE_DataConstRef_as_character(rdata), 'testing')
        call LIBMUSCLE_DataConstRef_free(rdata)

        ! O_F
        write (reply, '(A12, " ", I0)') 'testing back', i
        sdata = LIBMUSCLE_Data_create(reply)
        message = LIBMUSCLE_Message_create(LIBMUSCLE_Message_timestamp(msg), sdata)
        call LIBMUSCLE_Instance_send(instance, 'out', message)
        call LIBMUSCLE_Message_free(message)
        call LIBMUSCLE_Data_free(sdata)

        call LIBMUSCLE_Message_free(msg)
        i = i + 1
    end do

    call LIBMUSCLE_Instance_free(instance)

end program micro_model

