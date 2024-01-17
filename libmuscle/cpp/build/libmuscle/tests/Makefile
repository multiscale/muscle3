src_dir := $(CURDIR)/../../../src
libmuscle_testdir := $(src_dir)/libmuscle/tests
VPATH := $(libmuscle_testdir)

unit_tests := $(wildcard $(libmuscle_testdir)/test*.cpp)
integration_tests := $(wildcard $(libmuscle_testdir)/*test.cpp)

unit_test_bins := $(unit_tests:$(libmuscle_testdir)/%.cpp=%)
integration_test_bins := $(integration_tests:$(libmuscle_testdir)/%.cpp=%)

ifndef MUSCLE_ENABLE_CPP_MPI
integration_tests := $(filter-out mpi%,$(integration_tests))
integration_test_bins := $(filter-out mpi%,$(integration_test_bins))
endif

all_tests := $(unit_test_bins) $(integration_test_bins)
deps := $(all_tests:%=%.d)

# GTest sometimes installs in /lib, sometimes in /lib64, depending on platform
ifneq ("$(wildcard $(googletest_ROOT)/lib/libgtest.a)", "")
    googletest_LIB := $(googletest_ROOT)/lib/libgtest.a
else
    googletest_LIB := $(googletest_ROOT)/lib64/libgtest.a
endif

GTEST_OPTIONS = --gtest_catch_exceptions=0


.PHONY: test
test: $(foreach bin,$(unit_test_bins),run_$(bin)) $(foreach bin,$(api_test_bins),run_$(bin))

.PHONY: tests
tests: $(all_tests)

.PHONY: clean
clean:
	rm -f *.d
	rm -f *.o
	rm -f $(all_tests)

.PHONY: distclean
distclean: clean

cleantargets := clean distclean
ifeq "$(filter $(MAKECMDGOALS),$(cleantargets))" ""

EXTRA_LINK_DIRS := $(foreach DIR,$(DEP_DIRS),-Wl,-rpath,$(DIR)/lib)

CXXFLAGS += -I$(libmuscle_testdir) -isystem $(googletest_ROOT)/include -pthread
CXXFLAGS += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_PATH):$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --cflags msgpack)
CXXFLAGS += -DTESTING $(DEBUGFLAGS)

LDFLAGS += $(CURDIR)/../libmuscle_d.a $(CURDIR)/../../ymmsl/libymmsl_d.a
LDFLAGS += $(googletest_LIB) -pthread

LDFLAGS2 := $(LDFLAGS)
LDFLAGS2 += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_PATH):$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs msgpack)
LDFLAGS2 += $(EXTRA_LINK_DIRS)

-include $(deps)

endif

%.d: %.cpp
	$(CXX) $(CXXFLAGS) -E -MM -MT $(@:.d=.o) $< -o $@

mpi%.d: mpi%.cpp
	$(MPICXX) $(CXXFLAGS) -E -MM -MT $(@:.d=.o) $< -o $@

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

test_%: test_%.o $(CURDIR)/../libmuscle_d.a $(CURDIR)/../../ymmsl/libymmsl_d.a
	$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS2)

%_test: %_test.o $(CURDIR)/../libmuscle_d.a $(CURDIR)/../../ymmsl/libymmsl_d.a
	$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS2)

test_communicator.o: test_communicator.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@ -pthread

test_communicator: test_communicator.o $(CURDIR)/../../ymmsl/libymmsl_d.a
	$(CXX) $(CXXFLAGS) $^ -o $@ $(googletest_LIB) -pthread

test_instance.o: test_instance.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@ -pthread

test_instance: test_instance.o $(CURDIR)/../../ymmsl/libymmsl_d.a
	$(CXX) $(CXXFLAGS) $^ -o $@ $(googletest_LIB) -pthread $(LDFLAGS2)

test_logging.o: test_logging.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@ -pthread

test_logging: test_logging.o $(CURDIR)/../../ymmsl/libymmsl_d.a
	$(CXX) $(CXXFLAGS) $^ -o $@ $(googletest_LIB) -pthread

mpi_micro_model_test: mpi_micro_model_test.cpp $(CURDIR)/../../ymmsl/libymmsl_d.a $(CURDIR)/../../libmuscle/libmuscle_mpi_d.a
	$(MPICXX) $(CXXFLAGS) -I$(CURDIR)/.. $(MPIFLAGS) $^ -o $@ $(LDFLAGS2)

mpi_component_test: mpi_component_test.cpp $(CURDIR)/../../ymmsl/libymmsl_d.a $(CURDIR)/../libmuscle_mpi_d.a
	$(MPICXX) $(CXXFLAGS) -I$(CURDIR)/.. $(MPIFLAGS) $^ -o $@ $(LDFLAGS2)

mpi_snapshot_micro_test: mpi_snapshot_micro_test.cpp $(CURDIR)/../../ymmsl/libymmsl_d.a $(CURDIR)/../libmuscle_mpi_d.a
	$(MPICXX) $(CXXFLAGS) -I$(CURDIR)/.. $(MPIFLAGS) $^ -o $@ $(LDFLAGS2)


empty :=
space := $(empty) $(empty)
test_dep_lib_paths := $(subst $(space),:,$(foreach DIR,$(DEP_DIRS),$(DIR)/lib))

.PHONY: run_test%
run_test%: test%
	export LD_LIBRARY_PATH=$(test_dep_lib_paths):$(LD_LIBRARY_PATH) ; $(VALGRIND) ./$< $(GTEST_OPTIONS)

# This uses setrlimit, which is not compatible with Valgrind, so run without
.PHONY: run_test_data_memory_use
run_test_data_memory_use: test_data_memory_use
	export LD_LIBRARY_PATH=$(test_dep_lib_paths):$(LD_LIBRARY_PATH) ; ./$< $(GTEST_OPTIONS)
