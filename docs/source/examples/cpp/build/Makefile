CXXFLAGS += -std=c++14 -g $(shell pkg-config --cflags libmuscle ymmsl)
LDFLAGS += $(shell pkg-config --libs libmuscle ymmsl)

MPI_CXXFLAGS := -std=c++14 -g $(shell pkg-config --cflags libmuscle_mpi ymmsl)
MPI_LDFLAGS := $(shell pkg-config --libs libmuscle_mpi ymmsl)


binaries := reaction diffusion mc_driver load_balancer checkpointing_reaction checkpointing_diffusion benchmark
mpi_binaries := reaction_mpi


.PHONY: all
all: $(binaries)

.PHONY: mpi
mpi: $(mpi_binaries)

.PHONY: clean
clean:
	rm -f *.o $(binaries) $(mpi_binaries)


%_mpi.o: ../%_mpi.cpp
	$(MPICXX) -c $(MPI_CXXFLAGS) -o $@ $^

%_mpi: %_mpi.o
	$(MPICXX) -o $@ $^ $(MPI_LDFLAGS)

%.o: ../%.cpp
	$(CXX) -c $(CXXFLAGS) -o $@ $^

%: %.o
	$(CXX) -o $@ $^ $(LDFLAGS)

benchmark.o: ../benchmark.cpp
	$(CXX) -c $(CXXFLAGS) -O3 -march=native -o $@ $^
