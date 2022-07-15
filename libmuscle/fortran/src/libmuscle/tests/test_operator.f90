module tests
    use assert
    implicit none
contains
    subroutine test_operator_use
        use ymmsl

        integer(YMMSL_Operator) :: o1

        print *, '[  RUN     ] operator.use'
        o1 = YMMSL_Operator_NONE
        o1 = YMMSL_Operator_F_INIT
        o1 = YMMSL_Operator_O_I
        o1 = YMMSL_Operator_S
        o1 = YMMSL_Operator_B
        o1 = YMMSL_Operator_O_F
        print *, '[       OK ] operator.use'
    end subroutine test_operator_use
end module tests

program test_operator
    use tests
    implicit none

    print *, ''
    print *, '[==========] Fortran API Operator'

    call test_operator_use

    print *, '[==========] Fortran API Operator'
    print *, '[  PASSED  ] Fortran API Operator'
    print *, ''
end program test_operator

