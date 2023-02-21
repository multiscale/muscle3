program reaction
    use ymmsl
    use libmuscle
    implicit none

    type(LIBMUSCLE_PortsDescription) :: ports
    type(LIBMUSCLE_Instance) :: instance

    type(LIBMUSCLE_Message) :: rmsg
    type(LIBMUSCLE_DataConstRef) :: rdata, item


    type(LIBMUSCLE_Message) :: smsg
    type(LIBMUSCLE_Data) :: sdata, sitem

    real (selected_real_kind(15)) :: t_cur, t_max, dt, k
    real (selected_real_kind(15)), dimension(:), allocatable :: U


    ports = LIBMUSCLE_PortsDescription_create()
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_F_INIT, 'initial_state')
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_O_F, 'final_state')
    instance = LIBMUSCLE_Instance_create(ports, &
            LIBMUSCLE_InstanceFlags(USES_CHECKPOINT_API=.true.))
    call LIBMUSCLE_PortsDescription_free(ports)

    do while (LIBMUSCLE_Instance_reuse_instance(instance))
        ! F_INIT
        t_max = LIBMUSCLE_Instance_get_setting_as_real8(instance, 't_max')
        dt = LIBMUSCLE_Instance_get_setting_as_real8(instance, 'dt')
        k = LIBMUSCLE_Instance_get_setting_as_real8(instance, 'k')

        rmsg = LIBMUSCLE_Instance_receive(instance, 'initial_state')
        rdata = LIBMUSCLE_Message_get_data(rmsg)
        allocate (U(LIBMUSCLE_DataConstRef_size(rdata)))
        call LIBMUSCLE_DataConstRef_elements(rdata, U)
        call LIBMUSCLE_DataConstRef_free(rdata)

        t_cur = LIBMUSCLE_Message_timestamp(rmsg)
        t_max = LIBMUSCLE_Message_timestamp(rmsg) + t_max
        call LIBMUSCLE_Message_free(rmsg)

        do while (t_cur + dt < t_max)
            ! O_I

            ! S
            U = k * U * dt
            t_cur = t_cur + dt

            if (LIBMUSCLE_Instance_should_save_snapshot(instance, t_cur)) then
                sdata = LIBMUSCLE_Data_create_nils(2_LIBMUSCLE_size)
                sitem = LIBMUSCLE_Data_create_grid(U, 'x')
                call LIBMUSCLE_Data_set_item(sdata, 1_LIBMUSCLE_size, sitem)
                call LIBMUSCLE_Data_set_item(sdata, 2_LIBMUSCLE_size, t_max)
                smsg = LIBMUSCLE_Message_create(t_cur, sdata)
                call LIBMUSCLE_Instance_save_snapshot(instance, smsg)
                call LIBMUSCLE_Message_free(smsg)
                call LIBMUSCLE_Data_free(sitem)
                call LIBMUSCLE_Data_free(sdata)
            end if
        end do

        ! O_F
        sdata = LIBMUSCLE_Data_create_grid(U, 'x')
        smsg = LIBMUSCLE_Message_create(t_cur, sdata)
        call LIBMUSCLE_Instance_send(instance, 'final_state', smsg)
        call LIBMUSCLE_Message_free(smsg)
        call LIBMUSCLE_Data_free(sdata)
        deallocate (U)

        if (LIBMUSCLE_Instance_should_save_final_snapshot(instance)) then
            smsg = LIBMUSCLE_Message_create(t_cur)
            call LIBMUSCLE_Instance_save_final_snapshot(instance, smsg)
            call LIBMUSCLE_Message_free(smsg)
        end if
    end do

    call LIBMUSCLE_Instance_free(instance)

end program reaction

