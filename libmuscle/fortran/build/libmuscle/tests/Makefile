src_dir := $(CURDIR)/../../../src
libmuscle_testdir := $(src_dir)/libmuscle/tests
VPATH := $(libmuscle_testdir)

unit_tests := $(wildcard $(libmuscle_testdir)/test*.f03)
integration_tests := $(wildcard $(libmuscle_testdir)/*test.f03)
all_sources := $(wildcard $(libmuscle_testdir)/*.f03)

unit_test_bins := $(unit_tests:$(libmuscle_testdir)/%.f03=%)
integration_test_bins := $(integration_tests:$(libmuscle_testdir)/%.f03=%)
objects := $(all_sources:$(libmuscle_testdir)/%.f03=%.o)

ifndef MUSCLE_ENABLE_MPI
integration_tests := $(filter-out mpi%,$(integration_tests))
integration_test_bins := $(filter-out mpi%,$(integration_test_bins))
endif

all_tests := $(unit_test_bins) $(integration_test_bins)


.PHONY: test
test: $(foreach bin,$(unit_test_bins),run_$(bin))

.PHONY: tests
tests: $(all_tests)

.PHONY: clean
clean:
	rm -f *.o *.mod
	rm -f $(all_tests)

.PHONY: distclean
distclean: clean

cleantargets := clean distclean
ifeq "$(filter $(MAKECMDGOALS),$(cleantargets))" ""

EXTRA_LINK_DIRS := $(foreach DIR,$(DEP_DIRS),-Wl,-rpath-link,$(DIR)/lib)

FFLAGS += -std=f2003 -I. -I.. -I../../ymmsl

CPP_BUILD_DIR := $(CURDIR)/../../../../cpp/build

LDFLAGS += $(CURDIR)/../libmuscle_fortran.a $(CURDIR)/../../ymmsl/libymmsl_fortran.a
LDFLAGS += $(CPP_BUILD_DIR)/libmuscle/libmuscle_d.a $(CPP_BUILD_DIR)/ymmsl/libymmsl_d.a

LDFLAGS2 := $(LDFLAGS)
LDFLAGS2 += $(CURDIR)/../../../../cpp/build/muscle_manager_protocol/libmmp.a
LDFLAGS2 += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs protobuf)
LDFLAGS2 += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs grpc grpc++)
LDFLAGS2 += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs msgpack)
LDFLAGS2 += $(EXTRA_LINK_DIRS)
LDFLAGS2 += -lstdc++

endif

assert.o: $(libmuscle_testdir)/assert.f03
	$(FC) $(FFLAGS) $(DEBUGFLAGS) -c $< -o $@

%.o: $(libmuscle_testdir)/%.f03 assert.o
	$(FC) $(FFLAGS) $(DEBUGFLAGS) -c $< -o $@

test_%: test_%.o assert.o
	$(FC) $(FFLAGS) $(DEBUGFLAGS) $^ -o $@ $(LDFLAGS2)

%_test: %_test.o assert.o
	$(FC) $(FFLAGS) $(DEBUGFLAGS) $^ -o $@ $(LDFLAGS2)


empty :=
space := $(empty) $(empty)
test_dep_lib_paths := $(subst $(space),:,$(foreach DIR,$(DEP_DIRS),$(DIR)/lib))

.PHONY: run_test%
run_test%: test%
	export LD_LIBRARY_PATH=$(test_dep_lib_paths) ; ./$<

