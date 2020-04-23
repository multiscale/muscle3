export TOOLDIR := $(CURDIR)/scripts/gmake

version_file := $(CURDIR)/VERSION
export muscle_version := $(shell cat $(version_file))
export major_version := $(shell sed -e 's/^\([0-9]*\)\..*/\1/' $(version_file))
export minor_version := $(shell sed -e 's/^[0-9]*\.\([0-9]*\)\..*/\1/' $(version_file))
export patch_version := $(shell sed -e 's/^[0-9]*\.[0-9]*\.\([0-9]*\).*/\1/' $(version_file))


.PHONY: all
all: cpp fortran
	@echo
	@echo '    All done, now you can install MUSCLE 3 using:'
	@echo
	@echo '        PREFIX=/path/to/install make install'
	@echo

.PHONY: test
test: test_python test_scripts test_cpp test_fortran

.PHONY: test_python_only
test_python_only:
	MUSCLE_TEST_PYTHON_ONLY=1 python3 setup.py test

.PHONY: test_python
test_python: cpp_tests fortran_tests
	python3 setup.py test

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
	export MUSCLE3_HOME=$(CURDIR)/libmuscle/build/test_install && $(MAKE) -C docs/source/examples test


.PHONY: install
install: all
	cd libmuscle/cpp && $(MAKE) install
	cd libmuscle/fortran && $(MAKE) install
	@echo
	@echo '********************************************************************'
	@echo '*                                                                  *'
	@echo "    MUSCLE 3 is now installed in $(PREFIX)."
	@echo '*                                                                  *'
	@echo '*   To build your model with MUSCLE 3, use the following options   *'
	@echo "*   on your compiler's command line:                               *"
	@echo '*                                                                  *'
	@echo '*   C++ without MPI:                                               *'
	@echo '*                                                                  *'
	@echo "        Compiling: -I$(PREFIX)/include"
	@echo "        Linking: -L$(PREFIX)/lib -lymmsl -lmuscle"
	@echo '*                                                                  *'
	@echo '*   C++ with MPI:                                                  *'
	@echo '*                                                                  *'
	@echo "        Compiling: -I$(PREFIX)/include -DMUSCLE_ENABLE_MPI"
	@echo "        Linking: -L$(PREFIX)/lib -lymmsl -lmuscle_mpi"
	@echo '*                                                                  *'
	@echo '*   Fortran without MPI:                                           *'
	@echo '*                                                                  *'
	@echo "        Compiling: -I$(PREFIX)/include"
	@echo "        Linking: -L$(PREFIX)/lib -lymmsl_fortran"
	@echo "                 -lmuscle_fortran -lymmsl -lmuscle"
	@echo '*                                                                  *'
	@echo '*   Fortran with MPI:                                              *'
	@echo '*                                                                  *'
	@echo "        Compiling: -I$(PREFIX)/include"
	@echo "        Linking: -L$(PREFIX)/lib -lymmsl_fortran"
	@echo "                 -lmuscle_mpi_fortran -lymmsl -lmuscle_mpi"
	@echo '*                                                                  *'
	@echo '*                                                                  *'
	@echo "    You can also use pkg-config. Add $(PREFIX)/lib/pkgconfig"
	@echo '*   to your PKG_CONFIG_PATH environment variable and use module    *'
	@echo '*   names libmuscle, libmuscle_mpi, libmuscle_fortran or           *'
	@echo '*   libmuscle_mpi_fortran.                                         *'
	@echo '*                                                                  *'
	@echo '*   If the directory you installed MUSCLE 3 in is not in your      *'
	@echo "*   system's library search path, then you have to set             *"
	@echo '*   LD_LIBRARY_PATH before compiling, linking or running:          *'
	@echo '*                                                                  *'
	@echo "       export LD_LIBRARY_PATH=\$$LD_LIBRARY_PATH:$(PREFIX)/lib"
	@echo '*                                                                  *'
	@echo '*   If you get a "cannot open shared object file" error which      *'
	@echo '*   mentions libmuscle or ymmsl, then this is most likely the      *'
	@echo '*   problem, and setting LD_LIBRARY_PATH will fix it.              *'
	@echo '*                                                                  *'
	@echo '********************************************************************'

