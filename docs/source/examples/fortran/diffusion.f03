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


    type(LIBMUSCLE_Message) :: smsg
    type(LIBMUSCLE_Data) :: sdata

    real (selected_real_kind(15)) :: t_cur, t_next, t_max, dt, x_max, dx, d
    integer (LIBMUSCLE_size) :: U_size, n_steps, iteration
    real (selected_real_kind(15)), dimension(:), allocatable :: U, dU
    real (selected_real_kind(15)), dimension(:, :), allocatable :: Us


    ports = LIBMUSCLE_PortsDescription_create()
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_O_I, 'state_out')
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_S, 'state_in')
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_O_F, 'final_state_out')
    instance = LIBMUSCLE_Instance_create(ports)
    call LIBMUSCLE_PortsDescription_free(ports)

    do while (LIBMUSCLE_Instance_reuse_instance(instance))
        ! F_INIT
        t_max = LIBMUSCLE_Instance_get_setting_as_real8(instance, 't_max')
        dt = LIBMUSCLE_Instance_get_setting_as_real8(instance, 'dt')
        x_max = LIBMUSCLE_Instance_get_setting_as_real8(instance, 'x_max')
        dx = LIBMUSCLE_Instance_get_setting_as_real8(instance, 'dx')
        d = LIBMUSCLE_Instance_get_setting_as_real8(instance, 'd')

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
            smsg = LIBMUSCLE_Message_create(t_cur, sdata)
            call LIBMUSCLE_Data_free(sdata)
            t_next = t_cur + dt
            if (t_next + dt <= t_max) then
                call LIBMUSCLE_Message_set_next_timestamp(smsg, t_next)
            end if
            call LIBMUSCLE_Instance_send(instance, 'state_out', smsg)

            ! S
            rmsg = LIBMUSCLE_Instance_receive(instance, 'state_in', smsg)
            rdata = LIBMUSCLE_Message_get_data(rmsg)
            call LIBMUSCLE_DataConstRef_elements(rdata, U)
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
        end do

        ! O_F
        sdata = LIBMUSCLE_Data_create_grid(U, 'x')
        smsg = LIBMUSCLE_Message_create(t_cur, sdata)
        call LIBMUSCLE_Instance_send(instance, 'final_state_out', smsg)
        call LIBMUSCLE_Message_free(smsg)
        call LIBMUSCLE_Data_free(sdata)
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

