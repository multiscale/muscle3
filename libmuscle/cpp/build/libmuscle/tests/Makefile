.PHONY: tests
tests: test_libmuscle

.PHONY: clean
clean:
	rm -f test_ymmsl *.o
	rm -f test_libmuscle


src_dir := $(CURDIR)/../../../src
libmuscle_testdir := $(src_dir)/libmuscle/tests
VPATH := $(libmuscle_testdir)
CXXFLAGS += -I$(src_dir)

gtest_dir := $(CURDIR)/../../googletest/googletest

CXXFLAGS += -isystem -I$(gtest_dir)/include -pthread
CXXFLAGS += -I$(protobuf_ROOT)/include

%.o: %.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

test_objects := test_operator.o

test_libmuscle: $(test_objects)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $< -o $@ $(gtest_dir)/lib/libgtest.a ../../ymmsl/libymmsl.a ../libmuscle.a

