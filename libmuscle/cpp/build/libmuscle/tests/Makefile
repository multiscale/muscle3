src_dir := $(CURDIR)/../../../src
libmuscle_testdir := $(src_dir)/libmuscle/tests
VPATH := $(libmuscle_testdir)

unit_tests := $(wildcard $(libmuscle_testdir)/test*.cpp)
integration_tests := $(wildcard $(libmuscle_testdir)/*test.cpp)
unit_test_bins := $(unit_tests:$(libmuscle_testdir)/%.cpp=%)
integration_test_bins := $(integration_tests:$(libmuscle_testdir)/%.cpp=%)
all_tests := $(unit_test_bins) $(integration_test_bins)

.PHONY: tests
tests: $(all_tests)

.PHONY: clean
clean:
	rm -f *.o
	rm -f $(all_tests)

.PHONY: distclean
distclean: clean


EXTRA_LINK_DIRS := $(foreach DIR,$(DEP_DIRS),-Wl,-rpath-link,$(DIR)/lib)

CXXFLAGS += -isystem $(googletest_ROOT)/include -pthread

LDFLAGS += $(CURDIR)/../libmuscle_d.a $(CURDIR)/../../ymmsl/libymmsl_d.a
LDFLAGS += $(googletest_ROOT)/lib/libgtest.a -pthread

LDFLAGS2 := $(LDFLAGS)
LDFLAGS2 += $(CURDIR)/../../muscle_manager_protocol/libmmp.a
LDFLAGS2 += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs protobuf)
LDFLAGS2 += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs grpc grpc++)
LDFLAGS2 += $(EXTRA_LINK_DIRS)

%.o: %.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

test_%: test_%.o
	$(CXX) $(DEBUGFLAGS) $^ -o $@ $(LDFLAGS)

%_test: %_test.o
	$(CXX) $(DEBUGFLAGS) $^ -o $@ $(LDFLAGS2)

