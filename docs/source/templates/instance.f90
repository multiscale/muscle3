program instance
    ! MUSCLE3 Fortran component template.
    !
    ! Note that this template is not executable as is, please have a look at the
    ! examples in ``docs/source/examples`` to see working components.

    use ymmsl
    use libmuscle
    implicit none

    type(LIBMUSCLE_PortsDescription) :: ports
    type(LIBMUSCLE_Instance) :: instance

    type(LIBMUSCLE_Message) :: rmsg, smsg
    type(LIBMUSCLE_Data) :: data

    real (selected_real_kind(15)) :: t_cur, t_max, dt


    ports = LIBMUSCLE_PortsDescription_create()
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_F_INIT, 'F_INIT_Port')
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_O_I, 'O_I_Port')
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_S, 'S_Port')
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_O_F, 'O_F_Port')
    instance = LIBMUSCLE_Instance_create(ports)
    call LIBMUSCLE_PortsDescription_free(ports)

    do while (LIBMUSCLE_Instance_reuse_instance(instance))
        ! F_INIT
        setting = LIBMUSCLE_Instance_get_setting_as_real8(instance, 'setting')
        ! ...

        rmsg = LIBMUSCLE_Instance_receive(instance, 'F_INIT')
        call LIBMUSCLE_Message_free(rmsg)
        ! ...

        do while (t_cur <= t_max)
            ! O_I
            smsg = LIBMUSCLE_Message_create(t_cur, data)
            if (t_cur + dt <= t_max) then
                call LIBMUSCLE_Message_set_next_timestamp(smsg, t_cur + dt)
            end if
            call LIBMUSCLE_Instance_send(instance, 'O_I', smsg)
            call LIBMUSCLE_Message_free(smsg)
            ! ...

            ! S
            rmsg = LIBMUSCLE_Instance_receive(instance, 'S')
            call LIBMUSCLE_Message_free(rmsg)
            ! ...

            t_cur = t_cur + dt
        end do

        ! O_F
        smsg = LIBMUSCLE_Message_create(t_cur, data)
        call LIBMUSCLE_Instance_send(instance, 'final_state', smsg)
        call LIBMUSCLE_Message_free(smsg)
        ! ...

    end do

    call LIBMUSCLE_Instance_free(instance)

end program reaction

