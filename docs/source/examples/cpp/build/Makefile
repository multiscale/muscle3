ifeq "$(filter $(MAKECMDGOALS), clean)" ""

CXX ?= g++
CXXFLAGS += -std=c++14 -g $(shell pkg-config --cflags libmuscle ymmsl)
LDFLAGS += $(shell pkg-config --libs libmuscle ymmsl)

ifdef MUSCLE_ENABLE_CPP_MPI
    MPICXX := mpic++
    MPI_CXXFLAGS := -std=c++14 -g $(shell pkg-config --cflags libmuscle_mpi ymmsl)
    MPI_LDFLAGS := $(shell pkg-config --libs libmuscle_mpi ymmsl)
endif

endif

binaries := reaction diffusion mc_driver load_balancer
mpi_binaries := reaction_mpi

ifdef MUSCLE_ENABLE_CPP_MPI
    binaries += $(mpi_binaries)
endif


.PHONY: all
all: $(binaries)

.PHONY: clean
clean:
	rm -f $(binaries) $(mpi_binaries)


%_mpi.o: ../%_mpi.cpp
	$(MPICXX) -c $(MPI_CXXFLAGS) -o $@ $^

%_mpi: %_mpi.o
	$(MPICXX) -o $@ $^ $(MPI_LDFLAGS)

%.o: ../%.cpp
	$(CXX) -c $(CXXFLAGS) -o $@ $^

%: %.o
	$(CXX) -o $@ $^ $(LDFLAGS)

