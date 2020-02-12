! This is generated code. If it's broken, then you should
! fix the generation script, not this file.


module libmuscle
    use iso_c_binding
    use ymmsl

    private

    integer, parameter, public :: LIBMUSCLE_success = 0
    integer, parameter, public :: LIBMUSCLE_domain_error = 1
    integer, parameter, public :: LIBMUSCLE_out_of_range = 2
    integer, parameter, public :: LIBMUSCLE_logic_error = 3
    integer, parameter, public :: LIBMUSCLE_runtime_error = 4
    integer, parameter, public :: LIBMUSCLE_bad_cast = 5

    integer, parameter, public :: LIBMUSCLE_int1 = selected_int_kind(2)
    integer, parameter, public :: LIBMUSCLE_int2 = selected_int_kind(4)
    integer, parameter, public :: LIBMUSCLE_int4 = selected_int_kind(9)
    integer, parameter, public :: LIBMUSCLE_int8 = selected_int_kind(18)
    integer, parameter, public :: LIBMUSCLE_size = c_size_t
    integer, parameter, public :: LIBMUSCLE_real4 = selected_real_kind(6)
    integer, parameter, public :: LIBMUSCLE_real8 = selected_real_kind(15)

    type LIBMUSCLE_DataConstRef
        integer (c_intptr_t) :: ptr
    end type LIBMUSCLE_DataConstRef
    public :: LIBMUSCLE_DataConstRef

    public :: LIBMUSCLE_DataConstRef_create_nil
    public :: LIBMUSCLE_DataConstRef_create_logical
    public :: LIBMUSCLE_DataConstRef_create_character
    public :: LIBMUSCLE_DataConstRef_create_int1
    public :: LIBMUSCLE_DataConstRef_create_int2
    public :: LIBMUSCLE_DataConstRef_create_int4
    public :: LIBMUSCLE_DataConstRef_create_int8
    public :: LIBMUSCLE_DataConstRef_create_real4
    public :: LIBMUSCLE_DataConstRef_create_real8
    public :: LIBMUSCLE_DataConstRef_create_settings
    public :: LIBMUSCLE_DataConstRef_create_copy
    public :: LIBMUSCLE_DataConstRef_create
    public :: LIBMUSCLE_DataConstRef_free
    public :: LIBMUSCLE_DataConstRef_is_a_logical
    public :: LIBMUSCLE_DataConstRef_is_a_character
    public :: LIBMUSCLE_DataConstRef_is_a_int
    public :: LIBMUSCLE_DataConstRef_is_a_int1
    public :: LIBMUSCLE_DataConstRef_is_a_int2
    public :: LIBMUSCLE_DataConstRef_is_a_int4
    public :: LIBMUSCLE_DataConstRef_is_a_int8
    public :: LIBMUSCLE_DataConstRef_is_a_real4
    public :: LIBMUSCLE_DataConstRef_is_a_real8
    public :: LIBMUSCLE_DataConstRef_is_a_dict
    public :: LIBMUSCLE_DataConstRef_is_a_list
    public :: LIBMUSCLE_DataConstRef_is_a_byte_array
    public :: LIBMUSCLE_DataConstRef_is_nil
    public :: LIBMUSCLE_DataConstRef_is_a_settings
    public :: LIBMUSCLE_DataConstRef_size
    public :: LIBMUSCLE_DataConstRef_as_logical
    public :: LIBMUSCLE_DataConstRef_as_character
    public :: LIBMUSCLE_DataConstRef_as_int
    public :: LIBMUSCLE_DataConstRef_as_int1
    public :: LIBMUSCLE_DataConstRef_as_int2
    public :: LIBMUSCLE_DataConstRef_as_int4
    public :: LIBMUSCLE_DataConstRef_as_int8
    public :: LIBMUSCLE_DataConstRef_as_real4
    public :: LIBMUSCLE_DataConstRef_as_real8
    public :: LIBMUSCLE_DataConstRef_as_settings
    public :: LIBMUSCLE_DataConstRef_as_byte_array
    public :: LIBMUSCLE_DataConstRef_get_item_by_key
    public :: LIBMUSCLE_DataConstRef_get_item_by_index
    public :: LIBMUSCLE_DataConstRef_get_item
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
    public :: LIBMUSCLE_Data_create_dict
    public :: LIBMUSCLE_Data_create_list
    public :: LIBMUSCLE_Data_create_nils
    public :: LIBMUSCLE_Data_create_byte_array_empty
    public :: LIBMUSCLE_Data_create_byte_array_from_buf
    public :: LIBMUSCLE_Data_create_byte_array
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
    type LIBMUSCLE_PortsDescription
        integer (c_intptr_t) :: ptr
    end type LIBMUSCLE_PortsDescription
    public :: LIBMUSCLE_PortsDescription

    public :: LIBMUSCLE_PortsDescription_create
    public :: LIBMUSCLE_PortsDescription_free
    public :: LIBMUSCLE_PortsDescription_add
    public :: LIBMUSCLE_PortsDescription_num_ports
    public :: LIBMUSCLE_PortsDescription_get
    type LIBMUSCLE_Message
        integer (c_intptr_t) :: ptr
    end type LIBMUSCLE_Message
    public :: LIBMUSCLE_Message

    public :: LIBMUSCLE_Message_create_td
    public :: LIBMUSCLE_Message_create_tnd
    public :: LIBMUSCLE_Message_create_tds
    public :: LIBMUSCLE_Message_create_tnds
    public :: LIBMUSCLE_Message_create
    public :: LIBMUSCLE_Message_free
    public :: LIBMUSCLE_Message_timestamp
    public :: LIBMUSCLE_Message_set_timestamp
    public :: LIBMUSCLE_Message_has_next_timestamp
    public :: LIBMUSCLE_Message_next_timestamp
    public :: LIBMUSCLE_Message_set_next_timestamp
    public :: LIBMUSCLE_Message_unset_next_timestamp
    public :: LIBMUSCLE_Message_get_data
    public :: LIBMUSCLE_Message_set_data_d
    public :: LIBMUSCLE_Message_set_data_dcr
    public :: LIBMUSCLE_Message_set_data
    public :: LIBMUSCLE_Message_has_settings
    public :: LIBMUSCLE_Message_get_settings
    public :: LIBMUSCLE_Message_set_settings
    public :: LIBMUSCLE_Message_unset_settings
    type LIBMUSCLE_Instance
        integer (c_intptr_t) :: ptr
    end type LIBMUSCLE_Instance
    public :: LIBMUSCLE_Instance

    public :: LIBMUSCLE_Instance_create_autoports
    public :: LIBMUSCLE_Instance_create_with_ports
    public :: LIBMUSCLE_Instance_create
    public :: LIBMUSCLE_Instance_free
    public :: LIBMUSCLE_Instance_reuse_instance_default
    public :: LIBMUSCLE_Instance_reuse_instance_apply
    public :: LIBMUSCLE_Instance_reuse_instance
    public :: LIBMUSCLE_Instance_error_shutdown
    public :: LIBMUSCLE_Instance_get_setting_as_character
    public :: LIBMUSCLE_Instance_get_setting_as_int8
    public :: LIBMUSCLE_Instance_get_setting_as_real8
    public :: LIBMUSCLE_Instance_get_setting_as_logical
    public :: LIBMUSCLE_Instance_get_setting_as_real8array
    public :: LIBMUSCLE_Instance_get_setting_as_real8array2
    public :: LIBMUSCLE_Instance_list_ports
    public :: LIBMUSCLE_Instance_is_connected
    public :: LIBMUSCLE_Instance_is_vector_port
    public :: LIBMUSCLE_Instance_is_resizable
    public :: LIBMUSCLE_Instance_get_port_length
    public :: LIBMUSCLE_Instance_set_port_length
    public :: LIBMUSCLE_Instance_send_pm
    public :: LIBMUSCLE_Instance_send_pms
    public :: LIBMUSCLE_Instance_send
    public :: LIBMUSCLE_Instance_receive_p
    public :: LIBMUSCLE_Instance_receive_pd
    public :: LIBMUSCLE_Instance_receive
    public :: LIBMUSCLE_Instance_receive_ps
    public :: LIBMUSCLE_Instance_receive_psd
    public :: LIBMUSCLE_Instance_receive_on_slot
    public :: LIBMUSCLE_Instance_receive_with_settings_p
    public :: LIBMUSCLE_Instance_receive_with_settings_pd
    public :: LIBMUSCLE_Instance_receive_with_settings
    public :: LIBMUSCLE_Instance_receive_with_settings_ps
    public :: LIBMUSCLE_Instance_receive_with_settings_psd
    public :: LIBMUSCLE_Instance_receive_with_settings_on_slot

    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_success = 0
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_domain_error = 1
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_out_of_range = 2
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_logic_error = 3
    integer, parameter :: LIBMUSCLE_IMPL_BINDINGS_runtime_error = 4
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

        integer (c_intptr_t) function LIBMUSCLE_DataConstRef_create_nil_( &
                ) &
                bind(C, name="LIBMUSCLE_DataConstRef_create_nil_")

            use iso_c_binding
        end function LIBMUSCLE_DataConstRef_create_nil_

        integer (c_intptr_t) function LIBMUSCLE_DataConstRef_create_logical_( &
                value) &
                bind(C, name="LIBMUSCLE_DataConstRef_create_logical_")

            use iso_c_binding
            integer (c_int), value, intent(in) :: value
        end function LIBMUSCLE_DataConstRef_create_logical_

        integer (c_intptr_t) function LIBMUSCLE_DataConstRef_create_character_( &
                value, value_size) &
                bind(C, name="LIBMUSCLE_DataConstRef_create_character_")

            use iso_c_binding
            character, intent(in) :: value
            integer (c_size_t), value, intent(in) :: value_size
        end function LIBMUSCLE_DataConstRef_create_character_

        integer (c_intptr_t) function LIBMUSCLE_DataConstRef_create_int1_( &
                value) &
                bind(C, name="LIBMUSCLE_DataConstRef_create_int1_")

            use iso_c_binding
            integer (c_int8_t), value, intent(in) :: value
        end function LIBMUSCLE_DataConstRef_create_int1_

        integer (c_intptr_t) function LIBMUSCLE_DataConstRef_create_int2_( &
                value) &
                bind(C, name="LIBMUSCLE_DataConstRef_create_int2_")

            use iso_c_binding
            integer (c_short), value, intent(in) :: value
        end function LIBMUSCLE_DataConstRef_create_int2_

        integer (c_intptr_t) function LIBMUSCLE_DataConstRef_create_int4_( &
                value) &
                bind(C, name="LIBMUSCLE_DataConstRef_create_int4_")

            use iso_c_binding
            integer (c_int32_t), value, intent(in) :: value
        end function LIBMUSCLE_DataConstRef_create_int4_

        integer (c_intptr_t) function LIBMUSCLE_DataConstRef_create_int8_( &
                value) &
                bind(C, name="LIBMUSCLE_DataConstRef_create_int8_")

            use iso_c_binding
            integer (c_int64_t), value, intent(in) :: value
        end function LIBMUSCLE_DataConstRef_create_int8_

        integer (c_intptr_t) function LIBMUSCLE_DataConstRef_create_real4_( &
                value) &
                bind(C, name="LIBMUSCLE_DataConstRef_create_real4_")

            use iso_c_binding
            real (c_float), value, intent(in) :: value
        end function LIBMUSCLE_DataConstRef_create_real4_

        integer (c_intptr_t) function LIBMUSCLE_DataConstRef_create_real8_( &
                value) &
                bind(C, name="LIBMUSCLE_DataConstRef_create_real8_")

            use iso_c_binding
            real (c_double), value, intent(in) :: value
        end function LIBMUSCLE_DataConstRef_create_real8_

        integer (c_intptr_t) function LIBMUSCLE_DataConstRef_create_settings_( &
                value) &
                bind(C, name="LIBMUSCLE_DataConstRef_create_settings_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: value
        end function LIBMUSCLE_DataConstRef_create_settings_

        integer (c_intptr_t) function LIBMUSCLE_DataConstRef_create_copy_( &
                value) &
                bind(C, name="LIBMUSCLE_DataConstRef_create_copy_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: value
        end function LIBMUSCLE_DataConstRef_create_copy_

        subroutine LIBMUSCLE_DataConstRef_free_( &
                self) &
                bind(C, name="LIBMUSCLE_DataConstRef_free_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end subroutine LIBMUSCLE_DataConstRef_free_

        integer (c_int) function LIBMUSCLE_DataConstRef_is_a_logical_( &
                self) &
                bind(C, name="LIBMUSCLE_DataConstRef_is_a_logical_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_DataConstRef_is_a_logical_

        integer (c_int) function LIBMUSCLE_DataConstRef_is_a_character_( &
                self) &
                bind(C, name="LIBMUSCLE_DataConstRef_is_a_character_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_DataConstRef_is_a_character_

        integer (c_int) function LIBMUSCLE_DataConstRef_is_a_int_( &
                self) &
                bind(C, name="LIBMUSCLE_DataConstRef_is_a_int_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_DataConstRef_is_a_int_

        integer (c_int) function LIBMUSCLE_DataConstRef_is_a_int1_( &
                self) &
                bind(C, name="LIBMUSCLE_DataConstRef_is_a_int1_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_DataConstRef_is_a_int1_

        integer (c_int) function LIBMUSCLE_DataConstRef_is_a_int2_( &
                self) &
                bind(C, name="LIBMUSCLE_DataConstRef_is_a_int2_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_DataConstRef_is_a_int2_

        integer (c_int) function LIBMUSCLE_DataConstRef_is_a_int4_( &
                self) &
                bind(C, name="LIBMUSCLE_DataConstRef_is_a_int4_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_DataConstRef_is_a_int4_

        integer (c_int) function LIBMUSCLE_DataConstRef_is_a_int8_( &
                self) &
                bind(C, name="LIBMUSCLE_DataConstRef_is_a_int8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_DataConstRef_is_a_int8_

        integer (c_int) function LIBMUSCLE_DataConstRef_is_a_real4_( &
                self) &
                bind(C, name="LIBMUSCLE_DataConstRef_is_a_real4_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_DataConstRef_is_a_real4_

        integer (c_int) function LIBMUSCLE_DataConstRef_is_a_real8_( &
                self) &
                bind(C, name="LIBMUSCLE_DataConstRef_is_a_real8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_DataConstRef_is_a_real8_

        integer (c_int) function LIBMUSCLE_DataConstRef_is_a_dict_( &
                self) &
                bind(C, name="LIBMUSCLE_DataConstRef_is_a_dict_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_DataConstRef_is_a_dict_

        integer (c_int) function LIBMUSCLE_DataConstRef_is_a_list_( &
                self) &
                bind(C, name="LIBMUSCLE_DataConstRef_is_a_list_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_DataConstRef_is_a_list_

        integer (c_int) function LIBMUSCLE_DataConstRef_is_a_byte_array_( &
                self) &
                bind(C, name="LIBMUSCLE_DataConstRef_is_a_byte_array_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_DataConstRef_is_a_byte_array_

        integer (c_int) function LIBMUSCLE_DataConstRef_is_nil_( &
                self) &
                bind(C, name="LIBMUSCLE_DataConstRef_is_nil_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_DataConstRef_is_nil_

        integer (c_int) function LIBMUSCLE_DataConstRef_is_a_settings_( &
                self) &
                bind(C, name="LIBMUSCLE_DataConstRef_is_a_settings_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_DataConstRef_is_a_settings_

        integer (c_size_t) function LIBMUSCLE_DataConstRef_size_( &
                self) &
                bind(C, name="LIBMUSCLE_DataConstRef_size_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_DataConstRef_size_

        integer (c_int) function LIBMUSCLE_DataConstRef_as_logical_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_DataConstRef_as_logical_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_DataConstRef_as_logical_

        subroutine LIBMUSCLE_DataConstRef_as_character_( &
                self, ret_val, ret_val_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_DataConstRef_as_character_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            type (c_ptr), intent(out) :: ret_val
            integer (c_size_t), intent(out) :: ret_val_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_DataConstRef_as_character_

        integer (c_int) function LIBMUSCLE_DataConstRef_as_int_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_DataConstRef_as_int_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_DataConstRef_as_int_

        integer (c_int8_t) function LIBMUSCLE_DataConstRef_as_int1_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_DataConstRef_as_int1_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_DataConstRef_as_int1_

        integer (c_short) function LIBMUSCLE_DataConstRef_as_int2_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_DataConstRef_as_int2_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_DataConstRef_as_int2_

        integer (c_int32_t) function LIBMUSCLE_DataConstRef_as_int4_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_DataConstRef_as_int4_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_DataConstRef_as_int4_

        integer (c_int64_t) function LIBMUSCLE_DataConstRef_as_int8_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_DataConstRef_as_int8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_DataConstRef_as_int8_

        real (c_float) function LIBMUSCLE_DataConstRef_as_real4_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_DataConstRef_as_real4_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_DataConstRef_as_real4_

        real (c_double) function LIBMUSCLE_DataConstRef_as_real8_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_DataConstRef_as_real8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_DataConstRef_as_real8_

        integer (c_intptr_t) function LIBMUSCLE_DataConstRef_as_settings_( &
                self, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_DataConstRef_as_settings_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_DataConstRef_as_settings_

        subroutine LIBMUSCLE_DataConstRef_as_byte_array_( &
                self, ret_val, ret_val_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_DataConstRef_as_byte_array_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            type (c_ptr), intent(out) :: ret_val
            integer (c_size_t), intent(out) :: ret_val_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_DataConstRef_as_byte_array_

        integer (c_intptr_t) function LIBMUSCLE_DataConstRef_get_item_by_key_( &
                self, key, key_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_DataConstRef_get_item_by_key_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: key
            integer (c_size_t), value, intent(in) :: key_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_DataConstRef_get_item_by_key_

        integer (c_intptr_t) function LIBMUSCLE_DataConstRef_get_item_by_index_( &
                self, i, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_DataConstRef_get_item_by_index_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_size_t), value, intent(in) :: i
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_DataConstRef_get_item_by_index_

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

        integer (c_intptr_t) function LIBMUSCLE_Data_create_nils_( &
                size) &
                bind(C, name="LIBMUSCLE_Data_create_nils_")

            use iso_c_binding
            integer (c_size_t), value, intent(in) :: size
        end function LIBMUSCLE_Data_create_nils_

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

        integer (c_intptr_t) function LIBMUSCLE_PortsDescription_create_( &
                ) &
                bind(C, name="LIBMUSCLE_PortsDescription_create_")

            use iso_c_binding
        end function LIBMUSCLE_PortsDescription_create_

        subroutine LIBMUSCLE_PortsDescription_free_( &
                self) &
                bind(C, name="LIBMUSCLE_PortsDescription_free_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end subroutine LIBMUSCLE_PortsDescription_free_

        subroutine LIBMUSCLE_PortsDescription_add_( &
                self, op, port, port_size) &
                bind(C, name="LIBMUSCLE_PortsDescription_add_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), value, intent(in) :: op
            character, intent(in) :: port
            integer (c_size_t), value, intent(in) :: port_size
        end subroutine LIBMUSCLE_PortsDescription_add_

        integer (c_size_t) function LIBMUSCLE_PortsDescription_num_ports_( &
                self, op) &
                bind(C, name="LIBMUSCLE_PortsDescription_num_ports_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), value, intent(in) :: op
        end function LIBMUSCLE_PortsDescription_num_ports_

        subroutine LIBMUSCLE_PortsDescription_get_( &
                self, op, i, ret_val, ret_val_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_PortsDescription_get_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), value, intent(in) :: op
            integer (c_size_t), value, intent(in) :: i
            type (c_ptr), intent(out) :: ret_val
            integer (c_size_t), intent(out) :: ret_val_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_PortsDescription_get_

        integer (c_intptr_t) function LIBMUSCLE_Message_create_td_( &
                timestamp, data) &
                bind(C, name="LIBMUSCLE_Message_create_td_")

            use iso_c_binding
            real (c_double), value, intent(in) :: timestamp
            integer (c_intptr_t), value, intent(in) :: data
        end function LIBMUSCLE_Message_create_td_

        integer (c_intptr_t) function LIBMUSCLE_Message_create_tnd_( &
                timestamp, next_timestamp, data) &
                bind(C, name="LIBMUSCLE_Message_create_tnd_")

            use iso_c_binding
            real (c_double), value, intent(in) :: timestamp
            real (c_double), value, intent(in) :: next_timestamp
            integer (c_intptr_t), value, intent(in) :: data
        end function LIBMUSCLE_Message_create_tnd_

        integer (c_intptr_t) function LIBMUSCLE_Message_create_tds_( &
                timestamp, data, settings) &
                bind(C, name="LIBMUSCLE_Message_create_tds_")

            use iso_c_binding
            real (c_double), value, intent(in) :: timestamp
            integer (c_intptr_t), value, intent(in) :: data
            integer (c_intptr_t), value, intent(in) :: settings
        end function LIBMUSCLE_Message_create_tds_

        integer (c_intptr_t) function LIBMUSCLE_Message_create_tnds_( &
                timestamp, next_timestamp, data, settings) &
                bind(C, name="LIBMUSCLE_Message_create_tnds_")

            use iso_c_binding
            real (c_double), value, intent(in) :: timestamp
            real (c_double), value, intent(in) :: next_timestamp
            integer (c_intptr_t), value, intent(in) :: data
            integer (c_intptr_t), value, intent(in) :: settings
        end function LIBMUSCLE_Message_create_tnds_

        subroutine LIBMUSCLE_Message_free_( &
                self) &
                bind(C, name="LIBMUSCLE_Message_free_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end subroutine LIBMUSCLE_Message_free_

        real (c_double) function LIBMUSCLE_Message_timestamp_( &
                self) &
                bind(C, name="LIBMUSCLE_Message_timestamp_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Message_timestamp_

        subroutine LIBMUSCLE_Message_set_timestamp_( &
                self, timestamp) &
                bind(C, name="LIBMUSCLE_Message_set_timestamp_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            real (c_double), value, intent(in) :: timestamp
        end subroutine LIBMUSCLE_Message_set_timestamp_

        integer (c_int) function LIBMUSCLE_Message_has_next_timestamp_( &
                self) &
                bind(C, name="LIBMUSCLE_Message_has_next_timestamp_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Message_has_next_timestamp_

        real (c_double) function LIBMUSCLE_Message_next_timestamp_( &
                self) &
                bind(C, name="LIBMUSCLE_Message_next_timestamp_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Message_next_timestamp_

        subroutine LIBMUSCLE_Message_set_next_timestamp_( &
                self, next_timestamp) &
                bind(C, name="LIBMUSCLE_Message_set_next_timestamp_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            real (c_double), value, intent(in) :: next_timestamp
        end subroutine LIBMUSCLE_Message_set_next_timestamp_

        subroutine LIBMUSCLE_Message_unset_next_timestamp_( &
                self) &
                bind(C, name="LIBMUSCLE_Message_unset_next_timestamp_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end subroutine LIBMUSCLE_Message_unset_next_timestamp_

        integer (c_intptr_t) function LIBMUSCLE_Message_get_data_( &
                self) &
                bind(C, name="LIBMUSCLE_Message_get_data_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Message_get_data_

        subroutine LIBMUSCLE_Message_set_data_d_( &
                self, data) &
                bind(C, name="LIBMUSCLE_Message_set_data_d_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_intptr_t), value, intent(in) :: data
        end subroutine LIBMUSCLE_Message_set_data_d_

        subroutine LIBMUSCLE_Message_set_data_dcr_( &
                self, data) &
                bind(C, name="LIBMUSCLE_Message_set_data_dcr_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_intptr_t), value, intent(in) :: data
        end subroutine LIBMUSCLE_Message_set_data_dcr_

        integer (c_int) function LIBMUSCLE_Message_has_settings_( &
                self) &
                bind(C, name="LIBMUSCLE_Message_has_settings_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Message_has_settings_

        integer (c_intptr_t) function LIBMUSCLE_Message_get_settings_( &
                self) &
                bind(C, name="LIBMUSCLE_Message_get_settings_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Message_get_settings_

        subroutine LIBMUSCLE_Message_set_settings_( &
                self, settings) &
                bind(C, name="LIBMUSCLE_Message_set_settings_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_intptr_t), value, intent(in) :: settings
        end subroutine LIBMUSCLE_Message_set_settings_

        subroutine LIBMUSCLE_Message_unset_settings_( &
                self) &
                bind(C, name="LIBMUSCLE_Message_unset_settings_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end subroutine LIBMUSCLE_Message_unset_settings_

        integer (c_intptr_t) function LIBMUSCLE_Instance_create_autoports_( &
                cla) &
                bind(C, name="LIBMUSCLE_Instance_create_autoports_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: cla
        end function LIBMUSCLE_Instance_create_autoports_

        integer (c_intptr_t) function LIBMUSCLE_Instance_create_with_ports_( &
                cla, ports) &
                bind(C, name="LIBMUSCLE_Instance_create_with_ports_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: cla
            integer (c_intptr_t), value, intent(in) :: ports
        end function LIBMUSCLE_Instance_create_with_ports_

        subroutine LIBMUSCLE_Instance_free_( &
                self) &
                bind(C, name="LIBMUSCLE_Instance_free_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end subroutine LIBMUSCLE_Instance_free_

        integer (c_int) function LIBMUSCLE_Instance_reuse_instance_default_( &
                self) &
                bind(C, name="LIBMUSCLE_Instance_reuse_instance_default_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Instance_reuse_instance_default_

        integer (c_int) function LIBMUSCLE_Instance_reuse_instance_apply_( &
                self, apply_overlay) &
                bind(C, name="LIBMUSCLE_Instance_reuse_instance_apply_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            integer (c_int), value, intent(in) :: apply_overlay
        end function LIBMUSCLE_Instance_reuse_instance_apply_

        subroutine LIBMUSCLE_Instance_error_shutdown_( &
                self, message, message_size) &
                bind(C, name="LIBMUSCLE_Instance_error_shutdown_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: message
            integer (c_size_t), value, intent(in) :: message_size
        end subroutine LIBMUSCLE_Instance_error_shutdown_

        subroutine LIBMUSCLE_Instance_get_setting_as_character_( &
                self, name, name_size, ret_val, ret_val_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Instance_get_setting_as_character_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: name
            integer (c_size_t), value, intent(in) :: name_size
            type (c_ptr), intent(out) :: ret_val
            integer (c_size_t), intent(out) :: ret_val_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Instance_get_setting_as_character_

        integer (c_int64_t) function LIBMUSCLE_Instance_get_setting_as_int8_( &
                self, name, name_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Instance_get_setting_as_int8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: name
            integer (c_size_t), value, intent(in) :: name_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Instance_get_setting_as_int8_

        real (c_double) function LIBMUSCLE_Instance_get_setting_as_real8_( &
                self, name, name_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Instance_get_setting_as_real8_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: name
            integer (c_size_t), value, intent(in) :: name_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Instance_get_setting_as_real8_

        integer (c_int) function LIBMUSCLE_Instance_get_setting_as_logical_( &
                self, name, name_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Instance_get_setting_as_logical_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: name
            integer (c_size_t), value, intent(in) :: name_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Instance_get_setting_as_logical_

        subroutine LIBMUSCLE_Instance_get_setting_as_real8array_( &
                self, name, name_size, ret_val, ret_val_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Instance_get_setting_as_real8array_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: name
            integer (c_size_t), value, intent(in) :: name_size
            type (c_ptr), intent(out) :: ret_val
            integer (c_size_t), intent(out) :: ret_val_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Instance_get_setting_as_real8array_

        subroutine LIBMUSCLE_Instance_get_setting_as_real8array2_( &
                self, name, name_size, ret_val, ret_val_shape, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Instance_get_setting_as_real8array2_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: name
            integer (c_size_t), value, intent(in) :: name_size
            type (c_ptr), intent(out) :: ret_val
            integer (c_size_t), dimension(2), intent(out) :: ret_val_shape
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end subroutine LIBMUSCLE_Instance_get_setting_as_real8array2_

        integer (c_intptr_t) function LIBMUSCLE_Instance_list_ports_( &
                self) &
                bind(C, name="LIBMUSCLE_Instance_list_ports_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
        end function LIBMUSCLE_Instance_list_ports_

        integer (c_int) function LIBMUSCLE_Instance_is_connected_( &
                self, port, port_size) &
                bind(C, name="LIBMUSCLE_Instance_is_connected_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: port
            integer (c_size_t), value, intent(in) :: port_size
        end function LIBMUSCLE_Instance_is_connected_

        integer (c_int) function LIBMUSCLE_Instance_is_vector_port_( &
                self, port, port_size) &
                bind(C, name="LIBMUSCLE_Instance_is_vector_port_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: port
            integer (c_size_t), value, intent(in) :: port_size
        end function LIBMUSCLE_Instance_is_vector_port_

        integer (c_int) function LIBMUSCLE_Instance_is_resizable_( &
                self, port, port_size) &
                bind(C, name="LIBMUSCLE_Instance_is_resizable_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: port
            integer (c_size_t), value, intent(in) :: port_size
        end function LIBMUSCLE_Instance_is_resizable_

        integer (c_int) function LIBMUSCLE_Instance_get_port_length_( &
                self, port, port_size) &
                bind(C, name="LIBMUSCLE_Instance_get_port_length_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: port
            integer (c_size_t), value, intent(in) :: port_size
        end function LIBMUSCLE_Instance_get_port_length_

        subroutine LIBMUSCLE_Instance_set_port_length_( &
                self, port, port_size, length) &
                bind(C, name="LIBMUSCLE_Instance_set_port_length_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: port
            integer (c_size_t), value, intent(in) :: port_size
            integer (c_int), value, intent(in) :: length
        end subroutine LIBMUSCLE_Instance_set_port_length_

        subroutine LIBMUSCLE_Instance_send_pm_( &
                self, port_name, port_name_size, message) &
                bind(C, name="LIBMUSCLE_Instance_send_pm_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: port_name
            integer (c_size_t), value, intent(in) :: port_name_size
            integer (c_intptr_t), value, intent(in) :: message
        end subroutine LIBMUSCLE_Instance_send_pm_

        subroutine LIBMUSCLE_Instance_send_pms_( &
                self, port_name, port_name_size, message, slot) &
                bind(C, name="LIBMUSCLE_Instance_send_pms_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: port_name
            integer (c_size_t), value, intent(in) :: port_name_size
            integer (c_intptr_t), value, intent(in) :: message
            integer (c_int), value, intent(in) :: slot
        end subroutine LIBMUSCLE_Instance_send_pms_

        integer (c_intptr_t) function LIBMUSCLE_Instance_receive_p_( &
                self, port_name, port_name_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Instance_receive_p_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: port_name
            integer (c_size_t), value, intent(in) :: port_name_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Instance_receive_p_

        integer (c_intptr_t) function LIBMUSCLE_Instance_receive_pd_( &
                self, port_name, port_name_size, default_msg, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Instance_receive_pd_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: port_name
            integer (c_size_t), value, intent(in) :: port_name_size
            integer (c_intptr_t), value, intent(in) :: default_msg
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Instance_receive_pd_

        integer (c_intptr_t) function LIBMUSCLE_Instance_receive_ps_( &
                self, port_name, port_name_size, slot, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Instance_receive_ps_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: port_name
            integer (c_size_t), value, intent(in) :: port_name_size
            integer (c_int), value, intent(in) :: slot
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Instance_receive_ps_

        integer (c_intptr_t) function LIBMUSCLE_Instance_receive_psd_( &
                self, port_name, port_name_size, slot, default_message, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Instance_receive_psd_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: port_name
            integer (c_size_t), value, intent(in) :: port_name_size
            integer (c_int), value, intent(in) :: slot
            integer (c_intptr_t), value, intent(in) :: default_message
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Instance_receive_psd_

        integer (c_intptr_t) function LIBMUSCLE_Instance_receive_with_settings_p_( &
                self, port_name, port_name_size, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Instance_receive_with_settings_p_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: port_name
            integer (c_size_t), value, intent(in) :: port_name_size
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Instance_receive_with_settings_p_

        integer (c_intptr_t) function LIBMUSCLE_Instance_receive_with_settings_pd_( &
                self, port_name, port_name_size, default_msg, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Instance_receive_with_settings_pd_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: port_name
            integer (c_size_t), value, intent(in) :: port_name_size
            integer (c_intptr_t), value, intent(in) :: default_msg
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Instance_receive_with_settings_pd_

        integer (c_intptr_t) function LIBMUSCLE_Instance_receive_with_settings_ps_( &
                self, port_name, port_name_size, slot, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Instance_receive_with_settings_ps_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: port_name
            integer (c_size_t), value, intent(in) :: port_name_size
            integer (c_int), value, intent(in) :: slot
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Instance_receive_with_settings_ps_

        integer (c_intptr_t) function LIBMUSCLE_Instance_receive_with_settings_psd_( &
                self, port_name, port_name_size, slot, default_msg, err_code, err_msg, err_msg_len) &
                bind(C, name="LIBMUSCLE_Instance_receive_with_settings_psd_")

            use iso_c_binding
            integer (c_intptr_t), value, intent(in) :: self
            character, intent(in) :: port_name
            integer (c_size_t), value, intent(in) :: port_name_size
            integer (c_int), value, intent(in) :: slot
            integer (c_intptr_t), value, intent(in) :: default_msg
            integer (c_int), intent(out) :: err_code
            type (c_ptr), intent(out) :: err_msg
            integer (c_size_t), intent(out) :: err_msg_len
        end function LIBMUSCLE_Instance_receive_with_settings_psd_

    end interface

    interface LIBMUSCLE_DataConstRef_create
        module procedure &
            LIBMUSCLE_DataConstRef_create_nil, &
            LIBMUSCLE_DataConstRef_create_logical, &
            LIBMUSCLE_DataConstRef_create_character, &
            LIBMUSCLE_DataConstRef_create_int1, &
            LIBMUSCLE_DataConstRef_create_int2, &
            LIBMUSCLE_DataConstRef_create_int4, &
            LIBMUSCLE_DataConstRef_create_int8, &
            LIBMUSCLE_DataConstRef_create_real4, &
            LIBMUSCLE_DataConstRef_create_real8, &
            LIBMUSCLE_DataConstRef_create_settings, &
            LIBMUSCLE_DataConstRef_create_copy
    end interface

    interface LIBMUSCLE_DataConstRef_get_item
        module procedure &
            LIBMUSCLE_DataConstRef_get_item_by_key, &
            LIBMUSCLE_DataConstRef_get_item_by_index
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

    interface LIBMUSCLE_Data_get_item
        module procedure &
            LIBMUSCLE_Data_get_item_by_key, &
            LIBMUSCLE_Data_get_item_by_index
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

    interface LIBMUSCLE_Message_create
        module procedure &
            LIBMUSCLE_Message_create_td, &
            LIBMUSCLE_Message_create_tnd, &
            LIBMUSCLE_Message_create_tds, &
            LIBMUSCLE_Message_create_tnds
    end interface

    interface LIBMUSCLE_Message_set_data
        module procedure &
            LIBMUSCLE_Message_set_data_d, &
            LIBMUSCLE_Message_set_data_dcr
    end interface

    interface LIBMUSCLE_Instance_create
        module procedure &
            LIBMUSCLE_Instance_create_autoports, &
            LIBMUSCLE_Instance_create_with_ports
    end interface

    interface LIBMUSCLE_Instance_reuse_instance
        module procedure &
            LIBMUSCLE_Instance_reuse_instance_default, &
            LIBMUSCLE_Instance_reuse_instance_apply
    end interface

    interface LIBMUSCLE_Instance_send
        module procedure &
            LIBMUSCLE_Instance_send_pm, &
            LIBMUSCLE_Instance_send_pms
    end interface

    interface LIBMUSCLE_Instance_receive
        module procedure &
            LIBMUSCLE_Instance_receive_p, &
            LIBMUSCLE_Instance_receive_pd
    end interface

    interface LIBMUSCLE_Instance_receive_on_slot
        module procedure &
            LIBMUSCLE_Instance_receive_ps, &
            LIBMUSCLE_Instance_receive_psd
    end interface

    interface LIBMUSCLE_Instance_receive_with_settings
        module procedure &
            LIBMUSCLE_Instance_receive_with_settings_p, &
            LIBMUSCLE_Instance_receive_with_settings_pd
    end interface

    interface LIBMUSCLE_Instance_receive_with_settings_on_slot
        module procedure &
            LIBMUSCLE_Instance_receive_with_settings_ps, &
            LIBMUSCLE_Instance_receive_with_settings_psd
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

    function LIBMUSCLE_DataConstRef_create_nil()
        implicit none
        type(LIBMUSCLE_DataConstRef) :: LIBMUSCLE_DataConstRef_create_nil

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_create_nil_( &
    )

        LIBMUSCLE_DataConstRef_create_nil%ptr = ret_val
    end function LIBMUSCLE_DataConstRef_create_nil

    function LIBMUSCLE_DataConstRef_create_logical(value)
        implicit none
        logical, intent(in) :: value
        type(LIBMUSCLE_DataConstRef) :: LIBMUSCLE_DataConstRef_create_logical

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_create_logical_( &
            merge(1, 0, value))

        LIBMUSCLE_DataConstRef_create_logical%ptr = ret_val
    end function LIBMUSCLE_DataConstRef_create_logical

    function LIBMUSCLE_DataConstRef_create_character(value)
        implicit none
        character (len=*), intent(in) :: value
        type(LIBMUSCLE_DataConstRef) :: LIBMUSCLE_DataConstRef_create_character

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_create_character_( &
            value, int(len(value), c_size_t))

        LIBMUSCLE_DataConstRef_create_character%ptr = ret_val
    end function LIBMUSCLE_DataConstRef_create_character

    function LIBMUSCLE_DataConstRef_create_int1(value)
        implicit none
        integer (LIBMUSCLE_int1), intent(in) :: value
        type(LIBMUSCLE_DataConstRef) :: LIBMUSCLE_DataConstRef_create_int1

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_create_int1_( &
            value)

        LIBMUSCLE_DataConstRef_create_int1%ptr = ret_val
    end function LIBMUSCLE_DataConstRef_create_int1

    function LIBMUSCLE_DataConstRef_create_int2(value)
        implicit none
        integer (selected_int_kind(4)), intent(in) :: value
        type(LIBMUSCLE_DataConstRef) :: LIBMUSCLE_DataConstRef_create_int2

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_create_int2_( &
            value)

        LIBMUSCLE_DataConstRef_create_int2%ptr = ret_val
    end function LIBMUSCLE_DataConstRef_create_int2

    function LIBMUSCLE_DataConstRef_create_int4(value)
        implicit none
        integer (LIBMUSCLE_int4), intent(in) :: value
        type(LIBMUSCLE_DataConstRef) :: LIBMUSCLE_DataConstRef_create_int4

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_create_int4_( &
            value)

        LIBMUSCLE_DataConstRef_create_int4%ptr = ret_val
    end function LIBMUSCLE_DataConstRef_create_int4

    function LIBMUSCLE_DataConstRef_create_int8(value)
        implicit none
        integer (selected_int_kind(18)), intent(in) :: value
        type(LIBMUSCLE_DataConstRef) :: LIBMUSCLE_DataConstRef_create_int8

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_create_int8_( &
            value)

        LIBMUSCLE_DataConstRef_create_int8%ptr = ret_val
    end function LIBMUSCLE_DataConstRef_create_int8

    function LIBMUSCLE_DataConstRef_create_real4(value)
        implicit none
        real (LIBMUSCLE_real4), intent(in) :: value
        type(LIBMUSCLE_DataConstRef) :: LIBMUSCLE_DataConstRef_create_real4

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_create_real4_( &
            value)

        LIBMUSCLE_DataConstRef_create_real4%ptr = ret_val
    end function LIBMUSCLE_DataConstRef_create_real4

    function LIBMUSCLE_DataConstRef_create_real8(value)
        implicit none
        real (LIBMUSCLE_real8), intent(in) :: value
        type(LIBMUSCLE_DataConstRef) :: LIBMUSCLE_DataConstRef_create_real8

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_create_real8_( &
            value)

        LIBMUSCLE_DataConstRef_create_real8%ptr = ret_val
    end function LIBMUSCLE_DataConstRef_create_real8

    function LIBMUSCLE_DataConstRef_create_settings(value)
        implicit none
        type(YMMSL_Settings), intent(in) :: value
        type(LIBMUSCLE_DataConstRef) :: LIBMUSCLE_DataConstRef_create_settings

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_create_settings_( &
            value%ptr)

        LIBMUSCLE_DataConstRef_create_settings%ptr = ret_val
    end function LIBMUSCLE_DataConstRef_create_settings

    function LIBMUSCLE_DataConstRef_create_copy(value)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: value
        type(LIBMUSCLE_DataConstRef) :: LIBMUSCLE_DataConstRef_create_copy

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_create_copy_( &
            value%ptr)

        LIBMUSCLE_DataConstRef_create_copy%ptr = ret_val
    end function LIBMUSCLE_DataConstRef_create_copy

    subroutine LIBMUSCLE_DataConstRef_free(self)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self

        call LIBMUSCLE_DataConstRef_free_( &
            self%ptr)
    end subroutine LIBMUSCLE_DataConstRef_free

    function LIBMUSCLE_DataConstRef_is_a_logical(self)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        logical :: LIBMUSCLE_DataConstRef_is_a_logical

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_is_a_logical_( &
            self%ptr)

        LIBMUSCLE_DataConstRef_is_a_logical = ret_val .ne. 0
    end function LIBMUSCLE_DataConstRef_is_a_logical

    function LIBMUSCLE_DataConstRef_is_a_character(self)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        logical :: LIBMUSCLE_DataConstRef_is_a_character

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_is_a_character_( &
            self%ptr)

        LIBMUSCLE_DataConstRef_is_a_character = ret_val .ne. 0
    end function LIBMUSCLE_DataConstRef_is_a_character

    function LIBMUSCLE_DataConstRef_is_a_int(self)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        logical :: LIBMUSCLE_DataConstRef_is_a_int

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_is_a_int_( &
            self%ptr)

        LIBMUSCLE_DataConstRef_is_a_int = ret_val .ne. 0
    end function LIBMUSCLE_DataConstRef_is_a_int

    function LIBMUSCLE_DataConstRef_is_a_int1(self)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        logical :: LIBMUSCLE_DataConstRef_is_a_int1

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_is_a_int1_( &
            self%ptr)

        LIBMUSCLE_DataConstRef_is_a_int1 = ret_val .ne. 0
    end function LIBMUSCLE_DataConstRef_is_a_int1

    function LIBMUSCLE_DataConstRef_is_a_int2(self)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        logical :: LIBMUSCLE_DataConstRef_is_a_int2

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_is_a_int2_( &
            self%ptr)

        LIBMUSCLE_DataConstRef_is_a_int2 = ret_val .ne. 0
    end function LIBMUSCLE_DataConstRef_is_a_int2

    function LIBMUSCLE_DataConstRef_is_a_int4(self)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        logical :: LIBMUSCLE_DataConstRef_is_a_int4

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_is_a_int4_( &
            self%ptr)

        LIBMUSCLE_DataConstRef_is_a_int4 = ret_val .ne. 0
    end function LIBMUSCLE_DataConstRef_is_a_int4

    function LIBMUSCLE_DataConstRef_is_a_int8(self)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        logical :: LIBMUSCLE_DataConstRef_is_a_int8

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_is_a_int8_( &
            self%ptr)

        LIBMUSCLE_DataConstRef_is_a_int8 = ret_val .ne. 0
    end function LIBMUSCLE_DataConstRef_is_a_int8

    function LIBMUSCLE_DataConstRef_is_a_real4(self)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        logical :: LIBMUSCLE_DataConstRef_is_a_real4

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_is_a_real4_( &
            self%ptr)

        LIBMUSCLE_DataConstRef_is_a_real4 = ret_val .ne. 0
    end function LIBMUSCLE_DataConstRef_is_a_real4

    function LIBMUSCLE_DataConstRef_is_a_real8(self)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        logical :: LIBMUSCLE_DataConstRef_is_a_real8

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_is_a_real8_( &
            self%ptr)

        LIBMUSCLE_DataConstRef_is_a_real8 = ret_val .ne. 0
    end function LIBMUSCLE_DataConstRef_is_a_real8

    function LIBMUSCLE_DataConstRef_is_a_dict(self)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        logical :: LIBMUSCLE_DataConstRef_is_a_dict

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_is_a_dict_( &
            self%ptr)

        LIBMUSCLE_DataConstRef_is_a_dict = ret_val .ne. 0
    end function LIBMUSCLE_DataConstRef_is_a_dict

    function LIBMUSCLE_DataConstRef_is_a_list(self)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        logical :: LIBMUSCLE_DataConstRef_is_a_list

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_is_a_list_( &
            self%ptr)

        LIBMUSCLE_DataConstRef_is_a_list = ret_val .ne. 0
    end function LIBMUSCLE_DataConstRef_is_a_list

    function LIBMUSCLE_DataConstRef_is_a_byte_array(self)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        logical :: LIBMUSCLE_DataConstRef_is_a_byte_array

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_is_a_byte_array_( &
            self%ptr)

        LIBMUSCLE_DataConstRef_is_a_byte_array = ret_val .ne. 0
    end function LIBMUSCLE_DataConstRef_is_a_byte_array

    function LIBMUSCLE_DataConstRef_is_nil(self)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        logical :: LIBMUSCLE_DataConstRef_is_nil

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_is_nil_( &
            self%ptr)

        LIBMUSCLE_DataConstRef_is_nil = ret_val .ne. 0
    end function LIBMUSCLE_DataConstRef_is_nil

    function LIBMUSCLE_DataConstRef_is_a_settings(self)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        logical :: LIBMUSCLE_DataConstRef_is_a_settings

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_is_a_settings_( &
            self%ptr)

        LIBMUSCLE_DataConstRef_is_a_settings = ret_val .ne. 0
    end function LIBMUSCLE_DataConstRef_is_a_settings

    function LIBMUSCLE_DataConstRef_size(self)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        integer (LIBMUSCLE_size) :: LIBMUSCLE_DataConstRef_size

        integer (c_size_t) :: ret_val

        ret_val = LIBMUSCLE_DataConstRef_size_( &
            self%ptr)
        LIBMUSCLE_DataConstRef_size = ret_val
    end function LIBMUSCLE_DataConstRef_size

    function LIBMUSCLE_DataConstRef_as_logical(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        logical :: LIBMUSCLE_DataConstRef_as_logical

        integer (c_int) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_DataConstRef_as_logical_( &
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

        LIBMUSCLE_DataConstRef_as_logical = ret_val .ne. 0
    end function LIBMUSCLE_DataConstRef_as_logical

    function LIBMUSCLE_DataConstRef_as_character(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        character(:), allocatable :: LIBMUSCLE_DataConstRef_as_character

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

        call LIBMUSCLE_DataConstRef_as_character_( &
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
        allocate (character(ret_val_size) :: LIBMUSCLE_DataConstRef_as_character)
        do i_loop = 1, ret_val_size
            LIBMUSCLE_DataConstRef_as_character(i_loop:i_loop) = f_ret_ptr(i_loop)
        end do
    end function LIBMUSCLE_DataConstRef_as_character

    function LIBMUSCLE_DataConstRef_as_int(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        integer :: LIBMUSCLE_DataConstRef_as_int

        integer (c_int) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_DataConstRef_as_int_( &
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

        LIBMUSCLE_DataConstRef_as_int = ret_val
    end function LIBMUSCLE_DataConstRef_as_int

    function LIBMUSCLE_DataConstRef_as_int1(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        integer (LIBMUSCLE_int1) :: LIBMUSCLE_DataConstRef_as_int1

        integer (c_int8_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_DataConstRef_as_int1_( &
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

        LIBMUSCLE_DataConstRef_as_int1 = ret_val
    end function LIBMUSCLE_DataConstRef_as_int1

    function LIBMUSCLE_DataConstRef_as_int2(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        integer (selected_int_kind(4)) :: LIBMUSCLE_DataConstRef_as_int2

        integer (c_short) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_DataConstRef_as_int2_( &
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

        LIBMUSCLE_DataConstRef_as_int2 = ret_val
    end function LIBMUSCLE_DataConstRef_as_int2

    function LIBMUSCLE_DataConstRef_as_int4(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        integer (LIBMUSCLE_int4) :: LIBMUSCLE_DataConstRef_as_int4

        integer (c_int32_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_DataConstRef_as_int4_( &
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

        LIBMUSCLE_DataConstRef_as_int4 = ret_val
    end function LIBMUSCLE_DataConstRef_as_int4

    function LIBMUSCLE_DataConstRef_as_int8(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        integer (selected_int_kind(18)) :: LIBMUSCLE_DataConstRef_as_int8

        integer (c_int64_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_DataConstRef_as_int8_( &
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

        LIBMUSCLE_DataConstRef_as_int8 = ret_val
    end function LIBMUSCLE_DataConstRef_as_int8

    function LIBMUSCLE_DataConstRef_as_real4(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        real (LIBMUSCLE_real4) :: LIBMUSCLE_DataConstRef_as_real4

        real (c_float) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_DataConstRef_as_real4_( &
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

        LIBMUSCLE_DataConstRef_as_real4 = ret_val
    end function LIBMUSCLE_DataConstRef_as_real4

    function LIBMUSCLE_DataConstRef_as_real8(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        real (LIBMUSCLE_real8) :: LIBMUSCLE_DataConstRef_as_real8

        real (c_double) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_DataConstRef_as_real8_( &
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

        LIBMUSCLE_DataConstRef_as_real8 = ret_val
    end function LIBMUSCLE_DataConstRef_as_real8

    function LIBMUSCLE_DataConstRef_as_settings(self, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        type(YMMSL_Settings) :: LIBMUSCLE_DataConstRef_as_settings

        integer (c_intptr_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_DataConstRef_as_settings_( &
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

        LIBMUSCLE_DataConstRef_as_settings%ptr = ret_val
    end function LIBMUSCLE_DataConstRef_as_settings

    subroutine LIBMUSCLE_DataConstRef_as_byte_array(self, data, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
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

        call LIBMUSCLE_DataConstRef_as_byte_array_( &
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
    end subroutine LIBMUSCLE_DataConstRef_as_byte_array

    function LIBMUSCLE_DataConstRef_get_item_by_key(self, key, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        character (len=*), intent(in) :: key
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        type(LIBMUSCLE_DataConstRef) :: LIBMUSCLE_DataConstRef_get_item_by_key

        integer (c_intptr_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_DataConstRef_get_item_by_key_( &
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

        LIBMUSCLE_DataConstRef_get_item_by_key%ptr = ret_val
    end function LIBMUSCLE_DataConstRef_get_item_by_key

    function LIBMUSCLE_DataConstRef_get_item_by_index(self, i, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_DataConstRef), intent(in) :: self
        integer (LIBMUSCLE_size), intent(in) :: i
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        type(LIBMUSCLE_DataConstRef) :: LIBMUSCLE_DataConstRef_get_item_by_index

        integer (c_intptr_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_DataConstRef_get_item_by_index_( &
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

        LIBMUSCLE_DataConstRef_get_item_by_index%ptr = ret_val
    end function LIBMUSCLE_DataConstRef_get_item_by_index

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

    function LIBMUSCLE_Data_create_nils(size)
        implicit none
        integer (LIBMUSCLE_size), intent(in) :: size
        type(LIBMUSCLE_Data) :: LIBMUSCLE_Data_create_nils

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Data_create_nils_( &
            size)

        LIBMUSCLE_Data_create_nils%ptr = ret_val
    end function LIBMUSCLE_Data_create_nils

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

    function LIBMUSCLE_PortsDescription_create()
        implicit none
        type(LIBMUSCLE_PortsDescription) :: LIBMUSCLE_PortsDescription_create

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_PortsDescription_create_( &
    )

        LIBMUSCLE_PortsDescription_create%ptr = ret_val
    end function LIBMUSCLE_PortsDescription_create

    subroutine LIBMUSCLE_PortsDescription_free(self)
        implicit none
        type(LIBMUSCLE_PortsDescription), intent(in) :: self

        call LIBMUSCLE_PortsDescription_free_( &
            self%ptr)
    end subroutine LIBMUSCLE_PortsDescription_free

    subroutine LIBMUSCLE_PortsDescription_add(self, op, port)
        implicit none
        type(LIBMUSCLE_PortsDescription), intent(in) :: self
        integer(YMMSL_Operator), intent(in) :: op
        character (len=*), intent(in) :: port

        call LIBMUSCLE_PortsDescription_add_( &
            self%ptr, &
            op, &
            port, int(len(port), c_size_t))
    end subroutine LIBMUSCLE_PortsDescription_add

    function LIBMUSCLE_PortsDescription_num_ports(self, op)
        implicit none
        type(LIBMUSCLE_PortsDescription), intent(in) :: self
        integer(YMMSL_Operator), intent(in) :: op
        integer (LIBMUSCLE_size) :: LIBMUSCLE_PortsDescription_num_ports

        integer (c_size_t) :: ret_val

        ret_val = LIBMUSCLE_PortsDescription_num_ports_( &
            self%ptr, &
            op)
        LIBMUSCLE_PortsDescription_num_ports = ret_val
    end function LIBMUSCLE_PortsDescription_num_ports

    function LIBMUSCLE_PortsDescription_get(self, op, i, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_PortsDescription), intent(in) :: self
        integer(YMMSL_Operator), intent(in) :: op
        integer (LIBMUSCLE_size), intent(in) :: i
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        character(:), allocatable :: LIBMUSCLE_PortsDescription_get

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

        call LIBMUSCLE_PortsDescription_get_( &
            self%ptr, &
            op, &
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
        allocate (character(ret_val_size) :: LIBMUSCLE_PortsDescription_get)
        do i_loop = 1, ret_val_size
            LIBMUSCLE_PortsDescription_get(i_loop:i_loop) = f_ret_ptr(i_loop)
        end do
    end function LIBMUSCLE_PortsDescription_get

    function LIBMUSCLE_Message_create_td(timestamp, data)
        implicit none
        real (LIBMUSCLE_real8), intent(in) :: timestamp
        type(LIBMUSCLE_Data), intent(in) :: data
        type(LIBMUSCLE_Message) :: LIBMUSCLE_Message_create_td

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Message_create_td_( &
            timestamp, &
            data%ptr)

        LIBMUSCLE_Message_create_td%ptr = ret_val
    end function LIBMUSCLE_Message_create_td

    function LIBMUSCLE_Message_create_tnd(timestamp, next_timestamp, data)
        implicit none
        real (LIBMUSCLE_real8), intent(in) :: timestamp
        real (LIBMUSCLE_real8), intent(in) :: next_timestamp
        type(LIBMUSCLE_Data), intent(in) :: data
        type(LIBMUSCLE_Message) :: LIBMUSCLE_Message_create_tnd

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Message_create_tnd_( &
            timestamp, &
            next_timestamp, &
            data%ptr)

        LIBMUSCLE_Message_create_tnd%ptr = ret_val
    end function LIBMUSCLE_Message_create_tnd

    function LIBMUSCLE_Message_create_tds(timestamp, data, settings)
        implicit none
        real (LIBMUSCLE_real8), intent(in) :: timestamp
        type(LIBMUSCLE_Data), intent(in) :: data
        type(YMMSL_Settings), intent(in) :: settings
        type(LIBMUSCLE_Message) :: LIBMUSCLE_Message_create_tds

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Message_create_tds_( &
            timestamp, &
            data%ptr, &
            settings%ptr)

        LIBMUSCLE_Message_create_tds%ptr = ret_val
    end function LIBMUSCLE_Message_create_tds

    function LIBMUSCLE_Message_create_tnds(timestamp, next_timestamp, data, settings)
        implicit none
        real (LIBMUSCLE_real8), intent(in) :: timestamp
        real (LIBMUSCLE_real8), intent(in) :: next_timestamp
        type(LIBMUSCLE_Data), intent(in) :: data
        type(YMMSL_Settings), intent(in) :: settings
        type(LIBMUSCLE_Message) :: LIBMUSCLE_Message_create_tnds

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Message_create_tnds_( &
            timestamp, &
            next_timestamp, &
            data%ptr, &
            settings%ptr)

        LIBMUSCLE_Message_create_tnds%ptr = ret_val
    end function LIBMUSCLE_Message_create_tnds

    subroutine LIBMUSCLE_Message_free(self)
        implicit none
        type(LIBMUSCLE_Message), intent(in) :: self

        call LIBMUSCLE_Message_free_( &
            self%ptr)
    end subroutine LIBMUSCLE_Message_free

    function LIBMUSCLE_Message_timestamp(self)
        implicit none
        type(LIBMUSCLE_Message), intent(in) :: self
        real (LIBMUSCLE_real8) :: LIBMUSCLE_Message_timestamp

        real (c_double) :: ret_val

        ret_val = LIBMUSCLE_Message_timestamp_( &
            self%ptr)
        LIBMUSCLE_Message_timestamp = ret_val
    end function LIBMUSCLE_Message_timestamp

    subroutine LIBMUSCLE_Message_set_timestamp(self, timestamp)
        implicit none
        type(LIBMUSCLE_Message), intent(in) :: self
        real (LIBMUSCLE_real8), intent(in) :: timestamp

        call LIBMUSCLE_Message_set_timestamp_( &
            self%ptr, &
            timestamp)
    end subroutine LIBMUSCLE_Message_set_timestamp

    function LIBMUSCLE_Message_has_next_timestamp(self)
        implicit none
        type(LIBMUSCLE_Message), intent(in) :: self
        logical :: LIBMUSCLE_Message_has_next_timestamp

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Message_has_next_timestamp_( &
            self%ptr)

        LIBMUSCLE_Message_has_next_timestamp = ret_val .ne. 0
    end function LIBMUSCLE_Message_has_next_timestamp

    function LIBMUSCLE_Message_next_timestamp(self)
        implicit none
        type(LIBMUSCLE_Message), intent(in) :: self
        real (LIBMUSCLE_real8) :: LIBMUSCLE_Message_next_timestamp

        real (c_double) :: ret_val

        ret_val = LIBMUSCLE_Message_next_timestamp_( &
            self%ptr)
        LIBMUSCLE_Message_next_timestamp = ret_val
    end function LIBMUSCLE_Message_next_timestamp

    subroutine LIBMUSCLE_Message_set_next_timestamp(self, next_timestamp)
        implicit none
        type(LIBMUSCLE_Message), intent(in) :: self
        real (LIBMUSCLE_real8), intent(in) :: next_timestamp

        call LIBMUSCLE_Message_set_next_timestamp_( &
            self%ptr, &
            next_timestamp)
    end subroutine LIBMUSCLE_Message_set_next_timestamp

    subroutine LIBMUSCLE_Message_unset_next_timestamp(self)
        implicit none
        type(LIBMUSCLE_Message), intent(in) :: self

        call LIBMUSCLE_Message_unset_next_timestamp_( &
            self%ptr)
    end subroutine LIBMUSCLE_Message_unset_next_timestamp

    function LIBMUSCLE_Message_get_data(self)
        implicit none
        type(LIBMUSCLE_Message), intent(in) :: self
        type(LIBMUSCLE_DataConstRef) :: LIBMUSCLE_Message_get_data

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Message_get_data_( &
            self%ptr)

        LIBMUSCLE_Message_get_data%ptr = ret_val
    end function LIBMUSCLE_Message_get_data

    subroutine LIBMUSCLE_Message_set_data_d(self, data)
        implicit none
        type(LIBMUSCLE_Message), intent(in) :: self
        type(LIBMUSCLE_Data), intent(in) :: data

        call LIBMUSCLE_Message_set_data_d_( &
            self%ptr, &
            data%ptr)
    end subroutine LIBMUSCLE_Message_set_data_d

    subroutine LIBMUSCLE_Message_set_data_dcr(self, data)
        implicit none
        type(LIBMUSCLE_Message), intent(in) :: self
        type(LIBMUSCLE_DataConstRef), intent(in) :: data

        call LIBMUSCLE_Message_set_data_dcr_( &
            self%ptr, &
            data%ptr)
    end subroutine LIBMUSCLE_Message_set_data_dcr

    function LIBMUSCLE_Message_has_settings(self)
        implicit none
        type(LIBMUSCLE_Message), intent(in) :: self
        logical :: LIBMUSCLE_Message_has_settings

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Message_has_settings_( &
            self%ptr)

        LIBMUSCLE_Message_has_settings = ret_val .ne. 0
    end function LIBMUSCLE_Message_has_settings

    function LIBMUSCLE_Message_get_settings(self)
        implicit none
        type(LIBMUSCLE_Message), intent(in) :: self
        type(YMMSL_Settings) :: LIBMUSCLE_Message_get_settings

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Message_get_settings_( &
            self%ptr)

        LIBMUSCLE_Message_get_settings%ptr = ret_val
    end function LIBMUSCLE_Message_get_settings

    subroutine LIBMUSCLE_Message_set_settings(self, settings)
        implicit none
        type(LIBMUSCLE_Message), intent(in) :: self
        type(YMMSL_Settings), intent(in) :: settings

        call LIBMUSCLE_Message_set_settings_( &
            self%ptr, &
            settings%ptr)
    end subroutine LIBMUSCLE_Message_set_settings

    subroutine LIBMUSCLE_Message_unset_settings(self)
        implicit none
        type(LIBMUSCLE_Message), intent(in) :: self

        call LIBMUSCLE_Message_unset_settings_( &
            self%ptr)
    end subroutine LIBMUSCLE_Message_unset_settings

    type(LIBMUSCLE_Instance) function LIBMUSCLE_Instance_create_autoports()
        implicit none

        integer :: num_args, i, arg_len
        integer (c_intptr_t) :: cla
        character (kind=c_char, len=:), allocatable :: cur_arg

        num_args = command_argument_count()
        cla = LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create_(num_args + 1)
        do i = 0, num_args
            call get_Command_argument(i, length=arg_len)
            allocate (character(arg_len+1) :: cur_arg)
            call get_command_argument(i, value=cur_arg)
            cur_arg(arg_len+1:arg_len+1) = c_null_char
            call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_set_arg_( &
                   cla, i, cur_arg, int(len(cur_arg), c_size_t))
            deallocate(cur_arg)
        end do
        LIBMUSCLE_Instance_create_autoports%ptr = &
            LIBMUSCLE_Instance_create_autoports_(cla)
        call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_free_(cla)
    end function LIBMUSCLE_Instance_create_autoports

    type(LIBMUSCLE_Instance) function LIBMUSCLE_Instance_create_with_ports(ports)
        implicit none

        type(LIBMUSCLE_PortsDescription) :: ports
        integer :: num_args, i, arg_len
        integer (c_intptr_t) :: cla
        character (kind=c_char, len=:), allocatable :: cur_arg

        num_args = command_argument_count()
        cla = LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create_(num_args + 1)
        do i = 0, num_args
            call get_Command_argument(i, length=arg_len)
            allocate (character(arg_len+1) :: cur_arg)
            call get_command_argument(i, value=cur_arg)
            cur_arg(arg_len+1:arg_len+1) = c_null_char
            call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_set_arg_( &
                   cla, i, cur_arg, int(len(cur_arg), c_size_t))
            deallocate(cur_arg)
        end do
        LIBMUSCLE_Instance_create_with_ports%ptr = LIBMUSCLE_Instance_create_with_ports_(cla, ports%ptr)
        call LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_free_(cla)
    end function LIBMUSCLE_Instance_create_with_ports

    subroutine LIBMUSCLE_Instance_free(self)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self

        call LIBMUSCLE_Instance_free_( &
            self%ptr)
    end subroutine LIBMUSCLE_Instance_free

    function LIBMUSCLE_Instance_reuse_instance_default(self)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        logical :: LIBMUSCLE_Instance_reuse_instance_default

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Instance_reuse_instance_default_( &
            self%ptr)

        LIBMUSCLE_Instance_reuse_instance_default = ret_val .ne. 0
    end function LIBMUSCLE_Instance_reuse_instance_default

    function LIBMUSCLE_Instance_reuse_instance_apply(self, apply_overlay)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        logical, intent(in) :: apply_overlay
        logical :: LIBMUSCLE_Instance_reuse_instance_apply

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Instance_reuse_instance_apply_( &
            self%ptr, &
            merge(1, 0, apply_overlay))

        LIBMUSCLE_Instance_reuse_instance_apply = ret_val .ne. 0
    end function LIBMUSCLE_Instance_reuse_instance_apply

    subroutine LIBMUSCLE_Instance_error_shutdown(self, message)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: message

        call LIBMUSCLE_Instance_error_shutdown_( &
            self%ptr, &
            message, int(len(message), c_size_t))
    end subroutine LIBMUSCLE_Instance_error_shutdown

    function LIBMUSCLE_Instance_get_setting_as_character(self, name, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: name
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        character(:), allocatable :: LIBMUSCLE_Instance_get_setting_as_character

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

        call LIBMUSCLE_Instance_get_setting_as_character_( &
            self%ptr, &
            name, int(len(name), c_size_t), &
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
        allocate (character(ret_val_size) :: LIBMUSCLE_Instance_get_setting_as_character)
        do i_loop = 1, ret_val_size
            LIBMUSCLE_Instance_get_setting_as_character(i_loop:i_loop) = f_ret_ptr(i_loop)
        end do
    end function LIBMUSCLE_Instance_get_setting_as_character

    function LIBMUSCLE_Instance_get_setting_as_int8(self, name, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: name
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        integer (selected_int_kind(18)) :: LIBMUSCLE_Instance_get_setting_as_int8

        integer (c_int64_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Instance_get_setting_as_int8_( &
            self%ptr, &
            name, int(len(name), c_size_t), &
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

        LIBMUSCLE_Instance_get_setting_as_int8 = ret_val
    end function LIBMUSCLE_Instance_get_setting_as_int8

    function LIBMUSCLE_Instance_get_setting_as_real8(self, name, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: name
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        real (LIBMUSCLE_real8) :: LIBMUSCLE_Instance_get_setting_as_real8

        real (c_double) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Instance_get_setting_as_real8_( &
            self%ptr, &
            name, int(len(name), c_size_t), &
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

        LIBMUSCLE_Instance_get_setting_as_real8 = ret_val
    end function LIBMUSCLE_Instance_get_setting_as_real8

    function LIBMUSCLE_Instance_get_setting_as_logical(self, name, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: name
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        logical :: LIBMUSCLE_Instance_get_setting_as_logical

        integer (c_int) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Instance_get_setting_as_logical_( &
            self%ptr, &
            name, int(len(name), c_size_t), &
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

        LIBMUSCLE_Instance_get_setting_as_logical = ret_val .ne. 0
    end function LIBMUSCLE_Instance_get_setting_as_logical

    subroutine LIBMUSCLE_Instance_get_setting_as_real8array(self, name, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: name
        real (LIBMUSCLE_real8), dimension(:), intent(out) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        type (c_ptr) :: ret_val
        integer (c_size_t) :: ret_val_size
        real (LIBMUSCLE_real8), pointer, dimension(:) :: f_ret_ptr
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Instance_get_setting_as_real8array_( &
            self%ptr, &
            name, int(len(name), c_size_t), &
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
    end subroutine LIBMUSCLE_Instance_get_setting_as_real8array

    subroutine LIBMUSCLE_Instance_get_setting_as_real8array2(self, name, value, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: name
        real (LIBMUSCLE_real8), dimension(:,:), intent(out) :: value
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg

        type (c_ptr) :: ret_val
        integer (c_size_t), dimension(2) :: ret_val_shape
        real (LIBMUSCLE_real8), pointer, dimension(:,:) :: f_ret_ptr
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        call LIBMUSCLE_Instance_get_setting_as_real8array2_( &
            self%ptr, &
            name, int(len(name), c_size_t), &
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
    end subroutine LIBMUSCLE_Instance_get_setting_as_real8array2

    function LIBMUSCLE_Instance_list_ports(self)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        type(LIBMUSCLE_PortsDescription) :: LIBMUSCLE_Instance_list_ports

        integer (c_intptr_t) :: ret_val

        ret_val = LIBMUSCLE_Instance_list_ports_( &
            self%ptr)

        LIBMUSCLE_Instance_list_ports%ptr = ret_val
    end function LIBMUSCLE_Instance_list_ports

    function LIBMUSCLE_Instance_is_connected(self, port)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: port
        logical :: LIBMUSCLE_Instance_is_connected

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Instance_is_connected_( &
            self%ptr, &
            port, int(len(port), c_size_t))

        LIBMUSCLE_Instance_is_connected = ret_val .ne. 0
    end function LIBMUSCLE_Instance_is_connected

    function LIBMUSCLE_Instance_is_vector_port(self, port)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: port
        logical :: LIBMUSCLE_Instance_is_vector_port

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Instance_is_vector_port_( &
            self%ptr, &
            port, int(len(port), c_size_t))

        LIBMUSCLE_Instance_is_vector_port = ret_val .ne. 0
    end function LIBMUSCLE_Instance_is_vector_port

    function LIBMUSCLE_Instance_is_resizable(self, port)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: port
        logical :: LIBMUSCLE_Instance_is_resizable

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Instance_is_resizable_( &
            self%ptr, &
            port, int(len(port), c_size_t))

        LIBMUSCLE_Instance_is_resizable = ret_val .ne. 0
    end function LIBMUSCLE_Instance_is_resizable

    function LIBMUSCLE_Instance_get_port_length(self, port)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: port
        integer :: LIBMUSCLE_Instance_get_port_length

        integer (c_int) :: ret_val

        ret_val = LIBMUSCLE_Instance_get_port_length_( &
            self%ptr, &
            port, int(len(port), c_size_t))
        LIBMUSCLE_Instance_get_port_length = ret_val
    end function LIBMUSCLE_Instance_get_port_length

    subroutine LIBMUSCLE_Instance_set_port_length(self, port, length)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: port
        integer, intent(in) :: length

        call LIBMUSCLE_Instance_set_port_length_( &
            self%ptr, &
            port, int(len(port), c_size_t), &
            length)
    end subroutine LIBMUSCLE_Instance_set_port_length

    subroutine LIBMUSCLE_Instance_send_pm(self, port_name, message)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: port_name
        type(LIBMUSCLE_Message), intent(in) :: message

        call LIBMUSCLE_Instance_send_pm_( &
            self%ptr, &
            port_name, int(len(port_name), c_size_t), &
            message%ptr)
    end subroutine LIBMUSCLE_Instance_send_pm

    subroutine LIBMUSCLE_Instance_send_pms(self, port_name, message, slot)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: port_name
        type(LIBMUSCLE_Message), intent(in) :: message
        integer, intent(in) :: slot

        call LIBMUSCLE_Instance_send_pms_( &
            self%ptr, &
            port_name, int(len(port_name), c_size_t), &
            message%ptr, &
            slot)
    end subroutine LIBMUSCLE_Instance_send_pms

    function LIBMUSCLE_Instance_receive_p(self, port_name, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: port_name
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        type(LIBMUSCLE_Message) :: LIBMUSCLE_Instance_receive_p

        integer (c_intptr_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Instance_receive_p_( &
            self%ptr, &
            port_name, int(len(port_name), c_size_t), &
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

        LIBMUSCLE_Instance_receive_p%ptr = ret_val
    end function LIBMUSCLE_Instance_receive_p

    function LIBMUSCLE_Instance_receive_pd(self, port_name, default_msg, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: port_name
        type(LIBMUSCLE_Message), intent(in) :: default_msg
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        type(LIBMUSCLE_Message) :: LIBMUSCLE_Instance_receive_pd

        integer (c_intptr_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Instance_receive_pd_( &
            self%ptr, &
            port_name, int(len(port_name), c_size_t), &
            default_msg%ptr, &
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

        LIBMUSCLE_Instance_receive_pd%ptr = ret_val
    end function LIBMUSCLE_Instance_receive_pd

    function LIBMUSCLE_Instance_receive_ps(self, port_name, slot, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: port_name
        integer, intent(in) :: slot
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        type(LIBMUSCLE_Message) :: LIBMUSCLE_Instance_receive_ps

        integer (c_intptr_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Instance_receive_ps_( &
            self%ptr, &
            port_name, int(len(port_name), c_size_t), &
            slot, &
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

        LIBMUSCLE_Instance_receive_ps%ptr = ret_val
    end function LIBMUSCLE_Instance_receive_ps

    function LIBMUSCLE_Instance_receive_psd(self, port_name, slot, default_message, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: port_name
        integer, intent(in) :: slot
        type(LIBMUSCLE_Message), intent(in) :: default_message
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        type(LIBMUSCLE_Message) :: LIBMUSCLE_Instance_receive_psd

        integer (c_intptr_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Instance_receive_psd_( &
            self%ptr, &
            port_name, int(len(port_name), c_size_t), &
            slot, &
            default_message%ptr, &
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

        LIBMUSCLE_Instance_receive_psd%ptr = ret_val
    end function LIBMUSCLE_Instance_receive_psd

    function LIBMUSCLE_Instance_receive_with_settings_p(self, port_name, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: port_name
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        type(LIBMUSCLE_Message) :: LIBMUSCLE_Instance_receive_with_settings_p

        integer (c_intptr_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Instance_receive_with_settings_p_( &
            self%ptr, &
            port_name, int(len(port_name), c_size_t), &
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

        LIBMUSCLE_Instance_receive_with_settings_p%ptr = ret_val
    end function LIBMUSCLE_Instance_receive_with_settings_p

    function LIBMUSCLE_Instance_receive_with_settings_pd(self, port_name, default_msg, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: port_name
        type(LIBMUSCLE_Message), intent(in) :: default_msg
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        type(LIBMUSCLE_Message) :: LIBMUSCLE_Instance_receive_with_settings_pd

        integer (c_intptr_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Instance_receive_with_settings_pd_( &
            self%ptr, &
            port_name, int(len(port_name), c_size_t), &
            default_msg%ptr, &
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

        LIBMUSCLE_Instance_receive_with_settings_pd%ptr = ret_val
    end function LIBMUSCLE_Instance_receive_with_settings_pd

    function LIBMUSCLE_Instance_receive_with_settings_ps(self, port_name, slot, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: port_name
        integer, intent(in) :: slot
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        type(LIBMUSCLE_Message) :: LIBMUSCLE_Instance_receive_with_settings_ps

        integer (c_intptr_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Instance_receive_with_settings_ps_( &
            self%ptr, &
            port_name, int(len(port_name), c_size_t), &
            slot, &
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

        LIBMUSCLE_Instance_receive_with_settings_ps%ptr = ret_val
    end function LIBMUSCLE_Instance_receive_with_settings_ps

    function LIBMUSCLE_Instance_receive_with_settings_psd(self, port_name, slot, default_msg, err_code, err_msg)
        implicit none
        type(LIBMUSCLE_Instance), intent(in) :: self
        character (len=*), intent(in) :: port_name
        integer, intent(in) :: slot
        type(LIBMUSCLE_Message), intent(in) :: default_msg
        integer, optional, intent(out) :: err_code
        character(:), allocatable, optional, intent(out) :: err_msg
        type(LIBMUSCLE_Message) :: LIBMUSCLE_Instance_receive_with_settings_psd

        integer (c_intptr_t) :: ret_val
        integer (c_int) :: err_code_v
        type (c_ptr) :: err_msg_v
        integer (c_size_t) :: err_msg_len_v
        character (c_char), dimension(:), pointer :: err_msg_f
        character(:), allocatable :: err_msg_p
        integer (c_size_t) :: err_msg_i

        ret_val = LIBMUSCLE_Instance_receive_with_settings_psd_( &
            self%ptr, &
            port_name, int(len(port_name), c_size_t), &
            slot, &
            default_msg%ptr, &
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

        LIBMUSCLE_Instance_receive_with_settings_psd%ptr = ret_val
    end function LIBMUSCLE_Instance_receive_with_settings_psd


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

