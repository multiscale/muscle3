program reaction_mpi
    use mpi
    use ymmsl
    use libmuscle_mpi
    implicit none

    type(LIBMUSCLE_PortsDescription) :: ports
    type(LIBMUSCLE_Instance) :: instance

    type(LIBMUSCLE_Message) :: rmsg
    type(LIBMUSCLE_DataConstRef) :: rdata, item


    type(LIBMUSCLE_Message) :: smsg
    type(LIBMUSCLE_Data) :: sdata

    integer, parameter :: root_rank = 0
    integer :: rank, num_ranks, ierr
    real (selected_real_kind(15)) :: t_cur, t_max, t_end, dt, k
    integer :: i, U_size, U_all_size
    real (selected_real_kind(15)), dimension(:), allocatable :: U, U_all

    call MPI_Init(ierr)
    call MPI_Comm_rank(MPI_COMM_WORLD, rank, ierr)
    call MPI_Comm_size(MPI_COMM_WORLD, num_ranks, ierr)

    ports = LIBMUSCLE_PortsDescription()
    call ports%add(YMMSL_Operator_F_INIT, 'initial_state')
    call ports%add(YMMSL_Operator_O_F, 'final_state')
    instance = LIBMUSCLE_Instance(ports, communicator=MPI_COMM_WORLD, root=root_rank)
    call LIBMUSCLE_PortsDescription_free(ports)

    do while (instance%reuse_instance())
        ! F_INIT
        t_max = instance%get_setting_as_real8('t_max')
        dt = instance%get_setting_as_real8('dt')
        k = instance%get_setting_as_real8('k')

        rmsg = instance%receive('initial_state')

        if (rank == root_rank) then
            rdata = rmsg%get_data()
            U_all_size = rdata%size()
            allocate (U_all(U_all_size))
            call rdata%elements(U_all)
            call LIBMUSCLE_DataConstRef_free(rdata)

            t_cur = rmsg%timestamp()
            t_end = rmsg%timestamp() + t_max
            call LIBMUSCLE_Message_free(rmsg)

            U_size = U_all_size / num_ranks
            if (U_size * num_ranks /= U_all_size) then
                call instance%error_shutdown('State does not divide evenly')
                print *, 'State does not divide evenly'
                stop
            end if
        end if

        call MPI_Bcast(U_size, 1, MPI_INT, root_rank, MPI_COMM_WORLD, ierr)
        allocate (U(U_size))
        call MPI_Scatter(U_all, U_size, MPI_DOUBLE,  &
                         U, U_size, MPI_DOUBLE,      &
                         root_rank, MPI_COMM_WORLD, ierr)

        call MPI_Bcast(t_cur, 1, MPI_DOUBLE, root_rank, MPI_COMM_WORLD, ierr)
        call MPI_Bcast(t_end, 1, MPI_DOUBLE, root_rank, MPI_COMM_WORLD, ierr)

        do while (t_cur + dt < t_end)
            ! O_I

            ! S
            U = k * U * dt
            t_cur = t_cur + dt
        end do

        ! O_F
        call MPI_Gather(U, U_size, MPI_DOUBLE,       &
                        U_all, U_size, MPI_DOUBLE,   &
                        root_rank, MPI_COMM_WORLD, ierr)

        if (rank == root_rank) then
            sdata = LIBMUSCLE_Data_create_grid(U_all, 'x')
            smsg = LIBMUSCLE_Message(t_cur, sdata)
            call instance%send('final_state', smsg)

            call LIBMUSCLE_Message_free(smsg)
            call LIBMUSCLE_Data_free(sdata)
            deallocate (U_all)
        end if
        deallocate (U)
    end do

    call LIBMUSCLE_Instance_free(instance)
    call MPI_Finalize(ierr)

end program reaction_mpi

