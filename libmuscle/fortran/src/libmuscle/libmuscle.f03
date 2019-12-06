! This is generated code. If it's broken, then you should
! fix the generation script, not this file.


module libmuscle
    use iso_c_binding
    private

    integer, parameter, public :: LIBMUSCLE_runtime_error = 1
    integer, parameter, public :: LIBMUSCLE_domain_error = 2
    integer, parameter, public :: LIBMUSCLE_out_of_range = 3
    integer, parameter, public :: LIBMUSCLE_logic_error = 4

    type LIBMUSCLE_Data
        integer (c_intptr_t) :: ptr
    end type LIBMUSCLE_Data
    public :: LIBMUSCLE_Data

    public :: LIBMUSCLE_Data_create_nil
    public :: LIBMUSCLE_Data_create_bool
    public :: LIBMUSCLE_Data_create_string
    public :: LIBMUSCLE_Data_create_int
    public :: LIBMUSCLE_Data_create_int64t
    public :: LIBMUSCLE_Data_create_float
    public :: LIBMUSCLE_Data_create_double
    public :: LIBMUSCLE_Data_create
    public :: LIBMUSCLE_Data_free

    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_runtime_error = 1
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_domain_error = 2
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_out_of_range = 3
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_logic_error = 4

    type LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs
        integer (c_intptr_t) :: ptr
    end type LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs


    interface

        integer (c_intptr_t) function LIBMUSCLE_Data_create_nil_( &
                ) &
                bind(C, name="LIBMUSCLE_Data_create_nil_")

            use iso_c_binding
        end function LIBMUSCLE_Data_create_nil_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_bool_( &
                value) &
                bind(C, name="LIBMUSCLE_Data_create_bool_")

            use iso_c_binding
            integer (c_int), value, intent(in) :: value
        end function LIBMUSCLE_Data_create_bool_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_string_( &
                value, value_size) &
                bind(C, name="LIBMUSCLE_Data_create_string_")

            use iso_c_binding
            character, intent(in) :: value
            integer (c_size_t), value, intent(in) :: value_size
        end function LIBMUSCLE_Data_create_string_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_int_( &
                value) &
                bind(C, name="LIBMUSCLE_Data_create_int_")

            use iso_c_binding
            integer (c_int), value, intent(in) :: value
        end function LIBMUSCLE_Data_create_int_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_int64t_( &
                value) &
                bind(C, name="LIBMUSCLE_Data_create_int64t_")

            use iso_c_binding
            integer (c_int64_t), value, intent(in) :: value
        end function LIBMUSCLE_Data_create_int64t_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_float_( &
                value) &
                bind(C, name="LIBMUSCLE_Data_create_float_")

            use iso_c_binding
            real (selected_real_kind(6)), value, intent(in) :: value
        end function LIBMUSCLE_Data_create_float_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_double_( &
                value) &
                bind(C, name="LIBMUSCLE_Data_create_double_")

            use iso_c_binding
            real (selected_real_kind(15)), value, intent(in) :: value
        end function LIBMUSCLE_Data_create_double_

        subroutine LIBMUSCLE_Data_free_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_free_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end subroutine LIBMUSCLE_Data_free_

    end interface

    interface LIBMUSCLE_Data_create
        module procedure &
            LIBMUSCLE_Data_create_nil, &
            LIBMUSCLE_Data_create_bool, &
            LIBMUSCLE_Data_create_string, &
            LIBMUSCLE_Data_create_int, &
            LIBMUSCLE_Data_create_int64t, &
            LIBMUSCLE_Data_create_float, &
            LIBMUSCLE_Data_create_double
    end interface


    interface

        integer (c_intptr_t) function LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create_( &
                count) &
                bind(C, name="LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create_")

            use iso_c_binding
            integer (c_int), value, intent(in) :: count
        end function LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create_

        subroutine LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_free_( &
                self) &
                bind(C, name="LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_free_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end subroutine LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_free_

        subroutine LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_set_arg_( &
                self, i, arg, arg_size) &
                bind(C, name="LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_set_arg_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), value, intent(in) :: i
            character, intent(in) :: arg
            integer (c_size_t), value, intent(in) :: arg_size
        end subroutine LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_set_arg_

    end interface


contains

    function LIBMUSCLE_Data_create_nil()
        implicit none
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_nil

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_nil_( &
    )

        LIBMUSCLE_Data_create_nil%ptr = ret_val
    end function LIBMUSCLE_Data_create_nil

    function LIBMUSCLE_Data_create_bool(value)
        implicit none
        logical, intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_bool

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_bool_( &
            merge(1, 0, value))

        LIBMUSCLE_Data_create_bool%ptr = ret_val
    end function LIBMUSCLE_Data_create_bool

    function LIBMUSCLE_Data_create_string(value)
        implicit none
        character (len=*), intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_string

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_string_( &
            value, int(len(value), c_size_t))

        LIBMUSCLE_Data_create_string%ptr = ret_val
    end function LIBMUSCLE_Data_create_string

    function LIBMUSCLE_Data_create_int(value)
        implicit none
        integer, intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_int

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_int_( &
            value)

        LIBMUSCLE_Data_create_int%ptr = ret_val
    end function LIBMUSCLE_Data_create_int

    function LIBMUSCLE_Data_create_int64t(value)
        implicit none
        integer (selected_int_kind(18)), intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_int64t

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_int64t_( &
            value)

        LIBMUSCLE_Data_create_int64t%ptr = ret_val
    end function LIBMUSCLE_Data_create_int64t

    function LIBMUSCLE_Data_create_float(value)
        implicit none
        real (selected_real_kind(6)), intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_float

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_float_( &
            value)

        LIBMUSCLE_Data_create_float%ptr = ret_val
    end function LIBMUSCLE_Data_create_float

    function LIBMUSCLE_Data_create_double(value)
        implicit none
        real (selected_real_kind(15)), intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_double

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_double_( &
            value)

        LIBMUSCLE_Data_create_double%ptr = ret_val
    end function LIBMUSCLE_Data_create_double

    subroutine LIBMUSCLE_Data_free(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self

        call LIBMUSCLE_Data_free_( &
            self%ptr)
    end subroutine LIBMUSCLE_Data_free


    function LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create(count)
        implicit none
        integer, intent(in) :: count
        type(LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs) :: LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create_( &
            count)

        LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create%ptr = ret_val
    end function LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create

    subroutine LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_free(self)
        implicit none
        type(LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs), intent(in) :: self

        call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_free_( &
            self%ptr)
    end subroutine LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_free

    subroutine LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_set_arg(self, i, arg)
        implicit none
        type(LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs), intent(in) :: self
        integer, intent(in) :: i
        character (len=*), intent(in) :: arg

        call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_set_arg_( &
            self%ptr, &
            i, &
            arg, int(len(arg), c_size_t))
    end subroutine LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_set_arg


end module libmuscle

