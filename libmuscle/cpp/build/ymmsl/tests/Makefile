.PHONY: test
test: tests
	./test_ymmsl

.PHONY: tests
tests: test_ymmsl

.PHONY: clean
clean:
	rm -f test_ymmsl *.o

.PHONY: distclean
distclean: clean


# GTest sometimes install in /lib, sometimes in /lib64, depending on platform
ifneq ("$(wildcard $(googletest_ROOT)/lib/libgtest.a)", "")
    googletest_LIB := $(googletest_ROOT)/lib/libgtest.a
else
    googletest_LIB := $(googletest_ROOT)/lib64/libgtest.a
endif

src_dir := $(CURDIR)/../../../src
ymmsl_testdir := $(src_dir)/ymmsl/tests
VPATH := $(ymmsl_testdir)

CXXFLAGS += -isystem $(googletest_ROOT)/include -pthread

%.o: %.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

test_objects := main.o test_component.o test_identity.o test_settings.o test_model.o

test_ymmsl: $(test_objects) ../libymmsl.a
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(DEBUGFLAGS) $(test_objects) $(googletest_LIB) ../libymmsl_d.a -o $@

