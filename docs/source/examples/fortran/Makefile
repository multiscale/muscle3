FC ?= gfortran
MPIFC ?= mpigfortran
FFLAGS += -std=f2003 -g -I$(MUSCLE3_HOME)/include

MPI_LDFLAGS := $(LDFLAGS) -L$(MUSCLE3_HOME)/lib -lymmsl -lmuscle_mpi -lmpi
LDFLAGS := -L$(MUSCLE3_HOME)/lib -lymmsl_fortran -lmuscle_fortran -lymmsl -lmuscle


binaries := reaction diffusion mc_driver load_balancer
mpi_binaries := reaction_mpi

ifdef MUSCLE_ENABLE_MPI
    binaries += mpi_binaries
endif


.PHONY: all
all: $(binaries)

.PHONY: clean
clean:
	rm -f $(binaries) $(mpi_binaries)


%: %.f03
	LD_LIBRARY_PATH=$(MUSCLE3_HOME)/lib:$(LD_LIBRARY_PATH) $(FC) $(FFLAGS) -o $@ $^ $(LDFLAGS)

reaction_mpi: reaction_mpi.f03
	LD_LIBRARY_PATH=$(MUSCLE3_HOME)/lib:$(LD_LIBRARY_PATH) $(MPIFC) $(FCFLAGS) -o $@ $^ $(MPI_LDFLAGS)

