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


    ports = LIBMUSCLE_PortsDescription()
    call ports%add(YMMSL_Operator_F_INIT, 'F_INIT_Port')
    call ports%add(YMMSL_Operator_O_I, 'O_I_Port')
    call ports%add(YMMSL_Operator_S, 'S_Port')
    call ports%add(YMMSL_Operator_O_F, 'O_F_Port')
    instance = LIBMUSCLE_Instance(ports)
    call LIBMUSCLE_PortsDescription_free(ports)

    do while (instance%reuse_instance())
        ! F_INIT
        setting = instance%get_setting_as_real8('setting')
        ! ...

        rmsg = instance%receive('F_INIT')
        call LIBMUSCLE_Message_free(rmsg)
        ! ...

        do while (t_cur <= t_max)
            ! O_I
            smsg = LIBMUSCLE_Message(t_cur, data)
            if (t_cur + dt <= t_max) then
                call smsg%set_next_timestamp(t_cur + dt)
            end if
            call instance%send('O_I', smsg)
            call LIBMUSCLE_Message_free(smsg)
            ! ...

            ! S
            rmsg = instance%receive('S')
            call LIBMUSCLE_Message_free(rmsg)
            ! ...

            t_cur = t_cur + dt
        end do

        ! O_F
        smsg = LIBMUSCLE_Message(t_cur, data)
        call instance%send('final_state', smsg)
        call LIBMUSCLE_Message_free(smsg)
        ! ...

    end do

    call LIBMUSCLE_Instance_free(instance)

end program reaction

