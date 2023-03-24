! This is a part of the integration test suite, and is run from a Python
! test in /integration_test. It is not a unit test.

program snapshot_macro
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
    real (LIBMUSCLE_real8) :: dt, t_max, t_cur, t_next

    ports = LIBMUSCLE_PortsDescription()
    call ports%add(YMMSL_Operator_O_I, 'o_i')
    call ports%add(YMMSL_Operator_S, 's')
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
            i = rdata%as_int()

            call LIBMUSCLE_DataConstRef_free(rdata)
            call LIBMUSCLE_Message_free(msg)
        end if

        if (instance%should_init()) then
            t_cur = instance%get_setting_as_real8('t0')
            i = 0
        end if

        do while (t_cur + dt <= t_max)
            sdata = LIBMUSCLE_Data(i)
            msg = LIBMUSCLE_Message(t_cur, sdata)
            t_next = t_cur + dt
            if (t_next + dt <= t_max) then
                call msg%set_next_timestamp(t_next)
            end if
            call instance%send('o_i', msg)
            call LIBMUSCLE_Message_free(msg)
            call LIBMUSCLE_Data_free(sdata)

            msg = instance%receive('s')
            rdata = msg%get_data()
            call assert_eq_integer(rdata%as_int(), i)
            call LIBMUSCLE_DataConstRef_free(rdata)
            call LIBMUSCLE_Message_free(msg)

            i = i + 1
            t_cur = t_cur + dt

            if (instance%should_save_snapshot(t_cur)) then
                sdata = LIBMUSCLE_Data(i)
                msg = LIBMUSCLE_Message(t_cur, sdata)
                call instance%save_snapshot(msg)
                call LIBMUSCLE_Message_free(msg)
                call LIBMUSCLE_Data_free(sdata)
            end if
        end do

        if (instance%should_save_final_snapshot()) then
            sdata = LIBMUSCLE_Data(i)
            msg = LIBMUSCLE_Message(t_cur, sdata)
            call instance%save_final_snapshot(msg)
            call LIBMUSCLE_Message_free(msg)
            call LIBMUSCLE_Data_free(sdata)
        end if
    end do

    call LIBMUSCLE_Instance_free(instance)

end program snapshot_macro
