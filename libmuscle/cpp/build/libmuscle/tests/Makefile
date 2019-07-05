.PHONY: tests
tests: test_libmuscle

.PHONY: clean
clean:
	rm -f test_ymmsl *.o
	rm -f test_libmuscle


src_dir := $(CURDIR)/../../../src
libmuscle_testdir := $(src_dir)/libmuscle/tests
VPATH := $(libmuscle_testdir)

CXXFLAGS += -isystem $(googletest_ROOT)/include -pthread

%.o: %.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

test_objects := test_operator.o

test_libmuscle: $(test_objects)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $< -o $@ $(googletest_ROOT)/lib/libgtest.a ../../ymmsl/libymmsl.a ../libmuscle.a

