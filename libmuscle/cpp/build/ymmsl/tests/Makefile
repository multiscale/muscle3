.PHONY: tests
tests: test_ymmsl

.PHONY: clean
clean:
	rm -f test_ymmsl *.o


src_dir := $(CURDIR)/../../../src
ymmsl_testdir := $(src_dir)/ymmsl/tests
VPATH := $(ymmsl_testdir)

CXXFLAGS += -isystem $(googletest_ROOT)/include -pthread

%.o: %.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

test_objects := test_compute_element.o

test_ymmsl: $(test_objects)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $< $(googletest_ROOT)/lib/libgtest.a ../libymmsl.a -o $@

