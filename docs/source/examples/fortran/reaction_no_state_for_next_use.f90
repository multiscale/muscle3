program reaction
    use ymmsl
    use libmuscle
    implicit none

    type(LIBMUSCLE_PortsDescription) :: ports
    type(LIBMUSCLE_Instance) :: instance

    type(LIBMUSCLE_Message) :: rmsg
    type(LIBMUSCLE_DataConstRef) :: rdata, item


    type(LIBMUSCLE_Message) :: smsg
    type(LIBMUSCLE_Data) :: sdata

    real (selected_real_kind(15)) :: t_cur, t_max, dt, k
    real (selected_real_kind(15)), dimension(:), allocatable :: U


    ports = LIBMUSCLE_PortsDescription()
    call ports%add(YMMSL_Operator_F_INIT, 'initial_state')
    call ports%add(YMMSL_Operator_O_F, 'final_state')
    instance = LIBMUSCLE_Instance(ports, &
            LIBMUSCLE_InstanceFlags(KEEPS_NO_STATE_FOR_NEXT_USE=.true.))
    call LIBMUSCLE_PortsDescription_free(ports)

    do while (instance%reuse_instance())
        ! F_INIT
        t_max = instance%get_setting_as_real8('t_max')
        dt = instance%get_setting_as_real8('dt')
        k = instance%get_setting_as_real8('k')

        rmsg = instance%receive('initial_state')
        rdata = rmsg%get_data()
        allocate (U(rdata%size()))
        call rdata%elements(U)
        call LIBMUSCLE_DataConstRef_free(rdata)

        t_cur = rmsg%timestamp()
        t_max = rmsg%timestamp() + t_max
        call LIBMUSCLE_Message_free(rmsg)

        do while (t_cur + dt < t_max)
            ! O_I

            ! S
            U = k * U * dt
            t_cur = t_cur + dt
        end do

        ! O_F
        sdata = LIBMUSCLE_Data_create_grid(U, 'x')
        smsg = LIBMUSCLE_Message(t_cur, sdata)
        call instance%send('final_state', smsg)
        call LIBMUSCLE_Message_free(smsg)
        call LIBMUSCLE_Data_free(sdata)
        deallocate (U)
    end do

    call LIBMUSCLE_Instance_free(instance)

end program reaction

