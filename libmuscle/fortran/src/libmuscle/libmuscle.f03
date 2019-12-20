! This is generated code. If it's broken, then you should
! fix the generation script, not this file.


module libmuscle
    use iso_c_binding
    private

    integer, parameter, public :: LIBMUSCLE_success = 0
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
    public :: LIBMUSCLE_Data_create_dict
    public :: LIBMUSCLE_Data_create_list
    public :: LIBMUSCLE_Data_create_byte_array
    public :: LIBMUSCLE_Data_create_nils
    public :: LIBMUSCLE_Data_set_bool
    public :: LIBMUSCLE_Data_set_string
    public :: LIBMUSCLE_Data_set_char
    public :: LIBMUSCLE_Data_set_int16
    public :: LIBMUSCLE_Data_set_int
    public :: LIBMUSCLE_Data_set_int64
    public :: LIBMUSCLE_Data_set_float
    public :: LIBMUSCLE_Data_set_double
    public :: LIBMUSCLE_Data_set_data
    public :: LIBMUSCLE_Data_set
    public :: LIBMUSCLE_Data_set_nil
    public :: LIBMUSCLE_Data_is_a_bool
    public :: LIBMUSCLE_Data_is_a_string
    public :: LIBMUSCLE_Data_is_a_char
    public :: LIBMUSCLE_Data_is_a_int
    public :: LIBMUSCLE_Data_is_a_int16
    public :: LIBMUSCLE_Data_is_a_int64
    public :: LIBMUSCLE_Data_is_a_float
    public :: LIBMUSCLE_Data_is_a_double
    public :: LIBMUSCLE_Data_is_a_dict
    public :: LIBMUSCLE_Data_is_a_list
    public :: LIBMUSCLE_Data_is_a_byte_array
    public :: LIBMUSCLE_Data_is_nil
    public :: LIBMUSCLE_Data_size
    public :: LIBMUSCLE_Data_as_bool
    public :: LIBMUSCLE_Data_as_string
    public :: LIBMUSCLE_Data_as_char
    public :: LIBMUSCLE_Data_as_int16
    public :: LIBMUSCLE_Data_as_int
    public :: LIBMUSCLE_Data_as_int64
    public :: LIBMUSCLE_Data_as_float
    public :: LIBMUSCLE_Data_as_double
    public :: LIBMUSCLE_Data_as_byte_array
    public :: LIBMUSCLE_Data_get_item
    public :: LIBMUSCLE_Data_set_item_key_bool
    public :: LIBMUSCLE_Data_set_item_key_string
    public :: LIBMUSCLE_Data_set_item_key_char
    public :: LIBMUSCLE_Data_set_item_key_int16
    public :: LIBMUSCLE_Data_set_item_key_int
    public :: LIBMUSCLE_Data_set_item_key_int64
    public :: LIBMUSCLE_Data_set_item_key_float
    public :: LIBMUSCLE_Data_set_item_key_double
    public :: LIBMUSCLE_Data_set_item_key_data
    public :: LIBMUSCLE_Data_set_item

    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_success = 0
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

        integer (c_intptr_t) function LIBMUSCLE_Data_create_dict_( &
                ) &
                bind(C, name="LIBMUSCLE_Data_create_dict_")

            use iso_c_binding
        end function LIBMUSCLE_Data_create_dict_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_list_( &
                ) &
                bind(C, name="LIBMUSCLE_Data_create_list_")

            use iso_c_binding
        end function LIBMUSCLE_Data_create_list_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_byte_array_( &
                size) &
                bind(C, name="LIBMUSCLE_Data_create_byte_array_")

            use iso_c_binding
            integer (c_size_t), value, intent(in) :: size
        end function LIBMUSCLE_Data_create_byte_array_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_nils_( &
                size) &
                bind(C, name="LIBMUSCLE_Data_create_nils_")

            use iso_c_binding
            integer (c_size_t), value, intent(in) :: size
        end function LIBMUSCLE_Data_create_nils_

        subroutine LIBMUSCLE_Data_set_bool_( &
                self, value) &
                bind(C, name="LIBMUSCLE_Data_set_bool_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), value, intent(in) :: value
        end subroutine LIBMUSCLE_Data_set_bool_

        subroutine LIBMUSCLE_Data_set_string_( &
                self, value, value_size) &
                bind(C, name="LIBMUSCLE_Data_set_string_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: value
            integer (c_size_t), value, intent(in) :: value_size
        end subroutine LIBMUSCLE_Data_set_string_

        subroutine LIBMUSCLE_Data_set_char_( &
                self, value) &
                bind(C, name="LIBMUSCLE_Data_set_char_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int8_t), value, intent(in) :: value
        end subroutine LIBMUSCLE_Data_set_char_

        subroutine LIBMUSCLE_Data_set_int16_( &
                self, value) &
                bind(C, name="LIBMUSCLE_Data_set_int16_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_short), value, intent(in) :: value
        end subroutine LIBMUSCLE_Data_set_int16_

        subroutine LIBMUSCLE_Data_set_int_( &
                self, value) &
                bind(C, name="LIBMUSCLE_Data_set_int_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), value, intent(in) :: value
        end subroutine LIBMUSCLE_Data_set_int_

        subroutine LIBMUSCLE_Data_set_int64_( &
                self, value) &
                bind(C, name="LIBMUSCLE_Data_set_int64_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int64_t), value, intent(in) :: value
        end subroutine LIBMUSCLE_Data_set_int64_

        subroutine LIBMUSCLE_Data_set_float_( &
                self, value) &
                bind(C, name="LIBMUSCLE_Data_set_float_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            real (selected_real_kind(6)), value, intent(in) :: value
        end subroutine LIBMUSCLE_Data_set_float_

        subroutine LIBMUSCLE_Data_set_double_( &
                self, value) &
                bind(C, name="LIBMUSCLE_Data_set_double_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            real (selected_real_kind(15)), value, intent(in) :: value
        end subroutine LIBMUSCLE_Data_set_double_

        subroutine LIBMUSCLE_Data_set_data_( &
                self, value) &
                bind(C, name="LIBMUSCLE_Data_set_data_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_intptr_t), value, intent(in) :: value
        end subroutine LIBMUSCLE_Data_set_data_

        subroutine LIBMUSCLE_Data_set_nil_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_set_nil_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end subroutine LIBMUSCLE_Data_set_nil_

        integer (c_int) function LIBMUSCLE_Data_is_a_bool_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_bool_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_bool_

        integer (c_int) function LIBMUSCLE_Data_is_a_string_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_string_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_string_

        integer (c_int) function LIBMUSCLE_Data_is_a_char_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_char_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_char_

        integer (c_int) function LIBMUSCLE_Data_is_a_int_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_int_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_int_

        integer (c_int) function LIBMUSCLE_Data_is_a_int16_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_int16_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_int16_

        integer (c_int) function LIBMUSCLE_Data_is_a_int64_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_int64_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_int64_

        integer (c_int) function LIBMUSCLE_Data_is_a_float_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_float_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_float_

        integer (c_int) function LIBMUSCLE_Data_is_a_double_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_double_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_double_

        integer (c_int) function LIBMUSCLE_Data_is_a_dict_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_dict_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_dict_

        integer (c_int) function LIBMUSCLE_Data_is_a_list_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_list_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_list_

        integer (c_int) function LIBMUSCLE_Data_is_a_byte_array_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_byte_array_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_byte_array_

        integer (c_int) function LIBMUSCLE_Data_is_nil_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_nil_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_nil_

        integer (c_int64_t) function LIBMUSCLE_Data_size_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_size_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_size_

        integer (c_int) function LIBMUSCLE_Data_as_bool_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_bool_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_as_bool_

        subroutine LIBMUSCLE_Data_as_string_( &
                self, ret_val, ret_val_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_string_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            type (c_ptr), intent(out) :: ret_val
            integer (c_size_t), intent(out) :: ret_val_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_as_string_

        integer (c_int8_t) function LIBMUSCLE_Data_as_char_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_char_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_as_char_

        integer (c_short) function LIBMUSCLE_Data_as_int16_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_int16_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_as_int16_

        integer (c_int) function LIBMUSCLE_Data_as_int_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_int_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_as_int_

        integer (c_int64_t) function LIBMUSCLE_Data_as_int64_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_int64_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_as_int64_

        real (selected_real_kind(6)) function LIBMUSCLE_Data_as_float_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_float_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_as_float_

        real (selected_real_kind(15)) function LIBMUSCLE_Data_as_double_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_double_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_as_double_

        subroutine LIBMUSCLE_Data_as_byte_array_( &
                self, ret_val, ret_val_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_byte_array_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            type (c_ptr), intent(out) :: ret_val
            integer (c_size_t), intent(out) :: ret_val_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_as_byte_array_

        integer (c_intptr_t) function LIBMUSCLE_Data_get_item_( &
                self, key, key_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_get_item_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_get_item_

        subroutine LIBMUSCLE_Data_set_item_key_bool_( &
                self, key, key_size, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_key_bool_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_int), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_key_bool_

        subroutine LIBMUSCLE_Data_set_item_key_string_( &
                self, key, key_size, value, value_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_key_string_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            character, intent(in) :: value
            integer (c_size_t), value, intent(in) :: value_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_key_string_

        subroutine LIBMUSCLE_Data_set_item_key_char_( &
                self, key, key_size, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_key_char_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_int8_t), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_key_char_

        subroutine LIBMUSCLE_Data_set_item_key_int16_( &
                self, key, key_size, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_key_int16_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_short), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_key_int16_

        subroutine LIBMUSCLE_Data_set_item_key_int_( &
                self, key, key_size, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_key_int_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_int), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_key_int_

        subroutine LIBMUSCLE_Data_set_item_key_int64_( &
                self, key, key_size, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_key_int64_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_int64_t), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_key_int64_

        subroutine LIBMUSCLE_Data_set_item_key_float_( &
                self, key, key_size, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_key_float_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            real (selected_real_kind(6)), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_key_float_

        subroutine LIBMUSCLE_Data_set_item_key_double_( &
                self, key, key_size, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_key_double_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            real (selected_real_kind(15)), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_key_double_

        subroutine LIBMUSCLE_Data_set_item_key_data_( &
                self, key, key_size, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_key_data_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_intptr_t), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_key_data_

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

    interface LIBMUSCLE_Data_set
        module procedure &
            LIBMUSCLE_Data_set_bool, &
            LIBMUSCLE_Data_set_string, &
            LIBMUSCLE_Data_set_char, &
            LIBMUSCLE_Data_set_int16, &
            LIBMUSCLE_Data_set_int, &
            LIBMUSCLE_Data_set_int64, &
            LIBMUSCLE_Data_set_float, &
            LIBMUSCLE_Data_set_double, &
            LIBMUSCLE_Data_set_data
    end interface

    interface LIBMUSCLE_Data_set_item
        module procedure &
            LIBMUSCLE_Data_set_item_key_bool, &
            LIBMUSCLE_Data_set_item_key_string, &
            LIBMUSCLE_Data_set_item_key_char, &
            LIBMUSCLE_Data_set_item_key_int16, &
            LIBMUSCLE_Data_set_item_key_int, &
            LIBMUSCLE_Data_set_item_key_int64, &
            LIBMUSCLE_Data_set_item_key_float, &
            LIBMUSCLE_Data_set_item_key_double, &
            LIBMUSCLE_Data_set_item_key_data
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

    function LIBMUSCLE_Data_create_dict()
        implicit none
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_dict

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_dict_( &
    )

        LIBMUSCLE_Data_create_dict%ptr = ret_val
    end function LIBMUSCLE_Data_create_dict

    function LIBMUSCLE_Data_create_list()
        implicit none
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_list

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_list_( &
    )

        LIBMUSCLE_Data_create_list%ptr = ret_val
    end function LIBMUSCLE_Data_create_list

    function LIBMUSCLE_Data_create_byte_array(size)
        implicit none
        integer (selected_int_kind(18)), intent(in) :: size
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_byte_array

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_byte_array_( &
            size)

        LIBMUSCLE_Data_create_byte_array%ptr = ret_val
    end function LIBMUSCLE_Data_create_byte_array

    function LIBMUSCLE_Data_create_nils(size)
        implicit none
        integer (selected_int_kind(18)), intent(in) :: size
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_nils

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_nils_( &
            size)

        LIBMUSCLE_Data_create_nils%ptr = ret_val
    end function LIBMUSCLE_Data_create_nils

    subroutine LIBMUSCLE_Data_set_bool(self, value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical, intent(in) :: value

        call LIBMUSCLE_Data_set_bool_( &
            self%ptr, &
            merge(1, 0, value))
    end subroutine LIBMUSCLE_Data_set_bool

    subroutine LIBMUSCLE_Data_set_string(self, value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        character (len=*), intent(in) :: value

        call LIBMUSCLE_Data_set_string_( &
            self%ptr, &
            value, int(len(value), c_size_t))
    end subroutine LIBMUSCLE_Data_set_string

    subroutine LIBMUSCLE_Data_set_char(self, value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (selected_int_kind(2)), intent(in) :: value

        call LIBMUSCLE_Data_set_char_( &
            self%ptr, &
            value)
    end subroutine LIBMUSCLE_Data_set_char

    subroutine LIBMUSCLE_Data_set_int16(self, value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (selected_int_kind(4)), intent(in) :: value

        call LIBMUSCLE_Data_set_int16_( &
            self%ptr, &
            value)
    end subroutine LIBMUSCLE_Data_set_int16

    subroutine LIBMUSCLE_Data_set_int(self, value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, intent(in) :: value

        call LIBMUSCLE_Data_set_int_( &
            self%ptr, &
            value)
    end subroutine LIBMUSCLE_Data_set_int

    subroutine LIBMUSCLE_Data_set_int64(self, value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (selected_int_kind(18)), intent(in) :: value

        call LIBMUSCLE_Data_set_int64_( &
            self%ptr, &
            value)
    end subroutine LIBMUSCLE_Data_set_int64

    subroutine LIBMUSCLE_Data_set_float(self, value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        real (selected_real_kind(6)), intent(in) :: value

        call LIBMUSCLE_Data_set_float_( &
            self%ptr, &
            value)
    end subroutine LIBMUSCLE_Data_set_float

    subroutine LIBMUSCLE_Data_set_double(self, value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        real (selected_real_kind(15)), intent(in) :: value

        call LIBMUSCLE_Data_set_double_( &
            self%ptr, &
            value)
    end subroutine LIBMUSCLE_Data_set_double

    subroutine LIBMUSCLE_Data_set_data(self, value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        type(LIBMUSCLE_Data), intent(in) :: value

        call LIBMUSCLE_Data_set_data_( &
            self%ptr, &
            value%ptr)
    end subroutine LIBMUSCLE_Data_set_data

    subroutine LIBMUSCLE_Data_set_nil(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self

        call LIBMUSCLE_Data_set_nil_( &
            self%ptr)
    end subroutine LIBMUSCLE_Data_set_nil

    function LIBMUSCLE_Data_is_a_bool(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_bool

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_bool_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_bool = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_bool

    function LIBMUSCLE_Data_is_a_string(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_string

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_string_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_string = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_string

    function LIBMUSCLE_Data_is_a_char(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_char

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_char_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_char = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_char

    function LIBMUSCLE_Data_is_a_int(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_int

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_int_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_int = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_int

    function LIBMUSCLE_Data_is_a_int16(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_int16

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_int16_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_int16 = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_int16

    function LIBMUSCLE_Data_is_a_int64(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_int64

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_int64_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_int64 = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_int64

    function LIBMUSCLE_Data_is_a_float(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_float

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_float_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_float = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_float

    function LIBMUSCLE_Data_is_a_double(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_double

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_double_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_double = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_double

    function LIBMUSCLE_Data_is_a_dict(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_dict

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_dict_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_dict = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_dict

    function LIBMUSCLE_Data_is_a_list(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_list

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_list_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_list = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_list

    function LIBMUSCLE_Data_is_a_byte_array(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_byte_array

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_byte_array_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_byte_array = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_byte_array

    function LIBMUSCLE_Data_is_nil(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_nil

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_nil_( &
            self%ptr)

        LIBMUSCLE_Data_is_nil = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_nil

    function LIBMUSCLE_Data_size(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (selected_int_kind(18)) :: LIBMUSCLE_Data_size

        integer (c_int64_t) :: ret_val

        ret_val = LIBMUSCLE_Data_size_( &
            self%ptr)
        LIBMUSCLE_Data_size = ret_val
    end function LIBMUSCLE_Data_size

    function LIBMUSCLE_Data_as_bool(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        logical :: LIBMUSCLE_Data_as_bool

        integer (c_int) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_as_bool_( &
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
        else
            if (present(err_code)) then
                err_code = 0
            end if
        end if

        LIBMUSCLE_Data_as_bool = ret_val .ne. 0
    end function LIBMUSCLE_Data_as_bool

    function LIBMUSCLE_Data_as_string(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        character(:), allocatable :: LIBMUSCLE_Data_as_string

        type (c_ptr) :: ret_val
        integer (c_size_t) :: ret_val_size
        character (c_char), dimension(:), pointer :: f_ret_ptr
        integer :: i
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_as_string_( &
            self%ptr, &
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
        allocate (character(ret_val_size) :: LIBMUSCLE_Data_as_string)
        do i = 1, ret_val_size
            LIBMUSCLE_Data_as_string(i:i) = f_ret_ptr(i)
        end do
    end function LIBMUSCLE_Data_as_string

    function LIBMUSCLE_Data_as_char(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        integer (selected_int_kind(2)) :: LIBMUSCLE_Data_as_char

        integer (c_int8_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_as_char_( &
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
        else
            if (present(err_code)) then
                err_code = 0
            end if
        end if

        LIBMUSCLE_Data_as_char = ret_val
    end function LIBMUSCLE_Data_as_char

    function LIBMUSCLE_Data_as_int16(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        integer (selected_int_kind(4)) :: LIBMUSCLE_Data_as_int16

        integer (c_short) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_as_int16_( &
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
        else
            if (present(err_code)) then
                err_code = 0
            end if
        end if

        LIBMUSCLE_Data_as_int16 = ret_val
    end function LIBMUSCLE_Data_as_int16

    function LIBMUSCLE_Data_as_int(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        integer :: LIBMUSCLE_Data_as_int

        integer (c_int) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_as_int_( &
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
        else
            if (present(err_code)) then
                err_code = 0
            end if
        end if

        LIBMUSCLE_Data_as_int = ret_val
    end function LIBMUSCLE_Data_as_int

    function LIBMUSCLE_Data_as_int64(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        integer (selected_int_kind(18)) :: LIBMUSCLE_Data_as_int64

        integer (c_int64_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_as_int64_( &
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
        else
            if (present(err_code)) then
                err_code = 0
            end if
        end if

        LIBMUSCLE_Data_as_int64 = ret_val
    end function LIBMUSCLE_Data_as_int64

    function LIBMUSCLE_Data_as_float(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        real (selected_real_kind(6)) :: LIBMUSCLE_Data_as_float

        real (selected_real_kind(6)) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_as_float_( &
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
        else
            if (present(err_code)) then
                err_code = 0
            end if
        end if

        LIBMUSCLE_Data_as_float = ret_val
    end function LIBMUSCLE_Data_as_float

    function LIBMUSCLE_Data_as_double(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        real (selected_real_kind(15)) :: LIBMUSCLE_Data_as_double

        real (selected_real_kind(15)) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_as_double_( &
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
        else
            if (present(err_code)) then
                err_code = 0
            end if
        end if

        LIBMUSCLE_Data_as_double = ret_val
    end function LIBMUSCLE_Data_as_double

    subroutine LIBMUSCLE_Data_as_byte_array(self, data, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        character(len=1), dimension(:), intent(out) :: data
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        type (c_ptr) :: ret_val
        integer (c_size_t) :: ret_val_size
        character(len=1), pointer, dimension(:) :: f_ret_ptr
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_as_byte_array_( &
            self%ptr, &
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
        data = f_ret_ptr
    end subroutine LIBMUSCLE_Data_as_byte_array

    function LIBMUSCLE_Data_get_item(self, key, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        character (len=*), intent(in) :: key
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_get_item

        integer (c_intptr_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_get_item_( &
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

        LIBMUSCLE_Data_get_item%ptr = ret_val
    end function LIBMUSCLE_Data_get_item

    subroutine LIBMUSCLE_Data_set_item_key_bool(self, key, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        character (len=*), intent(in) :: key
        logical, intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_key_bool_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            merge(1, 0, value), &
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

    end subroutine LIBMUSCLE_Data_set_item_key_bool

    subroutine LIBMUSCLE_Data_set_item_key_string(self, key, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        character (len=*), intent(in) :: key
        character (len=*), intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_key_string_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            value, int(len(value), c_size_t), &
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

    end subroutine LIBMUSCLE_Data_set_item_key_string

    subroutine LIBMUSCLE_Data_set_item_key_char(self, key, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        character (len=*), intent(in) :: key
        integer (selected_int_kind(2)), intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_key_char_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            value, &
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

    end subroutine LIBMUSCLE_Data_set_item_key_char

    subroutine LIBMUSCLE_Data_set_item_key_int16(self, key, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        character (len=*), intent(in) :: key
        integer (selected_int_kind(4)), intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_key_int16_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            value, &
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

    end subroutine LIBMUSCLE_Data_set_item_key_int16

    subroutine LIBMUSCLE_Data_set_item_key_int(self, key, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        character (len=*), intent(in) :: key
        integer, intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_key_int_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            value, &
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

    end subroutine LIBMUSCLE_Data_set_item_key_int

    subroutine LIBMUSCLE_Data_set_item_key_int64(self, key, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        character (len=*), intent(in) :: key
        integer (selected_int_kind(18)), intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_key_int64_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            value, &
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

    end subroutine LIBMUSCLE_Data_set_item_key_int64

    subroutine LIBMUSCLE_Data_set_item_key_float(self, key, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        character (len=*), intent(in) :: key
        real (selected_real_kind(6)), intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_key_float_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            value, &
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

    end subroutine LIBMUSCLE_Data_set_item_key_float

    subroutine LIBMUSCLE_Data_set_item_key_double(self, key, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        character (len=*), intent(in) :: key
        real (selected_real_kind(15)), intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_key_double_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            value, &
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

    end subroutine LIBMUSCLE_Data_set_item_key_double

    subroutine LIBMUSCLE_Data_set_item_key_data(self, key, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        character (len=*), intent(in) :: key
        type(LIBMUSCLE_Data), intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_key_data_( &
            self%ptr, &
            key, int(len(key), c_size_t), &
            value%ptr, &
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

    end subroutine LIBMUSCLE_Data_set_item_key_data


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

