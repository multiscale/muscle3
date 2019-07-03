.PHONY: tests
tests: test_ymmsl

.PHONY: clean
clean:
	rm -f test_ymmsl *.o


src_dir := $(CURDIR)/../../../src
ymmsl_testdir := $(src_dir)/ymmsl/tests
VPATH := $(ymmsl_testdir)
CXXFLAGS += -I$(src_dir)

%.o: %.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

test_objects := test_compute_element.o

gtest_dir := ../../googletest/googletest

test_ymmsl: $(test_objects)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -isystem $(gtest_dir)/include -pthread $< $(gtest_dir)/lib/libgtest.a ../libymmsl.a -o $@

