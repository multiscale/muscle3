! This is a part of the integration test suite, and is run from a Python
! test in /integration_test. It is not a unit test.

program snapshot_micro
    use assert
    use ymmsl
    use libmuscle
    implicit none

    type(LIBMUSCLE_PortsDescription) :: ports
    type(LIBMUSCLE_Instance) :: instance
    type(LIBMUSCLE_Message) :: msg
    type(LIBMUSCLE_DataConstRef) :: rdata, rdata2
    type(LIBMUSCLE_Message) :: message
    type(LIBMUSCLE_Data) :: sdata
    integer :: i
    real (LIBMUSCLE_real8) :: dt, t_max, t_cur, t_next, t_stop

    ports = LIBMUSCLE_PortsDescription_create()
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_F_INIT, 'f_i')
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_O_F, 'o_f')
    instance = LIBMUSCLE_Instance_create( &
        ports, LIBMUSCLE_InstanceFlags(KEEPS_NO_STATE_FOR_NEXT_USE=.true.))
    call LIBMUSCLE_PortsDescription_free(ports)

    do while(LIBMUSCLE_Instance_reuse_instance(instance))
        dt = LIBMUSCLE_Instance_get_setting_as_real8(instance, 'dt')
        t_max = LIBMUSCLE_Instance_get_setting_as_real8(instance, 't_max')

        msg = LIBMUSCLE_Instance_receive(instance, 'f_i')
        t_cur = LIBMUSCLE_Message_timestamp(msg)

        rdata = LIBMUSCLE_Message_get_data(msg)
        i = LIBMUSCLE_DataConstRef_as_int(rdata)
        t_stop = t_cur + t_max

        call LIBMUSCLE_DataConstRef_free(rdata)
        call LIBMUSCLE_Message_free(msg)

        do while (t_cur <= t_stop)
            ! faux time-integration for testing snapshots
            t_cur = t_cur + dt
        end do

        sdata = LIBMUSCLE_Data_create(i)
        msg = LIBMUSCLE_Message_create(t_cur, sdata)
        call LIBMUSCLE_Instance_send(instance, 'o_f', msg)
        call LIBMUSCLE_Data_free(sdata)
        call LIBMUSCLE_Message_free(msg)
    end do

    call LIBMUSCLE_Instance_free(instance)

end program snapshot_micro
