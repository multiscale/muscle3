# Make module that verifies that we have all needed tools

# Check Fortran compiler
$(info )
$(info Looking for Fortran compiler...)
tool_var := FC
include $(TOOLDIR)/check_override.make

tool_command := gfortran
include $(TOOLDIR)/detect_tool_implicit.make
tool_command := f95
include $(TOOLDIR)/detect_tool_implicit.make
tool_command := f77
include $(TOOLDIR)/detect_tool_implicit.make

ifeq ($(origin FC), default)
    $(info - No Fortran compiler found! Please install gfortran.)
    $(info - Not building Fortran bindings.)
    export MUSCLE_DISABLE_FORTRAN := 1
else
    $(info - Will compile Fortran files using $(FC).)
endif

# Check MPI Fortran compiler
ifdef MUSCLE_ENABLE_MPI
    $(info )
    $(info Looking for MPI Fortran compiler...)
    tool_var := MPIFC
    include $(TOOLDIR)/check_override.make

    tool_command := mpi$(FC)
    include $(TOOLDIR)/detect_tool.make
    tool_command := mpifort
    include $(TOOLDIR)/detect_tool.make
    tool_command := mpif90
    include $(TOOLDIR)/detect_tool.make

    ifndef MPIFC
        $(info - No MPI Fortran compiler found!)
        $(info - Not building Fortran bindings.)
        export MUSCLE_DISABLE_FORTRAN := 1
    else
        $(info - Will compile MPI Fortran files using $(MPIFC).)
    endif
endif

# Check number of cores
ifndef NCORES
    NCORES := $(shell nproc 2>/dev/null || echo 2)
    export NCORES
endif
$(info )
$(info Using $(NCORES) cores to build; set NCORES to override.)
$(info )
