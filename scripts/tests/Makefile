all: test_use_echolib

CXX?=g++
FORTRAN?=gfortran


.PHONY: clean
clean:
	rm -f echolib_fortran_c.cpp echolib.f03 libecholib.so echolib.mod test_use_echolib

echolib_fortran_c.cpp: ../api_generator.py make_echolib_api.py
	PYTHONPATH=$(PWD)/../ ./make_echolib_api.py --fortran-c-wrappers >echolib_fortran_c.cpp

echolib.f03: ../api_generator.py make_echolib_api.py
	PYTHONPATH=$(PWD)/../ ./make_echolib_api.py --fortran-module >echolib.f03

libecholib.so: echolib.hpp echolib.cpp echolib_fortran_c.cpp cmdlineargs.cpp
	$(CXX) -g -o $@ -std=c++14 -pedantic -I. -fPIC -shared echolib.cpp cmdlineargs.cpp echolib_fortran_c.cpp

test_use_echolib: libecholib.so echolib.f03 test_use_echolib.f03
	$(FORTRAN) -g -std=f2003 -o $@ echolib.f03 test_use_echolib.f03 -L. -lecholib

test: test_use_echolib
	LD_LIBRARY_PATH=$(PWD) ./test_use_echolib
