src_dir := $(CURDIR)/../../../src
libmuscle_testdir := $(src_dir)/libmuscle/tests
VPATH := $(libmuscle_testdir)

unit_tests := $(wildcard $(libmuscle_testdir)/test*.cpp)
integration_tests := $(wildcard $(libmuscle_testdir)/*test.cpp)

unit_test_bins := $(unit_tests:$(libmuscle_testdir)/%.cpp=%)
integration_test_bins := $(integration_tests:$(libmuscle_testdir)/%.cpp=%)

ifndef MUSCLE_ENABLE_MPI
integration_tests := $(filter-out mpi%,$(integration_tests))
integration_test_bins := $(filter-out mpi%,$(integration_test_bins))
endif

all_tests := $(unit_test_bins) $(integration_test_bins)
deps := $(all_tests:%=%.d)


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

EXTRA_LINK_DIRS := $(foreach DIR,$(DEP_DIRS),-Wl,-rpath-link,$(DIR)/lib)

CXXFLAGS += -I$(libmuscle_testdir) -isystem $(googletest_ROOT)/include -pthread

LDFLAGS += $(CURDIR)/../libmuscle_d.a $(CURDIR)/../../ymmsl/libymmsl_d.a
LDFLAGS += $(googletest_ROOT)/lib/libgtest.a -pthread

LDFLAGS2 := $(LDFLAGS)
LDFLAGS2 += $(CURDIR)/../../muscle_manager_protocol/libmmp.a
LDFLAGS2 += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs protobuf)
LDFLAGS2 += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs grpc grpc++)
LDFLAGS2 += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs msgpack)
LDFLAGS2 += $(EXTRA_LINK_DIRS)

-include $(deps)

endif

%.d: %.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -E -MM -MT $(@:.d=.o) $< -o $@

%.o: %.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(DEBUGFLAGS) -c $< -o $@

test_%: test_%.o $(CURDIR)/../libmuscle_d.a $(CURDIR)/../../ymmsl/libymmsl_d.a
	$(CXX) $(DEBUGFLAGS) $< -o $@ $(LDFLAGS2)

%_test: %_test.o $(CURDIR)/../libmuscle_d.a $(CURDIR)/../../ymmsl/libymmsl_d.a
	$(CXX) $(DEBUGFLAGS) $< -o $@ $(LDFLAGS2)

test_communicator.o: test_communicator.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(DEBUGFLAGS) -c $< -o $@ -pthread

test_communicator: test_communicator.o $(CURDIR)/../../ymmsl/libymmsl_d.a
	$(CXX) $(DEBUGFLAGS) $^ -o $@ $(googletest_ROOT)/lib/libgtest.a -pthread

test_instance.o: test_instance.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(DEBUGFLAGS) -c $< -o $@ -pthread

test_instance: test_instance.o $(CURDIR)/../../ymmsl/libymmsl_d.a
	$(CXX) $(DEBUGFLAGS) $^ -o $@ $(googletest_ROOT)/lib/libgtest.a -pthread $(LDFLAGS2)

test_logging.o: test_logging.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(DEBUGFLAGS) -c $< -o $@ -pthread

test_logging: test_logging.o $(CURDIR)/../../ymmsl/libymmsl_d.a
	$(CXX) $(DEBUGFLAGS) $^ -o $@ $(googletest_ROOT)/lib/libgtest.a -pthread

mpi_micro_model_test: mpi_micro_model_test.cpp $(CURDIR)/../../ymmsl/libymmsl_d.a $(CURDIR)/../../libmuscle/libmuscle_mpi_d.a
	$(MPICXX) $(CXXFLAGS) $(DEBUGFLAGS) -I$(CURDIR)/.. $(MPIFLAGS) $^ -o $@ $(LDFLAGS2)

mpi_component_test: mpi_component_test.cpp $(CURDIR)/../../ymmsl/libymmsl_d.a $(CURDIR)/../libmuscle_mpi_d.a
	$(MPICXX) $(CXXFLAGS) $(DEBUGFLAGS) -I$(CURDIR)/.. $(MPIFLAGS) $^ -o $@ $(LDFLAGS2)


empty :=
space := $(empty) $(empty)
test_dep_lib_paths := $(subst $(space),:,$(foreach DIR,$(DEP_DIRS),$(DIR)/lib))

.PHONY: run_test%
run_test%: test%
	export LD_LIBRARY_PATH=$(test_dep_lib_paths) ; $(VALGRIND) ./$<

# This uses setrlimit, which is not compatible with Valgrind, so run without
.PHONY: run_test_data_memory_use
run_test_data_memory_use: test_data_memory_use
	export LD_LIBRARY_PATH=$(test_dep_lib_paths) ; ./$<
