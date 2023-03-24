! A simple diffusion model on a 1D grid.
!
! The state of this model is a 1D grid of concentrations. It sends out the
! state on each timestep on 'state_out', and can receive an updated state
! on 'state_in' at each state update.

program diffusion
    use ymmsl
    use libmuscle
    implicit none

    type(LIBMUSCLE_PortsDescription) :: ports
    type(LIBMUSCLE_Instance) :: instance

    type(LIBMUSCLE_Message) :: rmsg
    type(LIBMUSCLE_DataConstRef) :: rdata, item
    integer (LIBMUSCLE_size), dimension(2) :: shp

    type(LIBMUSCLE_Message) :: smsg
    type(LIBMUSCLE_Data) :: sdata, sitem

    real (selected_real_kind(15)) :: t_cur, t_next, t_max, dt, x_max, dx, d
    integer (LIBMUSCLE_size) :: U_size, n_steps, iteration
    real (selected_real_kind(15)), dimension(:), allocatable :: U, dU
    real (selected_real_kind(15)), dimension(:, :), allocatable :: Us


    ports = LIBMUSCLE_PortsDescription()
    call ports%add(YMMSL_Operator_O_I, 'state_out')
    call ports%add(YMMSL_Operator_S, 'state_in')
    call ports%add(YMMSL_Operator_O_F, 'final_state_out')
    instance = LIBMUSCLE_Instance(ports, &
            LIBMUSCLE_InstanceFlags(USES_CHECKPOINT_API=.true.))
    call LIBMUSCLE_PortsDescription_free(ports)

    do while (instance%reuse_instance())
       ! F_INIT
        t_max = instance%get_setting_as_real8('t_max')
        dt = instance%get_setting_as_real8('dt')
        x_max = instance%get_setting_as_real8('x_max')
        dx = instance%get_setting_as_real8('dx')
        d = instance%get_setting_as_real8('d')

        U_size = nint(x_max / dx)
        allocate (U(U_size), dU(U_size))
        U = 1e-20
        U(26) = 2.0
        U(51) = 2.0
        U(76) = 2.0

        n_steps = int(t_max / dt)
        allocate (Us(U_size, n_steps))

        iteration = 1
        Us(:, iteration) = U

        t_cur = 0.0
        do while (t_cur + dt < t_max)
            print *, 't_cur: ', t_cur, 't_max: ', t_max
            ! O_I
            sdata = LIBMUSCLE_Data_create_grid(U, 'x')
            smsg = LIBMUSCLE_Message(t_cur, sdata)
            call LIBMUSCLE_Data_free(sdata)
            t_next = t_cur + dt
            if (t_next + dt <= t_max) then
                call smsg%set_next_timestamp(t_next)
            end if
            call instance%send('state_out', smsg)

            ! S
            rmsg = instance%receive('state_in', smsg)
            rdata = rmsg%get_data()
            call rdata%elements(U)
            call LIBMUSCLE_DataConstRef_free(rdata)
            call LIBMUSCLE_Message_free(rmsg)
            call LIBMUSCLE_Message_free(smsg)

            dU(2:U_size-1) = d * laplacian(U, dx) * dt
            dU(1) = dU(2)
            dU(U_size) = dU(U_size - 1)

            U = U + dU
            iteration = iteration + 1
            Us(:, iteration) = U

            t_cur = t_cur + dt

            if (instance%should_save_snapshot(t_cur)) then
                sdata = LIBMUSCLE_Data_create_nils(2_LIBMUSCLE_size)
                sitem = LIBMUSCLE_Data_create_grid(Us)
                call sdata%set_item(1_LIBMUSCLE_size, sitem)
                call sdata%set_item(2_LIBMUSCLE_size, iteration)
                smsg = LIBMUSCLE_Message(t_cur, sdata)
                call instance%save_snapshot(smsg)
                call LIBMUSCLE_Message_free(smsg)
                call LIBMUSCLE_Data_free(sdata)
                call LIBMUSCLE_Data_free(sitem)
            end if
        end do

        ! O_F
        sdata = LIBMUSCLE_Data_create_grid(U, 'x')
        smsg = LIBMUSCLE_Message(t_cur, sdata)
        call instance%send('final_state_out', smsg)
        call LIBMUSCLE_Message_free(smsg)
        call LIBMUSCLE_Data_free(sdata)

        if (instance%should_save_final_snapshot()) then
            sdata = LIBMUSCLE_Data_create_nils(2_LIBMUSCLE_size)
            sitem = LIBMUSCLE_Data_create_grid(Us)
            call sdata%set_item(1_LIBMUSCLE_size, sitem)
            call sdata%set_item(2_LIBMUSCLE_size, iteration)
            smsg = LIBMUSCLE_Message(t_cur, sdata)
            call instance%save_snapshot(smsg)
            call LIBMUSCLE_Message_free(smsg)
            call LIBMUSCLE_Data_free(sdata)
            call LIBMUSCLE_Data_free(sitem)
        end if

        deallocate (U, dU, Us)
        print *, 'All done'
    end do

    call LIBMUSCLE_Instance_free(instance)

contains

    ! Calculates the Laplacian of vector Z.
    !
    ! @param Z A vector representing a series of samples along a line.
    ! @param dx The spacing between the samples.

    function laplacian(Z, dx)
        real (selected_real_kind(15)), dimension(:), intent(in) :: Z
        real (selected_real_kind(15)), intent(in) :: dx
        real (selected_real_kind(15)), allocatable, dimension(:) :: laplacian
        integer :: n

        n = size(Z)
        allocate(laplacian(size(Z) - 2))
        laplacian = (Z(1:n-2) + Z(3:n) - 2.0d0 * Z(2:n-1)) / (dx * dx)

    end function laplacian

end program diffusion

