FFLAGS += -g $(shell pkg-config --cflags libmuscle_fortran ymmsl_fortran)
LDFLAGS += $(shell pkg-config --libs libmuscle_fortran ymmsl_fortran)

MPI_FFLAGS += -g $(shell pkg-config --cflags libmuscle_mpi_fortran ymmsl_fortran)
MPI_LDFLAGS += $(shell pkg-config --libs libmuscle_mpi_fortran ymmsl_fortran)

ifdef MUSCLE_FC_INTEL
    FFLAGS += -e03
else ifdef MUSCLE_FC_GNU
    FFLAGS += -std=f2003
else ifdef MUSCLE_FC_CLANG
    FFLAGS += -std=f2003
endif

ifdef MUSCLE_FC_INTEL
    MPI_FFLAGS += -e03
else ifdef MUSCLE_FC_GNU
    MPI_FFLAGS += -std=f2003
else ifdef MUSCLE_FC_CLANG
    MPI_FFLAGS += -std=f2003
endif


binaries := reaction diffusion mc_driver load_balancer checkpointing_reaction checkpointing_diffusion
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

