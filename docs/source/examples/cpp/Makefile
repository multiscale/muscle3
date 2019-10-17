CXX ?= g++
CXXFLAGS += -g -I$(MUSCLE3_HOME)/include
LDFLAGS += -L$(MUSCLE3_HOME)/lib -lymmsl -lmuscle_d


binaries := reaction diffusion mc_driver load_balancer


.PHONY: all
all: $(binaries)

.PHONY: clean
clean:
	rm -f $(binaries)


%: %.cpp
	LD_LIBRARY_PATH=$(MUSCLE3_HOME)/lib:$(LD_LIBRARY_PATH) $(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)
