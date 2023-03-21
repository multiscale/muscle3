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
        ports, LIBMUSCLE_InstanceFlags(USES_CHECKPOINT_API=.true.))
    call LIBMUSCLE_PortsDescription_free(ports)

    do while (LIBMUSCLE_Instance_reuse_instance(instance))
        dt = LIBMUSCLE_Instance_get_setting_as_real8(instance, 'dt')
        t_max = LIBMUSCLE_Instance_get_setting_as_real8(instance, 't_max')

        if (LIBMUSCLE_Instance_resuming(instance)) then
            msg = LIBMUSCLE_Instance_load_snapshot(instance)
            ! load state from message
            t_cur = LIBMUSCLE_Message_timestamp(msg)
            rdata = LIBMUSCLE_Message_get_data(msg)

            rdata2 = LIBMUSCLE_DataConstRef_get_item(rdata, 1_LIBMUSCLE_size)
            i = LIBMUSCLE_DataConstRef_as_int(rdata2)
            call LIBMUSCLE_DataConstRef_free(rdata2)

            rdata2 = LIBMUSCLE_DataConstRef_get_item(rdata, 2_LIBMUSCLE_size)
            t_stop = LIBMUSCLE_DataConstRef_as_real8(rdata2)
            call LIBMUSCLE_DataConstRef_free(rdata2)

            call LIBMUSCLE_DataConstRef_free(rdata)
            call LIBMUSCLE_Message_free(msg)
        end if

        if (LIBMUSCLE_Instance_should_init(instance)) then
            msg = LIBMUSCLE_Instance_receive(instance, 'f_i')
            t_cur = LIBMUSCLE_Message_timestamp(msg)

            rdata = LIBMUSCLE_Message_get_data(msg)
            i = LIBMUSCLE_DataConstRef_as_int(rdata)
            t_stop = t_cur + t_max

            call LIBMUSCLE_DataConstRef_free(rdata)
            call LIBMUSCLE_Message_free(msg)
        end if

        do while (t_cur <= t_stop)
            ! faux time-integration for testing snapshots
            t_cur = t_cur + dt

            if (LIBMUSCLE_Instance_should_save_snapshot(instance, t_cur)) then
                sdata = LIBMUSCLE_Data_create_nils(2_LIBMUSCLE_size)
                call LIBMUSCLE_Data_set_item(sdata, 1_LIBMUSCLE_size, i)
                call LIBMUSCLE_Data_set_item(sdata, 2_LIBMUSCLE_size, t_stop)

                msg = LIBMUSCLE_Message_create(t_cur, sdata)
                call LIBMUSCLE_Instance_save_snapshot(instance, msg)

                call LIBMUSCLE_Message_free(msg)
                call LIBMUSCLE_Data_free(sdata)
            end if
        end do

        sdata = LIBMUSCLE_Data_create(i)
        msg = LIBMUSCLE_Message_create(t_cur, sdata)
        call LIBMUSCLE_Instance_send(instance, 'o_f', msg)
        call LIBMUSCLE_Data_free(sdata)
        call LIBMUSCLE_Message_free(msg)

        if (LIBMUSCLE_Instance_should_save_final_snapshot(instance)) then
            sdata = LIBMUSCLE_Data_create_nils(2_LIBMUSCLE_size)
            call LIBMUSCLE_Data_set_item(sdata, 1_LIBMUSCLE_size, i)
            call LIBMUSCLE_Data_set_item(sdata, 2_LIBMUSCLE_size, t_stop)

            msg = LIBMUSCLE_Message_create(t_cur, sdata)
            call LIBMUSCLE_Instance_save_final_snapshot(instance, msg)

            call LIBMUSCLE_Message_free(msg)
            call LIBMUSCLE_Data_free(sdata)
        end if
    end do

    call LIBMUSCLE_Instance_free(instance)

end program snapshot_micro
