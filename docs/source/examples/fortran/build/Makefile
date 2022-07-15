FFLAGS += -std=f2003 -g $(shell pkg-config --cflags libmuscle_fortran ymmsl_fortran)
LDFLAGS := $(shell pkg-config --libs libmuscle_fortran ymmsl_fortran)

MPI_FFLAGS := -std=f2003 -g $(shell pkg-config --cflags libmuscle_mpi_fortran ymmsl_fortran)
MPI_LDFLAGS := $(shell pkg-config --libs libmuscle_mpi_fortran ymmsl_fortran)


binaries := reaction diffusion mc_driver load_balancer
mpi_binaries := reaction_mpi


.PHONY: all
all: $(binaries)

.PHONY: mpi
mpi: $(mpi_binaries)

.PHONY: clean
clean:
	rm -f $(binaries) $(mpi_binaries)


%: ../%.f90
	$(FC) $(FFLAGS) -o $@ $^ $(LDFLAGS)

%_mpi: ../%_mpi.f90
	$(MPIFC) $(MPI_FFLAGS) -o $@ $^ $(MPI_LDFLAGS)

