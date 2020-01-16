! This is generated code. If it's broken, then you should
! fix the generation script, not this file.


module ymmsl
    use iso_c_binding
    private

    integer, parameter, public :: YMMSL_success = 0
    integer, parameter, public :: YMMSL_runtime_error = 1
    integer, parameter, public :: YMMSL_domain_error = 2
    integer, parameter, public :: YMMSL_out_of_range = 3
    integer, parameter, public :: YMMSL_logic_error = 4
    integer, parameter, public :: YMMSL_bad_cast = 5

    integer, parameter, public :: YMMSL_int1 = selected_int_kind(2)
    integer, parameter, public :: YMMSL_int2 = selected_int_kind(4)
    integer, parameter, public :: YMMSL_int4 = selected_int_kind(9)
    integer, parameter, public :: YMMSL_int8 = selected_int_kind(18)
    integer, parameter, public :: YMMSL_size = c_size_t
    integer, parameter, public :: YMMSL_real4 = selected_real_kind(6)
    integer, parameter, public :: YMMSL_real8 = selected_real_kind(15)

    type YMMSL_Settings
        integer (c_intptr_t) :: ptr
    end type YMMSL_Settings
    public :: YMMSL_Settings

    public :: YMMSL_Settings_create
    public :: YMMSL_Settings_free
    public :: YMMSL_Settings_equals
    public :: YMMSL_Settings_size
    public :: YMMSL_Settings_empty
    public :: YMMSL_Settings_set_character
    public :: YMMSL_Settings_set_int8
    public :: YMMSL_Settings_set_real8
    public :: YMMSL_Settings_set_logical
    public :: YMMSL_Settings_set_real8array
    public :: YMMSL_Settings_set_real8array2
    public :: YMMSL_Settings_set
    public :: YMMSL_Settings_get_as_character
    public :: YMMSL_Settings_get_as_int8
    public :: YMMSL_Settings_get_as_real8
    public :: YMMSL_Settings_get_as_logical
    public :: YMMSL_Settings_get_as_real8array
    public :: YMMSL_Settings_get_as_real8array2
    public :: YMMSL_Settings_contains

    interface

        integer (c_intptr_t) function YMMSL_Settings_create_( &
                ) &
                bind(C, name="YMMSL_Settings_create_")

            use iso_c_binding
        end function YMMSL_Settings_create_

        subroutine YMMSL_Settings_free_( &
                self) &
                bind(C, name="YMMSL_Settings_free_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end subroutine YMMSL_Settings_free_

        integer (c_int) function YMMSL_Settings_equals_( &
                self, other) &
                bind(C, name="YMMSL_Settings_equals_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_intptr_t), value, intent(in) :: other
        end function YMMSL_Settings_equals_

        integer (c_size_t) function YMMSL_Settings_size_( &
                self) &
                bind(C, name="YMMSL_Settings_size_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function YMMSL_Settings_size_

        integer (c_int) function YMMSL_Settings_empty_( &
                self) &
                bind(C, name="YMMSL_Settings_empty_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function YMMSL_Settings_empty_

        subroutine YMMSL_Settings_set_character_( &
                self, key, key_size, value, value_size) &
                bind(C, name="YMMSL_Settings_set_character_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            character, intent(in) :: value
            integer (c_size_t), value, intent(in) :: value_size
        end subroutine YMMSL_Settings_set_character_

        subroutine YMMSL_Settings_set_int8_( &
                self, key, key_size, value) &
                bind(C, name="YMMSL_Settings_set_int8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_int64_t), value, intent(in) :: value
        end subroutine YMMSL_Settings_set_int8_

        subroutine YMMSL_Settings_set_real8_( &
                self, key, key_size, value) &
                bind(C, name="YMMSL_Settings_set_real8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            real (c_double), value, intent(in) :: value
        end subroutine YMMSL_Settings_set_real8_

        subroutine YMMSL_Settings_set_logical_( &
                self, key, key_size, value) &
                bind(C, name="YMMSL_Settings_set_logical_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_int), value, intent(in) :: value
        end subroutine YMMSL_Settings_set_logical_

        subroutine YMMSL_Settings_set_real8array_( &
                self, key, key_size, value, value_size) &
                bind(C, name="YMMSL_Settings_set_real8array_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            real (c_double), dimension(*), intent(in) :: value
            integer (c_size_t), value, intent(in) :: value_size
        end subroutine YMMSL_Settings_set_real8array_

        subroutine YMMSL_Settings_set_real8array2_( &
                self, key, key_size, value, value_shape) &
                bind(C, name="YMMSL_Settings_set_real8array2_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            real (c_double), dimension(*), intent(in) :: value
            integer (c_size_t), dimension(2), intent(in) :: value_shape
        end subroutine YMMSL_Settings_set_real8array2_

        subroutine YMMSL_Settings_get_as_character_( &
                self, key, key_size, ret_val, ret_val_size, err_code, err_msg, err_msg_len) &
                bind(C, name="YMMSL_Settings_get_as_character_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            type (c_ptr), intent(out) :: ret_val
            integer (c_size_t), intent(out) :: ret_val_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine YMMSL_Settings_get_as_character_

        integer (c_int64_t) function YMMSL_Settings_get_as_int8_( &
                self, key, key_size, err_code, err_msg, err_msg_len) &
                bind(C, name="YMMSL_Settings_get_as_int8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function YMMSL_Settings_get_as_int8_

        real (c_double) function YMMSL_Settings_get_as_real8_( &
                self, key, key_size, err_code, err_msg, err_msg_len) &
                bind(C, name="YMMSL_Settings_get_as_real8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function YMMSL_Settings_get_as_real8_

        integer (c_int) function YMMSL_Settings_get_as_logical_( &
                self, key, key_size, err_code, err_msg, err_msg_len) &
                bind(C, name="YMMSL_Settings_get_as_logical_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function YMMSL_Settings_get_as_logical_

        subroutine YMMSL_Settings_get_as_real8array_( &
                self, key, key_size, ret_val, ret_val_size, err_code, err_msg, err_msg_len) &
                bind(C, name="YMMSL_Settings_get_as_real8array_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            type (c_ptr), intent(out) :: ret_val
            integer (c_size_t), intent(out) :: ret_val_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine YMMSL_Settings_get_as_real8array_

        subroutine YMMSL_Settings_get_as_real8array2_( &
                self, key, key_size, ret_val, ret_val_shape, err_code, err_msg, err_msg_len) &
                bind(C, name="YMMSL_Settings_get_as_real8array2_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            type (c_ptr), intent(out) :: ret_val
            integer (c_size_t), dimension(2), intent(out) :: ret_val_shape
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine YMMSL_Settings_get_as_real8array2_

        integer (c_int) function YMMSL_Settings_contains_( &
                self, key, key_size) &
                bind(C, name="YMMSL_Settings_contains_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
        end function YMMSL_Settings_contains_

    end interface

    interface YMMSL_Settings_set
        module procedure &
            YMMSL_Settings_set_character, &
            YMMSL_Settings_set_int8, &
            YMMSL_Settings_set_real8, &
            YMMSL_Settings_set_logical, &
            YMMSL_Settings_set_real8array, &
            YMMSL_Settings_set_real8array2
    end interface


contains

    function YMMSL_Settings_create()
        implicit none
        type(YMMSL_Settings) :: YMMSL_Settings_create

        integer (c_intptr_t) :: ret_val

        ret_val = YMMSL_Settings_create_( &
    )

        YMMSL_Settings_create%ptr = ret_val
    end function YMMSL_Settings_create

    subroutine YMMSL_Settings_free(self)
        implicit none
        type(YMMSL_Settings), intent(in) :: self

        call YMMSL_Settings_free_( &
            self%ptr)
    end subroutine YMMSL_Settings_free

    function YMMSL_Settings_equals(self, other)
        implicit none
        type(YMMSL_Settings), intent(in) :: self
        type(YMMSL_Settings), intent(in) :: other
        logical :: YMMSL_Settings_equals

        integer (c_int) :: ret_val

        ret_val = YMMSL_Settings_equals_( &
            self%ptr, &
            other%ptr)

        YMMSL_Settings_equals = ret_val .ne. 0
    end function YMMSL_Settings_equals

    function YMMSL_Settings_size(self)
        implicit none
        type(YMMSL_Settings), intent(in) :: self
        integer (YMMSL_size) :: YMMSL_Settings_size

        integer (c_size_t) :: ret_val

        ret_val = YMMSL_Settings_size_( &
            self%ptr)
        YMMSL_Settings_size = ret_val
    end function YMMSL_Settings_size

    function YMMSL_Settings_empty(self)
        implicit none
        type(YMMSL_Settings), intent(in) :: self
        logical :: YMMSL_Settings_empty

        integer (c_int) :: ret_val

        ret_val = YMMSL_Settings_empty_( &
            self%ptr)

        YMMSL_Settings_empty = ret_val .ne. 0
    end function YMMSL_Settings_empty

    subroutine YMMSL_Settings_set_character(self, key, value)
        implicit none
        type(YMMSL_Settings), intent(in) :: self
        character (len=*), intent(in) :: key
        character (len=*), intent(in) :: value

        call YMMSL_Settings_set_character_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            value, int(len(value), c_size_t))
    end subroutine YMMSL_Settings_set_character

    subroutine YMMSL_Settings_set_int8(self, key, value)
        implicit none
        type(YMMSL_Settings), intent(in) :: self
        character (len=*), intent(in) :: key
        integer (selected_int_kind(18)), intent(in) :: value

        call YMMSL_Settings_set_int8_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            value)
    end subroutine YMMSL_Settings_set_int8

    subroutine YMMSL_Settings_set_real8(self, key, value)
        implicit none
        type(YMMSL_Settings), intent(in) :: self
        character (len=*), intent(in) :: key
        real (YMMSL_real8), intent(in) :: value

        call YMMSL_Settings_set_real8_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            value)
    end subroutine YMMSL_Settings_set_real8

    subroutine YMMSL_Settings_set_logical(self, key, value)
        implicit none
        type(YMMSL_Settings), intent(in) :: self
        character (len=*), intent(in) :: key
        logical, intent(in) :: value

        call YMMSL_Settings_set_logical_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            merge(1, 0, value))
    end subroutine YMMSL_Settings_set_logical

    subroutine YMMSL_Settings_set_real8array(self, key, value)
        implicit none
        type(YMMSL_Settings), intent(in) :: self
        character (len=*), intent(in) :: key
        real (YMMSL_real8), dimension(:), intent(in) :: value

        call YMMSL_Settings_set_real8array_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            value, int(size(value), c_size_t))
    end subroutine YMMSL_Settings_set_real8array

    subroutine YMMSL_Settings_set_real8array2(self, key, value)
        implicit none
        type(YMMSL_Settings), intent(in) :: self
        character (len=*), intent(in) :: key
        real (YMMSL_real8), dimension(:,:), intent(in) :: value

        call YMMSL_Settings_set_real8array2_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            value, int(shape(value), c_size_t))
    end subroutine YMMSL_Settings_set_real8array2

    function YMMSL_Settings_get_as_character(self, key, err_code, err_msg)
        implicit none
        type(YMMSL_Settings), intent(in) :: self
        character (len=*), intent(in) :: key
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        character(:), allocatable :: YMMSL_Settings_get_as_character

        type (c_ptr) :: ret_val
        integer (c_size_t) :: ret_val_size
        character (c_char), dimension(:), pointer :: f_ret_ptr
        integer :: i_loop
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call YMMSL_Settings_get_as_character_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            ret_val, &
            ret_val_size, &
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
        else
            if (present(err_code)) then
                err_code = 0
            end if
        end if

        call c_f_pointer(ret_val, f_ret_ptr, (/ret_val_size/))
        allocate (character(ret_val_size) :: YMMSL_Settings_get_as_character)
        do i_loop = 1, ret_val_size
            YMMSL_Settings_get_as_character(i_loop:i_loop) = f_ret_ptr(i_loop)
        end do
    end function YMMSL_Settings_get_as_character

    function YMMSL_Settings_get_as_int8(self, key, err_code, err_msg)
        implicit none
        type(YMMSL_Settings), intent(in) :: self
        character (len=*), intent(in) :: key
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        integer (selected_int_kind(18)) :: YMMSL_Settings_get_as_int8

        integer (c_int64_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = YMMSL_Settings_get_as_int8_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
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
        else
            if (present(err_code)) then
                err_code = 0
            end if
        end if

        YMMSL_Settings_get_as_int8 = ret_val
    end function YMMSL_Settings_get_as_int8

    function YMMSL_Settings_get_as_real8(self, key, err_code, err_msg)
        implicit none
        type(YMMSL_Settings), intent(in) :: self
        character (len=*), intent(in) :: key
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        real (YMMSL_real8) :: YMMSL_Settings_get_as_real8

        real (c_double) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = YMMSL_Settings_get_as_real8_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
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
        else
            if (present(err_code)) then
                err_code = 0
            end if
        end if

        YMMSL_Settings_get_as_real8 = ret_val
    end function YMMSL_Settings_get_as_real8

    function YMMSL_Settings_get_as_logical(self, key, err_code, err_msg)
        implicit none
        type(YMMSL_Settings), intent(in) :: self
        character (len=*), intent(in) :: key
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        logical :: YMMSL_Settings_get_as_logical

        integer (c_int) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = YMMSL_Settings_get_as_logical_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
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
        else
            if (present(err_code)) then
                err_code = 0
            end if
        end if

        YMMSL_Settings_get_as_logical = ret_val .ne. 0
    end function YMMSL_Settings_get_as_logical

    subroutine YMMSL_Settings_get_as_real8array(self, key, value, err_code, err_msg)
        implicit none
        type(YMMSL_Settings), intent(in) :: self
        character (len=*), intent(in) :: key
        real (YMMSL_real8), dimension(:), intent(out) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        type (c_ptr) :: ret_val
        integer (c_size_t) :: ret_val_size
        real (YMMSL_real8), pointer, dimension(:) :: f_ret_ptr
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call YMMSL_Settings_get_as_real8array_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            ret_val, &
            ret_val_size, &
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
        else
            if (present(err_code)) then
                err_code = 0
            end if
        end if

        call c_f_pointer(ret_val, f_ret_ptr, (/ret_val_size/))
        value = f_ret_ptr
    end subroutine YMMSL_Settings_get_as_real8array

    subroutine YMMSL_Settings_get_as_real8array2(self, key, value, err_code, err_msg)
        implicit none
        type(YMMSL_Settings), intent(in) :: self
        character (len=*), intent(in) :: key
        real (YMMSL_real8), dimension(:,:), intent(out) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        type (c_ptr) :: ret_val
        integer (c_size_t), dimension(2) :: ret_val_shape
        real (YMMSL_real8), pointer, dimension(:,:) :: f_ret_ptr
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call YMMSL_Settings_get_as_real8array2_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            ret_val, &
            ret_val_shape, &
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
        else
            if (present(err_code)) then
                err_code = 0
            end if
        end if

        call c_f_pointer(ret_val, f_ret_ptr, ret_val_shape)
        value = f_ret_ptr
    end subroutine YMMSL_Settings_get_as_real8array2

    function YMMSL_Settings_contains(self, key)
        implicit none
        type(YMMSL_Settings), intent(in) :: self
        character (len=*), intent(in) :: key
        logical :: YMMSL_Settings_contains

        integer (c_int) :: ret_val

        ret_val = YMMSL_Settings_contains_( &
            self%ptr, &
            key, int(len(key), c_size_t))

        YMMSL_Settings_contains = ret_val .ne. 0
    end function YMMSL_Settings_contains


end module ymmsl

