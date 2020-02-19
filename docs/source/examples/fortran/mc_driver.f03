! A driver for plain Monte Carlo Uncertainty Quantification.
!
! This component attaches to a collection of model instances, and feeds
! in different parameter values generated pseudorandomly.
!
! Note that this uses pseudorandom numbers rather than a Sobol sequence
! like in the Python example, so as to avoid a dependency on a Sobol
! library. If you want to practice a bit, try splitting off the
! Sobol-based qmc driver from the Python example into a separate file,
! then run it instead of this component with the rest of the C++
! simulation.

program mc_driver
    use ymmsl
    use libmuscle
    implicit none

    type(LIBMUSCLE_PortsDescription) :: ports
    type(LIBMUSCLE_Instance) :: instance

    type(YMMSL_Settings) :: uq_parameters
    type(LIBMUSCLE_Message) :: smsg
    type(LIBMUSCLE_Data) :: sdata, means

    type(LIBMUSCLE_Message) :: rmsg
    type(LIBMUSCLE_DataConstRef) :: rdata

    integer (LIBMUSCLE_int4) :: sample, n_samples
    integer (LIBMUSCLE_size) :: i, U_size
    real (selected_real_kind(15)) :: d_min, d_max, k_min, k_max, t_max
    real (selected_real_kind(15)), dimension(:), allocatable :: ds, ks
    real (selected_real_kind(15)), dimension(:, :), allocatable :: Us


    ports = LIBMUSCLE_PortsDescription_create()
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_O_I, 'parameters_out[]')
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_S, 'states_in[]')
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_O_F, 'mean_out')
    instance = LIBMUSCLE_Instance_create(ports)
    call LIBMUSCLE_PortsDescription_free(ports)

    do while (LIBMUSCLE_Instance_reuse_instance(instance))
        ! F_INIT
        ! get and check parameter distributions
        n_samples = LIBMUSCLE_Instance_get_setting_as_int8(instance, 'n_samples')
        d_min = LIBMUSCLE_Instance_get_setting_as_real8(instance, 'd_min')
        d_max = LIBMUSCLE_Instance_get_setting_as_real8(instance, 'd_max')
        k_min = LIBMUSCLE_Instance_get_setting_as_real8(instance, 'k_min')
        k_max = LIBMUSCLE_Instance_get_setting_as_real8(instance, 'k_max')

        if (d_max < d_min) then
            call LIBMUSCLE_Instance_error_shutdown(instance, 'Invalid settings: d_max < d_min')
            stop
        end if

        if (k_max < k_min) then
            call LIBMUSCLE_Instance_error_shutdown(instance, 'Invalid settings: k_max < k_min')
            stop
        end if

        ! generate UQ parameter values
        allocate (ds(n_samples), ks(n_samples))
        call random_number(ds)
        ds = d_min + ds * (d_max - d_min)
        call random_number(ks)
        ks = k_min + ks * (k_max - k_min)

        ! configure output port
        if (.not. LIBMUSCLE_Instance_is_resizable(instance, 'parameters_out')) then
            call LIBMUSCLE_Instance_error_shutdown(instance, &
                'This component needs a resizable parameters_out port, but it&
                & is connected to something that cannot be resized. Maybe try&
                & adding a load balancer.')
            stop
        end if

        call LIBMUSCLE_Instance_set_port_length(instance, 'parameters_out', n_samples)

        ! O_I
        do sample = 1, n_samples
            uq_parameters = YMMSL_Settings_create()
            call YMMSL_Settings_set(uq_parameters, 'd', ds(sample))
            call YMMSL_Settings_set(uq_parameters, 'k', ks(sample))
            sdata = LIBMUSCLE_Data_create(uq_parameters)
            smsg = LIBMUSCLE_Message_create(0.0d0, sdata)
            call LIBMUSCLE_Instance_send(instance, 'parameters_out', smsg, sample - 1)
            call LIBMUSCLE_Message_free(smsg)
            call LIBMUSCLE_Data_free(sdata)
            call YMMSL_Settings_free(uq_parameters)
        end do
        deallocate (ds, ks)

        ! S
        print *, 'Entering S'
        t_max = 0.0d0
        do sample = 1, n_samples
            print *, 'Receiving states_in'
            rmsg = LIBMUSCLE_Instance_receive_with_settings_on_slot(instance, 'states_in', sample - 1)
            rdata = LIBMUSCLE_Message_get_data(rmsg)
            U_size = LIBMUSCLE_DataConstRef_size(rdata)
            if (.not. allocated(Us)) then
                allocate (Us(n_samples, U_size))
            end if

            do i = 1, U_size
                Us(sample, i) = LIBMUSCLE_DataConstRef_as_real8(LIBMUSCLE_DataConstRef_get_item(rdata, i))
            end do
            t_max = max(t_max, LIBMUSCLE_Message_timestamp(rmsg))

            call LIBMUSCLE_DataConstRef_free(rdata)
            call LIBMUSCLE_Message_free(rmsg)
        end do

        ! calculate mean
        means = LIBMUSCLE_Data_create_nils(U_size)

        do i = 1, U_size
            call LIBMUSCLE_Data_set_item(means, i, sum(Us(:, i)) / n_samples)
        end do
        smsg = LIBMUSCLE_Message_create(t_max, means)
        call LIBMUSCLE_Instance_send(instance, 'mean_out', smsg)

        call LIBMUSCLE_Message_free(smsg)
        call LIBMUSCLE_Data_free(means)
        deallocate (Us)
    end do

    call LIBMUSCLE_Instance_free(instance)

end program mc_driver

