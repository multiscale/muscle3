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
    public :: LIBMUSCLE_Data_create_char
    public :: LIBMUSCLE_Data_create_int
    public :: LIBMUSCLE_Data_create_int16t
    public :: LIBMUSCLE_Data_create_int64t
    public :: LIBMUSCLE_Data_create_float
    public :: LIBMUSCLE_Data_create_double
    public :: LIBMUSCLE_Data_create_copy
    public :: LIBMUSCLE_Data_create
    public :: LIBMUSCLE_Data_free
    public :: LIBMUSCLE_Data_is_a_bool
    public :: LIBMUSCLE_Data_is_a_string
    public :: LIBMUSCLE_Data_is_a_char
    public :: LIBMUSCLE_Data_is_a_int
    public :: LIBMUSCLE_Data_is_a_int16
    public :: LIBMUSCLE_Data_is_a_int64
    public :: LIBMUSCLE_Data_is_a_float
    public :: LIBMUSCLE_Data_is_a_double

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

        integer (c_intptr_t) function LIBMUSCLE_Data_create_char_( &
                value) &
                bind(C, name="LIBMUSCLE_Data_create_char_")

            use iso_c_binding
            integer (c_int8_t), value, intent(in) :: value
        end function LIBMUSCLE_Data_create_char_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_int_( &
                value) &
                bind(C, name="LIBMUSCLE_Data_create_int_")

            use iso_c_binding
            integer (c_int), value, intent(in) :: value
        end function LIBMUSCLE_Data_create_int_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_int16t_( &
                value) &
                bind(C, name="LIBMUSCLE_Data_create_int16t_")

            use iso_c_binding
            integer (c_short), value, intent(in) :: value
        end function LIBMUSCLE_Data_create_int16t_

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

        integer (c_intptr_t) function LIBMUSCLE_Data_create_copy_( &
                value) &
                bind(C, name="LIBMUSCLE_Data_create_copy_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: value
        end function LIBMUSCLE_Data_create_copy_

        subroutine LIBMUSCLE_Data_free_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_free_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end subroutine LIBMUSCLE_Data_free_

        integer (c_int) function LIBMUSCLE_Data_is_a_bool_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_is_a_bool_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_is_a_bool_

        integer (c_int) function LIBMUSCLE_Data_is_a_string_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_is_a_string_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_is_a_string_

        integer (c_int) function LIBMUSCLE_Data_is_a_char_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_is_a_char_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_is_a_char_

        integer (c_int) function LIBMUSCLE_Data_is_a_int_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_is_a_int_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_is_a_int_

        integer (c_int) function LIBMUSCLE_Data_is_a_int16_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_is_a_int16_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_is_a_int16_

        integer (c_int) function LIBMUSCLE_Data_is_a_int64_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_is_a_int64_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_is_a_int64_

        integer (c_int) function LIBMUSCLE_Data_is_a_float_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_is_a_float_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_is_a_float_

        integer (c_int) function LIBMUSCLE_Data_is_a_double_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_is_a_double_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_is_a_double_

    end interface

    interface LIBMUSCLE_Data_create
        module procedure &
            LIBMUSCLE_Data_create_nil, &
            LIBMUSCLE_Data_create_bool, &
            LIBMUSCLE_Data_create_string, &
            LIBMUSCLE_Data_create_char, &
            LIBMUSCLE_Data_create_int, &
            LIBMUSCLE_Data_create_int16t, &
            LIBMUSCLE_Data_create_int64t, &
            LIBMUSCLE_Data_create_float, &
            LIBMUSCLE_Data_create_double, &
            LIBMUSCLE_Data_create_copy
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

    function LIBMUSCLE_Data_create_char(value)
        implicit none
        integer (selected_int_kind(2)), intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_char

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_char_( &
            value)

        LIBMUSCLE_Data_create_char%ptr = ret_val
    end function LIBMUSCLE_Data_create_char

    function LIBMUSCLE_Data_create_int(value)
        implicit none
        integer, intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_int

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_int_( &
            value)

        LIBMUSCLE_Data_create_int%ptr = ret_val
    end function LIBMUSCLE_Data_create_int

    function LIBMUSCLE_Data_create_int16t(value)
        implicit none
        integer (selected_int_kind(4)), intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_int16t

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_int16t_( &
            value)

        LIBMUSCLE_Data_create_int16t%ptr = ret_val
    end function LIBMUSCLE_Data_create_int16t

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

    function LIBMUSCLE_Data_create_copy(value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_copy

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_copy_( &
            value%ptr)

        LIBMUSCLE_Data_create_copy%ptr = ret_val
    end function LIBMUSCLE_Data_create_copy

    subroutine LIBMUSCLE_Data_free(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self

        call LIBMUSCLE_Data_free_( &
            self%ptr)
    end subroutine LIBMUSCLE_Data_free

    function LIBMUSCLE_Data_is_a_bool(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        logical :: LIBMUSCLE_Data_is_a_bool

        integer (c_int) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_is_a_bool_( &
            self%ptr, &
            err_code_v, &
            err_msg_v, &
            err_msg_len_v)

        if (err_code_v .ne. 0) then
            if (present(err_code)) then
                err_code = err_code_v
                if (present(err_msg)) then
                    call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                    allocate (character(err_msg_len_v) :: err_msg)
                    do err_msg_i = 1, err_msg_len_v
                        err_msg(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                    end do
                end if
                return
            else
                call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                allocate (character(err_msg_len_v) :: err_msg_p)
                do err_msg_i = 1, err_msg_len_v
                    err_msg_p(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                end do
                print *, err_msg_p
                stop
            end if
        end if

        LIBMUSCLE_Data_is_a_bool = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_bool

    function LIBMUSCLE_Data_is_a_string(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        logical :: LIBMUSCLE_Data_is_a_string

        integer (c_int) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_is_a_string_( &
            self%ptr, &
            err_code_v, &
            err_msg_v, &
            err_msg_len_v)

        if (err_code_v .ne. 0) then
            if (present(err_code)) then
                err_code = err_code_v
                if (present(err_msg)) then
                    call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                    allocate (character(err_msg_len_v) :: err_msg)
                    do err_msg_i = 1, err_msg_len_v
                        err_msg(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                    end do
                end if
                return
            else
                call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                allocate (character(err_msg_len_v) :: err_msg_p)
                do err_msg_i = 1, err_msg_len_v
                    err_msg_p(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                end do
                print *, err_msg_p
                stop
            end if
        end if

        LIBMUSCLE_Data_is_a_string = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_string

    function LIBMUSCLE_Data_is_a_char(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        logical :: LIBMUSCLE_Data_is_a_char

        integer (c_int) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_is_a_char_( &
            self%ptr, &
            err_code_v, &
            err_msg_v, &
            err_msg_len_v)

        if (err_code_v .ne. 0) then
            if (present(err_code)) then
                err_code = err_code_v
                if (present(err_msg)) then
                    call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                    allocate (character(err_msg_len_v) :: err_msg)
                    do err_msg_i = 1, err_msg_len_v
                        err_msg(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                    end do
                end if
                return
            else
                call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                allocate (character(err_msg_len_v) :: err_msg_p)
                do err_msg_i = 1, err_msg_len_v
                    err_msg_p(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                end do
                print *, err_msg_p
                stop
            end if
        end if

        LIBMUSCLE_Data_is_a_char = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_char

    function LIBMUSCLE_Data_is_a_int(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        logical :: LIBMUSCLE_Data_is_a_int

        integer (c_int) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_is_a_int_( &
            self%ptr, &
            err_code_v, &
            err_msg_v, &
            err_msg_len_v)

        if (err_code_v .ne. 0) then
            if (present(err_code)) then
                err_code = err_code_v
                if (present(err_msg)) then
                    call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                    allocate (character(err_msg_len_v) :: err_msg)
                    do err_msg_i = 1, err_msg_len_v
                        err_msg(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                    end do
                end if
                return
            else
                call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                allocate (character(err_msg_len_v) :: err_msg_p)
                do err_msg_i = 1, err_msg_len_v
                    err_msg_p(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                end do
                print *, err_msg_p
                stop
            end if
        end if

        LIBMUSCLE_Data_is_a_int = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_int

    function LIBMUSCLE_Data_is_a_int16(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        logical :: LIBMUSCLE_Data_is_a_int16

        integer (c_int) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_is_a_int16_( &
            self%ptr, &
            err_code_v, &
            err_msg_v, &
            err_msg_len_v)

        if (err_code_v .ne. 0) then
            if (present(err_code)) then
                err_code = err_code_v
                if (present(err_msg)) then
                    call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                    allocate (character(err_msg_len_v) :: err_msg)
                    do err_msg_i = 1, err_msg_len_v
                        err_msg(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                    end do
                end if
                return
            else
                call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                allocate (character(err_msg_len_v) :: err_msg_p)
                do err_msg_i = 1, err_msg_len_v
                    err_msg_p(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                end do
                print *, err_msg_p
                stop
            end if
        end if

        LIBMUSCLE_Data_is_a_int16 = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_int16

    function LIBMUSCLE_Data_is_a_int64(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        logical :: LIBMUSCLE_Data_is_a_int64

        integer (c_int) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_is_a_int64_( &
            self%ptr, &
            err_code_v, &
            err_msg_v, &
            err_msg_len_v)

        if (err_code_v .ne. 0) then
            if (present(err_code)) then
                err_code = err_code_v
                if (present(err_msg)) then
                    call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                    allocate (character(err_msg_len_v) :: err_msg)
                    do err_msg_i = 1, err_msg_len_v
                        err_msg(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                    end do
                end if
                return
            else
                call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                allocate (character(err_msg_len_v) :: err_msg_p)
                do err_msg_i = 1, err_msg_len_v
                    err_msg_p(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                end do
                print *, err_msg_p
                stop
            end if
        end if

        LIBMUSCLE_Data_is_a_int64 = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_int64

    function LIBMUSCLE_Data_is_a_float(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        logical :: LIBMUSCLE_Data_is_a_float

        integer (c_int) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_is_a_float_( &
            self%ptr, &
            err_code_v, &
            err_msg_v, &
            err_msg_len_v)

        if (err_code_v .ne. 0) then
            if (present(err_code)) then
                err_code = err_code_v
                if (present(err_msg)) then
                    call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                    allocate (character(err_msg_len_v) :: err_msg)
                    do err_msg_i = 1, err_msg_len_v
                        err_msg(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                    end do
                end if
                return
            else
                call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                allocate (character(err_msg_len_v) :: err_msg_p)
                do err_msg_i = 1, err_msg_len_v
                    err_msg_p(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                end do
                print *, err_msg_p
                stop
            end if
        end if

        LIBMUSCLE_Data_is_a_float = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_float

    function LIBMUSCLE_Data_is_a_double(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        logical :: LIBMUSCLE_Data_is_a_double

        integer (c_int) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_is_a_double_( &
            self%ptr, &
            err_code_v, &
            err_msg_v, &
            err_msg_len_v)

        if (err_code_v .ne. 0) then
            if (present(err_code)) then
                err_code = err_code_v
                if (present(err_msg)) then
                    call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                    allocate (character(err_msg_len_v) :: err_msg)
                    do err_msg_i = 1, err_msg_len_v
                        err_msg(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                    end do
                end if
                return
            else
                call c_f_pointer(err_msg_v, err_msg_f, (/err_msg_len_v/))
                allocate (character(err_msg_len_v) :: err_msg_p)
                do err_msg_i = 1, err_msg_len_v
                    err_msg_p(err_msg_i:err_msg_i) = err_msg_f(err_msg_i)
                end do
                print *, err_msg_p
                stop
            end if
        end if

        LIBMUSCLE_Data_is_a_double = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_double


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

