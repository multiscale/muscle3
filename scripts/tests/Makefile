all: test_use_echolib

CXX?=g++
FC?=gfortran

ifneq (,$(filter ifort ifx, $(FC)))
	FFLAGS += -e03
else
	FFLAGS += -std=f2003
endif

DEBUGFLAGS += -g -pedantic


.PHONY: clean
clean:
	rm -f echolib_fortran_c.cpp echolib.f90 libecholib.so echolib.mod test_use_echolib

.PHONY: distclean
distclean: clean


echolib_fortran_c.cpp: ../api_generator.py make_echolib_api.py
	PYTHONPATH=$(PWD)/../ ./make_echolib_api.py --fortran-c-wrappers >echolib_fortran_c.cpp

echolib.f90: ../api_generator.py make_echolib_api.py
	PYTHONPATH=$(PWD)/../ ./make_echolib_api.py --fortran-module >echolib.f90

libecholib.so: echolib.hpp echolib.cpp echolib_fortran_c.cpp cmdlineargs.cpp
	$(CXX) -o $@ -std=c++14 $(DEBUGFLAGS) -I. -fPIC -shared echolib.cpp cmdlineargs.cpp echolib_fortran_c.cpp

test_use_echolib: libecholib.so echolib.f90 test_use_echolib.f90
	$(FC) -o $@ $(FFLAGS) $(DEBUGFLAGS) echolib.f90 test_use_echolib.f90 -L. -lecholib

test: test_use_echolib
	LD_LIBRARY_PATH=$(PWD):$(LD_LIBRARY_PATH) $(VALGRIND) ./test_use_echolib
