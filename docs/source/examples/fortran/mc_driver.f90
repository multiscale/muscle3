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


    ports = LIBMUSCLE_PortsDescription()
    call ports%add(YMMSL_Operator_O_I, 'parameters_out[]')
    call ports%add(YMMSL_Operator_S, 'states_in[]')
    call ports%add(YMMSL_Operator_O_F, 'mean_out')
    instance = LIBMUSCLE_Instance(ports)
    call LIBMUSCLE_PortsDescription_free(ports)

    do while (instance%reuse_instance())
        ! F_INIT
        ! get and check parameter distributions
        n_samples = instance%get_setting_as_int8('n_samples')
        d_min = instance%get_setting_as_real8('d_min')
        d_max = instance%get_setting_as_real8('d_max')
        k_min = instance%get_setting_as_real8('k_min')
        k_max = instance%get_setting_as_real8('k_max')

        if (d_max < d_min) then
            call instance%error_shutdown('Invalid settings: d_max < d_min')
            stop
        end if

        if (k_max < k_min) then
            call instance%error_shutdown('Invalid settings: k_max < k_min')
            stop
        end if

        ! generate UQ parameter values
        allocate (ds(n_samples), ks(n_samples))
        call random_number(ds)
        ds = d_min + ds * (d_max - d_min)
        call random_number(ks)
        ks = k_min + ks * (k_max - k_min)

        ! configure output port
        if (.not. instance%is_resizable('parameters_out')) then
            call instance%error_shutdown(&
                'This component needs a resizable parameters_out port, but it&
                & is connected to something that cannot be resized. Maybe try&
                & adding a load balancer.')
            stop
        end if

        call instance%set_port_length('parameters_out', n_samples)

        ! O_I
        do sample = 1, n_samples
            uq_parameters = YMMSL_Settings()
            call uq_parameters%set('d', ds(sample))
            call uq_parameters%set('k', ks(sample))
            sdata = LIBMUSCLE_Data(uq_parameters)
            smsg = LIBMUSCLE_Message(0.0d0, sdata)
            call instance%send('parameters_out', smsg, sample - 1)
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
            rmsg = instance%receive_with_settings_on_slot('states_in', sample - 1)
            rdata = rmsg%get_data()
            U_size = rdata%size()
            if (.not. allocated(Us)) then
                allocate (Us(n_samples, U_size))
            end if

            call rdata%elements(Us(sample, :))
            t_max = max(t_max, rmsg%timestamp())

            call LIBMUSCLE_DataConstRef_free(rdata)
            call LIBMUSCLE_Message_free(rmsg)
        end do

        ! calculate mean
        means = LIBMUSCLE_Data_create_grid(sum(Us, 1) / n_samples, 'x')
        smsg = LIBMUSCLE_Message(t_max, means)
        call instance%send('mean_out', smsg)

        call LIBMUSCLE_Message_free(smsg)
        call LIBMUSCLE_Data_free(means)
        deallocate (Us)
    end do

    call LIBMUSCLE_Instance_free(instance)

end program mc_driver

