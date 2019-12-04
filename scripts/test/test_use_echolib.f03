program use_echolib
    use echolib

    implicit none
    integer, parameter :: int64 = selected_int_kind(18)
    integer, parameter :: double = selected_real_kind(15)

    type(ECHO_Echo) :: e, e2, obj_echo
    integer :: int_echo
    integer (int64) :: int64_echo
    real (double) :: double_echo
    logical :: bool_echo
    integer(ECHO_Color) :: color_echo
    character(len=:), allocatable :: string_echo
    real (double), dimension(2) :: vecdbl_echo
    real (double), dimension(3,2) :: vecdbl2_in, vecdbl2_echo
    character(len=1), dimension(7) :: bytes_data, bytes_echo
    integer :: err_code
    character(:), allocatable :: err_msg

    e = ECHO_Echo_create()

    call ECHO_Echo_echo_nothing(e)

    int_echo = ECHO_Echo_echo_int(e, 42)
    if (int_echo .ne. 42) then
        print *, 'Error in int_echo: ', int_echo
        stop 1
    end if

    int64_echo = ECHO_Echo_echo_int64_t(e, 4242424242424242_int64)
    if (int64_echo .ne. 4242424242424242_int64) then
        print *, 'Error in int64_echo: ', int64_echo
        stop 1
    end if

    double_echo = ECHO_Echo_echo_double(e, 1.0000000001_double)
    if (double_echo .ne. 1.0000000001_double) then
        print *, 'Error in double_echo: ', double_echo
        stop 1
    end if

    bool_echo = ECHO_Echo_echo_bool(e, .true.)
    if (bool_echo .neqv. .true.) then
        print *, 'Error in bool_echo: ', bool_echo
        stop 1
    end if

    color_echo = ECHO_Echo_echo_enum(e, ECHO_Color_GREEN)
    if (color_echo .ne. ECHO_Color_GREEN) then
        print *, 'Error in color_echo: ', color_echo
        stop 1
    end if

    string_echo = ECHO_Echo_echo_string(e, 'Testing')
    if (string_echo .ne. 'Testing') then
        print *, 'Error in string_echo: ', string_echo
        stop 1
    end if
    deallocate(string_echo)

    call ECHO_Echo_echo_double_vec(e, (/1.414213562373095_double, 3.141592653589793_double/), vecdbl_echo)
    if (.not. all(vecdbl_echo .eq. (/1.414213562373095_double, 3.141592653589793_double/))) then
        print *, 'Error in vecdbl_echo: ', vecdbl_echo
        stop 1
    end if

    vecdbl2_in = reshape((/1.0_double, 2.0_double, 3.0_double, &
                   4.0_double, 5.0_double, 6.0_double/), &
                 (/3, 2/))
    call ECHO_Echo_echo_double_vec2(e, vecdbl2_in, vecdbl2_echo)
    if (.not. all(vecdbl2_echo .eq. vecdbl2_in)) then
        print *, 'Error in vecdbl2_echo: ', vecdbl2_echo
        stop 1
    end if

    obj_echo = ECHO_Echo_echo_object(e, e)
    ! Cannot test this very well
    call ECHO_Echo_free(obj_echo)

    bytes_data = (/'T', 'e', 's', 't', 'i', 'n', 'g'/)
    call ECHO_Echo_echo_bytes(e, bytes_data, bytes_echo)
    if (.not. all(bytes_echo .eq. bytes_data)) then
        print *, 'Error in bytes_echo: ', bytes_echo
        stop 1
    end if

    string_echo = ECHO_Echo_echo_error(e, 42.d0, err_code, err_msg)
    if (err_code .ne. ECHO_runtime_error) then
        print *, 'Error in echo_error: ', err_code
        stop 1
    else
        print *, err_code
        print *, len(err_msg)
        print *, err_msg
        deallocate(err_msg)
    end if

    int_echo = ECHO_Echo_echo_template_int(e, 42, err_code, err_msg)
    if (err_code .ne. ECHO_out_of_range) then
        print *, 'Error in echo_template_int: ', err_code
        stop 1
    else
        print *, err_code
        print *, err_msg
        deallocate(err_msg)
    end if

    double_echo = ECHO_Echo_echo_template_double(e, 1.0000000001_double, err_code, err_msg)
    if (double_echo .ne. 1.0000000001_double) then
        print *, 'Error in double_echo: ', double_echo
        stop 1
    end if

    string_echo = ECHO_Echo_echo_template_string(e, 'Testing', err_code, err_msg)
    if (string_echo .ne. 'Testing') then
        print *, 'Error in string_echo: ', string_echo
        stop 1
    end if
    deallocate(string_echo)

    int_echo = ECHO_Echo_echo(e, 42)
    if (int_echo .ne. 42) then
        print *, 'Error in int_echo: ', int_echo
        stop 1
    end if

    call ECHO_Echo_free(e)

end program use_echolib

