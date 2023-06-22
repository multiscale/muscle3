export TOOLDIR := $(CURDIR)/scripts/gmake

version_file := $(CURDIR)/VERSION
export muscle_version := $(shell cat $(version_file))
export major_version := $(shell sed -e 's/^\([0-9]*\)\..*/\1/' $(version_file))
export minor_version := $(shell sed -e 's/^[0-9]*\.\([0-9]*\)\..*/\1/' $(version_file))
export patch_version := $(shell sed -e 's/^[0-9]*\.[0-9]*\.\([0-9]*\).*/\1/' $(version_file))

include $(TOOLDIR)/check_tools.make

.PHONY: all
all: cpp fortran
ifeq "$(filter $(MAKECMDGOALS), install)" ""
	@echo
	@echo '    All done, now you can install MUSCLE3 using:'
	@echo
	@echo '        PREFIX=/path/to/install make install'
	@echo
endif

.PHONY: test
test: test_python test_scripts test_cpp test_fortran

.PHONY: test_python_only
test_python_only:
	MUSCLE_TEST_PYTHON_ONLY=1 tox

.PHONY: test_python
test_python: cpp_tests fortran_tests
	tox

.PHONY: test_cpp
test_cpp: cpp
	cd libmuscle/cpp && $(MAKE) test

.PHONY: test_fortran
test_fortran: fortran_tests
	cd libmuscle/fortran && $(MAKE) test

.PHONY: test_scripts
test_scripts:
	cd scripts && $(MAKE) test

.PHONY: test_install
test_install:
	PREFIX=$(CURDIR)/libmuscle/build/test_install $(MAKE) install

.PHONY: test_examples
test_examples: test_install
	. $(CURDIR)/libmuscle/build/test_install/bin/muscle3.env && $(MAKE) -C docs/source/examples test

.PHONY: benchmark
benchmark: test_install
	. $(CURDIR)/libmuscle/build/test_install/bin/muscle3.env && $(MAKE) -C docs/source/examples benchmark


.PHONY: install
install: all
	cd libmuscle/cpp && $(MAKE) install
	cd libmuscle/fortran && $(MAKE) install
	@echo
	@echo '********************************************************************'
	@echo '*                                                                  *'
	@echo "    MUSCLE3 is now installed in $(PREFIX)."
	@echo '*                                                                  *'
	@echo '*   To set up your environment, run:                               *'
	@echo '*                                                                  *'
	@echo "    source $(PREFIX)/bin/muscle3.env"
	@echo '*                                                                  *'
	@echo '*   To then build your model with MUSCLE3, use the following      *'
	@echo "*   options on your compiler's command line:                       *"
	@echo '*                                                                  *'
	@echo '*   C++ without MPI:                                               *'
	@echo '*                                                                  *'
	@echo '*       Compiling: -I$${MUSCLE3_HOME}/include                       *'
	@echo '*       Linking: -L$${MUSCLE3_HOME}/lib -lymmsl -lmuscle            *'
	@echo '*                                                                  *'
	@echo '*   C++ with MPI:                                                  *'
	@echo '*                                                                  *'
	@echo '*       Compiling: -I$${MUSCLE3_HOME}/include -DMUSCLE_ENABLE_MPI   *'
	@echo '*       Linking: -L$${MUSCLE3_HOME}/lib -lymmsl -lmuscle_mpi        *'
	@echo '*                                                                  *'
	@echo '*   Fortran without MPI:                                           *'
	@echo '*                                                                  *'
	@echo '*       Compiling: -I$${MUSCLE3_HOME}/include                       *'
	@echo '*       Linking: -L$${MUSCLE3_HOME}/lib -lymmsl_fortran             *'
	@echo '*                -lmuscle_fortran -lymmsl -lmuscle                 *'
	@echo '*                                                                  *'
	@echo '*   Fortran with MPI:                                              *'
	@echo '*                                                                  *'
	@echo '*       Compiling: -I$${MUSCLE3_HOME}/include                       *'
	@echo '*       Linking: -L$${MUSCLE3_HOME}/lib -lymmsl_fortran             *'
	@echo '*                -lmuscle_mpi_fortran -lymmsl -lmuscle_mpi         *'
	@echo '*                                                                  *'
	@echo '*                                                                  *'
	@echo '*   You can also use pkg-config, with module names libmuscle,      *'
	@echo '*   libmuscle_mpi, libmuscle_fortran, or libmuscle_mpi_fortran,    *'
	@echo '*   and for ymmsl either ymmsl or ymmsl_fortran. Be sure to        *'
	@echo '*   source the env file as described above, or pkg-config will not *'
	@echo '*   be able to find MUSCLE3.                                       *'
	@echo '*                                                                  *'
	@echo '*   If you get a "Cannot open shared object file" error which      *'
	@echo '*   mentions libmuscle or ymmsl, then you have probably forgotten  *'
	@echo '*   to source the env file.                                        *'
	@echo '*                                                                  *'
	@echo '********************************************************************'

.PHONY: docs
docs:
	tox -e docs

.PHONY: docsclean
docsclean:
	rm -rf docs/build/*
	rm -rf docs/build/.doctrees
	rm -f docs/build/.buildinfo
	rm -rf docs/doxygen/html/*
	rm -rf docs/doxygen/xml/*

.PHONY: clean
clean:
	cd libmuscle/cpp && $(MAKE) clean
	cd libmuscle/fortran && $(MAKE) clean
	cd scripts && $(MAKE) clean
	cd docs/source/examples && $(MAKE) clean
	rm -rf ./build
	rm -rf $(CURDIR)/libmuscle/build/test_install/*
	rm -rf libmuscle/python/libmuscle/version.py

.PHONY: distclean
distclean:
	cd libmuscle/cpp && $(MAKE) distclean
	cd libmuscle/fortran && $(MAKE) distclean
	cd scripts && $(MAKE) distclean
	cd docs/source/examples && $(MAKE) clean
	rm -rf ./build
	rm -rf $(CURDIR)/libmuscle/build/test_install/*
	rm -rf libmuscle/python/libmuscle/version.py

.PHONY: fortran
fortran: cpp
	cd libmuscle/fortran && $(MAKE)

.PHONY: cpp
cpp:
	cd libmuscle/cpp && $(MAKE)

.PHONY: cpp_tests
cpp_tests: cpp
	cd libmuscle/cpp && $(MAKE) tests

.PHONY: fortran_tests
fortran_tests: fortran cpp_tests
	cd libmuscle/fortran && $(MAKE) tests

# This rebuilds the auto-generated native bindings; for development only.
.PHONY: bindings
bindings:
	scripts/make_ymmsl_api.py --fortran-c-wrappers >libmuscle/cpp/src/ymmsl/bindings/ymmsl_fortran_c.cpp
	scripts/make_ymmsl_api.py --fortran-module >libmuscle/fortran/src/ymmsl/ymmsl.f90
	scripts/make_libmuscle_api.py --fortran-c-wrappers >libmuscle/cpp/src/libmuscle/bindings/libmuscle_fortran_c.cpp
	scripts/make_libmuscle_api.py --fortran-module >libmuscle/fortran/src/libmuscle/libmuscle.f90
	scripts/make_libmuscle_api.py --fortran-mpi-c-wrappers >libmuscle/cpp/src/libmuscle/bindings/libmuscle_mpi_fortran_c.cpp
	scripts/make_libmuscle_api.py --fortran-mpi-module >libmuscle/fortran/src/libmuscle/libmuscle_mpi.f90
