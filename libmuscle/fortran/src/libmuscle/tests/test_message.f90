module message_tests
    use assert
    implicit none
contains
    subroutine test_message_create
        use libmuscle
        use ymmsl
        implicit none

        type(LIBMUSCLE_Data) :: d1
        type(LIBMUSCLE_Message) :: m1
        type(YMMSL_Settings) :: s1

        print *, '[  RUN     ] message.create'
        d1 = LIBMUSCLE_Data()

        m1 = LIBMUSCLE_Message(0.0d0, d1)
        call LIBMUSCLE_Message_free(m1)

        m1 = LIBMUSCLE_Message(0.0d0, 1.0d0, d1)
        call LIBMUSCLE_Message_free(m1)

        s1 = YMMSL_Settings_create()
        m1 = LIBMUSCLE_Message(0.0d0, d1, s1)
        call LIBMUSCLE_Message_free(m1)
        call YMMSL_Settings_free(s1)

        s1 = YMMSL_Settings_create()
        m1 = LIBMUSCLE_Message(0.0d0, 10.0d0, d1, s1)
        call LIBMUSCLE_Message_free(m1)
        call YMMSL_Settings_free(s1)

        call LIBMUSCLE_Data_free(d1)
        print *, '[       OK ] message.create'
    end subroutine test_message_create

    subroutine test_message_timestamps
        use libmuscle
        implicit none

        type(LIBMUSCLE_Data) :: d1
        type(LIBMUSCLE_Message) :: m1

        print *, '[  RUN     ] message.timestamps'
        d1 = LIBMUSCLE_Data()
        m1 = LIBMUSCLE_Message(23.4d0, d1)

        call assert_eq_real8(m1%timestamp(), 23.4d0)
        call m1%set_timestamp(12.8d0)
        call assert_eq_real8(m1%timestamp(), 12.8d0)

        call assert_false(m1%has_next_timestamp())
        call m1%set_next_timestamp(101.0d0)
        call assert_true(m1%has_next_timestamp())
        call assert_eq_real8(m1%next_timestamp(), 101.0d0)
        call m1%unset_next_timestamp()
        call assert_false(m1%has_next_timestamp())

        call LIBMUSCLE_Message_free(m1)
        call LIBMUSCLE_Data_free(d1)
        print *, '[       OK ] message.timestamps'
    end subroutine test_message_timestamps

    subroutine test_message_data
        use libmuscle
        implicit none

        type(LIBMUSCLE_Data) :: d1, d2
        type(LIBMUSCLE_DataConstRef) :: d3
        type(LIBMUSCLE_Message) :: m1

        print *, '[  RUN     ] message.data'
        d1 = LIBMUSCLE_Data('Testing')
        m1 = LIBMUSCLE_Message(0.0d0, d1)
        call LIBMUSCLE_Data_free(d1)

        d3 = m1%get_data()
        call assert_eq_character(d3%as_character(), 'Testing')
        call LIBMUSCLE_DataConstRef_free(d3)

        d2 = LIBMUSCLE_Data(1001)
        call m1%set_data(d2)
        call LIBMUSCLE_Data_free(d2)

        d3 = m1%get_data()
        call assert_eq_int4(d3%as_int4(), 1001_LIBMUSCLE_int4)
        call LIBMUSCLE_DataConstRef_free(d3)

        d3 = LIBMUSCLE_DataConstRef('Still testing')
        call m1%set_data(d3)
        call LIBMUSCLE_DataConstRef_free(d3)

        d3 = m1%get_data()
        call assert_eq_character(d3%as_character(), 'Still testing')
        call LIBMUSCLE_DataConstRef_free(d3)

        call LIBMUSCLE_Message_free(m1)
        print *, '[       OK ] message.data'
    end subroutine test_message_data

    subroutine test_message_settings
        use libmuscle
        use ymmsl
        implicit none

        type(LIBMUSCLE_Data) :: d1
        type(YMMSL_Settings) :: s1, s2
        type(LIBMUSCLE_Message) :: m1

        print *, '[  RUN     ] message.settings'
        d1 = LIBMUSCLE_Data()
        m1 = LIBMUSCLE_Message(0.0d0, d1)
        call assert_false(m1%has_settings())
        call LIBMUSCLE_Message_free(m1)
        call LIBMUSCLE_Data_free(d1)

        d1 = LIBMUSCLE_Data()
        s1 = YMMSL_Settings_create()
        call YMMSL_Settings_set(s1, 'key', 'value')
        m1 = LIBMUSCLE_Message(0.0d0, d1, s1)
        call YMMSL_Settings_free(s1)
        call LIBMUSCLE_Data_free(d1)

        call assert_true(m1%has_settings())
        s2 = m1%get_settings()
        call assert_eq_character(YMMSL_Settings_get_as_character(s2, 'key'), 'value')
        call YMMSL_Settings_free(s2)

        s1 = YMMSL_Settings_create()
        call YMMSL_Settings_set(s1, 'key2', 'value2')
        call m1%set_settings(s1)
        call YMMSL_Settings_free(s1)

        s2 = m1%get_settings()
        call assert_eq_character(YMMSL_Settings_get_as_character(s2, 'key2'), 'value2')
        call YMMSL_Settings_free(s2)

        call m1%unset_settings()
        call assert_false(m1%has_settings())

        call LIBMUSCLE_Message_free(m1)
        print *, '[       OK ] message.settings'
    end subroutine test_message_settings
end module message_tests

program test_message
    use message_tests
    implicit none

    print *, ''
    print *, '[==========] Fortran API Message'

    call test_message_create
    call test_message_timestamps
    call test_message_data
    call test_message_settings

    print *, '[==========] Fortran API Message'
    print *, '[  PASSED  ] Fortran API Message'
    print *, ''
end program test_message

