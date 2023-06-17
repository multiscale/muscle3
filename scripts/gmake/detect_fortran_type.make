
ifndef MUSCLE_DISABLE_FORTRAN

    $(info )

    ifeq ($(shell $(FC) --version | grep -q GNU && echo FOUND),FOUND)
        MUSCLE_FC_GNU := 1
        export MUSCLE_FC_GNU
        $(info Fortran compiler detected as GNU)
    else ifeq ($(shell $(FC) --version | grep -q -i clang && echo FOUND),FOUND)
        MUSCLE_FC_CLANG := 1
        export MUSCLE_FC_CLANG
        $(info Fortran compiler detected as Clang)
    else ifeq ($(shell $(FC) --version | grep -q -i Intel && echo FOUND),FOUND)
        MUSCLE_FC_INTEL := 1
        export MUSCLE_FC_INTEL
        $(info Fortran compiler detected as Intel)
    else ifeq ($(shell $(FC) --version | grep -q -i Cray && echo FOUND),FOUND)
        MUSCLE_FC_CRAY := 1
        export MUSCLE_FC_CRAY
        $(info Fortran compiler detected as Cray)
    else
        MUSCLE_FC_GNU := 1
        export MUSCLE_FC_GNU
        $(info Fortran compiler type could not be detected, trying GNU)
        $(info Please report an issue, and include this:)
        $(info $(shell $(FC) --version))
    endif

endif

