ifeq "$(filter $(MAKECMDGOALS), clean)" ""
ifndef MUSCLE3_HOME
$(error MUSCLE3_HOME is not defined, use 'MUSCLE3_HOME=/path/to/muscle3 make <target>' to build)
endif
endif

export PKG_CONFIG_PATH := $(MUSCLE3_HOME)/lib/pkgconfig:$(PKG_CONFIG_PATH)

.PHONY: all
all: python cpp fortran rd_implementations.ymmsl

.PHONY: test
test: all
	LD_LIBRARY_PATH=${MUSCLE3_HOME}/lib muscle_manager --start-all rd_implementations.ymmsl rd_python.ymmsl rd_settings.ymmsl
	LD_LIBRARY_PATH=${MUSCLE3_HOME}/lib muscle_manager --start-all rd_implementations.ymmsl rd_cpp.ymmsl rd_settings.ymmsl
	LD_LIBRARY_PATH=${MUSCLE3_HOME}/lib muscle_manager --start-all rd_implementations.ymmsl rd_fortran.ymmsl rd_settings.ymmsl
	LD_LIBRARY_PATH=${MUSCLE3_HOME}/lib muscle_manager --start-all rd_implementations.ymmsl rd_python_cpp.ymmsl rd_settings.ymmsl
	LD_LIBRARY_PATH=${MUSCLE3_HOME}/lib muscle_manager --start-all rd_implementations.ymmsl rd_python_fortran.ymmsl rd_settings.ymmsl
	LD_LIBRARY_PATH=${MUSCLE3_HOME}/lib muscle_manager --start-all rd_implementations.ymmsl rdmc_cpp.ymmsl rdmc_settings.ymmsl
	LD_LIBRARY_PATH=${MUSCLE3_HOME}/lib muscle_manager --start-all rd_implementations.ymmsl rdmc_fortran.ymmsl rdmc_settings.ymmsl

.PHONY: test_mpi
test_mpi: all
	LD_LIBRARY_PATH=${MUSCLE3_HOME}/lib muscle_manager --start-all rd_implementations.ymmsl rd_cpp_mpi.ymmsl rd_settings.ymmsl
	LD_LIBRARY_PATH=${MUSCLE3_HOME}/lib muscle_manager --start-all rd_implementations.ymmsl rd_fortran_mpi.ymmsl rd_settings.ymmsl

ifdef MUSCLE_ENABLE_MPI
test: test_mpi
endif

.PHONY: python
python:
	make -C python all

.PHONY: cpp
cpp:
	make -C cpp all

.PHONY: fortran
fortran:
	make -C fortran all

rd_implementations.ymmsl: rd_implementations.ymmsl.in
	sed -e "s^MUSCLE3_EXAMPLES^${PWD}^g" $^ | sed -e "s^MUSCLE3_HOME^${MUSCLE3_HOME}^g" >$@

.PHONY: clean
clean:
	make -C cpp clean
	make -C fortran clean
	make -C python clean
	rm -f rd_implementations.ymmsl
	rm -rf run_*
