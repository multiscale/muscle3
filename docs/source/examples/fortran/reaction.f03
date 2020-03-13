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
    integer (LIBMUSCLE_size) :: i, U_size
    real (selected_real_kind(15)), dimension(:), allocatable :: U


    ports = LIBMUSCLE_PortsDescription_create()
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_F_INIT, 'initial_state')
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_O_F, 'final_state')
    instance = LIBMUSCLE_Instance_create(ports)
    call LIBMUSCLE_PortsDescription_free(ports)

    do while (LIBMUSCLE_Instance_reuse_instance(instance))
        ! F_INIT
        t_max = LIBMUSCLE_Instance_get_setting_as_real8(instance, 't_max')
        dt = LIBMUSCLE_Instance_get_setting_as_real8(instance, 'dt')
        k = LIBMUSCLE_Instance_get_setting_as_real8(instance, 'k')

        rmsg = LIBMUSCLE_Instance_receive(instance, 'initial_state')
        rdata = LIBMUSCLE_Message_get_data(rmsg)

        U_size = LIBMUSCLE_DataConstRef_size(rdata)
        allocate (U(U_size))
        do i = 1, U_size
            item = LIBMUSCLE_DataConstRef_get_item(rdata, i)
            U(i) = LIBMUSCLE_DataConstRef_as_real8(item)
            call LIBMUSCLE_DataConstRef_free(item)
        end do
        call LIBMUSCLE_DataConstRef_free(rdata)

        t_cur = LIBMUSCLE_Message_timestamp(rmsg)
        t_max = LIBMUSCLE_Message_timestamp(rmsg) + t_max
        call LIBMUSCLE_Message_free(rmsg)

        do while (t_cur + dt < t_max)
            ! O_I

            ! S
            U = k * U * dt
            t_cur = t_cur + dt
        end do

        ! O_F
        sdata = LIBMUSCLE_Data_create_nils(U_size)
        do i = 1, U_size
            call LIBMUSCLE_Data_set_item(sdata, i, U(i))
        end do

        smsg = LIBMUSCLE_Message_create(t_cur, sdata)
        call LIBMUSCLE_Instance_send(instance, 'final_state', smsg)

        call LIBMUSCLE_Message_free(smsg)
        call LIBMUSCLE_Data_free(sdata)
        deallocate (U)
    end do

    call LIBMUSCLE_Instance_free(instance)

end program reaction

