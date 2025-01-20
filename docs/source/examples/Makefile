ifeq "$(filter $(MAKECMDGOALS), clean)" ""
ifndef MUSCLE3_HOME
$(error MUSCLE3_HOME is not defined, source muscle3.env to build)
endif

# Detect tools
tool_var := CXX
tool_command := g++
include detect_tool_implicit.make
tool_command := clang++
include detect_tool_implicit.make

tool_var := MPICXX
tool_command := mpi$(CXX)
include detect_tool.make
tool_command := mpic++
include detect_tool.make

include detect_cpp_type.make

tool_var := FC
tool_command := gfortran
include detect_tool_implicit.make
tool_command := f95
include detect_tool_implicit.make
tool_command := f77
include detect_tool_implicit.make

tool_var := MPIFC
tool_command := mpi$(FC)
include detect_tool.make
tool_command := mpifort
include detect_tool.make
tool_command := mpif90
include detect_tool.make

include detect_fortran_type.make

endif

MPI_EXECUTION_MODEL ?= openmpi


# Main targets
.PHONY: all
all: base

.PHONY: test
test: test_python


ifneq ($(origin CXX), default)
all: cpp
test: test_cpp
endif

ifneq ($(origin FC), default)
all: fortran
test: test_fortran
endif

ifdef MPICXX
all: cpp_mpi
test: test_cpp_mpi
endif

ifdef MPIFC
all: fortran_mpi
test: test_fortran_mpi
endif


.PHONY: base
base: python rd_implementations.ymmsl benchmark_implementations.ymmsl dispatch_implementations.ymmsl



# Specific targets

.PHONY: python
python: rd_implementations.ymmsl
	$(MAKE) -C python all

.PHONY: cpp
cpp: base
	$(MAKE) -C cpp all

.PHONY: cpp_mpi
cpp_mpi: base
	$(MAKE) -C cpp mpi

.PHONY: fortran
fortran: base
	$(MAKE) -C fortran all

.PHONY: fortran_mpi
fortran_mpi: base
	$(MAKE) -C fortran mpi

%.ymmsl: %.ymmsl.in
	sed -e "s^MUSCLE3_EXAMPLES^$(shell pwd)^g" $^ | sed -e "s^MUSCLE3_HOME^${MUSCLE3_HOME}^g" | sed -e "s^EXECUTION_MODEL^${MPI_EXECUTION_MODEL}^g" >$@
	echo "Converted $^ into $@"
	cat $@


.PHONY: clean
clean:
	$(MAKE) -C cpp clean
	$(MAKE) -C fortran clean
	$(MAKE) -C python clean
	rm -f rd_implementations.ymmsl
	rm -f benchmark_implementations.ymmsl
	rm -f dispatch_implementations.ymmsl
	rm -rf run_*/


# Tests

.PHONY: test_python
test_python: base
	. python/build/venv/bin/activate && DONTPLOT=1 muscle_manager --start-all rd_implementations.ymmsl rd_python.ymmsl rd_settings.ymmsl
	. python/build/venv/bin/activate && DONTPLOT=1 muscle_manager --start-all rd_implementations.ymmsl rd_checkpoints_python.ymmsl rd_settings.ymmsl
	# test restarting, sleep 1 second to prevent reusing the same run directory
	. python/build/venv/bin/activate && sleep 1 && DONTPLOT=1 muscle_manager --start-all rd_implementations.ymmsl rd_checkpoints_python.ymmsl rd_settings.ymmsl \
		$$(ls $$(ls -d run_checkpointing_reaction_diffusion_python* | tail -n1)/snapshots/*.ymmsl | head -n1)
	make -C python test

.PHONY: test_cpp
test_cpp: base cpp
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rd_cpp.ymmsl rd_settings.ymmsl
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rd_checkpoints_cpp.ymmsl rd_settings.ymmsl
	# test restarting, sleep 1 second to prevent reusing the same run directory
	. python/build/venv/bin/activate && sleep 1 && muscle_manager --start-all rd_implementations.ymmsl rd_checkpoints_cpp.ymmsl rd_settings.ymmsl \
		$$(ls $$(ls -d run_checkpointing_reaction_diffusion_cpp* | tail -n1)/snapshots/*.ymmsl | head -n1)
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rd_python_cpp.ymmsl rd_settings.ymmsl
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rdmc_cpp.ymmsl rdmc_settings.ymmsl
	. python/build/venv/bin/activate && muscle_manager --start-all dispatch_implementations.ymmsl dispatch_cpp.ymmsl

.PHONY: test_cpp_mpi
test_cpp_mpi: base cpp_mpi
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rd_cpp_mpi.ymmsl rd_settings.ymmsl || cat run_reaction_diffusion_cpp_mpi_*/instances/micro/run_script.sh run_reaction_diffusion_cpp_mpi_*/instances/micro/stderr.txt

.PHONY: test_fortran
test_fortran: base fortran
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rd_fortran.ymmsl rd_settings.ymmsl
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rd_checkpoints_fortran.ymmsl rd_settings.ymmsl
	# test restarting, sleep 1 second to prevent reusing the same run directory
	. python/build/venv/bin/activate && sleep 1 && muscle_manager --start-all rd_implementations.ymmsl rd_checkpoints_fortran.ymmsl rd_settings.ymmsl \
		$$(ls $$(ls -d run_checkpointing_reaction_diffusion_fortran* | tail -n1)/snapshots/*.ymmsl | head -n1)
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rd_python_fortran.ymmsl rd_settings.ymmsl
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rdmc_fortran.ymmsl rdmc_settings.ymmsl

.PHONY: test_fortran_mpi
test_fortran_mpi: base fortran_mpi
	. python/build/venv/bin/activate && muscle_manager --start-all rd_implementations.ymmsl rd_fortran_mpi.ymmsl rd_settings.ymmsl

.PHONY: benchmark
benchmark: base cpp
	. python/build/venv/bin/activate && DONTPLOT=1 muscle_manager --start-all benchmark_implementations.ymmsl benchmark_python.ymmsl benchmark_settings.ymmsl
	. python/build/venv/bin/activate && DONTPLOT=1 muscle_manager --start-all benchmark_implementations.ymmsl benchmark_cpp.ymmsl benchmark_settings.ymmsl