.PHONY: docs
docs:
	python3 setup.py build_sphinx

.PHONY: docsclean
docsclean:
	rm -rf docs/build/*
	rm -rf docs/doxygen/html/*
	rm -rf docs/doxygen/xml/*

.PHONY: clean
clean:
	cd libmuscle/cpp && $(MAKE) clean
	cd libmuscle/fortran && $(MAKE) clean
	cd scripts && $(MAKE) clean
	cd docs/source/examples && $(MAKE) clean

.PHONY: distclean
distclean:
	cd libmuscle/cpp && $(MAKE) distclean
	cd libmuscle/fortran && $(MAKE) distclean
	cd scripts && $(MAKE) distclean
	cd docs/source/examples && $(MAKE) clean

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

# This rebuilds the gRPC generated code; for development only.
.PHONY: grpc
grpc:
	# Python
	python -m grpc_tools.protoc -Imuscle_manager_protocol --python_out=muscle_manager_protocol --grpc_python_out=muscle_manager_protocol --mypy_out=muscle_manager_protocol muscle_manager_protocol/muscle_manager_protocol.proto

	# C++
	pb_prefix=$$(PKG_CONFIG_PATH=libmuscle/cpp/build/protobuf/protobuf/lib/pkgconfig pkg-config --variable=prefix protobuf) && \
			grpc_prefix=$$(PKG_CONFIG_PATH=libmuscle/cpp/build/grpc/grpc/lib/pkgconfig pkg-config --variable=prefix grpc) && \
			PATH=$${pb_prefix}/bin:$${PATH} && export LD_LIBRARY_PATH=$${pb_prefix}/lib && \
			protoc --grpc_out=libmuscle/cpp/src --plugin=protoc-gen-grpc=$${grpc_prefix}/bin/grpc_cpp_plugin muscle_manager_protocol/muscle_manager_protocol.proto
	pb_prefix=$$(PKG_CONFIG_PATH=libmuscle/cpp/build/protobuf/protobuf/lib/pkgconfig pkg-config --variable=prefix protobuf) && \
			PATH=$${pb_prefix}/bin:$${PATH} && export LD_LIBRARY_PATH=$${pb_prefix}/lib && \
			protoc --cpp_out=libmuscle/cpp/src muscle_manager_protocol/muscle_manager_protocol.proto

# This rebuilds the auto-generated native bindings; for development only.
.PHONY: bindings
bindings:
	scripts/make_ymmsl_api.py --fortran-c-wrappers >libmuscle/cpp/src/ymmsl/bindings/ymmsl_fortran_c.cpp
	scripts/make_ymmsl_api.py --fortran-module >libmuscle/fortran/src/ymmsl/ymmsl.f03
	scripts/make_ymmsl_api.py --fortran-exports libmuscle/cpp/build/ymmsl/ymmsl.version.in libmuscle/cpp/build/ymmsl/ymmsl.version
	scripts/make_libmuscle_api.py --fortran-c-wrappers >libmuscle/cpp/src/libmuscle/bindings/libmuscle_fortran_c.cpp
	scripts/make_libmuscle_api.py --fortran-module >libmuscle/fortran/src/libmuscle/libmuscle.f03
	scripts/make_libmuscle_api.py --fortran-exports libmuscle/cpp/build/libmuscle/libmuscle.version.in libmuscle/cpp/build/libmuscle/libmuscle.version
	scripts/make_libmuscle_api.py --fortran-mpi-c-wrappers >libmuscle/cpp/src/libmuscle/bindings/libmuscle_mpi_fortran_c.cpp
	scripts/make_libmuscle_api.py --fortran-mpi-module >libmuscle/fortran/src/libmuscle/libmuscle_mpi.f03
	scripts/make_libmuscle_api.py --fortran-mpi-exports libmuscle/cpp/build/libmuscle/libmuscle.version.in libmuscle/cpp/build/libmuscle/libmuscle_mpi.version
