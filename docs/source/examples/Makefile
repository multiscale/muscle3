ifeq "$(filter $(MAKECMDGOALS), clean)" ""
ifndef MUSCLE3_HOME
$(error MUSCLE3_HOME is not defined, source muscle3.env to build)
endif
endif

.PHONY: all
all: python cpp fortran rd_implementations.ymmsl

.PHONY: test
test: all
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rd_python.ymmsl rd_settings.ymmsl
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rd_cpp.ymmsl rd_settings.ymmsl
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rd_fortran.ymmsl rd_settings.ymmsl
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rd_python_cpp.ymmsl rd_settings.ymmsl
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rd_python_fortran.ymmsl rd_settings.ymmsl
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rdmc_cpp.ymmsl rdmc_settings.ymmsl
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rdmc_fortran.ymmsl rdmc_settings.ymmsl

.PHONY: test_mpi_cpp
test_mpi_cpp: all
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rd_cpp_mpi.ymmsl rd_settings.ymmsl

.PHONY: test_mpi_fortran
test_mpi_fortran: all
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rd_fortran_mpi.ymmsl rd_settings.ymmsl

ifdef MUSCLE_ENABLE_CPP_MPI
test: test_mpi_cpp
endif

ifdef MUSCLE_ENABLE_FORTRAN_MPI
test: test_mpi_fortran
endif

.PHONY: python
python:
	$(MAKE) -C python all

.PHONY: cpp
cpp:
	$(MAKE) -C cpp all

.PHONY: fortran
fortran:
	$(MAKE) -C fortran all

rd_implementations.ymmsl: rd_implementations.ymmsl.in
	sed -e "s^MUSCLE3_EXAMPLES^$(shell pwd)^g" $^ | sed -e "s^MUSCLE3_HOME^${MUSCLE3_HOME}^g" >$@

.PHONY: clean
clean:
	$(MAKE) -C cpp clean
	$(MAKE) -C fortran clean
	$(MAKE) -C python clean
	rm -f rd_implementations.ymmsl
	rm -rf run_*
