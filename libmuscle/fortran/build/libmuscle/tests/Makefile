src_dir := $(CURDIR)/../../../src
libmuscle_testdir := $(src_dir)/libmuscle/tests
VPATH := $(libmuscle_testdir)

unit_tests := $(wildcard $(libmuscle_testdir)/test*.f90)
integration_tests := $(wildcard $(libmuscle_testdir)/*test.f90)
all_sources := $(wildcard $(libmuscle_testdir)/*.f90)

unit_test_bins := $(unit_tests:$(libmuscle_testdir)/%.f90=%)
integration_test_bins := $(integration_tests:$(libmuscle_testdir)/%.f90=%)
objects := $(all_sources:$(libmuscle_testdir)/%.f90=%.o)

ifndef MUSCLE_ENABLE_FORTRAN_MPI
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

FFLAGS += -g -I. -I.. -I../../ymmsl
ifeq ($(FC), ifort)
	FFLAGS += -e03
else
	FFLAGS += -std=f2003
endif


CPP_BUILD_DIR := $(CURDIR)/../../../../cpp/build

LDFLAGS += -pthread $(CURDIR)/../libmuscle_fortran.a $(CURDIR)/../../ymmsl/libymmsl_fortran.a
LDFLAGS += $(CPP_BUILD_DIR)/libmuscle/libmuscle_d.a $(CPP_BUILD_DIR)/ymmsl/libymmsl_d.a

LDFLAGS2 := $(LDFLAGS)
LDFLAGS2 += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIGPATH):$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs msgpack)
LDFLAGS2 += $(EXTRA_LINK_DIRS)
LDFLAGS2 += -lstdc++

LINK_DEPS = $(CURDIR)/../libmuscle_fortran.a $(CURDIR)/../../ymmsl/libymmsl_fortran.a
LINK_DEPS += $(CPP_BUILD_DIR)/libmuscle/libmuscle_d.a $(CPP_BUILD_DIR)/ymmsl/libymmsl_d.a

endif

assert.o: $(libmuscle_testdir)/assert.f90
	$(FC) $(FFLAGS) $(DEBUGFLAGS) -c $< -o $@

%.o: $(libmuscle_testdir)/%.f90 assert.o
	$(FC) $(FFLAGS) $(DEBUGFLAGS) -c $< -o $@

test_%: test_%.o assert.o $(LINK_DEPS)
	$(FC) $(FFLAGS) $(DEBUGFLAGS) $^ -o $@ $(LDFLAGS2)

%_test: %_test.o assert.o $(LINK_DEPS)
	$(FC) $(FFLAGS) $(DEBUGFLAGS) $^ -o $@ $(LDFLAGS2)


empty :=
space := $(empty) $(empty)
test_dep_lib_paths := $(subst $(space),:,$(foreach DIR,$(DEP_DIRS),$(DIR)/lib))

.PHONY: run_test%
run_test%: test%
	export LD_LIBRARY_PATH=$(test_dep_lib_paths):$(LD_LIBRARY_PATH) ; ./$<

