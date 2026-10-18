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

    ports = LIBMUSCLE_PortsDescription()
    call ports%add(YMMSL_Operator_F_INIT, 'f_i')
    call ports%add(YMMSL_Operator_O_F, 'o_f')
    instance = LIBMUSCLE_Instance( &
        ports, LIBMUSCLE_InstanceFlags(USES_CHECKPOINT_API=.true.))
    call LIBMUSCLE_PortsDescription_free(ports)

    do while (instance%reuse_instance())
        dt = instance%get_setting_as_real8('dt')
        t_max = instance%get_setting_as_real8('t_max')

        if (instance%resuming()) then
            msg = instance%load_snapshot()
            ! load state from message
            t_cur = msg%timestamp()
            rdata = msg%get_data()

            rdata2 = rdata%get_item(1_LIBMUSCLE_size)
            i = rdata2%as_int()
            call LIBMUSCLE_DataConstRef_free(rdata2)

            rdata2 = rdata%get_item(2_LIBMUSCLE_size)
            t_stop = rdata2%as_real8()
            call LIBMUSCLE_DataConstRef_free(rdata2)

            call LIBMUSCLE_DataConstRef_free(rdata)
            call LIBMUSCLE_Message_free(msg)
        end if

        if (instance%should_init()) then
            msg = instance%receive('f_i')
            t_cur = msg%timestamp()

            rdata = msg%get_data()
            i = rdata%as_int()
            t_stop = t_cur + t_max

            call LIBMUSCLE_DataConstRef_free(rdata)
            call LIBMUSCLE_Message_free(msg)
        end if

        do while (t_cur <= t_stop)
            ! faux time-integration for testing snapshots
            t_cur = t_cur + dt

            if (instance%should_save_snapshot(t_cur)) then
                sdata = LIBMUSCLE_Data_create_nils(2_LIBMUSCLE_size)
                call sdata%set_item(1_LIBMUSCLE_size, i)
                call sdata%set_item(2_LIBMUSCLE_size, t_stop)

                msg = LIBMUSCLE_Message(t_cur, sdata)
                call instance%save_snapshot(msg)

                call LIBMUSCLE_Message_free(msg)
                call LIBMUSCLE_Data_free(sdata)
            end if
        end do

        sdata = LIBMUSCLE_Data(i)
        msg = LIBMUSCLE_Message(t_cur, sdata)
        call instance%send('o_f', msg)
        call LIBMUSCLE_Data_free(sdata)
        call LIBMUSCLE_Message_free(msg)

        if (instance%should_save_final_snapshot()) then
            sdata = LIBMUSCLE_Data_create_nils(2_LIBMUSCLE_size)
            call sdata%set_item(1_LIBMUSCLE_size, i)
            call sdata%set_item(2_LIBMUSCLE_size, t_stop)

            msg = LIBMUSCLE_Message(t_cur, sdata)
            call instance%save_final_snapshot(msg)

            call LIBMUSCLE_Message_free(msg)
            call LIBMUSCLE_Data_free(sdata)
        end if
    end do

    call LIBMUSCLE_Instance_free(instance)

end program snapshot_micro
