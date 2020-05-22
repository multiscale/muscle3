module tests
    use assert
    implicit none
contains
    subroutine test_settings_create
        use ymmsl
        implicit none

        type(YMMSL_Settings) :: s1

        print *, '[  RUN     ] settings.create'
        s1 = YMMSL_Settings_create()
        call assert_true(YMMSL_Settings_empty(s1))
        call YMMSL_Settings_free(s1)
        print *, '[       OK ] settings.create'
    end subroutine test_settings_create

    subroutine test_settings_equals
        use ymmsl
        implicit none

        type(YMMSL_Settings) :: s1, s2

        print *, '[  RUN     ] settings.equals'
        s1 = YMMSL_Settings_create()
        s2 = YMMSL_Settings_create()
        call assert_true(YMMSL_Settings_equals(s1, s2))

        call YMMSL_Settings_set(s1, 'key', 'value')
        call assert_false(YMMSL_Settings_equals(s1, s2))

        call YMMSL_Settings_set(s2, 'key', 'value')
        call assert_true(YMMSL_Settings_equals(s1, s2))

        call YMMSL_Settings_free(s1)
        call YMMSL_Settings_free(s2)
        print *, '[       OK ] settings.equals'
    end subroutine test_settings_equals

    subroutine test_settings_size
        use ymmsl
        implicit none

        type(YMMSL_Settings) :: s1

        print *, '[  RUN     ] settings.size'
        s1 = YMMSL_Settings_create()

        call assert_eq_size(YMMSL_Settings_size(s1), 0_YMMSL_size)

        call YMMSL_Settings_free(s1)
        print *, '[       OK ] settings.size'
    end subroutine test_settings_size

    subroutine test_settings_set_get_as
        use ymmsl
        implicit none

        type(YMMSL_Settings) :: s1
        real(YMMSL_real8), dimension(2) :: ra1, ra2
        real(YMMSL_real8), dimension(3, 2) :: ra3, ra4

        print *, '[  RUN     ] settings.set_get_as'
        s1 = YMMSL_Settings_create()
        ra1 = (/1.0d0, 2.0d0/)
        ra3 = reshape((/1.0d0, 2.0d0, 3.0d0, 4.0d0, 5.0d0, 6.0d0/), (/3, 2/))

        call YMMSL_Settings_set(s1, 'key1', 'value1')
        call YMMSL_Settings_set(s1, 'key2', 242424242_YMMSL_int4)
        call YMMSL_Settings_set(s1, 'key3', 42424242424242_YMMSL_int8)
        call YMMSL_Settings_set(s1, 'key4', .false.)
        call YMMSL_Settings_set(s1, 'key5', 13.13d0)
        call YMMSL_Settings_set(s1, 'key6', ra1)
        call YMMSL_Settings_set(s1, 'key7', ra3)

        call assert_true(YMMSL_Settings_contains(s1, 'key1'))
        call assert_true(YMMSL_Settings_contains(s1, 'key2'))
        call assert_true(YMMSL_Settings_contains(s1, 'key3'))
        call assert_true(YMMSL_Settings_contains(s1, 'key4'))
        call assert_true(YMMSL_Settings_contains(s1, 'key5'))
        call assert_true(YMMSL_Settings_contains(s1, 'key6'))
        call assert_true(YMMSL_Settings_contains(s1, 'key7'))
        call assert_false(YMMSL_Settings_contains(s1, 'nokey'))

        call assert_eq_character(YMMSL_Settings_get_as_character(s1, 'key1'), 'value1')
        call assert_eq_int4(YMMSL_Settings_get_as_int4(s1, 'key2'), 242424242_YMMSL_int4)
        call assert_eq_int8(YMMSL_Settings_get_as_int8(s1, 'key2'), 242424242_YMMSL_int8)
        call assert_eq_int8(YMMSL_Settings_get_as_int8(s1, 'key3'), 42424242424242_YMMSL_int8)
        call assert_eq_logical(YMMSL_Settings_get_as_logical(s1, 'key4'), .false.)
        call assert_eq_real8(YMMSL_Settings_get_as_real8(s1, 'key5'), 13.13d0)
        call YMMSL_Settings_get_as_real8array(s1, 'key6', ra2)
        call assert_eq_real8array(ra2, ra1)
        call YMMSL_Settings_get_as_real8array2(s1, 'key7', ra4)
        call assert_eq_real8array2(ra4, ra3)

        call YMMSL_Settings_free(s1)
        print *, '[       OK ] settings.set_get_as'
    end subroutine test_settings_set_get_as

    subroutine test_settings_is_a
        use ymmsl
        implicit none

        type(YMMSL_Settings) :: s1
        real(YMMSL_real8), dimension(2) :: ra1
        real(YMMSL_real8), dimension(3, 2) :: ra2
        logical :: l1
        integer :: err_code

        print *, '[  RUN     ] settings.is_a'
        s1 = YMMSL_Settings_create()
        ra1 = (/1.0d0, 2.0d0/)
        ra2 = reshape((/1.0d0, 2.0d0, 3.0d0, 4.0d0, 5.0d0, 6.0d0/), (/3, 2/))

        call YMMSL_Settings_set(s1, 'key1', 'value1')
        call YMMSL_Settings_set(s1, 'key2', 242424242_YMMSL_int4)
        call YMMSL_Settings_set(s1, 'key3', 42424242424242_YMMSL_int8)
        call YMMSL_Settings_set(s1, 'key4', .false.)
        call YMMSL_Settings_set(s1, 'key5', 13.13d0)
        call YMMSL_Settings_set(s1, 'key6', ra1)
        call YMMSL_Settings_set(s1, 'key7', ra2)

        call assert_true(YMMSL_Settings_is_a_character(s1, 'key1'))
        call assert_true(YMMSL_Settings_is_a_int4(s1, 'key2'))
        call assert_true(YMMSL_Settings_is_a_int8(s1, 'key2'))
        call assert_false(YMMSL_Settings_is_a_int4(s1, 'key3'))
        call assert_true(YMMSL_Settings_is_a_int8(s1, 'key3'))
        call assert_true(YMMSL_Settings_is_a_logical(s1, 'key4'))
        call assert_true(YMMSL_Settings_is_a_real8(s1, 'key5'))
        call assert_true(YMMSL_Settings_is_a_real8array(s1, 'key6'))
        call assert_true(YMMSL_Settings_is_a_real8array2(s1, 'key7'))

        call assert_false(YMMSL_Settings_is_a_int8(s1, 'key1'))
        call assert_false(YMMSL_Settings_is_a_logical(s1, 'key1'))
        call assert_false(YMMSL_Settings_is_a_real8(s1, 'key1'))
        call assert_false(YMMSL_Settings_is_a_real8array(s1, 'key1'))
        call assert_false(YMMSL_Settings_is_a_real8array2(s1, 'key1'))

        l1 = YMMSL_Settings_is_a_logical(s1, 'nokey', err_code)
        call assert_eq_integer(err_code, YMMSL_out_of_range)

        call YMMSL_Settings_free(s1)
        print *, '[       OK ] settings.is_a'
    end subroutine test_settings_is_a

    subroutine test_settings_erase
        use ymmsl
        implicit none

        type(YMMSL_Settings) :: s1

        print *, '[  RUN     ] settings.erase'
        s1 = YMMSL_Settings_create()
        call YMMSL_Settings_set(s1, 'key', 'value')
        call assert_true(YMMSL_Settings_contains(s1, 'key'))
        call assert_eq_size(YMMSL_Settings_erase(s1, 'key'), 1_YMMSL_size)
        call assert_false(YMMSL_Settings_contains(s1, 'key'))
        call assert_eq_size(YMMSL_Settings_erase(s1, 'key'), 0_YMMSL_size)
        call YMMSL_Settings_free(s1)
        print *, '[       OK ] settings.erase'
    end subroutine test_settings_erase

    subroutine test_settings_clear
        use ymmsl
        implicit none

        type(YMMSL_Settings) :: s1

        print *, '[  RUN     ] settings.clear'
        s1 = YMMSL_Settings_create()
        call YMMSL_Settings_set(s1, 'key1', 'value')
        call YMMSL_Settings_set(s1, 'key2', 42_YMMSL_int8)

        call assert_true(YMMSL_Settings_contains(s1, 'key1'))
        call assert_true(YMMSL_Settings_contains(s1, 'key2'))

        call YMMSL_Settings_clear(s1)

        call assert_false(YMMSL_Settings_contains(s1, 'key1'))
        call assert_false(YMMSL_Settings_contains(s1, 'key2'))
        call assert_eq_size(YMMSL_Settings_size(s1), 0_YMMSL_size)

        call YMMSL_Settings_free(s1)
        print *, '[       OK ] settings.clear'
    end subroutine test_settings_clear

    subroutine test_settings_key
        use ymmsl
        implicit none

        type(YMMSL_Settings) :: s1
        character(len=:), allocatable :: c1, c2, err_msg
        integer :: err_code

        print *, '[  RUN     ] settings.key'
        s1 = YMMSL_Settings_create()
        call YMMSL_Settings_set(s1, 'key1', 'value')
        call YMMSL_Settings_set(s1, 'key2', 42_YMMSL_int8)

        c1 = YMMSL_Settings_key(s1, 1_YMMSL_size, err_code)
        call assert_eq_integer(err_code, YMMSL_success)
        c2 = YMMSL_Settings_key(s1, 2_YMMSL_size, err_code)
        call assert_eq_integer(err_code, YMMSL_success)

        call assert_true((c1 .eq. 'key1') .or. (c1 .eq. 'key2'))
        call assert_true((c2 .eq. 'key1') .or. (c2 .eq. 'key2'))
        call assert_true(c1 .ne. c2)

        c1 = YMMSL_Settings_key(s1, 0_YMMSL_size, err_code, err_msg)
        call assert_eq_integer(err_code, YMMSL_out_of_range)

        c1 = YMMSL_Settings_key(s1, 3_YMMSL_size, err_code)
        call assert_eq_integer(err_code, YMMSL_out_of_range)

        deallocate(c1)
        deallocate(c2)
        call YMMSL_Settings_free(s1)
        print *, '[       OK ] settings.key'
    end subroutine test_settings_key
end module tests

program test_settings
    use tests
    implicit none

    print *, ''
    print *, '[==========] Fortran API Settings'

        call test_settings_create
        call test_settings_equals
        call test_settings_size
        call test_settings_set_get_as
        call test_settings_erase
        call test_settings_clear
        call test_settings_is_a
        call test_settings_key

    print *, '[==========] Fortran API Settings'
    print *, '[  PASSED  ] Fortran API Settings'
    print *, ''
end program test_settings

