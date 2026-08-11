! A proxy which divides many calls over few instances.
!
! Put this component between a driver and a set of models, or between a
! macro model and a set of micro models. It will let the driver or macro-
! model submit as many calls as it wants, and divide them over the available
! (micro)model instances in a round-robin fashion.
!
! Assumes a fixed number of micro-model instances.

program load_balancer
    use ymmsl
    use libmuscle
    implicit none

    type(LIBMUSCLE_PortsDescription) :: ports
    type(LIBMUSCLE_Instance) :: instance

    type(LIBMUSCLE_Message) :: rmsg
    type(LIBMUSCLE_Message), allocatable :: result(:)
    type(LIBMUSCLE_DataConstRef) :: rdata

    integer :: started, done, num_calls, num_workers, i


    ports = LIBMUSCLE_PortsDescription()
    call ports%add(YMMSL_Operator_F_INIT, 'front_in[]')
    call ports%add(YMMSL_Operator_O_I, 'back_out[]')
    call ports%add(YMMSL_Operator_S, 'back_in[]')
    call ports%add(YMMSL_Operator_O_F, 'front_out[]')
    instance = LIBMUSCLE_Instance(ports, LIBMUSCLE_InstanceFlags(DONT_APPLY_OVERLAY=.true.))
    call LIBMUSCLE_PortsDescription_free(ports)

    do while (instance%reuse_instance())
        ! F_INIT
        started = 0
        done = 0

        num_calls = instance%get_port_length('front_in')
        num_workers = instance%get_port_length('back_out')
        allocate(result(num_calls))

        call instance%set_port_length('front_out', num_calls)

        do while (done < num_calls)
            do i = 0, num_workers-1
                if (started < num_calls) then
                    rmsg = instance%receive_with_settings_on_slot('front_in', started)
                else
                    rmsg = LIBMUSCLE_Message(-1d40)
                end if
                call instance%send('back_out', rmsg, i)
                call LIBMUSCLE_Message_free(rmsg)
                started = started + 1
            end do
            do i = 0, num_workers-1
                if (done < num_calls) then
                    done = done + 1
                    result(done) = instance%receive_with_settings_on_slot('back_in', mod(done, num_workers))
                end if
            end do
        end do

        do i = 1, num_calls
            call instance%send('front_out', result(i), i-1)
            call LIBMUSCLE_Message_free(result(i))
        end do
        deallocate(result)
    end do

    call LIBMUSCLE_Instance_free(instance)

end program load_balancer

