! This is a part of the integration test suite, and is run from a Python
! test in /integration_test. It is not a unit test.

program snapshot_macro_vector
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
    integer :: i, slot
    real (LIBMUSCLE_real8) :: dt, t_max, t_cur, t_next

    ports = LIBMUSCLE_PortsDescription_create()
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_O_I, 'o_i[]')
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_S, 's[]')
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
            i = LIBMUSCLE_DataConstRef_as_int(rdata)

            call LIBMUSCLE_DataConstRef_free(rdata)
            call LIBMUSCLE_Message_free(msg)
        end if

        if (LIBMUSCLE_Instance_should_init(instance)) then
            t_cur = LIBMUSCLE_Instance_get_setting_as_real8(instance, 't0')
            i = 0
        end if

        do while (t_cur + dt <= t_max)
            sdata = LIBMUSCLE_Data_create(i)
            msg = LIBMUSCLE_Message_create(t_cur, sdata)
            t_next = t_cur + dt
            if (t_next + dt <= t_max) then
                call LIBMUSCLE_Message_set_next_timestamp(msg, t_next)
            end if
            do slot = 1, LIBMUSCLE_Instance_get_port_length(instance, 'o_i')
                call LIBMUSCLE_Instance_send(instance, 'o_i', msg, slot - 1)
            end do
            call LIBMUSCLE_Message_free(msg)
            call LIBMUSCLE_Data_free(sdata)

            do slot = 1, LIBMUSCLE_Instance_get_port_length(instance, 's')
                msg = LIBMUSCLE_Instance_receive_on_slot(instance, 's', slot - 1)
                rdata = LIBMUSCLE_Message_get_data(msg)
                call assert_eq_integer(LIBMUSCLE_DataConstRef_as_int(rdata), i)
                call LIBMUSCLE_DataConstRef_free(rdata)
                call LIBMUSCLE_Message_free(msg)
            end do

            i = i + 1
            t_cur = t_cur + dt

            if (LIBMUSCLE_Instance_should_save_snapshot(instance, t_cur)) then
                sdata = LIBMUSCLE_Data_create(i)
                msg = LIBMUSCLE_Message_create(t_cur, sdata)
                call LIBMUSCLE_Instance_save_snapshot(instance, msg)
                call LIBMUSCLE_Message_free(msg)
                call LIBMUSCLE_Data_free(sdata)
            end if
        end do

        if (LIBMUSCLE_Instance_should_save_final_snapshot(instance)) then
            sdata = LIBMUSCLE_Data_create(i)
            msg = LIBMUSCLE_Message_create(t_cur, sdata)
            call LIBMUSCLE_Instance_save_final_snapshot(instance, msg)
            call LIBMUSCLE_Message_free(msg)
            call LIBMUSCLE_Data_free(sdata)
        end if
    end do

    call LIBMUSCLE_Instance_free(instance)

end program snapshot_macro_vector
