ifeq "$(filter $(MAKECMDGOALS), clean)" ""

FC ?= gfortran
FFLAGS += -std=f2003 -g $(shell pkg-config --cflags libmuscle_fortran ymmsl_fortran)
LDFLAGS := $(shell pkg-config --libs libmuscle_fortran ymmsl_fortran)

ifdef MUSCLE_ENABLE_FORTRAN_MPI
    MPIFC ?= mpifort
    MPI_FFLAGS := -std=f2003 -g $(shell pkg-config --cflags libmuscle_mpi_fortran ymmsl_fortran)
    MPI_LDFLAGS := $(shell pkg-config --libs libmuscle_mpi_fortran ymmsl_fortran)
endif

endif

binaries := reaction diffusion mc_driver load_balancer
mpi_binaries := reaction_mpi

ifdef MUSCLE_ENABLE_FORTRAN_MPI
    binaries += $(mpi_binaries)
endif


.PHONY: all
all: $(binaries)

.PHONY: clean
clean:
	rm -f $(binaries) $(mpi_binaries)


%: ../%.f03
	$(FC) $(FFLAGS) -o $@ $^ $(LDFLAGS)

%_mpi: ../%_mpi.f03
	$(MPIFC) $(MPI_FFLAGS) -o $@ $^ $(MPI_LDFLAGS)

