module instanceflags_tests
    use assert
    implicit none
contains
    subroutine test_instanceflags_default_create
        use libmuscle

        type(LIBMUSCLE_InstanceFlags) :: flags
        integer :: i

        print *, '[  RUN     ] instanceflags.default_create'
        flags = LIBMUSCLE_InstanceFlags()
        call assert_false(flags%DONT_APPLY_OVERLAY)
        call assert_false(flags%USES_CHECKPOINT_API)
        call assert_false(flags%KEEPS_NO_STATE_FOR_NEXT_USE)
        call assert_false(flags%STATE_NOT_REQUIRED_FOR_NEXT_USE)
        i = flags%to_int()
        call assert_eq_integer(i, 0)
        print *, '[       OK ] instanceflags.default_create'
    end subroutine test_instanceflags_default_create

    subroutine test_instanceflags_create_1
        use libmuscle

        type(LIBMUSCLE_InstanceFlags) :: flags
        integer :: i

        print *, '[  RUN     ] instanceflags.create_1'
        flags = LIBMUSCLE_InstanceFlags(DONT_APPLY_OVERLAY=.true.)
        call assert_true(flags%DONT_APPLY_OVERLAY)
        call assert_false(flags%USES_CHECKPOINT_API)
        call assert_false(flags%KEEPS_NO_STATE_FOR_NEXT_USE)
        call assert_false(flags%STATE_NOT_REQUIRED_FOR_NEXT_USE)
        i = flags%to_int()
        call assert_eq_integer(i, 1)
        print *, '[       OK ] instanceflags.create_1'
    end subroutine test_instanceflags_create_1

    subroutine test_instanceflags_create_2
        use libmuscle

        type(LIBMUSCLE_InstanceFlags) :: flags
        integer :: i

        print *, '[  RUN     ] instanceflags.create_2'
        flags = LIBMUSCLE_InstanceFlags(USES_CHECKPOINT_API=.true.)
        call assert_false(flags%DONT_APPLY_OVERLAY)
        call assert_true(flags%USES_CHECKPOINT_API)
        call assert_false(flags%KEEPS_NO_STATE_FOR_NEXT_USE)
        call assert_false(flags%STATE_NOT_REQUIRED_FOR_NEXT_USE)
        i = flags%to_int()
        call assert_eq_integer(i, 2)
        print *, '[       OK ] instanceflags.create_2'
    end subroutine test_instanceflags_create_2

    subroutine test_instanceflags_create_3
        use libmuscle

        type(LIBMUSCLE_InstanceFlags) :: flags
        integer :: i

        print *, '[  RUN     ] instanceflags.create_3'
        flags = LIBMUSCLE_InstanceFlags(KEEPS_NO_STATE_FOR_NEXT_USE=.true.)
        call assert_false(flags%DONT_APPLY_OVERLAY)
        call assert_false(flags%USES_CHECKPOINT_API)
        call assert_true(flags%KEEPS_NO_STATE_FOR_NEXT_USE)
        call assert_false(flags%STATE_NOT_REQUIRED_FOR_NEXT_USE)
        i = flags%to_int()
        call assert_eq_integer(i, 4)
        print *, '[       OK ] instanceflags.create_3'
    end subroutine test_instanceflags_create_3

    subroutine test_instanceflags_create_4
        use libmuscle

        type(LIBMUSCLE_InstanceFlags) :: flags
        integer :: i

        print *, '[  RUN     ] instanceflags.create_4'
        flags = LIBMUSCLE_InstanceFlags(STATE_NOT_REQUIRED_FOR_NEXT_USE=.true.)
        call assert_false(flags%DONT_APPLY_OVERLAY)
        call assert_false(flags%USES_CHECKPOINT_API)
        call assert_false(flags%KEEPS_NO_STATE_FOR_NEXT_USE)
        call assert_true(flags%STATE_NOT_REQUIRED_FOR_NEXT_USE)
        i = flags%to_int()
        call assert_eq_integer(i, 8)
        print *, '[       OK ] instanceflags.create_4'
    end subroutine test_instanceflags_create_4

    subroutine test_instanceflags_create_all
        use libmuscle

        type(LIBMUSCLE_InstanceFlags) :: flags
        integer :: i

        print *, '[  RUN     ] instanceflags.create_all'
        flags = LIBMUSCLE_InstanceFlags( &
            DONT_APPLY_OVERLAY=.true., &
            USES_CHECKPOINT_API=.true., &
            KEEPS_NO_STATE_FOR_NEXT_USE=.true., &
            STATE_NOT_REQUIRED_FOR_NEXT_USE=.true.)
        call assert_true(flags%DONT_APPLY_OVERLAY)
        call assert_true(flags%USES_CHECKPOINT_API)
        call assert_true(flags%KEEPS_NO_STATE_FOR_NEXT_USE)
        call assert_true(flags%STATE_NOT_REQUIRED_FOR_NEXT_USE)
        i = flags%to_int()
        call assert_eq_integer(i, 15)
        print *, '[       OK ] instanceflags.create_all'
    end subroutine test_instanceflags_create_all
end module instanceflags_tests

program test_instanceflags
    use instanceflags_tests
    implicit none

    print *, ''
    print *, '[==========] Fortran API InstanceFlags'

    call test_instanceflags_default_create
    call test_instanceflags_create_1
    call test_instanceflags_create_2
    call test_instanceflags_create_3
    call test_instanceflags_create_4
    call test_instanceflags_create_all

    print *, '[==========] Fortran API InstanceFlags'
    print *, '[  PASSED  ] Fortran API InstanceFlags'
    print *, ''
end program test_instanceflags
