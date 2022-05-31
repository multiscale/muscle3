module assert
    implicit none
contains
    subroutine assert_true(x)
        implicit none
        logical :: x

        if (.not. x) then
            print *, 'Assertion failed'
            stop
        end if
    end subroutine assert_true

    subroutine assert_false(x)
        implicit none
        logical :: x

        if (x) then
            print *, 'Assertion failed'
            stop
        end if
    end subroutine assert_false

    subroutine assert_eq_integer(x, y)
        use libmuscle
        implicit none
        integer :: x, y

        if (x .ne. y) then
            print *, 'Assertion failed'
            stop
        end if
    end subroutine assert_eq_integer

    subroutine assert_eq_int1(x, y)
        use libmuscle
        implicit none
        integer(kind=LIBMUSCLE_int1) :: x, y

        if (x .ne. y) then
            print *, 'Assertion failed'
            stop
        end if
    end subroutine assert_eq_int1

    subroutine assert_eq_int2(x, y)
        use libmuscle
        implicit none
        integer(kind=LIBMUSCLE_int2) :: x, y

        if (x .ne. y) then
            print *, 'Assertion failed'
            stop
        end if
    end subroutine assert_eq_int2

    subroutine assert_eq_int4(x, y)
        use libmuscle
        implicit none
        integer(kind=LIBMUSCLE_int4) :: x, y

        if (x .ne. y) then
            print *, 'Assertion failed'
            stop
        end if
    end subroutine assert_eq_int4

    subroutine assert_eq_int8(x, y)
        use libmuscle
        implicit none
        integer (LIBMUSCLE_int8) :: x, y

        if (x .ne. y) then
            print *, 'Assertion failed'
            stop
        end if
    end subroutine assert_eq_int8

    subroutine assert_eq_size(x, y)
        use libmuscle
        implicit none
        integer (LIBMUSCLE_size) :: x, y

        if (x .ne. y) then
            print *, 'Assertion failed'
            stop
        end if
    end subroutine assert_eq_size

    subroutine assert_eq_logical(x, y)
        implicit none
        logical :: x, y

        if (x .neqv. y) then
            print *, 'Assertion failed'
            stop
        end if
    end subroutine assert_eq_logical

    subroutine assert_eq_character(x, y)
        implicit none
        character(len=*) :: x, y

        if (x .ne. y) then
            print *, 'Assertion failed'
            stop
        end if
    end subroutine assert_eq_character

    subroutine assert_eq_real4(x, y)
        use libmuscle
        implicit none
        real (LIBMUSCLE_real4) :: x, y

        if (x .ne. y) then
            print *, 'Assertion failed'
            stop
        end if
    end subroutine assert_eq_real4

    subroutine assert_eq_real8(x, y)
        use libmuscle
        implicit none
        real (LIBMUSCLE_real8) :: x, y

        if (x .ne. y) then
            print *, 'Assertion failed'
            stop
        end if
    end subroutine assert_eq_real8

    subroutine assert_eq_real8array(x, y)
        use libmuscle
        implicit none
        real (LIBMUSCLE_real8), dimension(:) :: x
        real (LIBMUSCLE_real8), dimension(1:size(x)) :: y

        if (.not. all(x .eq. y)) then
            print *, 'Assertion failed'
            stop
        end if
    end subroutine assert_eq_real8array

    subroutine assert_eq_real8array2(x, y)
        use libmuscle
        implicit none
        real (LIBMUSCLE_real8), dimension(:, :) :: x
        real (LIBMUSCLE_real8), dimension(:, :) :: y

        if (.not. all(x .eq. y)) then
            print *, 'Assertion failed'
            stop
        end if
    end subroutine assert_eq_real8array2
end module assert

