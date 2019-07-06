src_dir := $(CURDIR)/../../../src
libmuscle_testdir := $(src_dir)/libmuscle/tests
VPATH := $(libmuscle_testdir)

source_files := $(wildcard $(libmuscle_testdir)/*.cpp)
all_tests := $(source_files:$(libmuscle_testdir)/%.cpp=%)

.PHONY: tests
tests: $(all_tests)

.PHONY: clean
clean:
	rm -f *.o
	rm -f $(all_tests)


CXXFLAGS += -isystem $(googletest_ROOT)/include -pthread

LDFLAGS += $(CURDIR)/../libmuscle.a $(CURDIR)/../../ymmsl/libymmsl.a
# LDFLAGS += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs protobuf)
# LDFLAGS += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs grpc grpc++)
LDFLAGS += $(googletest_ROOT)/lib/libgtest.a


%.o: %.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

test_%: test_%.o
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $^ -o $@  $(LDFLAGS)

