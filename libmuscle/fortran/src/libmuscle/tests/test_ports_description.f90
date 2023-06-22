module ports_description_tests
    use assert
    implicit none
contains
    subroutine test_ports_description_use
        use libmuscle
        use ymmsl
        implicit none

        type(LIBMUSCLE_PortsDescription) :: pd

        print *, '[  RUN     ] ports_description.use'
        pd = LIBMUSCLE_PortsDescription()
        call assert_eq_size(pd%num_ports(YMMSL_Operator_F_INIT), 0_LIBMUSCLE_size)
        call pd%add(YMMSL_Operator_F_INIT, 'init_state')
        call assert_eq_size(pd%num_ports(YMMSL_Operator_F_INIT), 1_LIBMUSCLE_size)
        call assert_eq_character(pd%get(YMMSL_Operator_F_INIT, 1_LIBMUSCLE_size), 'init_state')
        call LIBMUSCLE_PortsDescription_free(pd)
        print *, '[       OK ] ports_description.use'
    end subroutine test_ports_description_use
end module ports_description_tests

program test_ports_description
    use ports_description_tests
    implicit none

    print *, ''
    print *, '[==========] Fortran API PortsDescription'

    call test_ports_description_use

    print *, '[==========] Fortran API PortsDescription'
    print *, '[  PASSED  ] Fortran API PortsDescription'
    print *, ''
end program test_ports_description

