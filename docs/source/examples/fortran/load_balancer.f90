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
    type(LIBMUSCLE_DataConstRef) :: rdata

    integer :: started, done, num_calls, num_workers


    ports = LIBMUSCLE_PortsDescription_create()
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_F_INIT, 'front_in[]')
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_O_I, 'back_out[]')
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_S, 'back_in[]')
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_O_F, 'front_out[]')
    instance = LIBMUSCLE_Instance_create(ports)
    call LIBMUSCLE_PortsDescription_free(ports)

    do while (LIBMUSCLE_Instance_reuse_instance(instance, .false.))
        ! F_INIT
        started = 0
        done = 0

        num_calls = LIBMUSCLE_Instance_get_port_length(instance, 'front_in')
        num_workers = LIBMUSCLE_Instance_get_port_length(instance, 'back_out')

        call LIBMUSCLE_Instance_set_port_length(instance, 'front_out', num_calls)

        do while (done < num_calls)
            do while ((started - done < num_workers) .and. (started < num_calls))
                rmsg = LIBMUSCLE_Instance_receive_with_settings_on_slot(instance, 'front_in', started)
                call LIBMUSCLE_Instance_send(instance, 'back_out', rmsg, mod(started, num_workers))
                call LIBMUSCLE_Message_free(rmsg)
                started = started + 1
            end do

            rmsg = LIBMUSCLE_Instance_receive_with_settings_on_slot(instance, 'back_in', mod(done, num_workers))
            call LIBMUSCLE_Instance_send(instance, 'front_out', rmsg, done)
            call LIBMUSCLE_Message_free(rmsg)
            done = done + 1
        end do
    end do

    call LIBMUSCLE_Instance_free(instance)

end program load_balancer

