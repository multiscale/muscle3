.PHONY: all
all: component_openmpi


CXXFLAGS += $(shell pkg-config --cflags libmuscle_mpi ymmsl)
LDLIBS += $(shell pkg-config --libs libmuscle_mpi ymmsl)

CXXFLAGS += -g

component_openmpi: component.cpp
	mpic++ -o $@ $(CXXFLAGS) $^ $(LDLIBS)

