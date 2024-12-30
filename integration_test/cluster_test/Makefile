.PHONY: all
all: component_$(MPI_TYPE)


CXXFLAGS += $(shell pkg-config --cflags libmuscle_mpi ymmsl)
LDLIBS += $(shell pkg-config --libs libmuscle_mpi ymmsl)

CXXFLAGS += -g

component_$(MPI_TYPE): component.cpp
	mpicxx -o $@ $(CXXFLAGS) $^ $(LDLIBS)

