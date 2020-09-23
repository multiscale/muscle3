CXX ?= g++
CXXFLAGS += -std=c++14 -g $(shell pkg-config --cflags libmuscle ymmsl)
LDFLAGS += $(shell pkg-config --libs libmuscle ymmsl)

ifdef MUSCLE_ENABLE_MPI
    MPICXX := mpic++
    MPI_CXXFLAGS := -std=c++14 -g $(shell pkg-config --cflags libmuscle_mpi ymmsl)
    MPI_LDFLAGS := $(LDFLAGS) $(shell pkg-config --libs libmuscle_mpi ymmsl)
endif


binaries := reaction diffusion mc_driver load_balancer
mpi_binaries := reaction_mpi

ifdef MUSCLE_ENABLE_MPI
    binaries += $(mpi_binaries)
endif


.PHONY: all
all: $(binaries)

.PHONY: clean
clean:
	rm -f $(binaries) $(mpi_binaries)


%: ../%.cpp
	LD_LIBRARY_PATH=$(MUSCLE3_HOME)/lib:$(LD_LIBRARY_PATH) $(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

%_mpi: ../%_mpi.cpp
	LD_LIBRARY_PATH=$(MUSCLE3_HOME)/lib:$(LD_LIBRARY_PATH) $(MPICXX) $(MPI_CXXFLAGS) -o $@ $^ $(MPI_LDFLAGS)

