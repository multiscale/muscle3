CXX ?= g++
MPICXX += mpic++
CXXFLAGS += -std=c++14 -g -I$(MUSCLE3_HOME)/include
MPI_CXXFLAGS := $(CXXFLAGS) -DMUSCLE_ENABLE_MPI

MPI_LDFLAGS := $(LDFLAGS) -L$(MUSCLE3_HOME)/lib -lymmsl -lmuscle_mpi -lmpi
LDFLAGS += -L$(MUSCLE3_HOME)/lib -lymmsl -lmuscle


binaries := reaction diffusion mc_driver load_balancer

ifdef MUSCLE_ENABLE_MPI
    binaries += reaction_mpi
endif


.PHONY: all
all: $(binaries)

.PHONY: clean
clean:
	rm -f $(binaries)


%: %.cpp
	LD_LIBRARY_PATH=$(MUSCLE3_HOME)/lib:$(LD_LIBRARY_PATH) $(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

reaction_mpi: reaction_mpi.cpp
	LD_LIBRARY_PATH=$(MUSCLE3_HOME)/lib:$(LD_LIBRARY_PATH) $(MPICXX) $(MPI_CXXFLAGS) -o $@ $^ $(MPI_LDFLAGS)

