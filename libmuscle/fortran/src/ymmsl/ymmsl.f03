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


end module ymmsl

