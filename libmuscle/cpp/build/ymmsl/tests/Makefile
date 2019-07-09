.PHONY: tests
tests: test_ymmsl

.PHONY: clean
clean:
	rm -f test_ymmsl *.o

.PHONY: distclean
distclean: clean


src_dir := $(CURDIR)/../../../src
ymmsl_testdir := $(src_dir)/ymmsl/tests
VPATH := $(ymmsl_testdir)

CXXFLAGS += -isystem $(googletest_ROOT)/include -pthread

%.o: %.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

test_objects := main.o test_compute_element.o test_identity.o

test_ymmsl: $(test_objects) ../libymmsl.a
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(DEBUGFLAGS) $(test_objects) $(googletest_ROOT)/lib/libgtest.a ../libymmsl_d.a -o $@

