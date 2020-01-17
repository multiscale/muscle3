! This is generated code. If it's broken, then you should
! fix the generation script, not this file.


module libmuscle
    use iso_c_binding
    use ymmsl

    private

    integer, parameter, public :: LIBMUSCLE_success = 0
    integer, parameter, public :: LIBMUSCLE_runtime_error = 1
    integer, parameter, public :: LIBMUSCLE_domain_error = 2
    integer, parameter, public :: LIBMUSCLE_out_of_range = 3
    integer, parameter, public :: LIBMUSCLE_logic_error = 4
    integer, parameter, public :: LIBMUSCLE_bad_cast = 5

    integer, parameter, public :: LIBMUSCLE_int1 = selected_int_kind(2)
    integer, parameter, public :: LIBMUSCLE_int2 = selected_int_kind(4)
    integer, parameter, public :: LIBMUSCLE_int4 = selected_int_kind(9)
    integer, parameter, public :: LIBMUSCLE_int8 = selected_int_kind(18)
    integer, parameter, public :: LIBMUSCLE_size = c_size_t
    integer, parameter, public :: LIBMUSCLE_real4 = selected_real_kind(6)
    integer, parameter, public :: LIBMUSCLE_real8 = selected_real_kind(15)

    type LIBMUSCLE_Data
        integer (c_intptr_t) :: ptr
    end type LIBMUSCLE_Data
    public :: LIBMUSCLE_Data

    public :: LIBMUSCLE_Data_create_nil
    public :: LIBMUSCLE_Data_create_logical
    public :: LIBMUSCLE_Data_create_character
    public :: LIBMUSCLE_Data_create_int1
    public :: LIBMUSCLE_Data_create_int2
    public :: LIBMUSCLE_Data_create_int4
    public :: LIBMUSCLE_Data_create_int8
    public :: LIBMUSCLE_Data_create_real4
    public :: LIBMUSCLE_Data_create_real8
    public :: LIBMUSCLE_Data_create_settings
    public :: LIBMUSCLE_Data_create_copy
    public :: LIBMUSCLE_Data_create
    public :: LIBMUSCLE_Data_free
    public :: LIBMUSCLE_Data_create_dict
    public :: LIBMUSCLE_Data_create_list
    public :: LIBMUSCLE_Data_create_byte_array_empty
    public :: LIBMUSCLE_Data_create_byte_array_from_buf
    public :: LIBMUSCLE_Data_create_byte_array
    public :: LIBMUSCLE_Data_create_nils
    public :: LIBMUSCLE_Data_set_logical
    public :: LIBMUSCLE_Data_set_character
    public :: LIBMUSCLE_Data_set_int1
    public :: LIBMUSCLE_Data_set_int2
    public :: LIBMUSCLE_Data_set_int4
    public :: LIBMUSCLE_Data_set_int8
    public :: LIBMUSCLE_Data_set_real4
    public :: LIBMUSCLE_Data_set_real8
    public :: LIBMUSCLE_Data_set_data
    public :: LIBMUSCLE_Data_set
    public :: LIBMUSCLE_Data_set_nil
    public :: LIBMUSCLE_Data_is_a_logical
    public :: LIBMUSCLE_Data_is_a_character
    public :: LIBMUSCLE_Data_is_a_int
    public :: LIBMUSCLE_Data_is_a_int1
    public :: LIBMUSCLE_Data_is_a_int2
    public :: LIBMUSCLE_Data_is_a_int4
    public :: LIBMUSCLE_Data_is_a_int8
    public :: LIBMUSCLE_Data_is_a_real4
    public :: LIBMUSCLE_Data_is_a_real8
    public :: LIBMUSCLE_Data_is_a_dict
    public :: LIBMUSCLE_Data_is_a_list
    public :: LIBMUSCLE_Data_is_a_byte_array
    public :: LIBMUSCLE_Data_is_nil
    public :: LIBMUSCLE_Data_is_a_settings
    public :: LIBMUSCLE_Data_size
    public :: LIBMUSCLE_Data_as_logical
    public :: LIBMUSCLE_Data_as_character
    public :: LIBMUSCLE_Data_as_int
    public :: LIBMUSCLE_Data_as_int1
    public :: LIBMUSCLE_Data_as_int2
    public :: LIBMUSCLE_Data_as_int4
    public :: LIBMUSCLE_Data_as_int8
    public :: LIBMUSCLE_Data_as_real4
    public :: LIBMUSCLE_Data_as_real8
    public :: LIBMUSCLE_Data_as_settings
    public :: LIBMUSCLE_Data_as_byte_array
    public :: LIBMUSCLE_Data_get_item_by_key
    public :: LIBMUSCLE_Data_get_item_by_index
    public :: LIBMUSCLE_Data_get_item
    public :: LIBMUSCLE_Data_set_item_key_logical
    public :: LIBMUSCLE_Data_set_item_key_character
    public :: LIBMUSCLE_Data_set_item_key_int1
    public :: LIBMUSCLE_Data_set_item_key_int2
    public :: LIBMUSCLE_Data_set_item_key_int4
    public :: LIBMUSCLE_Data_set_item_key_int8
    public :: LIBMUSCLE_Data_set_item_key_real4
    public :: LIBMUSCLE_Data_set_item_key_real8
    public :: LIBMUSCLE_Data_set_item_key_data
    public :: LIBMUSCLE_Data_set_item_index_logical
    public :: LIBMUSCLE_Data_set_item_index_character
    public :: LIBMUSCLE_Data_set_item_index_int1
    public :: LIBMUSCLE_Data_set_item_index_int2
    public :: LIBMUSCLE_Data_set_item_index_int4
    public :: LIBMUSCLE_Data_set_item_index_int8
    public :: LIBMUSCLE_Data_set_item_index_real4
    public :: LIBMUSCLE_Data_set_item_index_real8
    public :: LIBMUSCLE_Data_set_item_index_data
    public :: LIBMUSCLE_Data_set_item
    public :: LIBMUSCLE_Data_key
    public :: LIBMUSCLE_Data_value

    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_success = 0
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_runtime_error = 1
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_domain_error = 2
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_out_of_range = 3
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_logic_error = 4
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_bad_cast = 5

    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_int1 = selected_int_kind(2)
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_int2 = selected_int_kind(4)
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_int4 = selected_int_kind(9)
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_int8 = selected_int_kind(18)
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_size = c_size_t
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_real4 = selected_real_kind(6)
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_real8 = selected_real_kind(15)

    type LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs
        integer (c_intptr_t) :: ptr
    end type LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs



    interface

        integer (c_intptr_t) function LIBMUSCLE_Data_create_nil_( &
                ) &
                bind(C, name="LIBMUSCLE_Data_create_nil_")

            use iso_c_binding
        end function LIBMUSCLE_Data_create_nil_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_logical_( &
                value) &
                bind(C, name="LIBMUSCLE_Data_create_logical_")

            use iso_c_binding
            integer (c_int), value, intent(in) :: value
        end function LIBMUSCLE_Data_create_logical_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_character_( &
                value, value_size) &
                bind(C, name="LIBMUSCLE_Data_create_character_")

            use iso_c_binding
            character, intent(in) :: value
            integer (c_size_t), value, intent(in) :: value_size
        end function LIBMUSCLE_Data_create_character_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_int1_( &
                value) &
                bind(C, name="LIBMUSCLE_Data_create_int1_")

            use iso_c_binding
            integer (c_int8_t), value, intent(in) :: value
        end function LIBMUSCLE_Data_create_int1_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_int2_( &
                value) &
                bind(C, name="LIBMUSCLE_Data_create_int2_")

            use iso_c_binding
            integer (c_short), value, intent(in) :: value
        end function LIBMUSCLE_Data_create_int2_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_int4_( &
                value) &
                bind(C, name="LIBMUSCLE_Data_create_int4_")

            use iso_c_binding
            integer (c_int32_t), value, intent(in) :: value
        end function LIBMUSCLE_Data_create_int4_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_int8_( &
                value) &
                bind(C, name="LIBMUSCLE_Data_create_int8_")

            use iso_c_binding
            integer (c_int64_t), value, intent(in) :: value
        end function LIBMUSCLE_Data_create_int8_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_real4_( &
                value) &
                bind(C, name="LIBMUSCLE_Data_create_real4_")

            use iso_c_binding
            real (c_float), value, intent(in) :: value
        end function LIBMUSCLE_Data_create_real4_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_real8_( &
                value) &
                bind(C, name="LIBMUSCLE_Data_create_real8_")

            use iso_c_binding
            real (c_double), value, intent(in) :: value
        end function LIBMUSCLE_Data_create_real8_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_settings_( &
                value) &
                bind(C, name="LIBMUSCLE_Data_create_settings_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: value
        end function LIBMUSCLE_Data_create_settings_

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

        integer (c_intptr_t) function LIBMUSCLE_Data_create_byte_array_empty_( &
                size) &
                bind(C, name="LIBMUSCLE_Data_create_byte_array_empty_")

            use iso_c_binding
            integer (c_size_t), value, intent(in) :: size
        end function LIBMUSCLE_Data_create_byte_array_empty_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_byte_array_from_buf_( &
                buf, buf_size) &
                bind(C, name="LIBMUSCLE_Data_create_byte_array_from_buf_")

            use iso_c_binding
            character(len=1), dimension(*), intent(in) :: buf
            integer (c_size_t), value, intent(in) :: buf_size
        end function LIBMUSCLE_Data_create_byte_array_from_buf_

        integer (c_intptr_t) function LIBMUSCLE_Data_create_nils_( &
                size) &
                bind(C, name="LIBMUSCLE_Data_create_nils_")

            use iso_c_binding
            integer (c_size_t), value, intent(in) :: size
        end function LIBMUSCLE_Data_create_nils_

        subroutine LIBMUSCLE_Data_set_logical_( &
                self, value) &
                bind(C, name="LIBMUSCLE_Data_set_logical_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), value, intent(in) :: value
        end subroutine LIBMUSCLE_Data_set_logical_

        subroutine LIBMUSCLE_Data_set_character_( &
                self, value, value_size) &
                bind(C, name="LIBMUSCLE_Data_set_character_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: value
            integer (c_size_t), value, intent(in) :: value_size
        end subroutine LIBMUSCLE_Data_set_character_

        subroutine LIBMUSCLE_Data_set_int1_( &
                self, value) &
                bind(C, name="LIBMUSCLE_Data_set_int1_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int8_t), value, intent(in) :: value
        end subroutine LIBMUSCLE_Data_set_int1_

        subroutine LIBMUSCLE_Data_set_int2_( &
                self, value) &
                bind(C, name="LIBMUSCLE_Data_set_int2_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_short), value, intent(in) :: value
        end subroutine LIBMUSCLE_Data_set_int2_

        subroutine LIBMUSCLE_Data_set_int4_( &
                self, value) &
                bind(C, name="LIBMUSCLE_Data_set_int4_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int32_t), value, intent(in) :: value
        end subroutine LIBMUSCLE_Data_set_int4_

        subroutine LIBMUSCLE_Data_set_int8_( &
                self, value) &
                bind(C, name="LIBMUSCLE_Data_set_int8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int64_t), value, intent(in) :: value
        end subroutine LIBMUSCLE_Data_set_int8_

        subroutine LIBMUSCLE_Data_set_real4_( &
                self, value) &
                bind(C, name="LIBMUSCLE_Data_set_real4_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            real (c_float), value, intent(in) :: value
        end subroutine LIBMUSCLE_Data_set_real4_

        subroutine LIBMUSCLE_Data_set_real8_( &
                self, value) &
                bind(C, name="LIBMUSCLE_Data_set_real8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            real (c_double), value, intent(in) :: value
        end subroutine LIBMUSCLE_Data_set_real8_

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

        integer (c_int) function LIBMUSCLE_Data_is_a_logical_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_logical_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_logical_

        integer (c_int) function LIBMUSCLE_Data_is_a_character_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_character_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_character_

        integer (c_int) function LIBMUSCLE_Data_is_a_int_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_int_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_int_

        integer (c_int) function LIBMUSCLE_Data_is_a_int1_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_int1_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_int1_

        integer (c_int) function LIBMUSCLE_Data_is_a_int2_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_int2_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_int2_

        integer (c_int) function LIBMUSCLE_Data_is_a_int4_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_int4_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_int4_

        integer (c_int) function LIBMUSCLE_Data_is_a_int8_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_int8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_int8_

        integer (c_int) function LIBMUSCLE_Data_is_a_real4_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_real4_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_real4_

        integer (c_int) function LIBMUSCLE_Data_is_a_real8_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_real8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_real8_

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

        integer (c_int) function LIBMUSCLE_Data_is_a_settings_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_is_a_settings_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_is_a_settings_

        integer (c_size_t) function LIBMUSCLE_Data_size_( &
                self) &
                bind(C, name="LIBMUSCLE_Data_size_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Data_size_

        integer (c_int) function LIBMUSCLE_Data_as_logical_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_logical_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_as_logical_

        subroutine LIBMUSCLE_Data_as_character_( &
                self, ret_val, ret_val_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_character_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            type (c_ptr), intent(out) :: ret_val
            integer (c_size_t), intent(out) :: ret_val_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_as_character_

        integer (c_int) function LIBMUSCLE_Data_as_int_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_int_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_as_int_

        integer (c_int8_t) function LIBMUSCLE_Data_as_int1_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_int1_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_as_int1_

        integer (c_short) function LIBMUSCLE_Data_as_int2_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_int2_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_as_int2_

        integer (c_int32_t) function LIBMUSCLE_Data_as_int4_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_int4_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_as_int4_

        integer (c_int64_t) function LIBMUSCLE_Data_as_int8_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_int8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_as_int8_

        real (c_float) function LIBMUSCLE_Data_as_real4_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_real4_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_as_real4_

        real (c_double) function LIBMUSCLE_Data_as_real8_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_real8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_as_real8_

        integer (c_intptr_t) function LIBMUSCLE_Data_as_settings_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_as_settings_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_as_settings_

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

        integer (c_intptr_t) function LIBMUSCLE_Data_get_item_by_key_( &
                self, key, key_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_get_item_by_key_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_get_item_by_key_

        integer (c_intptr_t) function LIBMUSCLE_Data_get_item_by_index_( &
                self, i, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_get_item_by_index_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_size_t), value, intent(in) :: i
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_get_item_by_index_

        subroutine LIBMUSCLE_Data_set_item_key_logical_( &
                self, key, key_size, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_key_logical_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_int), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_key_logical_

        subroutine LIBMUSCLE_Data_set_item_key_character_( &
                self, key, key_size, value, value_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_key_character_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            character, intent(in) :: value
            integer (c_size_t), value, intent(in) :: value_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_key_character_

        subroutine LIBMUSCLE_Data_set_item_key_int1_( &
                self, key, key_size, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_key_int1_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_int8_t), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_key_int1_

        subroutine LIBMUSCLE_Data_set_item_key_int2_( &
                self, key, key_size, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_key_int2_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_short), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_key_int2_

        subroutine LIBMUSCLE_Data_set_item_key_int4_( &
                self, key, key_size, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_key_int4_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_int), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_key_int4_

        subroutine LIBMUSCLE_Data_set_item_key_int8_( &
                self, key, key_size, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_key_int8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_int64_t), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_key_int8_

        subroutine LIBMUSCLE_Data_set_item_key_real4_( &
                self, key, key_size, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_key_real4_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            real (c_float), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_key_real4_

        subroutine LIBMUSCLE_Data_set_item_key_real8_( &
                self, key, key_size, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_key_real8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            real (c_double), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_key_real8_

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

        subroutine LIBMUSCLE_Data_set_item_index_logical_( &
                self, i, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_index_logical_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_size_t), value, intent(in) :: i
            integer (c_int), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_index_logical_

        subroutine LIBMUSCLE_Data_set_item_index_character_( &
                self, i, value, value_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_index_character_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_size_t), value, intent(in) :: i
            character, intent(in) :: value
            integer (c_size_t), value, intent(in) :: value_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_index_character_

        subroutine LIBMUSCLE_Data_set_item_index_int1_( &
                self, i, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_index_int1_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_size_t), value, intent(in) :: i
            integer (c_int8_t), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_index_int1_

        subroutine LIBMUSCLE_Data_set_item_index_int2_( &
                self, i, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_index_int2_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_size_t), value, intent(in) :: i
            integer (c_short), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_index_int2_

        subroutine LIBMUSCLE_Data_set_item_index_int4_( &
                self, i, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_index_int4_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_size_t), value, intent(in) :: i
            integer (c_int), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_index_int4_

        subroutine LIBMUSCLE_Data_set_item_index_int8_( &
                self, i, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_index_int8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_size_t), value, intent(in) :: i
            integer (c_int64_t), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_index_int8_

        subroutine LIBMUSCLE_Data_set_item_index_real4_( &
                self, i, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_index_real4_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_size_t), value, intent(in) :: i
            real (c_float), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_index_real4_

        subroutine LIBMUSCLE_Data_set_item_index_real8_( &
                self, i, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_index_real8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_size_t), value, intent(in) :: i
            real (c_double), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_index_real8_

        subroutine LIBMUSCLE_Data_set_item_index_data_( &
                self, i, value, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_set_item_index_data_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_size_t), value, intent(in) :: i
            integer (c_intptr_t), value, intent(in) :: value
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_set_item_index_data_

        subroutine LIBMUSCLE_Data_key_( &
                self, i, ret_val, ret_val_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_key_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_size_t), value, intent(in) :: i
            type (c_ptr), intent(out) :: ret_val
            integer (c_size_t), intent(out) :: ret_val_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Data_key_

        integer (c_intptr_t) function LIBMUSCLE_Data_value_( &
                self, i, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Data_value_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_size_t), value, intent(in) :: i
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Data_value_

    end interface

    interface LIBMUSCLE_Data_create
        module procedure &
            LIBMUSCLE_Data_create_nil, &
            LIBMUSCLE_Data_create_logical, &
            LIBMUSCLE_Data_create_character, &
            LIBMUSCLE_Data_create_int1, &
            LIBMUSCLE_Data_create_int2, &
            LIBMUSCLE_Data_create_int4, &
            LIBMUSCLE_Data_create_int8, &
            LIBMUSCLE_Data_create_real4, &
            LIBMUSCLE_Data_create_real8, &
            LIBMUSCLE_Data_create_settings, &
            LIBMUSCLE_Data_create_copy
    end interface

    interface LIBMUSCLE_Data_create_byte_array
        module procedure &
            LIBMUSCLE_Data_create_byte_array_empty, &
            LIBMUSCLE_Data_create_byte_array_from_buf
    end interface

    interface LIBMUSCLE_Data_set
        module procedure &
            LIBMUSCLE_Data_set_logical, &
            LIBMUSCLE_Data_set_character, &
            LIBMUSCLE_Data_set_int1, &
            LIBMUSCLE_Data_set_int2, &
            LIBMUSCLE_Data_set_int4, &
            LIBMUSCLE_Data_set_int8, &
            LIBMUSCLE_Data_set_real4, &
            LIBMUSCLE_Data_set_real8, &
            LIBMUSCLE_Data_set_data
    end interface

    interface LIBMUSCLE_Data_get_item
        module procedure &
            LIBMUSCLE_Data_get_item_by_key, &
            LIBMUSCLE_Data_get_item_by_index
    end interface

    interface LIBMUSCLE_Data_set_item
        module procedure &
            LIBMUSCLE_Data_set_item_key_logical, &
            LIBMUSCLE_Data_set_item_key_character, &
            LIBMUSCLE_Data_set_item_key_int1, &
            LIBMUSCLE_Data_set_item_key_int2, &
            LIBMUSCLE_Data_set_item_key_int4, &
            LIBMUSCLE_Data_set_item_key_int8, &
            LIBMUSCLE_Data_set_item_key_real4, &
            LIBMUSCLE_Data_set_item_key_real8, &
            LIBMUSCLE_Data_set_item_key_data, &
            LIBMUSCLE_Data_set_item_index_logical, &
            LIBMUSCLE_Data_set_item_index_character, &
            LIBMUSCLE_Data_set_item_index_int1, &
            LIBMUSCLE_Data_set_item_index_int2, &
            LIBMUSCLE_Data_set_item_index_int4, &
            LIBMUSCLE_Data_set_item_index_int8, &
            LIBMUSCLE_Data_set_item_index_real4, &
            LIBMUSCLE_Data_set_item_index_real8, &
            LIBMUSCLE_Data_set_item_index_data
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

    function LIBMUSCLE_Data_create_logical(value)
        implicit none
        logical, intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_logical

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_logical_( &
            merge(1, 0, value))

        LIBMUSCLE_Data_create_logical%ptr = ret_val
    end function LIBMUSCLE_Data_create_logical

    function LIBMUSCLE_Data_create_character(value)
        implicit none
        character (len=*), intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_character

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_character_( &
            value, int(len(value), c_size_t))

        LIBMUSCLE_Data_create_character%ptr = ret_val
    end function LIBMUSCLE_Data_create_character

    function LIBMUSCLE_Data_create_int1(value)
        implicit none
        integer (LIBMUSCLE_int1), intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_int1

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_int1_( &
            value)

        LIBMUSCLE_Data_create_int1%ptr = ret_val
    end function LIBMUSCLE_Data_create_int1

    function LIBMUSCLE_Data_create_int2(value)
        implicit none
        integer (selected_int_kind(4)), intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_int2

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_int2_( &
            value)

        LIBMUSCLE_Data_create_int2%ptr = ret_val
    end function LIBMUSCLE_Data_create_int2

    function LIBMUSCLE_Data_create_int4(value)
        implicit none
        integer (LIBMUSCLE_int4), intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_int4

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_int4_( &
            value)

        LIBMUSCLE_Data_create_int4%ptr = ret_val
    end function LIBMUSCLE_Data_create_int4

    function LIBMUSCLE_Data_create_int8(value)
        implicit none
        integer (selected_int_kind(18)), intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_int8

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_int8_( &
            value)

        LIBMUSCLE_Data_create_int8%ptr = ret_val
    end function LIBMUSCLE_Data_create_int8

    function LIBMUSCLE_Data_create_real4(value)
        implicit none
        real (LIBMUSCLE_real4), intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_real4

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_real4_( &
            value)

        LIBMUSCLE_Data_create_real4%ptr = ret_val
    end function LIBMUSCLE_Data_create_real4

    function LIBMUSCLE_Data_create_real8(value)
        implicit none
        real (LIBMUSCLE_real8), intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_real8

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_real8_( &
            value)

        LIBMUSCLE_Data_create_real8%ptr = ret_val
    end function LIBMUSCLE_Data_create_real8

    function LIBMUSCLE_Data_create_settings(value)
        implicit none
        type(YMMSL_Settings), intent(in) :: value
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_settings

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_settings_( &
            value%ptr)

        LIBMUSCLE_Data_create_settings%ptr = ret_val
    end function LIBMUSCLE_Data_create_settings

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

    function LIBMUSCLE_Data_create_byte_array_empty(size)
        implicit none
        integer (LIBMUSCLE_size), intent(in) :: size
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_byte_array_empty

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_byte_array_empty_( &
            size)

        LIBMUSCLE_Data_create_byte_array_empty%ptr = ret_val
    end function LIBMUSCLE_Data_create_byte_array_empty

    function LIBMUSCLE_Data_create_byte_array_from_buf(buf)
        implicit none
        character(len=1), dimension(:), intent(in) :: buf
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_byte_array_from_buf

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_byte_array_from_buf_( &
            buf, int(size(buf), c_size_t))

        LIBMUSCLE_Data_create_byte_array_from_buf%ptr = ret_val
    end function LIBMUSCLE_Data_create_byte_array_from_buf

    function LIBMUSCLE_Data_create_nils(size)
        implicit none
        integer (LIBMUSCLE_size), intent(in) :: size
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_nils

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_nils_( &
            size)

        LIBMUSCLE_Data_create_nils%ptr = ret_val
    end function LIBMUSCLE_Data_create_nils

    subroutine LIBMUSCLE_Data_set_logical(self, value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical, intent(in) :: value

        call LIBMUSCLE_Data_set_logical_( &
            self%ptr, &
            merge(1, 0, value))
    end subroutine LIBMUSCLE_Data_set_logical

    subroutine LIBMUSCLE_Data_set_character(self, value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        character (len=*), intent(in) :: value

        call LIBMUSCLE_Data_set_character_( &
            self%ptr, &
            value, int(len(value), c_size_t))
    end subroutine LIBMUSCLE_Data_set_character

    subroutine LIBMUSCLE_Data_set_int1(self, value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (LIBMUSCLE_int1), intent(in) :: value

        call LIBMUSCLE_Data_set_int1_( &
            self%ptr, &
            value)
    end subroutine LIBMUSCLE_Data_set_int1

    subroutine LIBMUSCLE_Data_set_int2(self, value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (selected_int_kind(4)), intent(in) :: value

        call LIBMUSCLE_Data_set_int2_( &
            self%ptr, &
            value)
    end subroutine LIBMUSCLE_Data_set_int2

    subroutine LIBMUSCLE_Data_set_int4(self, value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (LIBMUSCLE_int4), intent(in) :: value

        call LIBMUSCLE_Data_set_int4_( &
            self%ptr, &
            value)
    end subroutine LIBMUSCLE_Data_set_int4

    subroutine LIBMUSCLE_Data_set_int8(self, value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (selected_int_kind(18)), intent(in) :: value

        call LIBMUSCLE_Data_set_int8_( &
            self%ptr, &
            value)
    end subroutine LIBMUSCLE_Data_set_int8

    subroutine LIBMUSCLE_Data_set_real4(self, value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        real (LIBMUSCLE_real4), intent(in) :: value

        call LIBMUSCLE_Data_set_real4_( &
            self%ptr, &
            value)
    end subroutine LIBMUSCLE_Data_set_real4

    subroutine LIBMUSCLE_Data_set_real8(self, value)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        real (LIBMUSCLE_real8), intent(in) :: value

        call LIBMUSCLE_Data_set_real8_( &
            self%ptr, &
            value)
    end subroutine LIBMUSCLE_Data_set_real8

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

    function LIBMUSCLE_Data_is_a_logical(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_logical

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_logical_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_logical = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_logical

    function LIBMUSCLE_Data_is_a_character(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_character

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_character_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_character = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_character

    function LIBMUSCLE_Data_is_a_int(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_int

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_int_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_int = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_int

    function LIBMUSCLE_Data_is_a_int1(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_int1

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_int1_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_int1 = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_int1

    function LIBMUSCLE_Data_is_a_int2(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_int2

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_int2_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_int2 = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_int2

    function LIBMUSCLE_Data_is_a_int4(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_int4

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_int4_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_int4 = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_int4

    function LIBMUSCLE_Data_is_a_int8(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_int8

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_int8_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_int8 = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_int8

    function LIBMUSCLE_Data_is_a_real4(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_real4

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_real4_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_real4 = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_real4

    function LIBMUSCLE_Data_is_a_real8(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_real8

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_real8_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_real8 = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_real8

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

    function LIBMUSCLE_Data_is_a_settings(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        logical :: LIBMUSCLE_Data_is_a_settings

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Data_is_a_settings_( &
            self%ptr)

        LIBMUSCLE_Data_is_a_settings = ret_val .ne. 0
    end function LIBMUSCLE_Data_is_a_settings

    function LIBMUSCLE_Data_size(self)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (LIBMUSCLE_size) :: LIBMUSCLE_Data_size

        integer (c_size_t) :: ret_val

        ret_val = LIBMUSCLE_Data_size_( &
            self%ptr)
        LIBMUSCLE_Data_size = ret_val
    end function LIBMUSCLE_Data_size

    function LIBMUSCLE_Data_as_logical(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        logical :: LIBMUSCLE_Data_as_logical

        integer (c_int) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_as_logical_( &
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

        LIBMUSCLE_Data_as_logical = ret_val .ne. 0
    end function LIBMUSCLE_Data_as_logical

    function LIBMUSCLE_Data_as_character(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        character(:), allocatable :: LIBMUSCLE_Data_as_character

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

        call LIBMUSCLE_Data_as_character_( &
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
        allocate (character(ret_val_size) :: LIBMUSCLE_Data_as_character)
        do i_loop = 1, ret_val_size
            LIBMUSCLE_Data_as_character(i_loop:i_loop) = f_ret_ptr(i_loop)
        end do
    end function LIBMUSCLE_Data_as_character

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

    function LIBMUSCLE_Data_as_int1(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        integer (LIBMUSCLE_int1) :: LIBMUSCLE_Data_as_int1

        integer (c_int8_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_as_int1_( &
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

        LIBMUSCLE_Data_as_int1 = ret_val
    end function LIBMUSCLE_Data_as_int1

    function LIBMUSCLE_Data_as_int2(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        integer (selected_int_kind(4)) :: LIBMUSCLE_Data_as_int2

        integer (c_short) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_as_int2_( &
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

        LIBMUSCLE_Data_as_int2 = ret_val
    end function LIBMUSCLE_Data_as_int2

    function LIBMUSCLE_Data_as_int4(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        integer (LIBMUSCLE_int4) :: LIBMUSCLE_Data_as_int4

        integer (c_int32_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_as_int4_( &
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

        LIBMUSCLE_Data_as_int4 = ret_val
    end function LIBMUSCLE_Data_as_int4

    function LIBMUSCLE_Data_as_int8(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        integer (selected_int_kind(18)) :: LIBMUSCLE_Data_as_int8

        integer (c_int64_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_as_int8_( &
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

        LIBMUSCLE_Data_as_int8 = ret_val
    end function LIBMUSCLE_Data_as_int8

    function LIBMUSCLE_Data_as_real4(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        real (LIBMUSCLE_real4) :: LIBMUSCLE_Data_as_real4

        real (c_float) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_as_real4_( &
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

        LIBMUSCLE_Data_as_real4 = ret_val
    end function LIBMUSCLE_Data_as_real4

    function LIBMUSCLE_Data_as_real8(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        real (LIBMUSCLE_real8) :: LIBMUSCLE_Data_as_real8

        real (c_double) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_as_real8_( &
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

        LIBMUSCLE_Data_as_real8 = ret_val
    end function LIBMUSCLE_Data_as_real8

    function LIBMUSCLE_Data_as_settings(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        type(YMMSL_Settings) :: LIBMUSCLE_Data_as_settings

        integer (c_intptr_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_as_settings_( &
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

        LIBMUSCLE_Data_as_settings%ptr = ret_val
    end function LIBMUSCLE_Data_as_settings

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

    function LIBMUSCLE_Data_get_item_by_key(self, key, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        character (len=*), intent(in) :: key
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_get_item_by_key

        integer (c_intptr_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_get_item_by_key_( &
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

        LIBMUSCLE_Data_get_item_by_key%ptr = ret_val
    end function LIBMUSCLE_Data_get_item_by_key

    function LIBMUSCLE_Data_get_item_by_index(self, i, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (LIBMUSCLE_size), intent(in) :: i
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_get_item_by_index

        integer (c_intptr_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_get_item_by_index_( &
            self%ptr, &
            i, &
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

        LIBMUSCLE_Data_get_item_by_index%ptr = ret_val
    end function LIBMUSCLE_Data_get_item_by_index

    subroutine LIBMUSCLE_Data_set_item_key_logical(self, key, value, err_code, err_msg)
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

        call LIBMUSCLE_Data_set_item_key_logical_( &
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

    end subroutine LIBMUSCLE_Data_set_item_key_logical

    subroutine LIBMUSCLE_Data_set_item_key_character(self, key, value, err_code, err_msg)
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

        call LIBMUSCLE_Data_set_item_key_character_( &
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

    end subroutine LIBMUSCLE_Data_set_item_key_character

    subroutine LIBMUSCLE_Data_set_item_key_int1(self, key, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        character (len=*), intent(in) :: key
        integer (LIBMUSCLE_int1), intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_key_int1_( &
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

    end subroutine LIBMUSCLE_Data_set_item_key_int1

    subroutine LIBMUSCLE_Data_set_item_key_int2(self, key, value, err_code, err_msg)
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

        call LIBMUSCLE_Data_set_item_key_int2_( &
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

    end subroutine LIBMUSCLE_Data_set_item_key_int2

    subroutine LIBMUSCLE_Data_set_item_key_int4(self, key, value, err_code, err_msg)
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

        call LIBMUSCLE_Data_set_item_key_int4_( &
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

    end subroutine LIBMUSCLE_Data_set_item_key_int4

    subroutine LIBMUSCLE_Data_set_item_key_int8(self, key, value, err_code, err_msg)
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

        call LIBMUSCLE_Data_set_item_key_int8_( &
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

    end subroutine LIBMUSCLE_Data_set_item_key_int8

    subroutine LIBMUSCLE_Data_set_item_key_real4(self, key, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        character (len=*), intent(in) :: key
        real (LIBMUSCLE_real4), intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_key_real4_( &
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

    end subroutine LIBMUSCLE_Data_set_item_key_real4

    subroutine LIBMUSCLE_Data_set_item_key_real8(self, key, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        character (len=*), intent(in) :: key
        real (LIBMUSCLE_real8), intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_key_real8_( &
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

    end subroutine LIBMUSCLE_Data_set_item_key_real8

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

    subroutine LIBMUSCLE_Data_set_item_index_logical(self, i, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (LIBMUSCLE_size), intent(in) :: i
        logical, intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_index_logical_( &
            self%ptr, &
            i, &
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

    end subroutine LIBMUSCLE_Data_set_item_index_logical

    subroutine LIBMUSCLE_Data_set_item_index_character(self, i, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (LIBMUSCLE_size), intent(in) :: i
        character (len=*), intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_index_character_( &
            self%ptr, &
            i, &
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

    end subroutine LIBMUSCLE_Data_set_item_index_character

    subroutine LIBMUSCLE_Data_set_item_index_int1(self, i, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (LIBMUSCLE_size), intent(in) :: i
        integer (LIBMUSCLE_int1), intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_index_int1_( &
            self%ptr, &
            i, &
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

    end subroutine LIBMUSCLE_Data_set_item_index_int1

    subroutine LIBMUSCLE_Data_set_item_index_int2(self, i, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (LIBMUSCLE_size), intent(in) :: i
        integer (selected_int_kind(4)), intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_index_int2_( &
            self%ptr, &
            i, &
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

    end subroutine LIBMUSCLE_Data_set_item_index_int2

    subroutine LIBMUSCLE_Data_set_item_index_int4(self, i, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (LIBMUSCLE_size), intent(in) :: i
        integer, intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_index_int4_( &
            self%ptr, &
            i, &
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

    end subroutine LIBMUSCLE_Data_set_item_index_int4

    subroutine LIBMUSCLE_Data_set_item_index_int8(self, i, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (LIBMUSCLE_size), intent(in) :: i
        integer (selected_int_kind(18)), intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_index_int8_( &
            self%ptr, &
            i, &
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

    end subroutine LIBMUSCLE_Data_set_item_index_int8

    subroutine LIBMUSCLE_Data_set_item_index_real4(self, i, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (LIBMUSCLE_size), intent(in) :: i
        real (LIBMUSCLE_real4), intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_index_real4_( &
            self%ptr, &
            i, &
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

    end subroutine LIBMUSCLE_Data_set_item_index_real4

    subroutine LIBMUSCLE_Data_set_item_index_real8(self, i, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (LIBMUSCLE_size), intent(in) :: i
        real (LIBMUSCLE_real8), intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_index_real8_( &
            self%ptr, &
            i, &
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

    end subroutine LIBMUSCLE_Data_set_item_index_real8

    subroutine LIBMUSCLE_Data_set_item_index_data(self, i, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (LIBMUSCLE_size), intent(in) :: i
        type(LIBMUSCLE_Data), intent(in) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Data_set_item_index_data_( &
            self%ptr, &
            i, &
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

    end subroutine LIBMUSCLE_Data_set_item_index_data

    function LIBMUSCLE_Data_key(self, i, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (LIBMUSCLE_size), intent(in) :: i
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        character(:), allocatable :: LIBMUSCLE_Data_key

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

        call LIBMUSCLE_Data_key_( &
            self%ptr, &
            i, &
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
        allocate (character(ret_val_size) :: LIBMUSCLE_Data_key)
        do i_loop = 1, ret_val_size
            LIBMUSCLE_Data_key(i_loop:i_loop) = f_ret_ptr(i_loop)
        end do
    end function LIBMUSCLE_Data_key

    function LIBMUSCLE_Data_value(self, i, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Data), intent(in) :: self
        integer (LIBMUSCLE_size), intent(in) :: i
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_value

        integer (c_intptr_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Data_value_( &
            self%ptr, &
            i, &
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

        LIBMUSCLE_Data_value%ptr = ret_val
    end function LIBMUSCLE_Data_value


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

