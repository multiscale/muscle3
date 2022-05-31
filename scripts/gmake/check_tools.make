# Make module that verifies that we have all needed tools
$(info )

# Output some information about the environment
$(info Environment information:)

$(info Variables:)
$(info $(.VARIABLES))
$(info )
$(info Make invocation: $(MAKE))
$(info Make command goals: $(MAKECMDGOALS))
$(info Make flags: $(MAKEFLAGS))
$(info )

# Check Python version
$(info Looking for Python...)
_python_version := $(shell python3 --version || echo NOTFOUND)
ifneq ($(_python_version), NOTFOUND)
    $(info - Found Python version $(_python_version))
else
    $(info - Python 3 not found)
endif

# Check C++ compiler
$(info )
$(info Looking for C++ compiler...)
tool_var := CXX
include $(TOOLDIR)/check_override.make

tool_command := g++
include $(TOOLDIR)/detect_tool_implicit.make
tool_command := clang++
include $(TOOLDIR)/detect_tool_implicit.make

ifndef CXX
    $(error - No C++ compiler found! Please install either gcc or clang.)
else
    $(info - Will compile C++ files using $(CXX).)
endif

# Check MPI C++ compiler, and enable MPI if found
$(info )
$(info Looking for MPI C++ compiler...)
tool_var := MPICXX
include $(TOOLDIR)/check_override.make

tool_command := mpi$(CXX)
include $(TOOLDIR)/detect_tool.make
tool_command := mpic++
include $(TOOLDIR)/detect_tool.make

ifndef MPICXX
    $(info - No MPI C++ compiler found! Maybe there's no MPI installed?)
    $(info - Building without MPI support)
else
    $(info - Will compile MPI C++ files using $(MPICXX).)
    export MUSCLE_ENABLE_CPP_MPI := 1
endif

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
    $(info - Not building Fortran MPI bindings.)
else
    $(info - Will compile MPI Fortran files using $(MPIFC).)
    export MUSCLE_ENABLE_FORTRAN_MPI := 1
endif

# Check download tool (for downloading dependencies)
$(info )
$(info Looking for download tool...)
tool_var := DOWNLOAD
include $(TOOLDIR)/check_override.make

tool_command := wget
include $(TOOLDIR)/detect_tool.make
tool_command := curl
include $(TOOLDIR)/detect_tool.make

ifeq ($(DOWNLOAD), curl)
    export DOWNLOAD := curl -LO
endif

ifndef DOWNLOAD
    $(warning - Could not find either wget or curl, so I won't be able to download dependencies.)
    $(warning - To fix this, install wget or curl, or set DOWNLOAD to a command that can download http links.)
else
    $(info - Will download files using $(DOWNLOAD).)
endif

# Check tar tool (for unpacking dependencies)
$(info )
$(info Looking for tar...)
tool_var := TAR
include $(TOOLDIR)/check_override.make

tool_command := tar
include $(TOOLDIR)/detect_tool.make

ifndef TAR
    $(warning - Could not find tar, so I won't be able to unpack dependencies.)
    $(warning - To fix this, set TAR to a command that can extract tar archives.)
else
    $(info - Will extract archives using $(TAR).)
endif

# Check for valgrind (for testing for memory leaks)
$(info )
$(info Looking for valgrind...)
tool_var := VALGRIND
include $(TOOLDIR)/check_override.make

tool_command := valgrind
include $(TOOLDIR)/detect_tool.make

ifeq ($(VALGRIND), valgrind)
    export VALGRIND := valgrind --leak-check=full --error-exitcode=1
endif

ifndef VALGRIND
    $(warning - Could not find valgrind, so tests will run without it.)
    $(warning - To fix this, install valgrind and if necessary set VALGRIND to point to it.)
else
    $(info - Will check for leaks using $(VALGRIND).)
endif

# Check number of cores
ifndef NCORES
    NCORES := $(shell nproc 2>/dev/null || echo 2)
    export NCORES
endif
$(info )
$(info Using $(NCORES) cores to build; set NCORES to override.)
$(info )
